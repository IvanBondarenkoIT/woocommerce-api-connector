# Imunify360 — быстрое решение (без whitelist)

## Ошибка
```
500: Access denied by Imunify360 bot-protection. IPs used for automation should be whitelisted
```

## Решение (проверено 27.01.2026)

**Добавить `WC_USER_AGENT` в `.env`:**

```env
WC_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
```

Лучше взять актуальный User-Agent из браузера: **dimkava.ge → F12 → Network → любой запрос → Request Headers → User-Agent**.

Перезапустить приложение.

---

## Техническая суть

- Библиотека `woocommerce` **не использует** `session.headers` — установка User-Agent через `wcapi.session.headers` не работает.
- Работает **только** передача `user_agent` в конструктор `API()`.
- В проекте это уже сделано в `woocommerce_connector/connector.py`.
- Нужно лишь задать `WC_USER_AGENT` в `.env` (или использовать дефолт Chrome 131).

## Подробнее

- [IMUNIFY360_BYPASS_WITHOUT_WHITELIST.md](IMUNIFY360_BYPASS_WITHOUT_WHITELIST.md) — детали
- [IMUNIFY360_GUIDE.md](IMUNIFY360_GUIDE.md) — whitelist и другие варианты
