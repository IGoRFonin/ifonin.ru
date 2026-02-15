# Статья 6: Субагенты — изолированные контекстные окна

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Практическая, архитектурная
**Целевая аудитория**: Продвинутые пользователи, тимлиды

## Ключевой тезис

Субагент = свой контекст. Делегирование субагентам — это не просто параллельность, это способ ЗАЩИТИТЬ основной контекст от загрязнения исследовательским мусором.

## Основные идеи

### 1. Что такое субагент
- Lightweight instance Claude Code с собственным изолированным контекстным окном
- Запускается через Task tool из основной сессии
- Работает независимо, возвращает результат parent сессии
- Результат компактно вливается в основной контекст (summary, не весь output)

### 2. Типы встроенных агентов
| Тип | Инструменты | Назначение |
|---|---|---|
| Bash | Bash | Выполнение команд |
| Explore | All кроме Edit/Write/Task | Быстрое исследование кодовой базы |
| Plan | All кроме Edit/Write/Task | Проектирование плана реализации |
| general-purpose | All | Сложные мультишаговые задачи |

### 3. Паттерны использования

#### Параллельные (independent tasks)
```
Запусти параллельно:
1. Субагент: проверь безопасность auth модуля
2. Субагент: напиши unit тесты для API
3. Субагент: обнови документацию
```
- Все работают одновременно, не блокируют друг друга
- Каждый имеет свой контекст

#### Последовательные (dependent tasks)
- Результат первого → инпут второго
- Пример: Explore → Plan → Implement

#### Фоновые
- Ctrl+B: перевод текущего субагента в фон
- Основная сессия продолжает работу
- Результат доступен позже через TaskOutput

### 4. Agent Teams (Opus 4.6, новое)
- Несколько Claude инстансов с shared task list
- Могут общаться друг с другом (не только через lead)
- Automatic dependency management
- Challenge findings — проверяют работу друг друга
- Это НЕ субагенты, это peer-to-peer координация

### 5. Контекстная экономия
- Исследование кодовой базы через Explore субагент: весь мусор поиска остаётся в его контексте
- В основной контекст попадает только summary результата
- Правило: "если задача требует чтения 10+ файлов — делегируй субагенту"

### 6. Custom субагенты через Skills
- SKILL.md с `invocation: agent` или custom slash commands
- Пример: `/project:security-review` → запускает субагента со специализированными инструкциями
- Zach Wills: product-manager + ux-designer + senior-engineer как отдельные субагенты

### 7. Ограничения
- Output limit: 8192 токенов на субагента (workaround: запись в файл, возврат summary)
- Shared token budget с parent в некоторых сценариях (issue #10212)
- Не могут редактировать файлы которые редактирует parent одновременно
- Overhead на запуск: каждый субагент — отдельный API call

## Источники

### Практические гайды
1. **Claude Code Multi-Agents and Subagents: Complete Orchestration Guide** — Turion AI
   - URL: https://turion.ai/blog/claude-code-multi-agents-subagents-guide/
   - Дата: Dec 22, 2025
   - Ключевое: Task tool mechanics, parallel workflows, architecture diagrams

2. **How to Use Claude Code Subagents to Parallelize Development** — Zach Wills
   - URL: https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/
   - Ключевое: реальный пример с product-manager/ux-designer/engineer субагентами

3. **Claude Code Agent Teams: Complete Guide** — NxCode
   - URL: https://www.nxcode.io/resources/news/claude-agent-teams-parallel-ai-development-guide-2026
   - Дата: Feb 6, 2026
   - Ключевое: Agent Teams vs Subagents, setup instructions, Opus 4.6

4. **How to Set Up and Use Claude Code Agent Teams** — Dára Sobaloju / Medium
   - URL: https://darasoba.medium.com/how-to-set-up-and-use-claude-code-agent-teams-and-actually-get-great-results-9a34f8648f6d
   - Дата: Feb 2026
   - Ключевое: practical setup, когда одной сессии недостаточно

### Паттерны
5. **Claude Code Sub-Agent Best Practices: Parallel, Sequential, Background** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/agents/sub-agent-best-practices
   - Дата: Jan 12, 2026
   - Ключевое: routing rules, CLAUDE.md patterns для auto-выбора паттерна

6. **Claude Code Async: Background Agents & Parallel Tasks** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/agents/async-workflows
   - Дата: Jan 6, 2026
   - Ключевое: Ctrl+B для background, non-blocking workflows

7. **The Task Tool: Claude Code's Agent Orchestration System** — Dev.to (bhaidar)
   - URL: https://dev.to/bhaidar/the-task-tool-claude-codes-agent-orchestration-system-4bf2
   - Ключевое: architecture diagram, when to use which agent type

8. **Claude Code Agents: Engineering Autonomous AI Assistants** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/agents/agent-fundamentals
   - Дата: Jan 8, 2026
   - Ключевое: 5 agent approaches comparison table

### Проблемы
9. **[FEATURE] Independent Context Windows for Sub-Agents** — GitHub Issue #10212
   - URL: https://github.com/anthropics/claude-code/issues/10212
   - Дата: Oct 23, 2025
   - Ключевое: 8192 output limit, shared budget problem, workarounds

### Официальные
10. **How Claude Code works** — Claude Code Docs
    - URL: https://code.claude.com/docs/en/how-claude-code-works
    - Ключевое: секция "Manage context with skills and subagents"

11. **Claude Code Task Management: Distribute Work Across Agents** — ClaudeFast
    - URL: https://claudefa.st/blog/guide/agents/task-distribution
    - Дата: Jan 27, 2026
    - Ключевое: 7-parallel-Task distribution pattern, CLAUDE.md delegation rules
