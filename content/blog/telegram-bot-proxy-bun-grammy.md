---
title: "Как AI-инструмент нашёл прокси для Telegram бота в зависимостях"
date: 2026-03-23
lastmod: 2026-03-23
description: "Claude Code нашёл нативную поддержку proxy в Bun через grep по node_modules grammY - без дополнительных зависимостей"
tags: ["claude-code", "telegram", "bun", "вайб-кодинг"]
slug: "telegram-bot-proxy-bun-grammy"
draft: false
---

Когда Telegram API заблокирован на уровне провайдера, разработчикам обычно нужна горсть npm-пакетов для прокси. Claude Code нашёл нативное решение в одном grep-запросе по node_modules - без единой дополнительной зависимости.

## Блокировка Telegram API в РФ: как я на это наткнулся

api.telegram.org недоступен с большинства провайдеров в РФ (актуально на начало 2026). Когда я развернул бота на российском сервере, он просто не откликался. Я потратил час на диагностику, пока не понял - это блокировка, а не моя ошибка в коде.

Пробовал три пути: VPN глобально через env - не сработало. Установил https-proxy-agent - работало, но добавляло несколько строк настройки и ещё одну зависимость. Третий вариант - Telegram Bot API Server на tdlib - слишком тяжёлый для одного polling-бота.

## Как Claude Code нашёл решение в node_modules

Я запустил defi-usd-bot - бот для мониторинга доходности стейблкоинов на DeFi-площадках (Aave, Curve, примерно 50-60 источников). Стек: Bun, grammY, Playwright, croner. Промпт был простым: "сделай бота рабочим, он не может дозвониться до Telegram API".

Claude Code не полез гуглить пакеты. Запустил grep по node_modules grammY.

Когда я открыл исходники - оказалось, grammY использует стандартный fetch() и передаёт пользовательский объект baseFetchConfig напрямую в него как RequestInit. Без трансформаций, без обёрток. Просто `fetch(url, { ...baseFetchConfig })`.

Дальше - ключевой момент. Bun расширяет стандартный RequestInit собственным свойством `proxy`. Это не Web API, это Bun-специфичное расширение runtime. Node.js так не умеет.

Цепочка простая: grammY передаёт baseFetchConfig в fetch - Bun видит свойство proxy - маршрутизирует запросы. Ноль дополнительных зависимостей.

## Реализация

```typescript
import { Bot } from "grammy";

const token = process.env.TELEGRAM_BOT_TOKEN!;
const proxy = process.env.PROXY_URL; // http://proxy.example.com:8080

const bot = new Bot(token, {
  client: {
    baseFetchConfig: proxy ? { proxy } as any : undefined
  }
});
```

`as any` - необходимый костыль: TypeScript-типы grammY не включают Bun-специфичные расширения RequestInit. Это не баг grammY, просто Bun расширяет стандартный интерфейс.

С https-proxy-agent пришлось бы писать больше: импорт агента, создание экземпляра, настройка dispatcher. Здесь - одна строка с proxy. В том же проекте Playwright тоже ходит через прокси: `proxy: proxy ? { server: proxy } : undefined` в browser.ts. Весь proxy-код в двух файлах - несколько строк суммарно.

На весь бот ушло 6 промптов в Claude Code: структура проекта, парсинг данных, расписание через croner, рассылка в Telegram. Итого около 200 строк кода.

## Почему это работает только в Bun

Node.js не добавил нативную поддержку proxy в fetch. Хочешь прокси - ставь https-proxy-agent или undici с ProxyAgent.

Deno поддерживает HTTP_PROXY и HTTPS_PROXY как env-переменные, но не через аргументы fetch. Bun поддерживает оба варианта: и env-переменные, и явный `{ proxy }` в RequestInit.

Решение выше переносимо только при условии Bun runtime. На Node.js код с `{ proxy }` просто проигнорирует это поле - и бот не дозвонится до Telegram.

## Что из этого следует

Zero dependencies для proxy - это реальное преимущество. Меньше зависимостей, меньше точек поломки при обновлениях.

`as any` остаётся костылём, пока grammY или TypeScript не расширят типы для Bun. Жить с этим можно.

Самое неочевидное здесь - не сам код. Claude Code нашёл решение через чтение исходников grammY - и понял, как данные идут от пользователя до fetch. Иногда ответ уже встроен в runtime.
