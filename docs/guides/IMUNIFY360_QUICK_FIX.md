# Imunify360 — быстрое решение (без whitelist)

> **Главное правило:** [IMUNIFY360_MAIN_RULE.md](IMUNIFY360_MAIN_RULE.md)

## Ошибка
```
500: Access denied by Imunify360 bot-protection. IPs used for automation should be whitelisted
```

## Решение (проверено 27.01.2026)

**1. Добавить `WC_USER_AGENT` в `.env`:**

```env
WC_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
```

Лучше взять актуальный User-Agent из браузера: **dimkava.ge → F12 → Network → любой запрос → Request Headers → User-Agent**.

**2. Если на residential IP всё равно блокирует — задать прокси:**

```env
WC_HTTPS_PROXY=http://ваш-прокси:порт
```

Или `railway run python scripts/run_frontend.py` (запросы с IP Railway).

Перезапустить приложение.

**3. Если блокирует временами:** возможен **daily/rate limit** по IP — после сброса лимита заказы снова загружаются без смены настроек.

---

## Техническая суть

- Библиотека `woocommerce` **не использует** `session.headers` — установка User-Agent через `wcapi.session.headers` не работает.
- Работает **только** передача `user_agent` в конструктор `API()`.
- Для residential IP: `imunify_client.patch_api_with_browser_headers()` добавляет полный набор заголовков (Referer, Accept-Language, sec-ch-ua и др.) — запрос выглядит как от браузера.

## Подробнее

- [IMUNIFY360_BYPASS_WITHOUT_WHITELIST.md](IMUNIFY360_BYPASS_WITHOUT_WHITELIST.md) — детали
- [IMUNIFY360_GUIDE.md](IMUNIFY360_GUIDE.md) — whitelist и другие варианты
