# Скрипты проекта

Эта папка содержит утилитарные скрипты для работы с проектом.

## Основные скрипты

### Запуск приложений
- **[run_gui.py](run_gui.py)** - Запуск графического интерфейса
- **[run_connector.py](run_connector.py)** - Запуск CLI коннектора

## Тестовые скрипты

### Проверка подключения и товаров
- **[test_connection_and_products.py](test_connection_and_products.py)** - Проверка подключения к API и получение всех товаров
- **[test_orders.py](test_orders.py)** - Тестирование получения заказов

## Утилиты для проверки

### Проверка товаров
- **[check_all_products.py](check_all_products.py)** - Детальная проверка всех товаров
- **[check_products_complete.py](check_products_complete.py)** - Полная проверка товаров (включая вариации)
- **[check_system_status.py](check_system_status.py)** - Проверка статуса системы WooCommerce

### Проверка заказов
- **[check_specific_orders.py](check_specific_orders.py)** - Проверка конкретных заказов
- **[show_recent_orders.py](show_recent_orders.py)** - Показать недавние заказы

### LILU (синхронизация)
- **[test_lilu_client.py](test_lilu_client.py)** - Тест создания/удаления клиентов в LILU (без WooCommerce)
- **[sync_orders.py](sync_orders.py)** - Синхронизация заказов WooCommerce → LILU

## Утилиты

- **[get_my_ip.py](get_my_ip.py)** - Получить ваш публичный IP адрес (для whitelist Imunify360)

## Использование

Все скрипты запускаются из корневой директории проекта:

```bash
# Запуск GUI
python scripts/run_gui.py

# Запуск CLI коннектора
python scripts/run_connector.py

# Проверка подключения
python scripts/test_connection_and_products.py

# Получить IP адрес
python scripts/get_my_ip.py

# Тест LILU: создать и удалить тестового клиента
python scripts/test_lilu_client.py create --delete-after

# Тест LILU: создать клиента с Georgian телефоном
python scripts/test_lilu_client.py create --phone +995544445523

# Тест LILU: удалить клиента по ID
python scripts/test_lilu_client.py delete --id <lilu_client_id>
```

## Требования

Все скрипты требуют:
- Настроенный `.env` файл с учетными данными WooCommerce API
- Установленные зависимости из `requirements.txt`

См. [README.md](../README.md) для инструкций по установке.
