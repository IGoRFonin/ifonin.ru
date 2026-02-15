# Статья 8: Hooks — детерминистический контроль над контекстом

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Продвинутая, техническая
**Целевая аудитория**: Power users, DevOps-мыслящие разработчики

## Ключевой тезис

CLAUDE.md = suggestions (Claude может игнорировать). Hooks = enforcement (100% гарантия выполнения). Hooks экономят контекст, убирая необходимость повторных просьб и ручных approve.

## Основные идеи

### 1. Что такое hooks
- Shell команды, исполняемые автоматически на lifecycle events Claude Code
- Детерминистический контроль: "всегда делай X после Y" без надежды что Claude вспомнит
- Конфигурируются в `.claude/settings.json` или `~/.claude/settings.json`
- Три типа: command (shell), prompt (LLM-based), agent (agent-based)

### 2. 12 Lifecycle Events

| Event | Когда | Может блокировать? | Применение |
|---|---|---|---|
| SessionStart | Начало/возобновление сессии | Нет | Загрузка env, установка контекста |
| UserPromptSubmit | Пользователь нажал Enter | Да | Инъекция контекста, валидация |
| PreToolUse | Перед вызовом тула | Да | Security checks, input validation |
| PostToolUse | После выполнения тула | Нет | Авто-форматирование, уведомления |
| PreCompact | Перед сжатием контекста | Нет | Бекап контекста |
| SubagentStop | Субагент завершил работу | Нет | Обработка результатов |
| Stop | Claude завершил ответ | Нет | Cleanup, reporting |
| Notification | Claude нужно разрешение | Нет | Auto-approve patterns |
| + ещё 4 | ... | ... | ... |

### 3. Hooks для экономии контекста

#### PostToolUse → авто-форматирование
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "npx prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\""
      }]
    }]
  }
}
```
- Убирает "please format the code" из промптов
- Убирает approve click на каждый файл
- = меньше сообщений = меньше контекста

#### UserPromptSubmit → context injection
- Автоматически добавляет контекст к промптам
- Пример: всегда добавлять текущий git branch и status

#### PreCompact → бекап контекста
- Сохраняет полный контекст перед сжатием
- Threshold-based: бекапы на 30%, 15%, 5%
- Можно восстановить потерянные детали

#### SessionStart → начальная загрузка
- Загрузка environment variables
- Установка начального контекста из внешних источников

### 4. Matcher patterns
- Regex для matching tool names: `Write|Edit`, `Bash`, `.*`
- Позволяет таргетировать конкретные инструменты
- `$CLAUDE_TOOL_INPUT_*` — переменные с данными тула

### 5. Error codes и flow control
- Exit code 0: success, продолжить
- Exit code 2: BLOCK — отменить tool call
- Другие exit codes: warning, но продолжить
- Блокирующие hooks = security enforcement

### 6. Prompt-based hooks (LLM evaluation)
- Вместо shell команды — prompt для Claude
- Claude решает нужно ли блокировать action
- Для решений требующих judgment, не deterministic rules

### 7. Hooks vs CLAUDE.md vs Skills
| | CLAUDE.md | Skills | Hooks |
|---|---|---|---|
| Гарантия | Suggestion | Instruction | Enforcement |
| Когда | Always loaded | On demand | On event |
| Тип | Text context | Text context | Shell execution |
| Контекст-cost | Always | When needed | Zero (runs outside) |

## Источники

### Официальные
1. **Automate workflows with hooks** — Claude Code Docs
   - URL: https://docs.claude.com/en/docs/claude-code/hooks-guide
   - Ключевое: полная документация, event schemas, JSON I/O, async hooks

### Гайды
2. **Claude Code Hooks: Complete Guide to All 12 Lifecycle Events** — ClaudeFast
   - URL: https://claudefa.st/blog/tools/hooks/hooks-guide
   - Дата: Feb 11, 2026
   - Ключевое: таблица всех 12 events, production patterns, quick win примеры
   - **КЛЮЧЕВОЙ ИСТОЧНИК**

3. **Claude Code Hooks: A Practical Guide to Workflow Automation** — DataCamp
   - URL: https://www.datacamp.com/tutorial/claude-code-hooks
   - Ключевое: tutorials с кодом, formatting/testing/notifications/file protection

4. **Hooks System Mastery** — Developer Toolkit
   - URL: https://developertoolkit.ai/en/claude-code/advanced-techniques/hooks-automation/
   - Дата: Feb 3, 2026
   - Ключевое: PreToolUse, PostToolUse, UserPromptSubmit deep dive

5. **Claude Code Hooks: Making AI Gen Deterministic** — Rick Hightower / Medium
   - URL: https://medium.com/spillwave-solutions/claude-code-hooks-making-ai-gen-deterministic-ad4779c3a801
   - Дата: Sep 27, 2025
   - Ключевое: "deterministic hooks" концепция, AI reliability through enforcement

### GitHub repos
6. **disler/claude-code-hooks-mastery** — GitHub (2,974 stars)
   - URL: https://github.com/disler/claude-code-hooks-mastery
   - Ключевое: полный курс, Sub-Agents, Meta-Agent, Team-Based Validation, Output Styles, Custom Status Lines

### Архитектура
7. **Claude Code Hooks Architecture: Implementation Guide** — ClaudeCode JP
   - URL: https://claudecode.jp/en/news/engineer/how-to-configure-hooks
   - Дата: Jan 13, 2026

8. **Hooks System** — DeepWiki (claude-code-ultimate-guide)
   - URL: https://deepwiki.com/FlorianBruniaux/claude-code-ultimate-guide/5.4-hooks-system
   - Дата: Jan 9, 2026

### Context-specific hooks
9. **Never Lose Work to Compaction: Threshold-Based Context Backups** — ClaudeFast
   - URL: https://claudefa.st/blog/tools/hooks/context-recovery-hook
   - Дата: Jan 28, 2026
   - Ключевое: PreCompact hook, threshold monitoring, StatusLine integration

10. **The Complete Guide to Claude Code V2** — Reddit
    - URL: https://www.reddit.com/r/ClaudeAI/comments/1qcwckg/the_complete_guide_to_claude_code_v2_claudemd_mcp/
    - Ключевое: V2 добавляет Part 7: Skills & Hooks — enforcement layer
