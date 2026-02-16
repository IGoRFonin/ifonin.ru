---
title: "MCP-серверы на практике: 5 граблей при разработке и использовании"
date: 2026-02-16
lastmod: 2026-02-16
description: "Типичные грабли при разработке MCP-серверов: stdout pollution, axios proxy, REST vs agent design, schema drift и конфигурационные проблемы. Практический гайд с решениями."
tags: ["mcp", "claude-code", "ai-tools", "debugging"]
slug: "mcp-servery-5-grablei-na-praktike"
draft: false
---

Я потратил 185 промптов Claude на отладку MCP-сервера в проекте excalidecks. Сервер работал, тесты проходили, но Claude Desktop отказывался с ним общаться. Молча падал. Проблема? Один console.log() в середине кода ломал весь JSON-RPC протокол.

За последние два месяца я собрал пять типичных граблей, на которые наступают 90% разработчиков. MCP - молодой протокол (запущен в ноябре 2024), best practices еще не устоялись. Ошибки часто молчаливые: JSON-RPC не показывает внятный stack trace, просто разрывает соединение.

Разберем каждую проблему с примерами и решениями.

## Грабля #1: console.log() ломает JSON-RPC

В MCP stdio транспорте stdout зарезервирован ИСКЛЮЧИТЕЛЬНО для JSON-RPC сообщений. Каждая строка - отдельный JSON объект. Клиент парсит входящий поток построчно.

Теперь добавьте где-то в код:

```javascript
console.log("Server starting...");
```

Клиент получает вместо JSON строку "Server starting...". Парсер падает: `SyntaxError: Unexpected token S in JSON at position 0`. Буква S - начало вашего лога.

Я потратил 185 промптов в проекте excalidecks на эту проблему. Сервер запускался, tools регистрировались, но Claude Desktop видел только ошибку парсинга. Решение нашел случайно: запустил сервер вручную и увидел console.log в терминале. В MCP всё должно идти в stderr, не stdout.

**Неправильно:**

```javascript
console.log("[INFO] Server starting");
console.log(`Tool registered: ${toolName}`);
```

**Правильно:**

```javascript
console.error("[INFO] Server starting");
// Или используйте Winston
const logger = winston.createLogger({
  transports: [new winston.transports.Console()]
});
logger.info("Server starting"); // автоматически в stderr
```

Первый день отладки научил меня разнице между stdout и stderr. Которую я не знал раньше. Теперь знаю.

## Грабля #2: Axios + HTTPS proxy = 400

Я настраивал Exa MCP сервер для Claude Code через домашний прокси. Прямой curl работал нормально. Axios внутри Exa сервера возвращал 400 Bad Request.

124 промпта потрачено на отладку. Проблема оказалась в axios v1.7.x: он не умеет правильно туннелировать HTTPS через HTTP-прокси. Вместо CONNECT-запроса axios отправляет обычный HTTP-запрос на HTTPS-порт. Cloudflare отвечает 400.

Решение - preload-скрипт, который патчит https модуль до запуска MCP-сервера:

```javascript
// exa-proxy-preload.js
const proxy = process.env.HTTPS_PROXY || process.env.HTTP_PROXY;
if (proxy) {
  const { HttpsProxyAgent } = require('https-proxy-agent');
  const agent = new HttpsProxyAgent(proxy);

  // Удаляем env vars, чтобы axios не применял свой сломанный прокси
  delete process.env.HTTPS_PROXY;
  delete process.env.HTTP_PROXY;

  // Патчим https модуль - все запросы пойдут через правильный агент
  const https = require('https');
  const origRequest = https.request;
  https.request = function(options, cb) {
    if (typeof options === 'object' && !options.agent) {
      options.agent = agent;
    }
    return origRequest.call(this, options, cb);
  };
}
```

Запуск через NODE_OPTIONS:

```bash
NODE_OPTIONS="--require ./exa-proxy-preload.js" node server.js
```

Это была ночь, когда я понял что curl работает, но axios нет. Ключевой трюк - удалить переменные окружения прокси и подставить свой агент, иначе axios снова всё сломает.

## Грабля #3: REST API thinking vs. Agent-oriented design

Разработчики часто оборачивают существующие REST API как есть. Создают много маленьких инструментов, каждый делает один HTTP-запрос. Для синхронных клиентов это работает. Для AI-агентов - катастрофа.

Агенты имеют ограниченную память (контекст окно). Теряют информацию между round-trips. Не могут вернуться назад и переиграть действие.

Philipp Schmid в январе 2026 провел исследование на реальном use case - Order Tracking.

**Плохой дизайн:**

```javascript
get_order_status(order_id) → status
list_orders(user_id) → [orders]
get_user_by_email(email) → user
```

Агент должен найти заказ по email. Сценарий:

1. get_user_by_email("john@example.com") → user_id=123
2. list_orders(123) → [order1, order2, order3]
3. get_order_status(order1)
4. get_order_status(order2)
5. ...

Результат: fail rate 40%, latency 6+ секунд. Агент теряет контекст, забывает что уже запросил, запрашивает снова.

**Хороший дизайн:**

```javascript
track_order(customer_email) → {
  customer_id, name, email,
  orders: [{order_id, status, items, total}]
}
```

Один вызов. Все данные сразу. Fail rate 2%, latency 2 секунды. В 10 раз надежнее, в 3 раза быстрее.

Philipp резюмировал: "The protocol works fine. The servers don't. MCP is a User Interface for AI agents."

Правила:

1. Один инструмент = одна задача пользователя целиком. Не "создай сообщение" + "отправь уведомление", а "уведоми пользователя о событии"
2. Не больше 5-10 инструментов на сервер. Агент путается, если выбор слишком большой
3. Параметры инструмента - плоские, без вложенности. Не `{user: {name: "John", email: "..."}}`, а просто `user_name, user_email`
4. Ошибки должны объяснять что делать дальше, а не просто "Error 500". Пример: "API key expired, get a new one at settings/api"
5. Имена с префиксом сервиса: `slack_send_message`, не `send_message`. Агент работает с несколькими серверами и должен понимать кому адресован вызов

## Грабля #4: JSON Schema врёт о реальности

Команда Specmatic в 2025 году проверила популярные MCP-серверы автоматическими тестами. Нашли "schema drift" у топовых имплементаций - Hugging Face, Postman, GitHub.

Schema говорит одно, сервер требует другое. LLM читает schema, генерирует запрос, получает ошибку.

**Пример 1:** Hugging Face MCP

```json
{
  "properties": {
    "prompt": {
      "type": "string",
      "description": "The prompt text"
    }
  }
}
```

Нет required. LLM отправляет пустой запрос. Сервер отвечает: "no value provided for the required argument prompt".

**Пример 2:** Numeric bounds в description

```json
{
  "properties": {
    "max_tokens": {
      "type": "number",
      "description": "Maximum tokens, between 1 and 16"
    }
  }
}
```

LLM генерирует 705 (как в других API). Ошибка: "705 is greater than maximum 16".

Правильно:

```json
{
  "properties": {
    "max_tokens": {
      "type": "number",
      "minimum": 1,
      "maximum": 16,
      "description": "Maximum tokens"
    }
  }
}
```

Цитата из Specmatic: "Your schema is the contract you make with the world. If that contract is vague, every automated consumer will eventually break."

Правила:

1. Используйте машиночитаемые поля: required, minimum, maximum, pattern, enum, oneOf
2. Descriptions - НЕ substitute для constraints
3. Тестируйте schema против имплементации через Specmatic
4. Не меняйте требования без версионирования

## Грабля #5: Конфигурационные и PATH проблемы

MCPStack analysis показал: 97% connection failures вызваны пятью факторами.

- 43% - NVM/PATH issues (node не найден в PATH)
- 28% - NVM не инициализирован для процесса хоста
- 15% - invalid JSON синтаксис в config
- 9% - missing dependencies
- 5% - permission issues

**Типичная ошибка:**

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["./server.js"]
    }
  }
}
```

Claude Desktop не найдет node если он установлен через NVM. Относительные пути не работают.

**Правильно:**

```json
{
  "mcpServers": {
    "my-server": {
      "command": "/Users/username/.nvm/versions/node/v18.0.0/bin/node",
      "args": ["/absolute/path/to/server/index.js"],
      "env": {
        "API_KEY": "your-secret-key",
        "NODE_ENV": "production"
      }
    }
  }
}
```

Быстрый диагностический чек-лист:

```bash
which node  # найти абсолютный путь
/path/to/node --version  # проверить доступность
jq . ~/.config/Claude/claude_desktop_config.json  # JSON синтаксис
ls -la /path/to/server.js  # permissions должны быть 755
```

JP Caparas в декабре 2025: "Never hardcode or interpolate your sensitive environment variables. Pass them the documented way."

## Инструменты для отладки

MCP Inspector - обязательный инструмент для тестирования:

```bash
npx @modelcontextprotocol/inspector python server.py
npx @modelcontextprotocol/inspector node ./dist/server.js
```

Видите raw JSON-RPC сообщения в реальном времени. Вызываете tools с тестовыми параметрами. Экспортируете session logs для анализа.

Три уровня логирования:

1. Dev: human-readable, быстрая отладка
2. Prod: JSON, структурированные логи для агрегации
3. Security events: отдельный track для аудита

Используйте Winston или Pino, переключайте формат через NODE_ENV:

```javascript
const format = process.env.NODE_ENV === 'production'
  ? winston.format.json()
  : winston.format.simple();
```

## Финал

Когда ваш MCP-сервер "просто не работает" - не спешите пересоздавать всё с нуля. Запустите MCP Inspector. Проверьте stderr. Валидируйте JSON Schema. Проверьте абсолютные пути в конфиге.

90% граблей находятся в этих четырех местах. Я прошел через все пять за два месяца. Вы можете сэкономить время и нервы, прочитав эту статью.
