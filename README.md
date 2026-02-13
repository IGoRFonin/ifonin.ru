# ifonin.ru

Экспертный блог о вайб-кодинге, AI-инструментах и пет-проектах. На русском языке.

## Стек

- **Hugo** — генератор статических сайтов
- **Кастомная тема** с нуля (без сторонних тем)
- **CSS** — один файл `static/style.css`, без фреймворков
- **JS** — нет
- **Деплой** — GitHub → Coolify (self-hosted, российский VPS) → nginx

## Быстрый старт

### Требования

- [Hugo](https://gohugo.io/installation/) (extended edition)

### Установка Hugo

```bash
# macOS
brew install hugo

# Linux (snap)
snap install hugo

# Или скачать бинарник: https://github.com/gohugoio/hugo/releases
```

### Локальная разработка

```bash
git clone git@github.com:<user>/ifonin.ru.git
cd ifonin.ru

# Запуск dev-сервера с черновиками
hugo server -D
```

Сайт будет доступен по адресу http://localhost:1313

### Создание нового поста

```bash
hugo new blog/my-post-slug.md
```

Пост создаётся из архетипа `archetypes/blog.md` с заполненным front matter.

### Сборка для продакшена

```bash
hugo --minify
```

Результат — папка `public/`.

## Деплой через Docker

```bash
docker build -t igorf-ru .
docker run -p 8080:80 igorf-ru
```

Dockerfile использует multi-stage сборку: Hugo собирает сайт, nginx раздаёт статику.

## Структура проекта

```
├── archetypes/blog.md     — шаблон нового поста
├── content/
│   ├── _index.md          — главная страница
│   ├── about.md           — обо мне
│   └── blog/              — посты блога
├── layouts/
│   ├── _default/baseof.html — базовый wrapper
│   ├── index.html         — шаблон главной
│   ├── blog/              — list.html, single.html
│   └── partials/seo/      — meta, opengraph, jsonld
├── static/                — картинки, favicon, robots.txt
├── hugo.toml              — конфигурация сайта
└── Dockerfile             — сборка и деплой
```

## Дизайн

Бруталистский минимализм: системный `monospace`, без внешних шрифтов, иконок и анимаций. Максимальная ширина контента — 640px.
