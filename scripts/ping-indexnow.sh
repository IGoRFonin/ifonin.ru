#!/usr/bin/env bash
set -euo pipefail

SITE_URL="https://ifonin.ru"
KEY="3102e3d2-20c1-4cc9-bf32-aa467de2d211"
SITEMAP="public/sitemap.xml"

if [ ! -f "$SITEMAP" ]; then
  echo "Sitemap не найден: $SITEMAP"
  exit 1
fi

# Извлекаем все URL из sitemap
URLS=$(sed -n 's/.*<loc>\(.*\)<\/loc>.*/\1/p' "$SITEMAP")
COUNT=$(echo "$URLS" | wc -l | tr -d ' ')

# Формируем JSON-массив URL
URL_LIST=$(echo "$URLS" | sed 's/.*/"&"/' | paste -sd ',' -)

JSON=$(cat <<EOF
{
  "host": "ifonin.ru",
  "key": "$KEY",
  "keyLocation": "$SITE_URL/$KEY.txt",
  "urlList": [$URL_LIST]
}
EOF
)

# Отправляем в IndexNow через Yandex (раздаёт всем участникам)
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "https://yandex.com/indexnow" \
  -H "Content-Type: application/json" \
  -d "$JSON")

if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "202" ]; then
  echo "IndexNow: отправлено $COUNT URL (HTTP $RESPONSE)"
else
  echo "IndexNow: ошибка HTTP $RESPONSE"
  exit 1
fi
