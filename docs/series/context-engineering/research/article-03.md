# Статья 3: Compaction — трёхслойная система сжатия контекста

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Техническая, deep dive
**Целевая аудитория**: Продвинутые пользователи Claude Code

## Ключевой тезис

Compaction — это НЕ "summarize and hope". Это операционный механизм: structured working state + rehydration. Понимание трёх слоёв позволяет работать С системой, а не против неё.

## Основные идеи

### 1. Три слоя compaction

#### Microcompaction (ранний сброс)
- Сбрасывает тяжёлые tool outputs раньше остальных
- Результаты `cat`, `grep`, длинные error logs — первые кандидаты
- Происходит автоматически, незаметно для пользователя
- Цель: освободить место без потери смысла

#### Auto-compaction (автоматическое сжатие)
- Триггер: ~77-78% заполнения контекста
- Claude Code суммаризирует всю историю в "structured working state"
- Контракт суммаризации: summary должен быть reconstruction-grade
- Что сохраняется: текущая задача, принятые решения, найденные проблемы, текущий прогресс
- Что теряется: точные error messages, конкретные function signatures, промежуточные рассуждения

#### Manual `/compact` (ручной вызов)
- Вызов: `/compact` или `/compact [focus instruction]`
- Пример: `/compact focus on the authentication module we've been debugging`
- Позволяет направить суммаризацию на нужные аспекты
- Рекомендация: вызывать до auto-compact, чтобы контролировать что сохраняется

### 2. Rehydration Sequence
После compaction Claude Code выполняет восстановление:
1. Перечитывает recent files (последние файлы с которыми работали)
2. Восстанавливает task list (TodoWrite items)
3. Вставляет continuation instruction — "продолжай работу"
- Это не просто summary — это active state restoration

### 3. Compaction Contract
Summary должен содержать:
- Текущую цель и подцели
- Принятые архитектурные решения
- Обнаруженные проблемы и их статус
- Список изменённых файлов
- Следующие шаги
- Всё что нужно чтобы "новый Claude" мог продолжить работу

### 4. Стратегии работы с compaction
- **Proactive `/compact`**: вызывать на ~50-60% чтобы сохранить контроль
- **Focus instructions**: направлять что сохранить
- **PreCompact hooks**: бекапить полный контекст перед сжатием
- **Threshold-based backups**: бекапы на 30%, 15%, 5%
- **Новая сессия вместо compaction**: для сложных задач лучше начать заново с хорошим промптом

### 5. Compaction API (Opus 4.6)
- Новая фича: programmatic compaction через API
- Позволяет агентным системам управлять compaction самостоятельно
- Ключевое для long-running agents

## Источники

### Реверс-инжиниринг
1. **Inside Claude Code's Compaction System** — Decode Claude
   - URL: https://decodeclaude.com/claude-code-compaction/
   - Дата: Jan 21, 2026
   - Ключевое: reverse-engineered из shipped bundle, три слоя, compaction contract, rehydration sequence
   - **ГЛАВНЫЙ ИСТОЧНИК ДЛЯ СТАТЬИ**

2. **Inside Claude Code's Compaction System** (duplicate/extended)
   - URL: https://decodeclaude.com/compaction-deep-dive/
   - Дата: Jan 21, 2026

### Практические решения
3. **Never Lose Work to Compaction: Threshold-Based Context Backups** — ClaudeFast
   - URL: https://claudefa.st/blog/tools/hooks/context-recovery-hook
   - Дата: Jan 28, 2026
   - Ключевое: hook для бекапов на порогах 30/15/5%, код примеры

4. **The /compact Command** — DeepWiki (claude-code-ultimate-guide)
   - URL: https://deepwiki.com/FlorianBruniaux/claude-code-ultimate-guide/3.3-the-compact-command
   - Дата: Jan 24, 2026
   - Ключевое: подробное описание команды, примеры usage

5. **Context Management and Compaction** — DeepWiki (anthropics/claude-cookbooks)
   - URL: https://deepwiki.com/anthropics/claude-cookbooks/5.3-context-management-and-compaction
   - Дата: Jan 4, 2026

### Официальные
6. **Compaction** — Claude API Docs
   - URL: https://platform.claude.com/docs/en/build-with-claude/compaction (ссылка из навигации API docs)

7. **Introducing Claude Opus 4.6** — Anthropic
   - URL: https://www.anthropic.com/news/claude-opus-4-6
   - Дата: Feb 5, 2026
   - Ключевое: Compaction API упоминается как key feature

### Контекст
8. **[FEATURE] Configurable Auto-Compact Threshold** — GitHub Issue
   - URL: https://github.com/anthropics/claude-code/issues/11819
   - Ключевое: community запрос на настраиваемый порог, пока hardcoded
