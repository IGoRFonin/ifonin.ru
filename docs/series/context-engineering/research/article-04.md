# Статья 4: CLAUDE.md — персистентная память проекта

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Практическая
**Целевая аудитория**: Все пользователи Claude Code

## Ключевой тезис

CLAUDE.md — самый простой и мощный способ дать Claude контекст. Но каждая строка стоит токенов. Мастерство — в балансе между полнотой и лаконичностью.

## Основные идеи

### 1. Иерархия CLAUDE.md файлов

| Уровень | Расположение | Загружается | Назначение |
|---|---|---|---|
| Enterprise/Org | Managed policy | Всегда | Политики безопасности, корпоративные правила |
| User | `~/.claude/CLAUDE.md` | Всегда, во всех проектах | Личные предпочтения, стиль |
| Project root | `./CLAUDE.md` | Всегда в этом проекте | Архитектура, стек, конвенции команды |
| Subdirectory | `src/api/CLAUDE.md` | Когда Claude работает в этой директории | Контекст подсистемы |
| Rules dir | `.claude/rules/*.md` | По glob-паттернам | Модульные правила |

### 2. Структура эффективного CLAUDE.md
- **Краткость**: каждая строка = токены в КАЖДОЙ сессии
- **Императивный стиль**: "Use TypeScript strict mode" а не "We prefer to use..."
- **Что включать**: стек, ключевые команды (build/test/lint), архитектурные решения, naming conventions
- **Что НЕ включать**: длинные объяснения "почему", примеры кода (→ перенести в Skills), temporary notes

### 3. Rules Directory (.claude/rules/)
- Появилось в v2.0.64+
- Модульная организация: `rules/testing.md`, `rules/api-conventions.md`
- Path-specific rules через glob-паттерны:
  ```
  # .claude/rules/frontend.md
  ---
  globs: ["src/components/**/*.tsx", "src/hooks/**/*.ts"]
  ---
  Use React functional components with hooks...
  ```
- Загружается ТОЛЬКО когда Claude работает с файлами matching glob
- Экономит контекст по сравнению с всё-в-одном CLAUDE.md

### 4. Антипаттерны
- **Bloated CLAUDE.md**: 500+ строк → каждая сессия стартует с огромным overhead
- **CLAUDE.md как enforcement**: это SUGGESTIONS, не гарантии. Claude может игнорировать. Для гарантий → hooks
- **Дублирование**: одно и то же в project CLAUDE.md и user CLAUDE.md
- **Устаревшие правила**: CLAUDE.md должен поддерживаться актуальным

### 5. Миграция в Skills
- Инструкции используемые не в каждой сессии → перенести в Skills
- Skills загружаются по требованию = экономия контекста
- Правило: если инструкция нужна < 50% сессий → в Skill, не в CLAUDE.md

### 6. CLAUDE.md imports
- Можно импортировать другие md файлы
- Структурирует длинные конфигурации
- Позволяет шарить общие правила между проектами

## Источники

### Официальные
1. **Using CLAUDE.md files** — Anthropic Blog
   - URL: https://www.claude.com/blog/using-claude-md-files
   - Дата: Nov 25, 2025
   - Ключевое: официальный гайд, примеры, best practices

2. **Manage Claude's memory** — Claude Code Docs
   - URL: https://code.claude.com/docs/en/memory
   - Ключевое: полная документация по memory system, включая rules dir, imports, auto memory

3. **Best Practices for Claude Code** — Claude Code Docs
   - URL: https://code.claude.com/docs/en/best-practices
   - Ключевое: секция "Write an effective CLAUDE.md"

### Гайды
4. **The Complete Guide to CLAUDE.md** — Claude Directory
   - URL: https://www.claudedirectory.org/blog/claude-md-guide
   - Дата: Feb 10, 2026
   - Ключевое: от структуры до advanced patterns, примеры для каждого стека

5. **CLAUDE.md Optimization: Tips 16-25** — Developer Toolkit
   - URL: https://developertoolkit.ai/en/claude-code/tips-tricks/claude-md-optimization/
   - Дата: Feb 9, 2026
   - Ключевое: 10 конкретных tips, strategic placement, team alignment

6. **Claude.md: Best Practices Learned from Optimizing with Prompt Learning** — Arize
   - URL: https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/
   - Ключевое: data-driven подход к оптимизации CLAUDE.md

7. **The Complete Guide to Claude Code V2** — Reddit (TheDecipherist)
   - URL: https://www.reddit.com/r/ClaudeAI/comments/1qcwckg/the_complete_guide_to_claude_code_v2_claudemd_mcp/
   - Ключевое: viral guide, V2 добавляет "rules are suggestions" insight, enforcement layer

8. **Claude Code Customization: CLAUDE.md, Slash Commands, Skills, and Subagents** — alexop.dev
   - URL: https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/
   - Дата: Dec 21, 2025
   - Ключевое: связь CLAUDE.md → Commands → Skills → Subagents, Dexie.js пример
