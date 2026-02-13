---
title: "Docker vs UFW: порт закрыт, но доступен всем"
date: 2026-02-15
lastmod: 2026-02-15
description: "Docker обходит UFW и открывает порты мимо файрвола. Почему так происходит и три способа это исправить."
tags: ["docker", "linux", "безопасность", "vps", "devops"]
slug: "docker-ufw-port-closed-but-open"
---

Настраиваешь UFW. Закрываешь все порты. Пишешь `ufw deny 8080`, и VPS кажется защищённым. Потом запускаешь Docker с `-p 8080:80` - порт всё равно открыт для всего интернета.

Это архитектурная ловушка Linux. В июне 2024 Alok из realogs.in описал инцидент: MongoDB на порту 27017 в контейнере, UFW блокирует порт. БД доступна извне. Крипто-майнер нашёл её и украл данные.

Я деплоил свой блог через Coolify на российский VPS - Redis был доступен снаружи несмотря на UFW. Час дебага, пока не понял: Docker работает на другом уровне iptables.

## Проблема за 30 секунд

Запусти это:

```bash
sudo ufw deny 8080
sudo ufw status
# Вывод: 8080 DENIED Anywhere

docker run -d -p 8080:80 nginx:alpine

curl http://YOUR_SERVER_IP:8080
# Вывод: Welcome to nginx!
```

UFW говорит "закрыто". Порт доступен всем.

## Почему Docker обходит UFW

Linux обрабатывает пакеты через iptables в несколько этапов. Docker вставляет свои правила на этапе **PREROUTING** (NAT таблица) - когда пакет только пришёл на сервер. UFW работает на этапе **INPUT** (filter таблица) - когда решение уже принято.

```
Входящий пакет на 8080
  ↓
PREROUTING (nat) - Docker одобряет ЗДЕСЬ
  ↓
Routing decision
  ↓
INPUT (filter) - UFW проверяет ЗДЕСЬ (слишком поздно!)
  ↓
Контейнер получает пакет
```

К тому моменту, когда пакет доходит до UFW, Docker уже изменил его адрес на 172.17.0.2:80. Отправил в контейнер. UFW видит пакет - ничего не может сделать.

Srikanth K описал это как следствие устройства фильтрации пакетов в ядре Linux. Docker и UFW работают корректно, но на разных уровнях. Viktor Petersson опубликовал "The Dangers of UFW + Docker" 3 ноября 2014 года.

## Решение #1: DOCKER-USER chain

В 2017 Docker добавил цепь DOCKER-USER в iptables (Docker CE 17.06). Она срабатывает ДО всех Docker-правил.

Docker гарантирует, что никогда не перезапишет её.

Отредактируй `/etc/ufw/after.rules`, добавь в конец:

```bash
# BEGIN UFW AND DOCKER
*filter
:ufw-user-forward - [0:0]
:DOCKER-USER - [0:0]

# Пропустить трафик через UFW цепи
-A DOCKER-USER -j ufw-user-forward

# Разрешить established connections
-A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN

# Блокировать invalid пакеты
-A DOCKER-USER -m conntrack --ctstate INVALID -j DROP

# Разрешить Docker-to-Docker
-A DOCKER-USER -i docker0 -o docker0 -j ACCEPT

# Вернуть контроль UFW
-A DOCKER-USER -j RETURN

COMMIT
# END UFW AND DOCKER
```

Применить:

```bash
sudo ufw reload
```

Теперь UFW работает. Чтобы разрешить контейнер на порту 80:

```bash
sudo ufw route allow proto tcp from any to any port 80
```

Заблокировать MongoDB:

```bash
sudo ufw route deny proto tcp from any to any port 27017
```

Проверка:

```bash
sudo iptables -L DOCKER-USER -n -v
```

## Решение #2: ufw-docker (автоматизация)

Не хочешь редактировать файлы вручную? Есть готовый скрипт с 6230 звёздами на GitHub:

```bash
sudo wget -O /usr/local/bin/ufw-docker \
  https://github.com/chaifeng/ufw-docker/raw/master/ufw-docker
sudo chmod +x /usr/local/bin/ufw-docker
sudo ufw-docker install
sudo ufw reload
```

Управление контейнерами через простые команды:

```bash
docker run -d --name web -p 8080:80 nginx:alpine
sudo ufw-docker allow web 80
```

Для пользователей Coolify проще скопировать первое решение. Занимает 2 минуты.

## Решение #3: Bind к 127.0.0.1 + reverse proxy

Самое надёжное архитектурное решение.

Контейнеры слушают только localhost, весь внешний трафик идёт через nginx или Caddy на хосте.

```bash
# Вместо
docker run -p 8080:80 nginx

# Использовать
docker run -p 127.0.0.1:8080:80 nginx
```

Порт 8080 физически недоступен снаружи - даже если UFW сломается. На хосте поставь Caddy:

```bash
sudo apt install caddy
```

В `/etc/caddy/Caddyfile`:

```
example.com {
  reverse_proxy localhost:8080
}
```

UFW правила становятся простыми:

```bash
sudo ufw allow 80
sudo ufw allow 443
```

## Что нельзя делать

**Не отключай iptables в Docker.** Это ломает DNS внутри контейнеров, inter-container communication и NAT. Docker сам не рекомендует этот подход в документации.

**Не редактируй DOCKER цепи напрямую.** Docker перезапишет все изменения при рестарте.

**Не надейся на UFW без интеграции.** UFW не видит Docker-трафик без DOCKER-USER.

## Это критично прямо сейчас

28 февраля 2025 вышел Docker Engine v28 с улучшенной изоляцией контейнеров в локальных сетях. Порты, опубликованные через `-p`, всё равно доступны извне без дополнительной настройки.

На публичных VPS это серьёзный риск.

Задокументированы инциденты: MongoDB ransomware, crypto-mining malware, DDOS через открытые порты.

5 минут на конфигурацию DOCKER-USER сейчас - спокойный сон потом. Проверь свой VPS прямо сейчас:

```bash
sudo ufw status
docker ps --format "table {{.Ports}}"
```

Видишь опубликованные порты (`0.0.0.0:8080->80/tcp`), а UFW говорит `DENIED`? Ты в зоне риска.
