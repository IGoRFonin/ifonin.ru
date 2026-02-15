# Статья 5: MCP и скрытый "токен-налог" серверов

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Техническая, разоблачительная
**Целевая аудитория**: Пользователи MCP серверов, разработчики агентов

## Ключевой тезис

Каждый подключённый MCP-сервер — это невидимый налог на ваш контекст. Один GitHub MCP = 46K токенов. Решение существует: MCP Tool Search + осознанный выбор между MCP и Skills.

## Основные идеи

### 1. Проблема: скрытое потребление
- Каждый MCP-сервер добавляет tool definitions в контекст
- Типичный сервер: 500-2000 токенов
- Тяжёлые серверы (GitHub, Playwright): 10K-14K токенов КАЖДЫЙ
- Scott Spence задокументировал: 66K+ токенов потрачено ДО первого сообщения
- С 7+ серверами: 50-70% контекста съедено на старте
- Joe Njenga: 51K токенов на 4 сервера

### 2. Реальные числа (из ресерча)
- mcp-omnisearch: 20 tools (~14,114 tokens)
- playwright: 21 tools (~13,647 tokens)
- GitHub MCP: 91 tools (~46,000 tokens)
- Средний сервер: ~500-2000 tokens
- `/doctor` показывает warning если MCP > 25K tokens

### 3. MCP Tool Search — решение от Anthropic
- Выпущен ~январь 2026
- Lazy loading: вместо загрузки всех tool definitions — поиск нужных по запросу
- Автоматически включается если MCP tools > 10% контекста
- Результат: 51K → 8.5K токенов (83% снижение, до 95% в некоторых случаях)
- Simon Willison: "context pollution is why I rarely used MCP, now that it's solved there's no reason not to hook up dozens or even hundreds of MCPs"

### 4. Skills vs MCP: 32x разница в эффективности
- Исследование Ryan Smith: MCP = 10-100x больше токенов чем Skills для эквивалентных операций
- MCP: загружает определения всех тулов + передаёт промежуточные результаты через контекст
- Skills с скриптами: загружается только SKILL.md + скрипт исполняется вне контекста
- Гибридный паттерн: Skills для частых операций, MCP для интеграций с внешними системами

### 5. Code execution approach (Anthropic Engineering)
- Вместо прямых tool calls агент пишет код для вызова тулов
- Промежуточные результаты обрабатываются в коде, не в контексте
- Значительно масштабируется для 100+ тулов

### 6. Практические рекомендации
- Начать с 3-5 essential серверов, добавлять по необходимости
- Отключать неиспользуемые серверы (`claude mcp remove`)
- Проверять потребление: `/doctor`, `/context`
- Переносить частые операции в Skills
- Использовать `enable_tool_search` если не включён автоматически

## Источники

### Первоисточники проблемы
1. **Optimising MCP Server Context Usage in Claude Code** — Scott Spence
   - URL: https://scottspence.com/posts/optimising-mcp-server-context-usage-in-claude-code
   - Дата: Sep 30, 2025
   - Ключевое: первое подробное документирование проблемы, 66K+ tokens consumed, `/doctor` discovery

2. **Claude Code Just Cut MCP Context Bloat by 46.9%** — Joe Njenga / Medium
   - URL: https://medium.com/@joe.njenga/claude-code-just-cut-mcp-context-bloat-by-46-9-51k-tokens-down-to-8-5k-with-new-tool-search-ddf9e905f734
   - Дата: Jan 16, 2026
   - Ключевое: до/после Tool Search с конкретными цифрами

### Решения
3. **MCP Tool Search: Claude Code Lazy Loading for 95% Context Reduction** — ClaudeFast
   - URL: https://claudefa.st/blog/tools/mcp-extensions/mcp-tool-search
   - Дата: Jan 17, 2026
   - Ключевое: как работает Tool Search, конфигурация, 95% reduction claim

4. **What is MCP Tool Search? The Feature That Fixes Context Pollution** — Cyrus/Atcyrus
   - URL: https://www.atcyrus.com/stories/mcp-tool-search-claude-code-context-pollution-guide
   - Дата: Jan 15, 2026
   - Ключевое: Simon Willison tweet, историческая перспектива

5. **How Claude Code's New MCP Tool Search Slashes Context Bloat** — TechBuddies
   - URL: https://www.techbuddies.io/2026/01/18/how-claude-codes-new-mcp-tool-search-slashes-context-bloat-and-supercharges-ai-agents/
   - Дата: Jan 18, 2026

6. **Solving MCP Context Bloat with Claude's Tool Search API** — Can Dedeoglu
   - URL: https://www.candede.com/articles/claude-tool-search
   - Дата: Jan 16, 2026
   - Ключевое: GitHub MCP 91 tools = 46K tokens → <500 tokens with Tool Search

### Архитектурный анализ
7. **The Hidden Token Tax of MCP Servers** — Ryan Smith / Substack
   - URL: https://smithhorngroup.substack.com/p/the-hidden-token-tax-of-mcp-servers
   - Дата: Jan 14, 2026
   - Ключевое: 32x efficiency difference Skills vs MCP, hybrid pattern
   - **КЛЮЧЕВОЙ ИСТОЧНИК**

8. **Code execution with MCP: Building more efficient agents** — Anthropic Engineering
   - URL: https://www.anthropic.com/engineering/code-execution-with-mcp
   - Дата: Nov 04, 2025
   - Ключевое: агент пишет код вместо прямых tool calls, масштабирование

### Гайды по выбору серверов
9. **MCP Server Selection Guide** — Claude World
   - URL: https://claude-world.com/articles/mcp-server-selection-guide/
   - Дата: Jan 18, 2026
   - Ключевое: правило 3-5 серверов, context cost per server, Essential Starter Kit

10. **Claude Code MCP Servers: Complete Configuration Guide** — BrainGrid
    - URL: https://www.braingrid.ai/blog/claude-code-mcp
    - Дата: Dec 24, 2025
    - Ключевое: пошаговая настройка, top 10 серверов

11. **Connect Claude Code to tools via MCP** — Claude Code Docs
    - URL: https://code.claude.com/docs/en/mcp
    - Ключевое: официальная документация

### Оптимизаторы
12. **token-optimizer-mcp** — GitHub (ooples)
    - URL: https://github.com/ooples/token-optimizer-mcp
    - Ключевое: MCP-сервер для оптимизации токенов через caching и compression, 95%+ reduction claim
