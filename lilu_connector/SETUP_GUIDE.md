# 🚀 Руководство по настройке LILU Connector

## 📋 Быстрый старт

### Шаг 1: Создайте файл `.env`

Создайте файл `.env` в корне проекта (рядом с `lilu_connector/`) со следующим содержимым:

```env
# LILU API Configuration
LILU_API_URL=https://api.servus-ululu.com
LILU_API_TOKEN=your_api_token_here
LILU_API_VERSION=v2
LILU_TIMEOUT=30
LILU_MAX_RETRIES=3
LILU_RETRY_DELAY=1
```

**Важно:** Замените `your_api_token_here` на реальный токен из вашего личного кабинета LILU.

### Шаг 2: Установите зависимости

```bash
pip install requests python-dotenv
```

### Шаг 3: Используйте коннектор

```python
from lilu_connector import LILUConnector

# Создаём коннектор
connector = LILUConnector()

# Получаем список клиентов
clients = connector.get_clients()

# Выводим информацию о клиентах
for client in clients:
    print(f"{client.name} - {client.email}")
```

## 🔧 Получение API токена

1. Войдите в личный кабинет LILU (Servus Ululu)
2. Перейдите в раздел "API Settings" или "Настройки API"
3. Создайте новый API токен или скопируйте существующий
4. Скопируйте `API Token`
5. Вставьте его в файл `.env` как значение `LILU_API_TOKEN`

## ⚙️ Настройки

### Обязательные настройки

- `LILU_API_URL` - Базовый URL API (обычно `https://api.servus-ululu.com`)
- `LILU_API_TOKEN` - Ваш API токен для аутентификации

### Опциональные настройки

- `LILU_API_VERSION` - Версия API (по умолчанию `v2`)
- `LILU_TIMEOUT` - Таймаут для запросов в секундах (по умолчанию `30`)
- `LILU_MAX_RETRIES` - Количество повторных попыток (по умолчанию `3`)
- `LILU_RETRY_DELAY` - Интервал между попытками в секундах (по умолчанию `1`)

## 🧪 Проверка подключения

```python
from lilu_connector import LILUConnector

connector = LILUConnector()

# Проверка доступности API
if connector.health_check():
    print("✅ API доступен")
else:
    print("❌ API недоступен")
```

## 📝 Примеры использования

### Получение клиентов

```python
from lilu_connector import LILUConnector

connector = LILUConnector()

# Получить всех клиентов
clients = connector.get_clients()

# Получить клиентов с пагинацией
clients = connector.get_clients(page=1, limit=50)

# Получить только активных клиентов
active_clients = connector.get_clients(status='active')

# Получить конкретного клиента
client = connector.get_client(client_id=123)
print(f"Клиент: {client.name}, Email: {client.email}")
```

### Создание клиента

```python
from lilu_connector import LILUConnector

connector = LILUConnector()

# Создать нового клиента
new_client = connector.create_client({
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '+1234567890'
})

print(f"Создан клиент с ID: {new_client.id}")
```

### Работа с продуктами

```python
from lilu_connector import LILUConnector

connector = LILUConnector()

# Получить все продукты
products = connector.get_products()

# Получить продукты из категории
products = connector.get_products(category='electronics')

# Получить конкретный продукт
product = connector.get_product(product_id=456)
print(f"Продукт: {product.name}, Цена: {product.price}")
```

### Работа с заказами

```python
from lilu_connector import LILUConnector

connector = LILUConnector()

# Получить все заказы
orders = connector.get_orders()

# Получить заказы конкретного клиента
client_orders = connector.get_orders(client_id=123)

# Получить заказы по статусу
pending_orders = connector.get_orders(status='pending')

# Получить конкретный заказ
order = connector.get_order(order_id=789)
print(f"Заказ #{order.id}: {order.total_amount} руб.")
```

## 🔒 Безопасность

**Важно:** Никогда не коммитьте файл `.env` в Git!

Убедитесь, что `.env` добавлен в `.gitignore`:

```
.env
*.env
```

## ❓ Проблемы и решения

### Проблема: `ConfigurationError: LILU_API_TOKEN is required`

**Решение:** Проверьте, что файл `.env` существует и содержит все обязательные настройки, включая `LILU_API_TOKEN`.

### Проблема: `AuthenticationError: Authentication failed`

**Решение:** 
1. Проверьте правильность API токена
2. Убедитесь, что токен активен в личном кабинете LILU
3. Проверьте, что в `.env` нет лишних пробелов вокруг токена
4. Убедитесь, что токен не истёк (если у токенов есть срок действия)

### Проблема: `NetworkError: Connection timeout`

**Решение:**
1. Проверьте интернет-соединение
2. Проверьте правильность URL в `LILU_API_URL`
3. Увеличьте таймаут: `LILU_TIMEOUT=60`

## 📚 Дополнительная документация

- [README.md](README.md) - Основная документация
- [JUNIOR_GUIDE.md](JUNIOR_GUIDE.md) - Руководство для Junior разработчиков
- [API_NOTES.md](API_NOTES.md) - Ключевые моменты из инструкции LILU API
- [Документация API LILU](../data/input/liloo_API%20v%202.0-120126-144149.pdf)
