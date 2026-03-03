# Обход Imunify360 без whitelist IP

## Проблема

Ошибка при доступе к WooCommerce API:
```
500: Access denied by Imunify360 bot-protection. IPs used for automation should be whitelisted
```

## Решение без whitelist: User-Agent

Imunify360 определяет ботов по нескольким признакам, в том числе по **User-Agent**. Запросы с типичным User-Agent автоматизации (`WooCommerce-Python-REST-API/3.0.0`) блокируются. Если отправлять **User-Agent браузера (Chrome)**, часть запросов может проходить без whitelist.

---

## Ключевое техническое открытие

**Библиотека `woocommerce` (Python) не использует `requests.Session`.**  
Она вызывает `requests.request()` напрямую и собирает заголовки внутри `__request()`.

Поэтому **не работает**:
```python
# НЕ РАБОТАЕТ — session вообще не используется в реальных запросах
wcapi = API(...)
wcapi.session.headers['User-Agent'] = '...'   # Нет эффекта
wcapi._session.headers['User-Agent'] = '...'  # Нет эффекта
```

**Работает только один способ** — передать `user_agent` в конструктор `API()`:
```python
wcapi = API(
    url=...,
    consumer_key=...,
    consumer_secret=...,
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
)
```

В `woocommerce/api.py` (строка 70–72):
```python
headers = {
    "user-agent": f"{self.user_agent}",
    "accept": "application/json"
}
```

User-Agent берётся только из `self.user_agent`, который задаётся в `__init__` через `kwargs.get("user_agent", ...)`.

---

## Где в проекте задаётся User-Agent

Все места, где создаётся WooCommerce `API()`, должны передавать `user_agent`:

| Файл | Место | Статус |
|------|-------|--------|
| `woocommerce_connector/connector.py` | `WooCommerceConnector.__init__` → `API(user_agent=...)` | ✅ |
| `woocommerce_connector/connector.py` | `check_api_version()` → `API(user_agent=...)` | ✅ |
| `woocommerce_connector/connector.py` | `check_api_version_standalone()` → `API(user_agent=...)` | ✅ |

Если где-то вызывается `API()` без `user_agent`, запросы будут идти с `WooCommerce-Python-REST-API/3.0.0` и могут блокироваться Imunify360.

---

## Настройка .env

**Важно:** Скопируйте User-Agent из браузера, когда открываете dimkava.ge — это обеспечивает совпадение с «живым» трафиком.

1. Откройте https://dimkava.ge в браузере.
2. F12 → вкладка Network → обновите страницу → выберите любой запрос.
3. В Request Headers скопируйте значение `User-Agent`.
4. Добавьте в `.env`:

```env
WC_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
```

(подставьте скопированное значение)

Если `WC_USER_AGENT` не задан, используется Chrome 131 по умолчанию.

---

## Полный чеклист для обхода без whitelist

1. **Убедиться, что `user_agent` передаётся во все вызовы `API()`**  
   См. раздел «Где в проекте задаётся User-Agent».

2. **Проверить .env**  
   Добавить `WC_USER_AGENT` с User-Agent браузера или убедиться, что используется дефолт.

3. **Перезапустить приложение**  
   После изменений в `.env` нужен перезапуск.

4. **Проверка**  
   ```bash
   python scripts/test_connection_and_products.py
   ```

---

## Если всё равно блокируют

- User-Agent **не гарантирует** обход, Imunify360 может учитывать и другие признаки.
- Для стабильной работы рекомендуется **whitelist IP** (см. [IMUNIFY360_GUIDE.md](IMUNIFY360_GUIDE.md)).
- Можно попробовать более «свежий» User-Agent Chrome.

---

## Ссылки

- [IMUNIFY360_GUIDE.md](IMUNIFY360_GUIDE.md) — whitelist и другие варианты
- [API_CONNECTION_GUIDE.md](API_CONNECTION_GUIDE.md) — подключение к API
- `woocommerce_connector/connector.py` — эталонная реализация
