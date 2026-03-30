---
title: "Как подключить Chrome DevTools MCP к Claude Code: инструкция для разработчиков"
date: 2026-03-30
lastmod: 2026-03-30
description: "Пошаговая инструкция по настройке Chrome DevTools MCP с Claude Code для работы с авторизованными сайтами через Chrome Remote Debugging Protocol"
tags: ["claude-code", "mcp", "chrome", "devtools"]
slug: "chrome-devtools-mcp-claude-code"
draft: false
---

AI-агенты неплохо умеют писать код, но слепы в том, что происходит внутри браузера. Chrome DevTools MCP решает эту проблему. Claude Code может видеть DOM, кликать по элементам и заполнять формы - он получает полный доступ к Chrome через Chrome DevTools Protocol, а не просто скриншот экрана.

## Зачем это нужно

Классическая ситуация: вы отлаживаете UI-баг, описываете его Claude Code текстом, получаете правки, проверяете в браузере, снова описываете. Пять итераций на то, что можно было показать за секунду.

Chrome DevTools MCP (Google анонсировал его в сентябре 2025) убирает этот зазор. Агент подключается к живому браузеру через Chrome Remote Debugging Protocol и работает с ним напрямую. Никакого посредника.

Что становится возможным:

- **Авторизованные сайты.** Claude может открыть Twitter, LinkedIn, GitHub под вашим аккаунтом и работать с данными, которые недоступны без логина.
- **Отладка UI.** Вы описываете, что сломалось - агент смотрит в браузер, видит DOM и CSS, сразу понимает причину.
- **Повторяемые ручные сценарии.** Заполнение форм, навигация по шагам, обработка пагинации - всё, что вы делаете руками снова и снова.
- **Скрапинг приватного контента.** Данные за авторизацией - то, что headless-браузер без cookies не достанет.

## Как это устроено

Chrome DevTools Protocol (CDP) - это JSON-based API для управления браузером. Chrome слушает входящие WebSocket-соединения на порту 9222 и принимает команды в формате `{"id": 1, "method": "Page.navigate", "params": {"url": "..."}}`. Результаты возвращаются в том же формате. MCP-сервер подключается к этому порту и транслирует команды от Claude Code в браузер.

```
Claude Code
    ↓ (stdio)
chrome-devtools-mcp
    ↓ (WebSocket ws://127.0.0.1:9222)
Chrome DevTools Protocol
    ↓
Google Chrome + --user-data-dir
```

MCP расшифровывается как Model Context Protocol - стандарт Anthropic для подключения внешних инструментов к AI-агентам. Через stdio-транспорт Claude Code запускает MCP-сервер как subprocess и общается с ним через stdin/stdout.

Ключевой момент - флаг `--user-data-dir`. В Chrome 136+ он обязателен для включения удалённой отладки. Флаг указывает на отдельную папку с профилем: cookies, история, расширения хранятся там. На macOS debugging-профиль живёт в `~/.chrome-debug-profile`. Основной Chrome продолжает работать как раньше - debugging-сессия изолирована.

## Настройка за три шага

### Шаг 1: Запустить Chrome с флагами

На macOS Chrome запускается из терминала с двумя флагами:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.chrome-debug-profile"
```

`--remote-debugging-port=9222` включает CDP на порту 9222. `--user-data-dir` указывает папку для отдельного профиля - она создастся автоматически, если её нет.

После запуска откройте `http://127.0.0.1:9222`. Должна появиться страница с JSON-ответом: список открытых вкладок с их id, url и title. Проверить из терминала:

```bash
curl http://127.0.0.1:9222/json
```

### Шаг 2: Подключить MCP к Claude Code

Одна команда добавляет chrome-devtools-mcp в конфигурацию:

```bash
claude mcp add --transport stdio chrome-devtools -- \
  npx -y chrome-devtools-mcp@latest --browserUrl=http://127.0.0.1:9222
```

`--transport stdio` - способ общения с MCP-сервером. `chrome-devtools` - имя, под которым инструмент появится в Claude Code. `--browserUrl` задаёт адрес подключения к CDP, `@latest` подтягивает актуальную версию пакета.

Конфиг сохранится в `~/.claude/mcp.json`. Перезапустите сессию Claude Code - инструмент будет доступен.

### Шаг 3: Проверить, что всё работает

Откройте любой сайт в debugging-браузере. Потом в Claude Code напишите:

> Can you navigate to https://example.com and take a screenshot?

Claude должен открыть страницу, сделать скриншот и вернуть его вам. Если видите скриншот - настройка прошла успешно.

## Удобный запуск

Каждый раз вводить длинную команду неудобно. Два способа починить это.

**Скрипт:**

```bash
#!/bin/bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.chrome-debug-profile" \
  > /dev/null 2>&1 &

echo "Chrome запущен (PID: $!)"
```

Сохраните как `~/chrome-debug.sh`, сделайте исполняемым (`chmod +x ~/chrome-debug.sh`), запускайте одной командой.

**Alias в `~/.zshrc`:**

```bash
alias chrome:debug="/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=\"$HOME/.chrome-debug-profile\" \
  > /dev/null 2>&1 &"
```

После `source ~/.zshrc` Chrome запускается командой `chrome:debug` из любого места.

## Примеры промптов

Три паттерна, которые работают сразу после настройки.

**Twitter / X.** Зайдите в аккаунт в debugging-браузере, потом попросите Claude:

> Открой Twitter и напиши черновик твита про Chrome DevTools MCP. Не публикуй, просто покажи, что получилось.

Claude откроет compose-форму, напишет текст, вернёт скриншот на проверку.

**GitHub.** Заходить не нужно - GitHub частично открыт:

> Найди на github.com/microsoft/vscode все открытые issues с меткой "bug" за последние 7 дней и выведи список заголовков.

**Отладка UI.** Открываете баг в браузере. Спрашиваете: "Посмотри на текущую страницу. Кнопка Submit неактивна. Почему - найди в DOM и CSS." Агент инспектирует элемент через CDP-метод `DOM.getAttributes`, находит причину, объясняет.

## Безопасность

Порт 9222 доступен любому процессу на вашей машине без аутентификации - WebSocket-соединение принимается от любого локального клиента. Для разработки это нормально, но у подхода есть конкретные ограничения.

Не используйте debugging-профиль для логина в банки, корпоративные системы с SSO, OAuth-приложения с широкими правами доступа, хранилища паролей. Лучше создайте отдельный аккаунт Google для тестирования.

`--user-data-dir` защищает ваш основной профиль: cookies и localStorage основного Chrome debugging-сессии недоступны. Но всё, что вы открываете в debugging-браузере, потенциально видит любой локальный процесс через тот же порт 9222.

## Troubleshooting

**"Failed to connect to browser"** - Chrome не запущен с нужными флагами. Проверьте, что запускаете именно ту команду из шага 1, а не обычный Chrome.

**"Browser closes immediately"** - скорее всего, уже запущен другой Chrome без debug-флага. Закройте все окна Chrome, потом запустите debugging-версию.

**"Can't find Chrome executable"** - неверный путь. На macOS стандартный путь `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`.

**Порт 9222 занят** - другой процесс использует этот порт. Найдите и завершите его:

```bash
lsof -ti:9222 | xargs kill -9
```

**Скриншоты не работают** - версия Chrome ниже 136. Обновите браузер.

Диагностика одной командой:

```bash
curl http://127.0.0.1:9222/json | jq .
```

Если возвращается JSON со списком вкладок - Chrome работает и MCP может к нему подключиться.

## Другие агенты и ОС

Chrome DevTools MCP работает с любым агентом, который поддерживает MCP: Cursor, Gemini CLI и другие. Принцип один - MCP-сервер подключается к порту 9222, агент общается с MCP-сервером. Команда `claude mcp add` специфична для Claude Code, но аналогичная настройка есть у других клиентов.

На Linux путь к Chrome другой:

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-debug-profile"
```

На Windows команда запускается из PowerShell:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$env:USERPROFILE\.chrome-debug-profile"
```

---

Настройка занимает 5 минут. Chrome DevTools MCP - это один из немногих инструментов, где разница ощущается сразу: AI-агент из текстового помощника превращается в напарника, который видит тот же экран, что и вы.

Напишите, какую автоматизацию вы настроили первой - интересно, какие use cases находят читатели.
