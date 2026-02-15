# Статья 9: Persistent Memory — память между сессиями

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Практическая, обзорная
**Целевая аудитория**: Все пользователи, кто устал объяснять заново каждую сессию

## Ключевой тезис

Claude Code забывает всё между сессиями — by design. Но есть встроенные и community-решения, которые дают persistent memory без перегрузки контекста.

## Основные идеи

### 1. Проблема "амнезии"
- Каждая сессия Claude Code стартует с нуля
- Не помнит: предыдущие разговоры, решения, найденные баги, архитектурный контекст
- После auto-compaction: даже внутри сессии теряются детали
- Двойная проблема: intra-session (compaction) + inter-session (no memory)

### 2. Встроенные механизмы

#### Auto Memory
- Claude автоматически сохраняет полезный контекст
- Расположение: `~/.claude/projects/<project-hash>/memory/MEMORY.md`
- Загружается: первые 200 строк в каждую сессию (в system prompt)
- Что сохраняет: паттерны проекта, ключевые команды, предпочтения пользователя
- Что НЕ сохраняет: session-specific контекст, незавершённые задачи

#### /memory command
- Прямое редактирование auto memory
- `claude /memory` — открывает memory для правки
- Можно попросить Claude: "запомни что мы используем bun вместо npm"

#### CLAUDE.md (ручная memory)
- Файл который ты контролируешь полностью
- Не меняется автоматически
- Best practice: после каждого архитектурного решения — обновлять CLAUDE.md

#### .claude/rules/ (модульная memory)
- Правила по категориям, загружаются по glob-паттернам
- Эффективнее чем один большой CLAUDE.md

### 3. PreCompact Hook для сохранения контекста
- Hook который срабатывает перед compaction
- Может сохранить полный контекст в файл
- Пример: бекап на порогах 30/15/5%
- Позволяет вернуться к потерянным деталям

### 4. Community решения

#### claude-mem (12.9K+ GitHub stars)
- Плагин от thedotmack
- Автоматически захватывает observations (что Claude делает)
- Сжимает через agent-sdk (AI-based compression)
- 3-слойный поиск: search (index) → detail → full
- Token-efficient: загружает только релевантное
- Web Viewer UI на localhost:37777
- Установка: `/plugin marketplace add thedotmack/claude-mem`

#### Doobidoo mcp-memory-service (1.3K+ stars)
- MCP сервер для семантической памяти
- ChromaDB-based semantic search через embeddings
- Теги для организации воспоминаний
- Поиск по времени (natural language: "yesterday", "last week")
- Точный поиск по содержимому
- Автоматические бекапы
- Cross-platform

#### Continuous Claude (3.5K+ stars)
- Полная среда persistent learning
- Ledgers + handoffs для передачи состояния между сессиями
- MCP execution без context pollution
- Agent orchestration с изолированными окнами
- 20+ контрибьюторов

### 5. Стратегия выбора

| Потребность | Решение |
|---|---|
| Базовые предпочтения | Auto Memory (встроено) |
| Архитектура проекта | CLAUDE.md |
| Правила по контексту | .claude/rules/ |
| Полная история работы | claude-mem |
| Семантический поиск | Doobidoo memory service |
| Multi-agent persistent env | Continuous Claude |

## Источники

### Официальные
1. **Manage Claude's memory** — Claude Code Docs
   - URL: https://code.claude.com/docs/en/memory
   - Ключевое: полная документация: auto memory, CLAUDE.md, rules dir, imports, /memory command
   - **КЛЮЧЕВОЙ ИСТОЧНИК**

2. **Manage Claude's memory** — Claude Docs (альтернативный URL)
   - URL: https://docs.claude.com/en/docs/claude-code/memory
   - Ключевое: та же информация, другой формат

### Аналитика
3. **Claude Code's Memory Evolution: Auto Memory & PreCompact Hooks** — Yuanchang
   - URL: https://yuanchang.org/en/posts/claude-code-auto-memory-and-hooks/
   - Дата: Feb 10, 2026
   - Ключевое: две проблемы (compaction protection + cross-session memory), как Auto Memory работает под капотом

4. **Claude Code Session Memory: How Your AI Remembers** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/mechanics/session-memory
   - Дата: Feb 10, 2026
   - Ключевое: automatic cross-session context

5. **Claude Code Memory: Never Re-Explain Your Project Again** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/mechanics/memory-optimization
   - Дата: Jan 27, 2026
   - Ключевое: end repetitive context setup

6. **Claude Code Memory System** — Developer Toolkit
   - URL: https://developertoolkit.ai/en/claude-code/advanced-techniques/memory-system/
   - Дата: Dec 21, 2025
   - Ключевое: multi-tier architecture, rules directory deep dive

### Community solutions
7. **Claude-Mem: Persistent Memory for Claude Code** — YUV.AI Blog
   - URL: https://yuv.ai/blog/claude-mem
   - Дата: Feb 5, 2026
   - Ключевое: обзор claude-mem, 3-layer workflow, key features

8. **thedotmack/claude-mem** — GitHub
   - URL: https://github.com/thedotmack/claude-mem
   - Ключевое: исходный код, документация, plugin architecture

9. **Claude-Mem docs** — Official
   - URL: https://docs.claude-mem.ai/introduction
   - Ключевое: quick start, features list, privacy controls

10. **doobidoo/mcp-memory-service** — GitHub Wiki
    - URL: https://github.com/doobidoo/mcp-memory-service/wiki
    - Ключевое: setup guide, semantic search, ChromaDB integration

11. **MCP Memory Service** — Glama
    - URL: https://glama.ai/mcp/servers/@doobidoo/mcp-memory-service
    - Ключевое: capabilities overview, integrations

12. **Continuous Claude v3** — GitHub (parcadei)
    - URL: https://github.com/parcadei/Continuous-Claude-v3
    - Ключевое: ledgers, handoffs, MCP without pollution, agent orchestration

13. **Persistent Memory for Claude Code: "Never Lose Context"** — Agent Native / Medium
    - URL: https://agentnativedev.medium.com/persistent-memory-for-claude-code-never-lose-context-setup-guide-2cb6c7f92c58
    - Дата: Jan 29, 2026
    - Ключевое: обзор funded startups в memory space (Mem0 $24M, Letta $10M, Supermemory $2.6M)
