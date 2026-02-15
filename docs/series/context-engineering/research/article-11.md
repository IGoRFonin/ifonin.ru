# Статья 11: Prompt Caching и Adaptive Thinking — API-уровень оптимизации

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Техническая, для продвинутых
**Целевая аудитория**: Разработчики API, те кто хочет понять что под капотом

## Ключевой тезис

Claude Code использует API-level оптимизации под капотом: prompt caching для переиспользования контекста между вызовами, и adaptive thinking для динамического распределения "бюджета размышлений". Понимание этих механизмов объясняет почему Claude Code быстрее и дешевле чем наивное использование API.

## Основные идеи

### 1. Prompt Caching

#### Что это
- Кеширование неизменяемых префиксов промпта между API-вызовами
- System prompts, tool definitions, CLAUDE.md — кешируются
- Кешированные токены стоят значительно дешевле

#### Цифры
- До 90% снижение стоимости input токенов
- До 85% снижение latency
- Cache TTL: 5 минут (обновляется при каждом использовании)
- Минимум для кеширования: 1024 токена (Sonnet), 2048 (Opus)

#### Как работает в Claude Code
- Каждый tool call = новый API request с тем же системным промптом
- System prompt + CLAUDE.md + tool definitions = большой кешируемый префикс
- Чем длиннее сессия = тем больше экономия
- Claude Code автоматически использует caching (не нужно настраивать)

#### Token-efficient tool use (март 2025)
- Anthropic оптимизировал формат tool definitions
- Меньше токенов на описание каждого инструмента
- Автоматически для всех клиентов

### 2. Context Reuse Patterns (под капотом)

#### LMCache исследование
- Claude Code переиспользует context между tool calls
- Pattern: long shared prefix + short varying suffix
- Идеально для кеширования: большая часть контекста одинакова
- "CacheBlend" pattern: постепенное обновление кеша вместо полной перегенерации

### 3. Adaptive Thinking (Opus 4.6)

#### Что это
- Вместо фиксированного thinking token budget — Claude сам решает сколько думать
- Динамическое масштабирование глубины рассуждений по сложности задачи

#### Уровни effort
| Effort | Поведение | Когда использовать |
|---|---|---|
| `low` | Минимум thinking, пропускает для простых задач | Форматирование, простые вопросы |
| `medium` | Может пропустить thinking для простого | Обычная работа |
| `high` (default) | Почти всегда думает глубоко | Сложные задачи, дебаг |
| `max` | Всегда думает без ограничений | Критические решения |

#### Interleaved thinking
- Claude может думать МЕЖДУ tool calls
- Не только перед первым ответом, а на каждом шаге агентного цикла
- Улучшает качество решений в multi-step workflows

#### Контекстная стоимость
- Thinking tokens потребляют контекст но НЕ видимы пользователю
- На `max` effort: thinking может занять значительную часть окна
- Trade-off: качество рассуждений vs доступный контекст

### 4. 1M Context Window (Opus 4.6 beta)
- 5x увеличение доступного контекста
- Промпты > 200K стоят 2x ($10/$37.50 per M tokens)
- 76% accuracy на MRCR v2 (8-needle, 1M variant) vs 18.5% Sonnet
- Пока бета: API/Enterprise only
- Implications: меньше необходимость в aggressive compaction

### 5. Compaction API
- Programmatic control over compaction через API
- Агенты могут решать КОГДА сжимать
- Ключевое для long-running autonomous agents

## Источники

### Prompt Caching
1. **Prompt caching** — Claude API Docs
   - URL: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
   - Ключевое: полная документация, code examples, pricing

2. **Token-saving updates on the Anthropic API** — Claude Blog
   - URL: https://claude.com/blog/token-saving-updates
   - Дата: Mar 13, 2025
   - Ключевое: cache-aware rate limits, simpler prompt caching, token-efficient tool use

3. **How to Use Prompt Caching in Claude API: Complete 2026 Guide** — AI Free API
   - URL: https://aifreeapi.com/en/posts/claude-api-prompt-caching-guide
   - Дата: Jan 9, 2026
   - Ключевое: 90% cost reduction, $4K/month savings example, implementation guide

4. **Prompt Caching Explained** — DigitalOcean
   - URL: https://www.digitalocean.com/community/tutorials/prompt-caching-explained
   - Дата: Dec 26, 2025
   - Ключевое: how it works behind the scenes, prompt structure for max cache hits

### Context Reuse
5. **Context Engineering & Reuse Pattern Under the Hood of Claude Code** — LMCache Blog
   - URL: https://blog.lmcache.ai/en/2025/12/23/context-engineering-reuse-pattern-under-the-hood-of-claude-code/
   - Дата: Dec 23, 2025
   - Ключевое: CacheBlend pattern, benchmark results, how Claude Code reuses context internally
   - **КЛЮЧЕВОЙ ИСТОЧНИК**

### Adaptive Thinking
6. **Adaptive thinking** — Claude API Docs
   - URL: https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking
   - Ключевое: официальная документация, effort levels, interleaved thinking

7. **What is Adaptive Thinking in Claude Code** — ClaudeLog
   - URL: https://www.claudelog.com/faqs/what-is-adaptive-thinking-in-claude-code/
   - Дата: Feb 5, 2026
   - Ключевое: практическое объяснение, effort levels comparison

### Opus 4.6
8. **Introducing Claude Opus 4.6** — Anthropic
   - URL: https://www.anthropic.com/news/claude-opus-4-6
   - Дата: Feb 5, 2026
   - Ключевое: 1M context window, Compaction API, adaptive thinking, benchmarks

9. **Claude Opus 4.6: What Actually Changed and Why It Matters** — Han HELOIR YAN / Medium
   - URL: https://medium.com/data-science-collective/claude-opus-4-6-what-actually-changed-and-why-it-matters-1c81baeea0c9
   - Дата: Feb 2026
   - Ключевое: practical implications, migration decisions, real trade-offs

10. **Opus 4.6 breakdown** — Reddit (r/ClaudeAI)
    - URL: https://www.reddit.com/r/ClaudeAI/comments/1qxdv8h/opus_46_breakdown_what_the_benchmarks_actually/
    - Ключевое: community analysis, Compaction API highlight, 1M context real performance
