# Статья 2: Как устроен контекст внутри — токены, окно, буфер

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Техническая, объяснительная
**Целевая аудитория**: Разработчики которые хотят понять механику

## Ключевой тезис

Контекстное окно — это не пассивное хранилище, а активная рабочая память. Понимание его устройства — основа всей оптимизации.

## Основные идеи

### 1. Цифры и ограничения
- Окно Sonnet 4.5: 200K токенов
- Окно Opus 4.6: до 1M токенов (бета, >200K стоит 2x)
- Зарезервированный compaction buffer: ~45K токенов (22.5%) — hardcoded
- Реально доступно: ~155K токенов
- 1000 токенов ≈ 750 слов ≈ 40 строк кода
- Auto-compact триггер: ~77-78% заполнения окна

### 2. Что заполняет контекст
- System prompts (встроенные инструкции Claude Code)
- CLAUDE.md файлы (все уровни)
- Auto Memory (MEMORY.md — первые 200 строк)
- MCP tool definitions (500-2000 токенов на сервер)
- Каждое сообщение пользователя
- Каждый ответ Claude
- Все tool inputs и outputs (чтение файлов, команды, ошибки)
- Extended thinking tokens (не видимы, но занимают место)

### 3. Context Buffer — скрытый резерв
- 45K токенов зарезервированы и не могут быть использованы
- Существует для: генерации ответа, thinking, tool calls
- Нельзя изменить — hardcoded в Claude Code
- Compaction срабатывает задолго до реального заполнения

### 4. Деградация по мере заполнения
- Первыми деградируют: code review с пониманием архитектуры, дебаг сложных взаимодействий, рефакторинг нескольких файлов
- Последними деградируют: изолированные задачи (написание одной функции, форматирование)
- Гипотеза Matsuoka: Anthropic намеренно понижает порог auto-compact для сохранения качества рассуждений

### 5. Как отслеживать
- Status bar в Claude Code — процент оставшегося контекста
- `/cost` — показывает потребление токенов
- `/context` — детали использования контекста
- `/doctor` — диагностика, включая MCP context warnings

## Источники

### Первоисточники (Anthropic)
1. **Context windows** — API docs
   - URL: https://platform.claude.com/docs/en/build-with-claude/context-windows
   - Ключевое: официальная документация по контекстным окнам

2. **How Claude Code works** — Claude Code docs
   - URL: https://code.claude.com/docs/en/how-claude-code-works
   - Ключевое: agentic loop, context window section, when context fills up

3. **Manage costs effectively** — Claude Code docs
   - URL: https://code.claude.com/docs/en/costs
   - Ключевое: track costs, reduce token usage, manage context proactively

### Аналитические статьи
4. **Claude Code Context Buffer: Why 45K Tokens Are Reserved** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/mechanics/context-buffer-management
   - Дата: Jan 28, 2026
   - Ключевое: 45K buffer breakdown, compaction trigger точные цифры, workarounds

5. **How Claude Code Got Better by Protecting More Context** — Robert Matsuoka
   - URL: https://hyperdev.matsuoka.com/p/how-claude-code-got-better-by-protecting
   - Дата: Dec 10, 2025
   - Ключевое: гипотеза про intentional early compaction, 54% gap между reported и actual usage

6. **Claude Code Context Window: Optimize Your Token Usage** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/mechanics/context-management
   - Дата: Jan 17, 2026
   - Ключевое: memory-intensive vs isolated tasks, 5x effective context strategies

7. **Understanding Context Windows and Token Limits** — Developer Toolkit
   - URL: https://developertoolkit.ai/en/shared-workflows/context-management/context-windows/
   - Дата: Feb 9, 2026
   - Ключевое: правила пальца по потреблению контекста разными типами задач, prompts for recovery

8. **The Ultimate Guide to Claude Code Context Management** — Substratia
   - URL: https://substratia.io/blog/context-management-guide/
   - Дата: Jan 11, 2026
   - Ключевое: 12 min deep dive, практический опыт ежедневного использования

9. **Managing Costs and Token Usage in Claude Code** — Steve Kinney
   - URL: https://stevekinney.com/courses/ai-development/cost-management
   - Ключевое: cost drivers breakdown, model choice impact (Opus = 5x Sonnet)

10. **Mastering Claude's Context Window: A 2025 Deep Dive** — Sparkco AI
    - URL: https://sparkco.ai/blog/mastering-claudes-context-window-a-2025-deep-dive
    - Дата: Oct 22, 2025
    - Ключевое: context quality > quantity, multi-turn conversations strategies
