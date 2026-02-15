# Статья 1: Context Engineering — новая парадигма

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Вводная, концептуальная
**Целевая аудитория**: Разработчики, начинающие использовать Claude Code; те кто знаком с prompt engineering

## Ключевой тезис

2025 = год промптов, 2026 = год контекста. Сдвиг от "как правильно спросить" к "что модель видит в момент генерации". Prompt engineering — это подмножество context engineering.

## Основные идеи

### 1. Определение Context Engineering
- **Цитата Karpathy**: "Context engineering is the delicate art and science of filling the context window with just the right information for the next step"
- Context = все токены, которые модель видит при генерации: system prompts, history, tool outputs, injected files
- Engineering = оптимизация полезности этих токенов при ограниченном бюджете

### 2. Почему промпт-инженерия недостаточна
- Промпт — это одна строка. Контекст — это всё окружение: CLAUDE.md, MCP tools, файлы, история
- В агентных системах контекст постоянно меняется — агент сам решает что читать, какие тулы вызывать
- "Clever prompts" ломаются когда контекст заполнен мусором

### 3. Четыре детерминистических паттерна контекста (по Kane Zhu)
- Паттерн 1: Structured project context (CLAUDE.md)
- Паттерн 2: Skill-based dynamic loading
- Паттерн 3: Tool isolation через субагентов
- Паттерн 4: Deterministic enforcement через hooks

### 4. Шесть столпов (Six Pillars Framework)
- Из статьи ClaudeFast — фреймворк для систематического подхода к context engineering в Claude Code

### 5. Практический пример
- Плохо: `claude "Here's my entire codebase architecture, all conventions, every pattern we use, plus the task..."`
- Хорошо: `claude "Build the auth module"` + Skills загружают нужный контекст автоматически

## Источники

### Первоисточники (Anthropic)
1. **Effective context engineering for AI agents** — каноничная статья Anthropic
   - URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
   - Дата: Sep 29, 2025
   - Ключевое: определение context engineering, стратегии оптимизации, thinking in context

### Аналитические статьи
2. **Beyond Prompts: 4 Context Engineering Secrets for Claude Code** — Kane Zhu
   - URL: https://kane.mx/posts/2025/context-engineering-secrets-claude-code/
   - Дата: Nov 14, 2025
   - Ключевое: 4 детерминистических паттерна, практические примеры с Claude Code

3. **Context Engineering: The Six Pillars That Make Claude Code Reliable** — ClaudeFast
   - URL: https://claudefa.st/blog/guide/mechanics/context-engineering
   - Ключевое: 6-столпный фреймворк, сравнение prompt vs context engineering

4. **Context Engineering vs Prompt Engineering: The 2025 AI Shift** — Aqil Khan
   - URL: https://medium.com/@aqilraza/context-engineering-vs-prompt-engineering-the-2025-ai-shift-13156842c8a3
   - Дата: Jan 24, 2026
   - Ключевое: эволюция от prompt к context, почему это фундаментальный сдвиг

5. **Prompt Engineering vs Context Engineering** — Anup Jadhav
   - URL: https://www.anup.io/prompt-engineering-vs-context-engineering/
   - Дата: Oct 06, 2025
   - Ключевое: фреймы различий, аналогия с software architecture

6. **Claude Skills Architecture Decoded: From Prompt Engineering to Context Engineering** — JIN / AImonks
   - URL: https://medium.com/aimonks/claude-skills-architecture-decoded-from-prompt-engineering-to-context-engineering-a6625ddaf53c
   - Дата: Jan 21, 2026
   - Ключевое: архитектурный взгляд, сравнение с микросервисами

7. **Context Engineering for Developers: The Complete Guide** — Faros AI
   - URL: https://www.faros.ai/blog/context-engineering-for-developers
   - Ключевое: гайд для разработчиков, практические стратегии

### Контекст тренда
8. **Maja Voje (LinkedIn)**: "2025 was the year of the Prompt. 2026 is the year of Context"
   - URL: https://www.linkedin.com/posts/majavoje_2025-was-the-year-of-the-prompt-2026-is-activity-7426655997605101568-fhVD
   - Ключевое: trend framing, GTM perspective

9. **Learning Claude Code — From Context Engineering to Multi-Agent Workflows** — Aayush Agrawal
   - URL: https://medium.com/@aayushmnit/learning-claude-code-from-context-engineering-to-multi-agent-workflows-4825e216403f
   - Дата: Jan 25, 2026
   - Ключевое: learning journey, от контекста к мульти-агентам
