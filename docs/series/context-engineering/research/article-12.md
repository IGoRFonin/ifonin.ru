# Статья 12: Практические рецепты и workflow

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Сводная, практическая, "шпаргалка"
**Целевая аудитория**: Все — от новичков до продвинутых

## Ключевой тезис

Вот конкретные действия которые можно сделать СЕГОДНЯ чтобы получать больше от Claude Code. Без теории, только рецепты.

## Рецепты

### Быстрые wins (5 минут)

#### 1. Следи за контекстом
- Смотри на % в status bar
- На 80% → `/compact` или новая сессия
- `/cost` — текущее потребление
- `/context` — детали использования

#### 2. Переключи модель для простых задач
```
/model haiku
```
- Haiku для: syntax help, quick explanations, simple code gen
- Sonnet для: обычной работы
- Opus для: сложных архитектурных задач
- Не забудь переключить обратно: `/model sonnet`

#### 3. Конкретные промпты
```
# Плохо (много итераций = много контекста):
"Fix the bug"

# Хорошо (одна итерация):
"Fix the TypeError in src/auth/login.ts:42 where
user.email is undefined when OAuth callback has no profile"
```

#### 4. Отключи неиспользуемые MCP серверы
```bash
claude mcp list          # посмотри что подключено
claude mcp remove <name> # удали ненужные
```

### Средние wins (15-30 минут)

#### 5. Создай базовый CLAUDE.md
```markdown
# Project: MyApp
Stack: TypeScript, React, PostgreSQL, Prisma
Test: vitest
Build: npm run build
Lint: npm run lint

## Conventions
- Functional React components with hooks
- API routes in src/api/
- Shared types in src/types/
```
Кратко, по делу. Каждая строка = токены.

#### 6. Перенеси длинные инструкции в Skills
```bash
mkdir -p .claude/skills/code-review
```
Создай `.claude/skills/code-review/SKILL.md` с подробными инструкциями ревью.
Теперь они загружаются только при `/code-review`, а не каждую сессию.

#### 7. PostToolUse hook для автоформатирования
В `.claude/settings.json`:
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

#### 8. Делегируй исследование субагентам
```
Use an Explore subagent to find all files related to
authentication and summarize the architecture.
```
Весь мусор поиска остаётся в контексте субагента. В твой контекст попадает только summary.

### Продвинутые wins (1 час+)

#### 9. Plan Mode для сложных задач
- Shift+Tab x2 → Plan Mode
- Claude исследует без изменений
- Ты утверждаешь план
- Только потом — реализация
- Экономия: нет откатов, нет "oops wrong approach"

#### 10. Git Worktrees для параллельной работы
```bash
git worktree add .worktrees/feature-a -b feature-a
git worktree add .worktrees/feature-b -b feature-b
# Открой Claude Code в каждом worktree
```

#### 11. Модульные rules для контекстно-зависимых инструкций
```
.claude/rules/
├── frontend.md  (globs: src/components/**)
├── api.md       (globs: src/api/**)
├── testing.md   (globs: **/*.test.*)
└── database.md  (globs: src/db/**)
```
Каждый файл загружается ТОЛЬКО когда Claude работает с matching файлами.

#### 12. PreCompact hook для бекапов
Бекапить контекст на порогах перед compaction — подробности в статье 3 (Compaction).

### Workflow шаблоны

#### Одна фича (single session)
1. Начни сессию с конкретным промптом
2. Plan Mode → утверди план
3. Реализация с делегированием субагентам
4. `/compact` если контекст > 60%
5. Тесты → commit

#### Параллельная работа (multi session)
1. Создай worktrees для каждой фичи
2. Открой Claude в каждом
3. Дай задачу каждому инстансу
4. Merge через PR

#### Long-running проект (multi day)
1. Хороший CLAUDE.md с архитектурой
2. Skills для повторяющихся workflows
3. Auto Memory для автоматических заметок
4. Каждая сессия = одна задача
5. Commit + новая сессия вместо long-running session

## Источники

### Официальные
1. **Best Practices for Claude Code** — Claude Code Docs
   - URL: https://code.claude.com/docs/en/best-practices
   - Ключевое: explore first → plan → code, verify work, manage context aggressively
   - **ГЛАВНЫЙ ИСТОЧНИК**

2. **How Claude Code works** — Claude Code Docs
   - URL: https://code.claude.com/docs/en/how-claude-code-works
   - Ключевое: agentic loop, tips for working effectively

3. **Manage costs effectively** — Claude Code Docs
   - URL: https://code.claude.com/docs/en/costs
   - Ключевое: reduce token usage strategies, model choice, MCP overhead, hooks/skills offloading

### Community guides
4. **Claude Code: keep the context clean** — Arthur / Medium
   - URL: https://medium.com/@arthurpro/claude-code-keep-the-context-clean-d4c629ed4ac5
   - Дата: Nov 30, 2025
   - Ключевое: TL;DR-формат, disable unused MCP, use Skills, run noisy tools in sub-agents, match control to task

5. **Context Issues** — DeepWiki (claude-code-ultimate-guide)
   - URL: https://deepwiki.com/FlorianBruniaux/claude-code-ultimate-guide/13.1-context-issues
   - Ключевое: troubleshooting context problems, session management commands

6. **Claude Code Context: Never Lose Project State** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/performance/context-preservation
   - Дата: Feb 11, 2026
   - Ключевое: continuous update techniques, `/compact` usage

7. **Claude Code Speed: Rev the Engine** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/performance/speed-optimization
   - Дата: Feb 3, 2026
   - Ключевое: `/model haiku` quick win, speed multiplier approach

### Workflows
8. **Learning Claude Code — From Context Engineering to Multi-Agent Workflows** — Aayush Agrawal
   - URL: https://medium.com/@aayushmnit/learning-claude-code-from-context-engineering-to-multi-agent-workflows-4825e216403f
   - Дата: Jan 25, 2026
   - Ключевое: learning journey, progressive complexity

9. **My Claude Code Setup** — Pedro Sant'Anna
   - URL: https://psantanna.com/claude-code-my-workflow/workflow-guide.html
   - Ключевое: real academic workflow, plan → implement → review → verify → present

10. **Plan Mode** — ClaudeLog
    - URL: https://www.claudelog.com/mechanics/plan-mode/
    - Ключевое: Shift+Tab activation, safe exploration, Opus + complex changes recommendation

11. **2026 Agentic Coding Trends Report** — Anthropic PDF
    - URL: https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf
    - Ключевое: industry context, single agents → coordinated teams, long-running agents
