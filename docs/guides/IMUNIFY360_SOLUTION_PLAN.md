# План решения Imunify360 — раз и навсегда

## Проблема

```
500: Access denied by Imunify360 bot-protection. IPs used for automation should be whitelisted
```

При загрузке заказов с WooCommerce на localhost — блокировка.

---

## Корневая причина (из IMUNIFY360_MAIN_RULE)

| Тип IP        | Результат                          |
|---------------|------------------------------------|
| Datacenter    | Imunify360 часто пропускает        |
| Residential   | Imunify360 блокирует по IP         |

**Важно:** На residential IP заголовки (User-Agent, Referer и т.д.) **не помогают** — блокировка идёт по IP. Whitelist не используется в проекте.

---

## Рабочие решения (без whitelist)

### Вариант 1: Railway run (рекомендуется для локальной разработки)

Запросы идут с IP Railway (datacenter).

```bash
railway run python scripts/run_frontend.py
```

Требует: Railway CLI, `railway link` к проекту.

### Вариант 2: Прокси с datacenter egress

Если есть HTTP(S) прокси с выходом в datacenter:

```env
# .env
WC_HTTPS_PROXY=http://proxy.example.com:8080
```

Или в PowerShell перед запуском:

```powershell
$env:HTTPS_PROXY = "http://proxy.example.com:8080"
python scripts/run_frontend.py
```

`requests` использует `HTTPS_PROXY` / `WC_HTTPS_PROXY` автоматически.

### Вариант 3: Деплой на Railway

Продакшен работает всегда — там datacenter IP.

---

## План реализации (шаги)

### Шаг 1: Поддержка WC_HTTPS_PROXY в коде

- Добавить `WC_HTTPS_PROXY` в `.env.example` и `WooCommerceConfig`
- Передавать `proxies` в `Session.request()` в `imunify_client.py`
- Логировать при старте, используется ли прокси

### Шаг 2: Усиление warmup и retry

- Увеличить задержки retry: 3, 6, 12 сек
- Добавить небольшой случайный jitter перед warmup
- Warmup: GET главной → wp-json → повтор при 403

### Шаг 3: Скрипт run_frontend с railway run

- Автоопределение: если `railway` в PATH и проект залинкован — запуск через `railway run`
- Fallback на обычный запуск
- Логирование способа (локально / railway run / proxy)

### Шаг 4: Тест загрузки заказов

- `tests/test_orders_imunify.py`: загрузка 1 заказа через connector
- Skip если `WC_HTTPS_PROXY` и `RAILWAY_ENVIRONMENT` не заданы (резидентный IP)
- Или mock WooCommerce API для CI

### Шаг 5: Документация

- Обновить IMUNIFY360_MAIN_RULE, BYPASS_WITHOUT_WHITELIST
- Добавить IMUNIFY360_SOLUTION_PLAN в DOCUMENTATION_INDEX
- Краткий чеклист в README / QUICK_FIX

### Шаг 6: Чеклист для пользователя

1. `WC_USER_AGENT` в .env (скопировать из браузера)
2. Вариант A: `railway run python scripts/run_frontend.py`
3. Вариант B: задать `WC_HTTPS_PROXY` (прокси с datacenter) и `python scripts/run_frontend.py`
4. Вариант C: деплой на Railway

---

## Почему утром работало, а потом нет

Возможные причины:

- **Daily / rate limit** — лимит запросов по IP за сутки; после сброса (например, на следующий день) заказы снова загружаются без смены настроек
- Смена IP (динамический IP провайдера)
- Обновление правил Imunify360
- Временное ослабление защиты (кэш/таймаут)

---

## Достигнутое состояние (зафиксировано)

- Заказы загружаются на localhost при текущей конфигурации (User-Agent + warmup + retry).
- Реализовано: `WC_USER_AGENT`, `WC_HTTPS_PROXY`, усиленный warmup и retry в `imunify_client`, опция `railway run` в `run_frontend.py`, тесты и документация.
- При повторной блокировке: проверить daily/rate limit (подождать или использовать прокси/Railway).

---

## Где настраивается в проекте

| Компонент             | Файл                        |
|-----------------------|-----------------------------|
| User-Agent, патч API  | `woocommerce_connector/connector.py` |
| Warmup, retry, прокси | `woocommerce_connector/api/imunify_client.py` |
| Конфиг WC_*           | `woocommerce_connector/config/__init__.py` |
| Запуск фронтенда      | `scripts/run_frontend.py`   |

---

## Ссылки

- [IMUNIFY360_MAIN_RULE.md](IMUNIFY360_MAIN_RULE.md)
- [IMUNIFY360_BYPASS_WITHOUT_WHITELIST.md](IMUNIFY360_BYPASS_WITHOUT_WHITELIST.md)
- [IMUNIFY360_QUICK_FIX.md](IMUNIFY360_QUICK_FIX.md)
