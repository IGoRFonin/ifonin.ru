# Статья 10: Git Worktrees — физическая изоляция для параллельных агентов

**Серия**: Оптимизация контекста в Claude Code
**Тип**: Практическая, workflow
**Целевая аудитория**: Разработчики, работающие с несколькими задачами одновременно

## Ключевой тезис

Субагенты изолируют контекст. Worktrees изолируют файловую систему. Вместе — это полная изоляция для параллельной AI-разработки. Правило: 1 агент = 1 worktree = 1 ветка.

## Основные идеи

### 1. Проблема: конфликт при параллельной работе
- Два Claude Code инстанса в одной директории = перезапись файлов друг другом
- Ветки не спасают: файловая система одна, git checkout меняет файлы для обоих
- `git stash` при переключении контекста = потеря momentum, риск конфликтов

### 2. Что такое Git Worktrees
- Несколько рабочих директорий, разделяющих один `.git`
- Каждая директория = своя ветка, свои файлы, полная изоляция
- Общая git history без overhead полного клона
- Lightweight: не копирует repo, создаёт symlink на .git

### 3. Базовый setup
```bash
# Из основного проекта
git worktree add .worktrees/feature-auth -b feature-auth
git worktree add .worktrees/bugfix-api -b bugfix-api
git worktree add .worktrees/refactor-db -b refactor-db

# Открыть Claude Code в каждом
cd .worktrees/feature-auth && claude
# (в другом терминале)
cd .worktrees/bugfix-api && claude
```

### 4. Workflow: параллельная разработка
1. Создать worktrees для каждой задачи
2. Открыть Claude Code в каждом worktree
3. Назначить задачу каждому инстансу
4. Работать параллельно — полная изоляция
5. Merge результаты через обычный git merge/PR

### 5. Два режима оркестрации (parallel-worktrees skill)
#### Background Orchestration
- Main agent делегирует background agents в worktrees
- Main продолжает работу
- Синхронизирует результаты когда background agents завершили

#### Manual Multi-Terminal
- Разработчик открывает несколько терминалов
- Каждый терминал = свой worktree + свой Claude
- Человек координирует

### 6. LLM Non-determinism как фича
- N параллельных агентов = N различных решений
- Выбираешь лучшее (или комбинируешь)
- SpillwaveSolutions: "exploits LLM non-determinism as a feature"

### 7. CLAUDE.md в worktrees
- Каждый worktree может иметь свой CLAUDE.md
- Или наследовать от основного проекта
- Можно давать разные инструкции разным агентам через разные CLAUDE.md

### 8. Cleanup
```bash
# Удалить worktree после merge
git worktree remove .worktrees/feature-auth
# Или prune неиспользуемые
git worktree prune
```

## Источники

### Полные гайды
1. **Git Worktrees with Claude Code: The Complete Guide** — Engineering Notes (Muthu)
   - URL: https://notes.muthu.co/2026/02/git-worktrees-with-claude-code-the-complete-guide/
   - Дата: Feb 2, 2026
   - Ключевое: от основ до advanced, custom commands, automation scripts, troubleshooting
   - **КЛЮЧЕВОЙ ИСТОЧНИК**

2. **Running Multiple Claude Code Agents Safely with Git Worktrees** — Coderflex
   - URL: https://coderflex.com/blog/running-multiple-claude-code-agents-safely-with-git-worktrees
   - Дата: Jan 18, 2026
   - Ключевое: core rule "1 agent = 1 worktree = 1 branch", filesystem isolation focus

3. **Claude Code Worktree: The Complete Developer Guide** — Supatest AI
   - URL: https://supatest.ai/blog/claude-code-worktree-the-complete-developer-guide
   - Дата: Sep 22, 2025
   - Ключевое: context pollution avoidance, multi-threaded development, step-by-step setup

### Параллельные workflows
4. **The Parallel Claude Workflow: Running Multiple AI Agents** — ASleekGeek
   - URL: https://asleekgeek.com/articles/parallel-claude-workflow
   - Ключевое: narrative + practical guide, Commodore 64 аналогия, orchestration patterns

5. **Running Claude Agents in Parallel with Git Worktrees** — CuriouslyChase
   - URL: https://curiouslychase.com/ai-development/running-claude-agents-in-parallel-with-git-worktrees/
   - Дата: Oct 30, 2025
   - Ключевое: minimal setup guide, problem/solution format

6. **Supercharging Development: Using Git Worktree & AI Agents** — Mike Welsh / Medium
   - URL: https://medium.com/@mike-welsh/supercharging-development-using-git-worktree-ai-agents-4486916435cb
   - Дата: Jul 2, 2025
   - Ключевое: large codebase focus, context switching elimination

### Tools & Skills
7. **SpillwaveSolutions/parallel-worktrees** — GitHub
   - URL: https://github.com/spillwavesolutions/parallel-worktrees
   - Ключевое: SKILL.md для parallel worktrees, two modes (background + manual), LLM non-determinism as feature

8. **Git Worktrees with Claude Code Agents: A Standard Operating Procedure** — Alchemist Studios
   - URL: https://alchemiststudios.ai/articles/git-worktrees-claude-code-agents.html
   - Дата: Jan 6, 2025
   - Ключевое: SOP формат, junior-friendly, fundamentals explained
