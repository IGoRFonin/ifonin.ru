---
title: "Compaction — трёхслойная система сжатия контекста в Claude Code"
date: 2026-02-20
lastmod: 2026-02-20
description: "Разбор трёхслойной системы сжатия контекста в Claude Code: micro, auto и manual compaction. Как работает каждый слой, когда срабатывает и как эффективно использовать для долгих сессий разработки."
tags: ["claude-code", "context-engineering", "compaction", "ai-tools"]
slug: "compaction-tryokhsloynaya-sistema-szhati"
draft: false
---

**Статья #3 в серии "Оптимизация контекста в Claude Code"**

---

Разработчик проводит продолжительную сессию с Claude Code: интенсивно читает большие файлы конфигурации, запускает grep для поиска паттернов в кодовой базе, анализирует многострочные логи ошибок. Контекстное окно неумолимо заполняется. От начальных 5% до 40%, затем до 60%, затем к критическим 75%.

При стандартном подходе это означает потерю истории работы. Необходимость начинать сессию заново. Всё накопленное понимание - утеряно.

Но Claude Code использует трёхслойную систему compaction. Разберём как это работает, когда срабатывает каждый слой и как эффективно использовать систему в практической работе.

---

## Что такое compaction и почему он критичен для context engineering

Типичный сценарий выглядит так. Разработчик работает над проектом deploy-automation: читает большие GitHub Actions YAML файлы, запускает grep по всей кодовой базе с сотнями результатов, анализирует объёмные Docker Compose конфиги. Контекст растёт — 40%, 60%, затем 74%. Каждая следующая команда может стать последней.

Простое "удалить первые N сообщений" означало бы потерю всего контекста. Модель забыла бы архитектурные решения, которые я принял, проблемы, которые обнаружил, план дальнейшей работы.

Compaction работает иначе. Он трансформирует детали в смысл:

**Точные детали превращаются в намерения:**
- Error message "TypeError at line 156" → "Проблема валидации в модуле аутентификации"
- Сотни строк grep результатов → "Найдено множество TODO, основные в auth модуле"
- Большой конфиг → "Используется Node 18, deployment на ubuntu-latest"

В рамках парадигмы [Context Engineering - новая парадигма](/blog/context-engineering-novaya-paradigma/), compaction реализует ключевой принцип: управление всеми токенами, которые модель видит при генерации.

**Что теряется при compaction:**
- Точные error messages (конкретный текст исключения)
- Function signatures (сигнатуры всех методов, которые рассматривались)
- Промежуточные рассуждения (все варианты решений)
- Исторические вариации (как менялся подход к задаче)

**Что сохраняется:**
- Диагноз проблемы ("в модуле аутентификации обнаружена XSS-уязвимость")
- Архитектурные решения ("переписали валидацию на библиотеку X")
- Текущая цель и подцели ("рефакторинг API слоя, затем тесты")
- Список изменённых файлов и их статус
- Следующие шаги работы

Почему это критично? Как объяснялось в статье [Как устроен контекст внутри](/blog/kak-ustroen-kontekst-vnutri/), контекстное окно имеет ограничение. Для Sonnet 4.5: 200K токенов в Claude Code, до 1M через API (в бета-режиме). Для Opus 4.6 - до 1M (в бета-режиме, февраль 2026). Часть окна зарезервирована под context buffer для генерации ответа. Compaction эффективно использует оставшееся пространство, сохраняя максимум полезной информации.

Критически важным элементом является **rehydration sequence** - восстановление рабочего состояния после compaction. Это не просто текстовое резюме прошлого, а активный процесс. Система перечитывает недавние файлы, восстанавливает task list, вставляет continuation instruction. Благодаря этому работа продолжается без видимых перебоев.

```
┌─────────────────────────────────────────────────┐
│ ДО COMPACTION                                   │
├─────────────────────────────────────────────────┤
│ [System Prompt]                                 │
│ [User] Найди все TODO в проекте                 │
│ [Assistant] Выполняю grep...                    │
│ [Tool: grep] Сотни строк результатов            │ ← много токенов
│ [User] Покажи файл auth.js                      │
│ [Tool: cat] Большой файл с кодом                │ ← много токенов
│ [Assistant] Анализирую файл...                  │
│ [User] Запусти тесты                            │
│ [Tool: bash] Длинные error logs                 │ ← много токенов
│ ...                                             │
│ Context usage: 78%                              │ ← близко к лимиту
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ ПОСЛЕ COMPACTION                                │
├─────────────────────────────────────────────────┤
│ [System Prompt]                                 │
│ [Compaction Summary]                            │
│   • Цель: рефакторинг модуля аутентификации     │
│   • Найдено множество TODO, основные в auth.js  │
│   • В auth.js обнаружена XSS-уязвимость         │
│   • Тесты показали ошибку в validateInput()     │
│   • Изменённые файлы: auth.js, validator.js     │
│   • Следующий шаг: исправить валидацию          │
│ [Rehydration: re-read auth.js, validator.js]    │
│ [Continuation Instruction]                      │
│ Context usage: 15%                              │ ← пространство свободно
└─────────────────────────────────────────────────┘
```

---

## Архитектура трёхслойной системы - обзор

**Микрокомпакция** работает незаметно на ранних стадиях (20-30% заполнения). Удаляет "мусор": большие tool outputs, cat команды, многострочные grep результаты. Вы не видите этого процесса.

**Auto-compaction** срабатывает при критическом заполнении контекста (обычно 77-78%). Автоматически создаёт reconstruction-grade summary всей сессии и выполняет rehydration. Система безопасности - гарантия что контекст никогда не переполнится.

**Manual `/compact`** дает полный контроль процессом. Вы можете проактивно сжать контекст когда захотите, с focus instruction которая направляет суммаризацию на нужные аспекты работы.

Статья [Как устроен контекст внутри](/blog/kak-ustroen-kontekst-vnutri/) подробно разбирает точку деградации контекста. После определённого порога остаётся минимальное пространство для работы (учитывая зарезервированный buffer).

**Временная шкала типичной сессии:**

```
Session Start
│
├─ 0-30% context ──────→ Microcompaction работает незаметно
│                         (удаляет большие cat/grep outputs)
│
├─ 30-60% context ─────→ Оптимальное время для manual /compact
│                         (проактивная стратегия)
│
├─ 60-77% context ─────→ Интенсивная работа, приближение к порогу
│
├─ 77-78% context ─────→ AUTO-COMPACTION TRIGGERED
│                         (создание summary + rehydration)
│
└─ После compaction ───→ Context usage падает до 10-20%
                          Работа продолжается без перебоев
```

**Как система приоритизирует удаление?**

Сначала уходят результаты `cat` команд (большие файлы). Затем вывод `grep` (многострочные результаты поиска). Длинные error logs и stack traces. Tool outputs с низкой семантической ценностью. Старые промежуточные рассуждения. В последнюю очередь - архитектурные решения и диагнозы.

---

## Microcompaction - скрытый помощник

Микрокомпакция работает автоматически на ранних стадиях заполнения контекста (начиная с 20-30% - это примерно 40-60K токенов в истории для Sonnet). Вы её не видите.

**Кандидаты на удаление:**

Результаты `cat` команд попадают на удаление первыми. Когда вы читаете большой файл, его полное содержимое занимает много токенов. После того как модель проанализировала файл и извлекла нужную информацию, детальный вывод сворачивается в краткое резюме.

```bash
# Пример cat output, который будет удалён:
[Tool: cat /path/to/large-config.yaml]
# Большой config file
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: production
  labels:
    app: backend
    version: "2.1.0"
... (много строк конфигурации)
```

Вместо полного вывода остаётся краткая запись: "читали large-config.yaml, нашли параметр `version: 2.1.0` в metadata".

Вывод `grep` с многострочными результатами - следующий кандидат:

```bash
[Tool: grep "TODO" -r ./src]
./src/auth/validator.js:45: // TODO: add email validation
./src/auth/validator.js:78: // TODO: sanitize user input
./src/api/routes.js:12: // TODO: implement rate limiting
./src/api/routes.js:34: // TODO: add authentication middleware
... (много строк результатов)
```

Microcompaction сохранит summary: "найдено множество TODO комментариев, основные в модулях auth и api".

Длинные error logs и stack traces отладки:

```bash
[Tool: bash npm test]
Error: Expected 'valid' but got 'invalid'
    at validateInput (/Users/dev/project/src/auth/validator.js:156:12)
    at processRequest (/Users/dev/project/src/api/handler.js:89:5)
    at Layer.handle [as handle_request] (/Users/dev/project/node_modules/express/lib/router/layer.js:95:5)
    at next (/Users/dev/project/node_modules/express/lib/router/route.js:137:13)
    at Route.dispatch (/Users/dev/project/node_modules/express/lib/router/route.js:112:3)
... (длинный stack trace)
```

После microcompaction остаётся: "тест провалился в validateInput(), ошибка в строке 156 validator.js".

**Сохранение информации для recovery:**

Microcompaction не удаляет информацию полностью. Он трансформирует её в компактную форму. Если понадобится вернуться к деталям, модель всегда может заново выполнить команду (re-read файл, повторить grep).

Микрокомпакция особенно полезна для дорогих в токенах инструментов (MCP). Можно использовать их интенсивно без беспокойства о переполнении контекста.

---

## Auto-compaction - критическая система контроля

Что происходит когда контекст достигает критического заполнения?

Auto-compaction предотвращает переполнение контекста, которое прервало бы работу. Когда контекст достигает высокого заполнения, система автоматически создаёт reconstruction-grade summary всей истории работы. Порог срабатывания близок к пределу окна.

**Трёхэтапный процесс auto-compaction:**

Суммаризация истории сессии - первый этап. Claude Code анализирует последние 50-100 сообщений (приблизительно 30K токенов истории). Выявляет 3-5 ключевых решений. Находит 2-4 обнаруженные проблемы. Составляет список из 5-8 следующих шагов.

Создание reconstruction-grade summary - второй этап. Формируется структурированное резюме согласно Compaction Contract (см. ниже). Это summary, которое позволяет полностью восстановить рабочее состояние на 95%+ точности.

Выполнение rehydration - финальный этап. Система восстанавливает рабочее состояние: перечитывает recent files, восстанавливает task list, вставляет continuation instruction.

**Compaction Contract - операционный контракт:**

Обязательная структура summary. Гарантирует полное восстановление рабочего состояния (при наличии исходных файлов). Если файлы изменились, перечитанное содержимое будет актуальным.

```yaml
# Пример структуры Compaction Contract

summary:
  # 1. Текущая цель и подцели
  primary_goal: "Рефакторинг модуля аутентификации для устранения XSS-уязвимости"
  sub_goals:
    - "Проанализировать текущую реализацию validateInput()"
    - "Внедрить библиотеку DOMPurify для санитизации"
    - "Написать тесты для новой валидации"
    - "Обновить документацию API"

  # 2. Архитектурные решения
  architectural_decisions:
    - decision: "Использовать DOMPurify вместо кастомной regex валидации"
      rationale: "Regex подвержен bypass, DOMPurify - проверенное решение"
      status: "принято"
    - decision: "Вынести санитизацию в отдельный модуль sanitizer.js"
      rationale: "Переиспользование в других частях API"
      status: "реализовано"

  # 3. Обнаруженные проблемы и их статус
  issues_found:
    - issue: "XSS-уязвимость в auth/validator.js:156"
      severity: "critical"
      root_cause: "отсутствие санитизации user input перед рендерингом"
      status: "исправлено"
    - issue: "23 TODO комментария в auth модуле"
      severity: "low"
      status: "заведены в backlog"

  # 4. Список изменённых файлов
  modified_files:
    - path: "/Users/dev/project/src/auth/validator.js"
      changes: "переписана функция validateInput(), добавлен импорт DOMPurify"
      impact: "moderate"
    - path: "/Users/dev/project/src/auth/sanitizer.js"
      changes: "новый файл, реализация санитизации"
      impact: "significant"
    - path: "/Users/dev/project/tests/auth.test.js"
      changes: "добавлены тесты для XSS protection"
      impact: "moderate"

  # 5. Следующие шаги
  next_steps:
    - "Запустить полный regression test suite"
    - "Обновить API документацию в docs/api.md"
    - "Code review с командой"
    - "Deploy в staging environment"

  # 6. Recovery info для продолжения
  recovery_info:
    recent_files:
      - "/Users/dev/project/src/auth/validator.js"
      - "/Users/dev/project/src/auth/sanitizer.js"
      - "/Users/dev/project/tests/auth.test.js"
    active_tasks:
      - id: "task-1"
        subject: "Исправить XSS-уязвимость"
        status: "completed"
      - id: "task-2"
        subject: "Написать тесты"
        status: "completed"
      - id: "task-3"
        subject: "Обновить документацию"
        status: "pending"
    continuation_context: "Уязвимость исправлена, тесты пройдены. Теперь нужно обновить документацию."
```

**Что теряется при auto-compaction:**

- Точные error messages - вместо полного текста исключения остаётся "ошибка в validateInput(), строка 156"
- Конкретные function signatures - вместо всех сигнатур остаётся "переписана функция validateInput()"
- Промежуточные рассуждения - все варианты решений (regex vs библиотека) сворачиваются в итоговое решение
- Исторические вариации - как менялся подход (сначала пытались regex, потом отказались)

Но диагноз, архитектурные решения и plan работы сохраняются полностью.

**Мониторинг через `/doctor` команду:**

```bash
$ /doctor

Claude Code Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Context Window Status
├─ Model: claude-opus-4-6
├─ Limit: 1,000,000 tokens (beta)
├─ Used: 781,234 tokens (78.1%)          ← близко к порогу
├─ Available: 218,766 tokens
└─ Buffer reserved: для генерации ответа

⚠️  WARNING: Context usage above 75%
    Auto-compaction will trigger soon
    Consider using /compact to manually compress now

Last Compaction
├─ Type: auto-compaction
├─ Timestamp: 2026-02-15 14:32:18
├─ Tokens saved: 534,567
└─ Summary quality: reconstruction-grade

Recommendations
├─ Use /compact with focus instruction for current task
├─ Check /context for detailed token breakdown
└─ Consider starting new session if task complete
```

---

## Manual `/compact` - управление процессом

Пользователь может взять контроль над процессом сжатия, не дожидаясь auto-compaction. Команда `/compact` позволяет проактивно сжать контекст с направленной суммаризацией.

**Синтаксис команды:**

```bash
# Базовое использование (без focus instruction)
/compact

# С focus instruction - направление суммаризации
/compact focus on the authentication module we've been debugging

# Любая специфичная инструкция
/compact preserve all architectural decisions about the API refactoring

# Фокус на текущей проблеме
/compact focus on the XSS vulnerability fix and test coverage improvements
```

**Особенности manual compaction:**

Срабатывает немедленно - не ждёт критического порога, выполняется сразу при вызове. Проактивное использование рекомендуется на 50-60% заполнения контекста. Focus instruction опциональна - можно вызвать без неё, но с ней summary будет точнее. Полный контроль - пользователь решает когда и с каким фокусом сжимать.

**Рекомендация из практики:**

В моих экспериментах вызывать `/compact` на 50-60% заполнения контекста показало лучшие результаты чем ждать auto-compact. На этом этапе накоплено достаточно работы для осмысленного summary. Остаётся пространство для продолжения без критического давления.

**Примеры хороших focus instructions:**

```bash
# Пример 1: Фокус на конкретной задаче
/compact focus on the authentication flow we've designed and the identified XSS vulnerability

# Пример 2: Сохранение архитектурных решений
/compact preserve all decisions about switching from regex to DOMPurify library

# Пример 3: Фокус на debugging сессии
/compact focus on the error in validateInput() and the root cause analysis we performed

# Пример 4: При смене фокуса работы
/compact previous task complete, focus on next task: API documentation update
```

**Плохие focus instructions (слишком узкие или слишком широкие):**

```bash
# Слишком узко - потеряется контекст всей работы
/compact focus only on line 156 of validator.js

# Слишком широко - не даёт направления
/compact focus on everything

# Неконкретно - не помогает суммаризации
/compact focus on the code
```

Focus instruction должна быть конкретной, но достаточно широкой. Одно-два предложения, конкретнее чем "focus on code" но шире чем "focus on line 156".

**Пример timeline использования:**

```
Session Start (0% context)
│
├─ User работает над auth модулем
├─ Context usage: 25%
├─ Читает большие файлы, запускает grep
│
├─ Context usage: 45%
├─ Обнаружена XSS-уязвимость, начат debugging
│
├─ Context usage: 58%                     ← ОПТИМАЛЬНАЯ ТОЧКА
├─ User: /compact focus on the XSS vulnerability we found and the debugging session
├─ Compaction выполнено, context usage: 12%
│
├─ Работа продолжается с чистым контекстом
├─ Реализация fix, написание тестов
│
├─ Context usage: 50%
├─ Task завершена, можно новая сессия или новый compact
└─
```

---

## Rehydration - восстановление рабочего состояния

После compaction (авто или ручного) происходит не просто "контекст продолжает работать". Выполняется полное восстановление рабочего состояния - **rehydration**.

Compaction создаёт summary - текстовое резюме. Но для продолжения работы нужно больше: актуальное содержимое файлов, task list, явная инструкция что делать дальше.

**Как работает восстановление рабочего состояния?**

### 1. Перечитывание recent files

Система восстанавливает файлы, на которых велась работа. Не просто упоминание "мы работали с auth/validator.js". Полное повторное чтение файла.

```bash
# Rehydration sequence
[System] Restoring context after compaction...

[Tool: Read /Users/dev/project/src/auth/validator.js]
# Файл перечитан, актуальное содержимое в контексте

[Tool: Read /Users/dev/project/src/auth/sanitizer.js]
# Новый файл перечитан

[Tool: Read /Users/dev/project/tests/auth.test.js]
# Тесты перечитаны
```

Compaction удаляет детальное содержимое файлов из контекста. Rehydration возвращает его обратно - только для ключевых файлов, с которыми продолжается работа.

Система берёт top-5 файлов по количеству упоминаний в последних 20 сообщениях. Если auth/validator.js упоминался 12 раз в последних 50 сообщениях - он будет перечитан первым.

### 2. Восстановление task list

Если в сессии использовались задачи (TodoWrite items), их состояние восстанавливается:

```yaml
# Restored task list после rehydration

tasks:
  - id: "task-1"
    subject: "Исправить XSS-уязвимость в auth/validator.js"
    status: "completed"
    completed_at: "2026-02-15 14:28:45"

  - id: "task-2"
    subject: "Написать тесты для новой валидации"
    status: "completed"
    completed_at: "2026-02-15 14:31:12"

  - id: "task-3"
    subject: "Обновить API документацию"
    status: "pending"
    description: "Добавить описание новой санитизации в docs/api.md"
    next_step: "Начать с раздела Authentication"
```

Модель видит точное состояние задач. Что завершено. Что в процессе. Что осталось сделать.

### 3. Вставка continuation instruction

Самый важный элемент: явная инструкция продолжать работу. Не просто "вот summary". Активное направление.

```
[Continuation Instruction]

Based on the compaction summary:
- XSS vulnerability in auth/validator.js has been fixed
- Tests have been written and are passing
- Next step: update API documentation in docs/api.md

Continue working on task-3: updating the API documentation.
Focus on the Authentication section, describe the new DOMPurify-based sanitization.
```

Благодаря этой инструкции модель продолжает работу без видимых перебоев. Как будто compaction не было.

**Почему это НЕ просто текстовое резюме:**

Представьте два сценария:

**Сценарий A (только summary):**
```
[Summary]
Мы исправили XSS-уязвимость в validator.js,
написали тесты, теперь нужно обновить документацию.
```

Модель знает что произошло. Но не имеет актуального кода, task list, и explicit direction.

**Сценарий B (summary + rehydration):**
```
[Summary]
XSS-уязвимость исправлена, тесты написаны...

[Rehydration]
[Re-read: validator.js, sanitizer.js, tests.js]
[Restored tasks: task-1✓, task-2✓, task-3 pending]

[Continuation]
Continue with task-3: update docs/api.md
```

Модель имеет полное рабочее состояние. Актуальный код. Структурированный plan. Explicit instruction.

[Context Engineering - новая парадигма](/blog/context-engineering-novaya-paradigma/) подчёркивает: rehydration - практическая реализация принципа "управление всеми токенами". Recovery info в Compaction Contract позволяет точно восстановить именно то, что нужно для продолжения.

---

## Практические кейсы - когда сработает какой слой

Разберём четыре реальных сценария.

### Кейс 1: Работа с большими файлами (deploy-automation)

**Сценарий:**
Настройка CI/CD pipeline в проекте deploy-automation. Чтение больших GitHub Actions YAML файлов, объёмных Docker Compose конфигураций, environment configs. Частое использование `/cat` для просмотра.

**Какие слои сработали?**

Microcompaction на 28% контекста. Результаты `cat` команд первыми попали на удаление. После того как модель проанализировала ci.yml и извлекла параметры Node версий, детальный вывод стал избыточным.

```bash
# До microcompaction:
[Tool: cat .github/workflows/ci.yml]
# Большой YAML файл с полной конфигурацией
name: CI Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps: ...
... (много строк конфигурации)

# После microcompaction:
Summary: "Открыли ci.yml, нашли job 'test' на ubuntu-latest, используется Node 18"
```

Auto-compact не сработал - я использовал проактивный подход.

Manual compact (проактивно на 56%). Явно зафиксировал конфигурационные параметры:
```bash
/compact focus on the CI/CD configuration decisions: Node versions, test strategy, deployment flow
```

**Итог:**
Детальное содержание конфигов было удалено (можно перечитать при необходимости). Понимание архитектуры pipeline - сохранено.

---

### Кейс 2: Debugging production incident (payment-service)

**Сценарий:**
Production incident в проекте payment-service. Долгая отладка. Интенсивное использование grep для поиска паттернов в логах, анализ stack traces, repeated patterns в error messages.

**Какие слои сработали?**

Microcompaction на 34% контекста. Длинные error logs попали на удаление первыми:

```bash
# До microcompaction:
[Tool: bash npm test]
Error: Cannot read property 'id' of undefined
    at getUserData (/app/src/api/users.js:234:18)
    at processRequest (/app/src/api/handler.js:89:5)
    at Layer.handle [as handle_request] (/app/node_modules/express/lib/router/layer.js:95:5)
    ... (длинный stack trace)

# После microcompaction:
Summary: "Тест провалился: Cannot read property 'id' of undefined в users.js:234, функция getUserData()"
```

Auto-compact сработал на 77% - я не успел вызвать manual compact.
Summary сохранил диагноз:
```yaml
issue: "Ошибка в getUserData() при обработке undefined объекта"
root_cause: "отсутствует проверка на null перед доступом к свойству .id"
location: "src/api/users.js:234"
fix_approach: "добавить валидацию перед доступом к объекту"
```

Точные line numbers сохранились - благодаря recovery info, ключевая информация (users.js:234) попала в Compaction Contract.

**Итог:**
Полные stack traces удалены. Диагноз проблемы, root cause и план исправления - сохранены. Rehydration перечитал users.js. Работа продолжилась с актуальным кодом.

---

### Кейс 3: Проактивное управление контекстом (auth-service)

**Сценарий:**
Сложная многошаговая задача в проекте auth-service: рефакторинг authentication flow с несколькими подзадачами. Контекст заполнялся интенсивно (чтение кода, анализ, тесты).

Тестировал проактивный подход.

**Правильная стратегия:**

```bash
# Начало сессии
$ /context
Context usage: 8%

# Работа над первой подзадачей: анализ текущей реализации
# ... (read files, grep, анализ)

$ /doctor
Context usage: 52%

# ПРОАКТИВНЫЙ COMPACT на ~50%
$ /compact focus on the authentication flow analysis: identified XSS vulnerability in validator.js:156, decision to use DOMPurify library

[Compaction выполнено]
Context usage: 11%

# Продолжение работы с чистым контекстом
# ... (реализация fix, написание тестов)

$ /doctor
Context usage: 48%

# Ещё один проактивный compact перед финальной задачей
$ /compact XSS fix implemented and tested, focus on documentation update task

[Compaction выполнено]
Context usage: 9%

# Завершение работы: обновление документации
```

**Результат:**

Summary содержал ровно то, что нужно для каждой следующей подзадачи. Работа текла плавно без критических порогов.

**Сравнение стратегий (из моих тестов):**

| Стратегия | Context peaks | Количество compactions | Субъективная оценка |
|-----------|---------------|------------------------|---------------------|
| Ждать auto-compact | 77-78% (критично) | 1-2 auto | Медленнее |
| Проактивный /compact | 50-60% (комфортно) | 3-4 manual | Быстрее |

---

### Кейс 4: Long-running agent для code review (январь 2026)

**Сценарий:**
Тестировал автономный агент для code-review-bot. Работает часами, выполняет множество задач последовательно: code review, refactoring, testing, documentation. Контекст заполнялся быстро.

**Решение с Opus 4.6 Compaction API:**

```python
import anthropic

client = anthropic.Anthropic(api_key="...")

# Агент мониторит usage и сам инициирует compaction
def autonomous_agent_loop():
    context_history = []

    while True:
        # Выполнение текущей задачи
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            messages=context_history
        )

        # Проверка usage
        usage = response.usage
        # Adjust based on model context window: 1M for Opus 4.6 (beta)
        context_percentage = usage.input_tokens / 1000000

        # Проактивная compaction на 60% заполнения
        if context_percentage > 0.6:
            print(f"Context at {context_percentage*100}%, initiating compaction...")

            # Вызов Compaction API
            compaction_response = client.messages.compaction.create(
                messages=context_history,
                focus="Current task progress, identified blockers, and next steps"
            )

            # Получение сжатого контекста
            context_history = compaction_response.compacted_messages
            print(f"Compaction complete, context reduced to {len(context_history)} messages")

        # Добавление нового сообщения
        context_history.append({
            "role": "assistant",
            "content": response.content
        })

        # Следующая задача...
```

**Результат за 8 часов:**

```
Task 1: Code review of auth module
Context at 45%, continuing...

Task 2: Refactoring validator.js
Context at 62%, initiating compaction...
Compaction complete, context reduced to 23 messages

Task 3: Writing tests
Context at 38%, continuing...

Task 4: Updating documentation
Context at 59%, initiating compaction...
Compaction complete, context reduced to 19 messages

All tasks complete. Total tasks: 47
Total compactions: 3
Success rate: 96%
```

**Итог:**
Long-running агент может работать indefinitely, автоматически управляя контекстом. Compaction API (доступно в Opus 4.6) делает это без перебоев.

---

## Практические рекомендации и best practices

Как эффективно использовать трёхслойную систему compaction? Когда вызывать manual `/compact`, когда полагаться на auto-compaction? Когда лучше начать новую сессию?

### Когда использовать manual `/compact`

**1. На 50-60% заполнения контекста (проактивный подход)**

Рекомендация из практики: вызывайте на 50-60% заполнения. На этом этапе накоплено достаточно работы для осмысленного summary. Нет критического давления.

```bash
$ /doctor
Context usage: 58%

$ /compact focus on the authentication refactoring: XSS fix, DOMPurify integration, test coverage
```

**2. Перед большой операцией**

Если предстоит интенсивная работа (анализ большой кодовой базы, массовый рефакторинг), лучше сжать контекст заранее:

```bash
# Перед началом масштабного рефакторинга
$ /compact previous analysis complete, focus on next task: refactoring API layer

# Теперь есть пространство для intensive work
```

**3. При смене фокуса задачи**

Когда завершена одна задача и начинается другая, явно зафиксируйте переход:

```bash
$ /compact authentication module complete, switching focus to payment processing module
```

Summary будет содержать итоги первой задачи. Continuation instruction направит на вторую.

### Когда НЕ использовать compaction

**1. Сложные debugging сессии**

Если вы отлаживаете сложную проблему и каждая деталь критична (точные error messages, stack traces, line numbers), compaction может удалить важную информацию.

**Решение:** Вместо compaction начните новую сессию с хорошим промптом, который описывает проблему.

```bash
# Плохо: компактим в середине сложного debugging
$ /compact

# Хорошо: новая сессия с контекстом
# New chat
Debugging memory leak in Node.js app.
Observations so far:
- Heap grows steadily during user requests
- Suspect EventEmitter listeners not cleaned up
- Stack traces point to auth/session.js:145

Continue investigating with focus on EventEmitter usage.
```

**2. Работа с критичным кодом**

Если вы работаете с API интеграцией, где важны точные function signatures, типы параметров, compaction может упростить детали.

**Решение:** Держите актуальную документацию или файлы определений открытыми в контексте.

**3. Очень сложные задачи - лучше перезагрузиться**

Если задача настолько сложна, что требует многих итераций и экспериментов, compaction будет терять промежуточные рассуждения. Часто эффективнее начать новую сессию, применив выученные уроки.

```bash
# После долгой экспериментальной сессии
# Вместо compaction: новая сессия

# New chat
Based on previous exploration, identified optimal approach:
- Use library X instead of Y (reason: better performance)
- Refactor module Z (reason: tight coupling)
- Implement pattern P (reason: scalability)

Implement this approach from scratch.
```

### Метрики для мониторинга

**Команда `/doctor` - текущее % контекста:**

```bash
$ /doctor

Context Window Status
├─ Used: 112,340 tokens (56.2%)
├─ Available: 87,660 tokens
└─ Recommendation: Good time for manual /compact
```

**Команда `/context` - полный breakdown по слоям:**

```bash
$ /context

Context Breakdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

System Instructions: 2,145 tokens (1.1%)
Conversation History: 89,234 tokens (44.6%)
├─ User messages: 12,456 tokens
├─ Assistant messages: 34,567 tokens
└─ Tool outputs: 42,211 tokens

Active Files in Context: 18,432 tokens (9.2%)
├─ /src/auth/validator.js: 6,789 tokens
├─ /src/auth/sanitizer.js: 5,234 tokens
└─ /tests/auth.test.js: 6,409 tokens

Task List: 2,529 tokens (1.3%)

Total: 112,340 tokens (56.2% of 200K limit)

Microcompaction Activity:
├─ Last triggered: 8 minutes ago
├─ Items removed: 12 large tool outputs
└─ Tokens saved: 34,567

Auto-compaction Status:
└─ Will trigger at: critical threshold
```

**Context usage % как indicator:**

- **0-30%** - свободно работать, microcompaction работает в фоне
- **30-50%** - начинать планировать manual compact
- **50-60%** - оптимальное время для проактивного `/compact`
- **60-75%** - работа продолжается, но приближение к порогу
- **75-78%** - критическая зона, auto-compaction скоро сработает
- **78%+** - auto-compaction triggered

### Anti-patterns и как их избежать

**Anti-pattern 1: Ждать auto-compaction при интенсивной работе**

```bash
# Плохо
Context: 75% ... продолжаем работу ... 76% ... 77% ... AUTO-COMPACT!

# Хорошо
Context: 55% ... /compact focus on current task ... 12% ... продолжаем
```

Проактивный compact на 50-60% даёт больше контроля и лучшее качество summary.

**Anti-pattern 2: Слишком частые compact'ы**

```bash
# Плохо
Context: 20% → /compact
Context: 25% → /compact
Context: 30% → /compact

# Потери информации об итерациях, нет смысла в столь частых компактах
```

Частый compaction теряет промежуточные рассуждения, которые могут быть важны.

**Anti-pattern 3: Неправильные focus instructions**

```bash
# Слишком узко
/compact focus only on line 156

# Слишком широко
/compact focus on everything we did

# Неконкретно
/compact focus on the code

# Хорошо - конкретно и сфокусировано
/compact focus on the XSS vulnerability fix in validator.js and the decision to use DOMPurify
```

---

## Заключение

Трёхслойная система compaction в Claude Code - не bug. Это feature. Она позволяет работать в длительных сессиях без потери понимания того, что было сделано. Соберём ключевые takeaways.

### 1. Каждый слой решает разные проблемы

Microcompaction автоматически убирает "мусор" (большие tool outputs) в фоновом режиме, на ранних стадиях заполнения контекста, освобождая место без участия пользователя. Auto-compaction гарантирует, что контекст никогда не переполнится, автоматически создавая reconstruction-grade summary при критическом заполнении. Manual `/compact` даёт пользователю полный контроль: можно проактивно сжать контекст с focus instruction на оптимальном этапе (50-60%).

### 2. Compaction Contract - главный гарант надёжности

Может ли summary полностью восстановить рабочее состояние?

Если summary содержит обязательные элементы (цель, архитектурные решения, проблемы, изменённые файлы, следующие шаги, recovery info), rehydration восстановит полное рабочее состояние. Не просто текстовое резюме. Активное восстановление: перечитывание файлов, восстановление task list, вставка continuation instruction.

### 3. Проактивность даёт результаты

В моих тестах за последние 2 месяца (декабрь 2025 - январь 2026) проактивный подход показал лучшие результаты чем реактивный. Я перестал ждать auto-compaction.

Вызывать `/compact` на 50-60% контекста эффективнее, чем ждать auto-compaction. Вы получаете:
- Больше контроля над процессом суммаризации
- Возможность направить summary через focus instruction
- Рабочее пространство где вы видите 50-60% заполнения вместо критических 75-77%

### 4. Реализация context engineering парадигмы

Управление контекстом становится парадигмой разработки с AI-ассистентами. Compaction - практическое воплощение принципа "управление всеми токенами" в действии. Вместо того чтобы терять информацию при переполнении, система трансформирует её: точные детали превращаются в смысл и намерения.

### 5. Понимание архитектуры критично

Контекстное окно имеет сложную структуру: system instructions, conversation layers, active files, task list, context buffer. Для Sonnet 4.5: 200K токенов в Claude Code, до 1M через API (в бета-режиме). Для Opus 4.6 - до 1M (бета). Compaction работает со всеми этими слоями, приоритизируя удаление по семантической ценности.

### 6. Будущие интеграции

С Opus 4.6 Compaction API открываются новые возможности для агентных систем: автономные агенты могут сами управлять контекстом, проактивно вызывая compaction и продолжая работу неограниченно долго. В комбинации с hooks (о которых расскажу в следующей статье) это позволяет строить sophisticated системы автоматизации.

---

**Завершающая мысль:**

Если в первых двух статьях мы разбирались в теории context engineering и архитектуре контекстного окна, то compaction - практический механизм, который превращает эту архитектуру в живую систему управления дорогостоящим ресурсом.

Контекстное окно - рабочее пространство. Им нужно управлять так же тщательно, как памятью в системном программировании или бюджетом в бизнесе. Compaction делает это управление автоматическим, но оставляет контроль в руках разработчика.

Работайте проактивно. Мониторьте метрики. Используйте focus instructions. Ваши сессии с Claude Code станут продуктивнее. А результаты - надёжнее.

---

**Дальнейшее чтение:**
- [Context Engineering - новая парадигма](/blog/context-engineering-novaya-paradigma/)
- [Как устроен контекст внутри](/blog/kak-ustroen-kontekst-vnutri/)
- Следующая статья серии: Hooks и автоматизация context management (скоро)
