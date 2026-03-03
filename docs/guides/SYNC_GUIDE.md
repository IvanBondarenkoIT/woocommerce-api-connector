# 🔄 Руководство по синхронизации WooCommerce → LILU

## 📋 Описание

Автоматическая синхронизация заказов из WooCommerce в CRM LILU:
- Отлавливает новые заказы из WooCommerce
- Извлекает информацию о клиенте (телефон, имя, email)
- Ищет клиента в LILU по номеру телефона
- Если клиент не найден - создает нового с тегом "api woo"
- Обновляет теги существующих клиентов при необходимости

---

## 🚀 Быстрый старт

### 1. Настройка

Убедитесь, что настроены оба коннектора:

**`.env` файл должен содержать:**

```env
# WooCommerce
WC_URL=https://your-store.com
WC_CONSUMER_KEY=ck_...
WC_CONSUMER_SECRET=cs_...

# LILU
LILU_API_URL=https://api.leeloo.ai
LILU_API_SECRET=your_secret_here
```

### 2. Запуск синхронизации

```bash
# Синхронизировать новые заказы
python scripts/sync_orders.py --new

# Синхронизировать все заказы (первоначальная загрузка)
python scripts/sync_orders.py --all

# Синхронизировать конкретный заказ
python scripts/sync_orders.py --order-id 12345

# Показать статистику
python scripts/sync_orders.py --stats
```

---

## 💻 Использование в коде

### Базовый пример

```python
from woocommerce_connector.connector import WooCommerceConnector
from lilu_connector.connector import LILUConnector
from woocommerce_connector.services import SyncService

# Инициализация коннекторов
wc_connector = WooCommerceConnector()
lilu_connector = LILUConnector()

# Создание сервиса синхронизации
sync_service = SyncService(
    wc_connector=wc_connector,
    lilu_connector=lilu_connector,
    default_tag="api woo"
)

# Синхронизация новых заказов
results = sync_service.sync_new_orders()

# Статистика
for result in results:
    print(f"Order #{result.order_id}: {result.action}")
    if result.lilu_client_id:
        print(f"  LILU Client ID: {result.lilu_client_id}")
```

### С дополнительными правилами для тегов

```python
# Правила для определения тегов на основе заказа
additional_rules = [
    # Добавлять тег "vip" для заказов больше 10000
    {
        'tag': 'vip',
        'condition': {
            'field': 'total',
            'operator': '>',
            'value': 10000
        }
    },
    # Добавлять тег "completed" для завершенных заказов
    {
        'tag': 'completed',
        'condition': {
            'field': 'status',
            'operator': '==',
            'value': 'completed'
        }
    },
    # Добавлять тег "new_year_2026" для заказов в январе 2026
    {
        'tag': 'new_year_2026',
        'condition': {
            'field': 'date_created',
            'operator': 'contains',
            'value': '2026-01'
        }
    }
]

sync_service = SyncService(
    wc_connector=wc_connector,
    lilu_connector=lilu_connector,
    default_tag="api woo",
    additional_tag_rules=additional_rules
)
```

### Синхронизация одного заказа

```python
from woocommerce_connector.models.order import Order

# Получаем заказ
order_data = wc_connector.get_order_by_id(12345)
order = Order.from_dict(order_data)

# Синхронизируем
result = sync_service.sync_order(order)

if result.success:
    print(f"✅ Успешно: {result.action}")
    print(f"   LILU Client ID: {result.lilu_client_id}")
    if result.tags_added:
        print(f"   Теги: {', '.join(result.tags_added)}")
else:
    print(f"❌ Ошибка: {result.error_message}")
```

---

## 🔧 Настройка

### Параметры SyncService

```python
SyncService(
    wc_connector,              # Коннектор WooCommerce (обязательно)
    lilu_connector,            # Коннектор LILU (обязательно)
    default_tag="api woo",     # Базовый тег для новых клиентов
    additional_tag_rules=[],   # Дополнительные правила для тегов
    tracker_file="data/sync_tracker.json",  # Файл для отслеживания
    default_country='RU'       # Код страны для нормализации телефонов
)
```

### Правила для тегов

Правило состоит из:
- `tag` - название тега для добавления
- `condition` - условие, при котором тег добавляется
  - `field` - поле заказа (total, status, item_count, date_created)
  - `operator` - оператор (>, >=, <, <=, ==, !=, in, contains)
  - `value` - значение для сравнения

**Примеры полей:**
- `total` - сумма заказа (число)
- `status` - статус заказа (строка: "completed", "pending", и т.д.)
- `item_count` - количество товаров в заказе (число)
- `date_created` - дата создания заказа (строка ISO)

**Примеры операторов:**
- `>` - больше
- `>=` - больше или равно
- `<` - меньше
- `<=` - меньше или равно
- `==` - равно
- `!=` - не равно
- `in` - содержится в списке (для списков)
- `contains` - содержит подстроку (для строк)

---

## 📊 Отслеживание обработанных заказов

Система автоматически отслеживает обработанные заказы в файле `data/sync_tracker.json`.

Это позволяет:
- Избежать дублирования при повторных запусках
- Видеть историю синхронизации
- Получать статистику

**Формат данных:**
```json
{
  "12345": {
    "order_id": 12345,
    "processed_at": "2026-01-27T10:30:00",
    "lilu_client_id": "69660055fb13db648fc58795",
    "status": "created",
    "tags_added": ["api woo", "vip"]
  }
}
```

---

## 🔍 Как это работает

### Процесс синхронизации одного заказа:

1. **Проверка** - был ли заказ уже обработан?
2. **Извлечение данных** - телефон, имя, email из заказа
3. **Нормализация телефона** - приведение к единому формату (+79991234567)
4. **Поиск в LILU** - поиск клиента по телефону
5. **Действие:**
   - Если найден → проверка тегов → обновление при необходимости
   - Если не найден → создание нового клиента с тегом "api woo"
6. **Отметка** - заказ помечается как обработанный

### Нормализация телефонов

Телефоны приводятся к международному формату:
- `8 (999) 123-45-67` → `+79991234567`
- `+7 999 123 45 67` → `+79991234567`
- `9991234567` → `+79991234567` (если default_country='RU')

---

## ⚠️ Важные замечания

1. **Телефон обязателен** - заказы без телефона пропускаются
2. **Дубликаты предотвращаются** - система отслеживает обработанные заказы
3. **Теги объединяются** - при обновлении существующих клиентов теги добавляются, а не заменяются
4. **Ошибки логируются** - все ошибки записываются в логи и в трекер

---

## 📈 Статистика

```python
stats = sync_service.get_statistics()
print(stats)
# {
#   'tracker': {
#     'total_processed': 150,
#     'created': 45,
#     'updated': 100,
#     'skipped': 3,
#     'errors': 2
#   },
#   'default_tag': 'api woo',
#   'additional_rules_count': 2
# }
```

---

## 🐛 Решение проблем

### Заказ пропускается

**Причина:** Нет телефона в заказе
**Решение:** Проверьте, что в заказе WooCommerce заполнено поле "Телефон" в billing данных

### Клиент не создается

**Причина:** Ошибка API LILU
**Решение:** 
- Проверьте логи: `logs/woocommerce_connector.services.sync_service.log`
- Проверьте настройки LILU API в `.env`
- Убедитесь, что API токен валидный

### Теги не обновляются

**Причина:** LILU API может не поддерживать обновление только тегов
**Решение:** Проверьте документацию LILU API для метода обновления клиента

---

## 📚 Дополнительная документация

- [План интеграции](../development/SYNC_INTEGRATION_PLAN.md) - детальный план реализации
- [Архитектура проекта](../../ARCHITECTURE.md) - общая архитектура
- [LILU Connector README](../../lilu_connector/README.md) - документация LILU коннектора

---

*Последнее обновление: 2026-01-27*
