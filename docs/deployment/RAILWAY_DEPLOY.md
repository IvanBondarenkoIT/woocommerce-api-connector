# Деплой на Railway

## Быстрый старт

1. **Подключите репозиторий**
   - railway.app → New Project → Deploy from GitHub
   - Выберите `woocommerce-api-connector`

2. **Переменные окружения**
   Добавьте в Railway (Settings → Variables):

   ```
   WC_URL=https://dimkava.ge
   WC_CONSUMER_KEY=ck_...
   WC_CONSUMER_SECRET=cs_...
   WC_API_VERSION=wc/v3
   WC_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
   LILU_API_URL=https://api.leeloo.ai/api
   LILU_API_KEY=X-Leeloo-AuthToken
   LILU_API_SECRET=...
   LILU_API_VERSION=v2
   ```

3. **Публичный URL**
   - Settings → Networking → Generate Domain

## Файлы деплоя

- `Dockerfile` — сборка (python:3.11-slim)
- `railway.json` — конфиг (builder: DOCKERFILE)
- `requirements-railway.txt` — зависимости (без customtkinter)

Если Railway всё ещё использует Nixpacks: Settings → Build → Builder → **Dockerfile**.

## Локальная проверка

```bash
railway login
railway link   # привязать к проекту
railway up    # деплой
```

## Важно

- **WC_USER_AGENT** обязателен для Imunify360 (dimkava.ge)
- IP Railway будет другим — если Imunify360 блокирует по IP, добавьте IP Railway в whitelist или используйте User-Agent
