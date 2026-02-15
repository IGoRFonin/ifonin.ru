# Статья 7: Skills — контекст по требованию

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Практическая
**Целевая аудитория**: Все пользователи Claude Code

## Ключевой тезис

Skills — это on-demand context injection. В отличие от CLAUDE.md (always loaded), Skills загружаются только когда нужны. Это главный механизм экономии контекста для инструкций.

## Основные идеи

### 1. Что такое Skill
- SKILL.md файл + опциональная директория с supporting files
- Markdown инструкции + YAML frontmatter
- Может содержать reference data, templates, examples — всё в своей директории
- Следует открытому стандарту Agent Skills

### 2. Два типа invocation
- **User-invocable**: вызывается через `/skill-name` из терминала
- **Auto-discovered**: Claude сам находит и загружает когда контекст релевантен
- Контролируется через frontmatter: `invocation: user | auto | agent`

### 3. Расположение
```
.claude/skills/
├── code-review/
│   └── SKILL.md
├── deploy/
│   ├── SKILL.md
│   └── deploy-checklist.md
└── test-patterns/
    ├── SKILL.md
    └── examples/
        ├── unit-test-template.ts
        └── integration-test-template.ts
```
- `.claude/skills/` — project-level
- `~/.claude/skills/` — user-level (все проекты)
- Legacy: `.claude/commands/*.md` — продолжают работать как skills

### 4. Frontmatter
```yaml
---
name: code-review
description: Reviews code for quality, security, and performance
invocation: user
---
```
- `name`: для вызова через `/name`
- `description`: Claude использует для auto-discovery
- `invocation`: кто может вызвать (user/auto/agent)

### 5. Преимущество для контекста
- CLAUDE.md: 100 строк инструкций = ~500 токенов В КАЖДОЙ сессии
- Skill: те же 100 строк = 0 токенов пока не нужен
- Правило миграции: инструкция нужна < 50% сессий → переноси в Skill
- Из доки Anthropic: "Move instructions from CLAUDE.md to skills"

### 6. Skills vs MCP: контекстная эффективность
- Skills с скриптами: 10-100x меньше токенов чем MCP
- MCP: загружает tool definitions + промежуточные результаты в контекст
- Skill со скриптом: исполняет скрипт ВНЕ контекста, возвращает только результат
- Для частых операций: Skill > MCP

### 7. Dynamic context injection
- Skill может подгрузить reference files из своей директории
- Claude читает supporting файлы когда Skill активирован
- Пример: deploy skill подгружает checklist и infra docs только при деплое

### 8. Subagent execution
- Skills могут запускаться как субагенты (свой контекст)
- `invocation: agent` — Claude запускает skill в изолированном окне
- Двойная экономия: on-demand загрузка + изоляция контекста

## Источники

### Официальные
1. **Extend Claude with skills** — Claude Code Docs
   - URL: https://code.claude.com/docs/en/skills
   - Ключевое: полная документация, slash commands merger, frontmatter options, Agent Skills standard

2. **The Complete Guide to Building Skills for Claude** — Anthropic PDF
   - URL: https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf
   - Ключевое: официальный 28-страничный гайд, planning → testing → distribution
   - **КЛЮЧЕВОЙ ИСТОЧНИК**

3. **Best Practices for Claude Code** — Claude Code Docs
   - URL: https://code.claude.com/docs/en/best-practices
   - Ключевое: секции "Create skills", "Move instructions from CLAUDE.md to skills"

### Гайды
4. **Claude Code Skills and Slash Commands: The Complete Guide** — OneAway
   - URL: https://oneaway.io/blog/claude-code-skills-slash-commands
   - Ключевое: реальные примеры от growth agency, SOP для AI, token usage optimization

5. **Claude Skills Architecture Decoded: From Prompt Engineering to Context Engineering** — JIN / AImonks
   - URL: https://medium.com/aimonks/claude-skills-architecture-decoded-from-prompt-engineering-to-context-engineering-a6625ddaf53c
   - Дата: Jan 21, 2026
   - Ключевое: архитектурный анализ, аналогия с микросервисами

6. **Claude Code Customization: CLAUDE.md, Slash Commands, Skills, and Subagents** — alexop.dev
   - URL: https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/
   - Дата: Dec 21, 2025
   - Ключевое: полное сравнение CLAUDE.md vs Commands vs Skills vs Subagents

7. **Ultimate guide to extending Claude Code** — Alireza Rezvani / GitHub Gist
   - URL: https://gist.github.com/alirezarezvani/a0f6e0a984d4a4adc4842bbe124c5935
   - Ключевое: ecosystem overview: Tresor + Skill Factory + Skills Library (26+ packages)

### Экосистема
8. **awesome-claude-skills** — GitHub (ComposioHQ)
   - URL: https://github.com/ComposioHQ/awesome-claude-skills
   - Ключевое: 23K+ stars, MCP builder reference, community skills collection

9. **Claude Code Custom Commands: Build Your Own AI Agents** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/agents/custom-agents
   - Дата: Jan 17, 2026
   - Ключевое: quick start (2 min), .claude/commands/ pattern, reusable prompts
