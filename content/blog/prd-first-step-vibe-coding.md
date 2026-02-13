---
title: "Почему PRD — первый шаг вайб-кодинга, а не лишняя бюрократия"
date: 2026-02-12
lastmod: 2026-02-12
description: "Без PRD Claude Code выбирает среднестатистическое решение. 10 минут на документ экономят часы переделок."
tags: ["вайб-кодинг", "prd", "claude-code", "продуктивность"]
slug: "prd-first-step-vibe-coding"
draft: false
---

Ты открываешь Claude Code. Пишешь "сделай авторизацию". Через пять минут — рабочий код. Который ты потом переделываешь два дня.

Знакомо? У меня так было в двух проектах подряд. Проект igorf-tech — 28 промптов, пытаясь объяснить Claude Code, что мне нужно. Youtube-me — 37. Каждый третий промпт начинался с "нет, я имел в виду другое". Инструмент тут ни при чём. Я просто не объяснил, чего хочу.

## Почему AI выбирает "среднее"

Когда ты пишешь "сделай авторизацию", Claude Code не знает: тебе нужен JWT или сессии? OAuth через Google или email/password? Роли нужны или нет? Он берёт самый вероятный вариант из обучающих данных. Среднестатистическое решение для среднестатистического проекта.

Андрей Карпатый назвал это context engineering — искусство заполнить контекстное окно правильной информацией. Мало контекста — AI выбирает наугад. Переизбыток деталей топит в шуме, и модель теряет фокус. По данным CodeRabbit, AI-код без чётких спецификаций содержит в 1.7 раза больше проблем: логические ошибки, дыры в безопасности, пропущенная обработка ошибок.

## PRD как ограничитель

Для вайб-кодинга этот документ — не монстр на 30 страниц из корпоративного мира. Одна страница. Десять минут работы. Иногда пять.

Что туда входит: какую проблему решаем, для кого, что точно НЕ делаем, и как поймём что готово. Всё. Четыре пункта.

Luke Bechtel, автор концепции "vibe specs", замерил: 10-20 минут планирования экономят часы переделок. Фичи стали занимать заметно меньше времени — он говорит о существенном сокращении цикла разработки. Не потому что кодил быстрее. Потому что кодил правильное.

"Неважно, как быстро ты создаёшь что-то, если оно бесполезно" — его слова.

## Мой workflow сейчас

Я открываю Claude Code и пишу `/create-prd`. Под капотом — вот такой промпт:

```
You are a senior Product Manager creating a Product Requirements Document.

## Process

### Phase 1: DISCOVER
Ask me **5 targeted questions** to understand the feature. Questions should cover:
- What problem are we solving and for whom?
- What does success look like? (measurable outcomes)
- Are there existing solutions or workarounds?
- What are the constraints? (time, tech, budget)
- What's the scope boundary? (what is NOT included)

Wait for my answers before proceeding.

### Phase 2: CLARIFY
Based on my answers:
- Identify gaps, ambiguities, or contradictions
- Ask **2-3 follow-up questions** to resolve them
- If anything is still unclear, ask again — do NOT assume

Wait for my answers before proceeding.

### Phase 3: GENERATE
Create the PRD with these sections:

# PRD: [Feature Name]

**Author:** [auto-detect from git or ask]
**Date:** [today]
**Status:** Draft
**Version:** 1.0

## 1. Problem Statement
What problem exists and why it matters. Include evidence or user pain points.

## 2. Goals & Success Metrics
- Goal 1 → Metric (measurable, with target)
- Goal 2 → Metric
- Goal 3 → Metric

## 3. Target Users
Who are the primary and secondary users. Include relevant personas or segments.

## 4. User Stories
- As a [user], I want [action] so that [outcome]
- One story per behavior, each must be testable

## 5. Functional Requirements

### P0 — Must Have
- [ ] REQ-001: ...
- [ ] REQ-002: ...

### P1 — Should Have
- [ ] REQ-010: ...

### P2 — Nice to Have
- [ ] REQ-020: ...

## 6. Non-Functional Requirements
- Performance: ...
- Security: ...
- Scalability: ...
- Accessibility: ...

## 7. Acceptance Criteria
Testable conditions that must be true for the feature to be considered complete.
- [ ] AC-001: Given [context], when [action], then [result]
- [ ] AC-002: ...

## 8. Design Considerations
UI/UX notes, wireframe references, or interaction patterns.

## 9. Technical Considerations
Architecture decisions, API changes, database schema, dependencies, migration needs.

## 10. Out of Scope
Explicitly list what this PRD does NOT cover to prevent scope creep.

## 11. Open Questions
Unresolved items that need answers before or during implementation.

## 12. Dependencies & Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| ...  | ...    | ...        |

### Phase 4: VALIDATE
Score the PRD on a 100-point scale:
- **Functional Clarity** (30 pts): Are requirements specific and testable?
- **Technical Specificity** (25 pts): Can an engineer implement from this alone?
- **Business Context** (25 pts): Is the "why" clear with measurable goals?
- **Completeness** (20 pts): Are all sections filled, no TBDs?

If score < 85: identify weak sections and ask me to provide more details.
If score >= 85: present the final PRD for my approval.

### Phase 5: SAVE
After my approval, save the PRD to: ./docs/prd-$ARGUMENTS.md

If the ./docs/ directory does not exist, create it.

---

## Rules
- Use clear, specific language. Avoid "fast", "secure", "scalable" without concrete numbers.
- Every requirement must be testable — if you can't write a test for it, rewrite it.
- Use "shall" for mandatory requirements, "should" for recommended, "may" for optional.
- Do NOT write any code. This is a requirements document only.
- Communicate in the same language the user uses.
```

AI сам задаёт правильные вопросы: что за фича, кто пользователь, какие ограничения, что вне скоупа. За 10 минут у меня готовый документ. Дальше кодинг идёт точно в цель.

Разница? В youtube-me до этого я тратил 37 промптов на фичу, половина — переделки и уточнения. Теперь — 5-7 промптов, и результат с первого подхода. Claude Code перестал гадать, потому что я перестал заставлять его гадать.

## Итог

Десять минут структурирования мыслей против часов переделок. Математика простая. Такой подход не замедляет вайб-кодинг — он даёт AI понять, чего ты хочешь.

Алекс Лукашевич из Forte Group говорил примерно так: "AI не решает архитектуру — он обнажает её отсутствие". Документ с требованиями — это та самая архитектура. Минимальная, но достаточная.
