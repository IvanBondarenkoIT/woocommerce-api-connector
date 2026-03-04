# Imunify360 — главное правило (без whitelist)

## Факт

**Whitelist IP не используется.** В Imunify360 нет ни одного whitelist IP — ни Railway, ни локального.

## Проблема

```
500 / 200: Access denied by Imunify360 bot-protection. IPs used for automation should be whitelisted
```

Imunify360 иногда возвращает **200** с текстом ошибки в теле (вместо 500).

## Рабочее решение (без whitelist)

### 1. User-Agent — обязательно

В **каждый** вызов `API()` передавать `user_agent` — браузерный User-Agent Chrome:

```python
wcapi = API(
    url=...,
    consumer_key=...,
    consumer_secret=...,
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
)
```

**Важно:** `session.headers` не работает — библиотека woocommerce не использует session.

### 2. WC_USER_AGENT в .env

```env
WC_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
```

Скопировать из браузера: dimkava.ge → F12 → Network → Request Headers → User-Agent.

### 3. Патч с браузерными заголовками

`patch_api_with_browser_headers()` добавляет: Referer, Accept-Language, sec-ch-ua, sec-fetch-*.

Версия Chrome в sec-ch-ua должна совпадать с User-Agent (извлекается автоматически).

### 4. Retry при блокировке

При ответе с "Imunify360" в теле — автоматический retry 3 раза с задержками 2, 4, 8 сек.

### 5. Проверка ответа

Если после retry в теле всё ещё "Imunify360" — выбрасывается `APIResponseError(403)`.

## Почему Railway работает, а локально — нет

- **Railway** — datacenter IP, Imunify360 пропускает
- **Локально** — residential IP, Imunify360 блокирует

На residential IP заголовки (User-Agent, Referer и т.д.) **не помогают** — блокировка идёт по IP. Whitelist не используется.

## Для локальной разработки (3 варианта)

### 1. Прокси с datacenter egress (рекомендуется)

Добавьте в `.env`:

```env
WC_HTTPS_PROXY=http://ваш-прокси:порт
```

Или в PowerShell перед запуском: `$env:HTTPS_PROXY = "http://proxy:port"`

### 2. Railway run

```bash
railway run python scripts/run_frontend.py
```

API-запросы идут с IP Railway (если Railway проксирует egress).

### 3. Деплой на Railway

Работает всегда — там datacenter IP.

## Чеклист

1. `WC_USER_AGENT` в .env
2. `user_agent` в каждом `API()`
3. `patch_api_with_browser_headers()` вызывается
4. Перезапуск после смены .env

## См. также

- [IMUNIFY360_BYPASS_WITHOUT_WHITELIST.md](IMUNIFY360_BYPASS_WITHOUT_WHITELIST.md) — детали
- [IMUNIFY360_QUICK_FIX.md](IMUNIFY360_QUICK_FIX.md) — быстрый фикс
