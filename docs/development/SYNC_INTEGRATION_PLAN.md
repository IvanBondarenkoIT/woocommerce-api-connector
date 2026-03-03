# 🔄 План интеграции синхронизации WooCommerce → LILU

> **⚠️ УСТАРЕВШИЙ ПЛАН**  
> Этот план был обновлен. См. [SYNC_INTEGRATION_PLAN_V2.md](SYNC_INTEGRATION_PLAN_V2.md) для актуальной версии с приоритетом на фронтенд и ручной контроль.

## 📋 Цель проекта

Автоматически синхронизировать заказы из WooCommerce в CRM LILU:
1. Отлавливать новые заказы из WooCommerce
2. Извлекать информацию о клиенте (телефон, имя, email)
3. Искать клиента в LILU по номеру телефона
4. Если клиент не найден - создавать нового с тегом "api woo"
5. Возможность добавлять дополнительные теги в зависимости от целей и акций

---

## 🏗️ Архитектура решения

### Компоненты системы

```
sync_service/
├── __init__.py
├── sync_service.py          # Главный сервис синхронизации
├── order_processor.py       # Обработка заказов WooCommerce
├── client_matcher.py        # Поиск/создание клиентов в LILU
├── phone_normalizer.py      # Нормализация телефонов
└── sync_tracker.py          # Отслеживание обработанных заказов
```

### Поток данных

```
1. WooCommerce Order
   ↓
2. OrderProcessor.extract_customer_data()
   → phone, name, email
   ↓
3. PhoneNormalizer.normalize()
   → +79991234567 (единый формат)
   ↓
4. ClientMatcher.find_by_phone()
   → Ищет в LILU по телефону
   ↓
5a. Если найден → ClientMatcher.update_client()
   → Добавляет теги если нужно
   ↓
5b. Если не найден → ClientMatcher.create_client()
   → Создает с тегом "api woo"
   ↓
6. SyncTracker.mark_processed()
   → Сохраняет ID заказа для избежания дублей
```

---

## 📝 Детальный план реализации

### ЭТАП 1: Инфраструктура (Приоритет: 🔴 КРИТИЧНО)

#### 1.1 Утилита нормализации телефонов

**Файл:** `woocommerce_connector/utils/phone_normalizer.py`

**Задачи:**
- Привести телефон к единому формату (международный формат)
- Убрать пробелы, дефисы, скобки
- Добавить код страны если отсутствует
- Обработать разные форматы: +7, 8, 7, без кода

**Пример:**
```python
normalize_phone("8 (999) 123-45-67") → "+79991234567"
normalize_phone("+7 999 123 45 67") → "+79991234567"
normalize_phone("9991234567") → "+79991234567" (если default_country="RU")
```

#### 1.2 Система отслеживания обработанных заказов

**Файл:** `woocommerce_connector/services/sync_tracker.py`

**Задачи:**
- Хранить ID обработанных заказов
- Проверять, был ли заказ уже обработан
- Сохранять метаданные (дата обработки, статус)
- Поддержка разных хранилищ (JSON файл, SQLite, PostgreSQL)

**Структура данных:**
```json
{
  "processed_orders": {
    "12345": {
      "processed_at": "2026-01-27T10:30:00Z",
      "lilu_client_id": "69660055fb13db648fc58795",
      "status": "created|updated",
      "tags_added": ["api woo"]
    }
  }
}
```

---

### ЭТАП 2: Поиск клиентов в LILU (Приоритет: 🔴 КРИТИЧНО)

#### 2.1 Метод поиска по телефону в LILUConnector

**Файл:** `lilu_connector/connector.py`

**Метод:** `find_client_by_phone(phone: str) -> Optional[ClientModel]`

**Логика:**
1. Нормализовать телефон
2. Использовать фильтр LILU API: `filter[phone]=+79991234567`
3. Если найдено несколько - вернуть первый
4. Если не найдено - вернуть None

**API запрос:**
```http
GET /api/v2/people?limit=1&offset=0&filter[phone]=+79991234567&authToken=...
```

#### 2.2 Метод обновления тегов клиента

**Метод:** `update_client_tags(client_id: str, tags: List[str], merge: bool = True) -> ClientModel`

**Логика:**
1. Получить текущего клиента
2. Объединить теги (если merge=True) или заменить (если merge=False)
3. Убедиться что тег "api woo" присутствует
4. Обновить клиента через API

---

### ЭТАП 3: Обработка заказов (Приоритет: 🔴 КРИТИЧНО)

#### 3.1 Извлечение данных клиента из заказа

**Файл:** `woocommerce_connector/services/order_processor.py`

**Класс:** `OrderProcessor`

**Метод:** `extract_customer_data(order: Order) -> Dict[str, Any]`

**Извлекаемые данные:**
- `phone` - из `order.billing.get('phone')`
- `email` - из `order.billing.get('email')`
- `name` - из `order.customer_name` или `billing.first_name + last_name`
- `order_id` - для отслеживания
- `order_date` - дата заказа
- `order_total` - сумма заказа

**Валидация:**
- Телефон обязателен (без него нельзя искать/создавать)
- Email опционален
- Имя опционально (можно использовать телефон как имя)

#### 3.2 Определение тегов на основе заказа

**Метод:** `determine_tags(order: Order, config: SyncConfig) -> List[str]`

**Логика:**
- Базовый тег: `"api woo"` (всегда)
- Дополнительные теги из конфигурации:
  - По сумме заказа: `"vip"` если total > 10000
  - По статусу: `"completed"` если status == "completed"
  - По дате: `"new_year_2026"` если заказ в период акции
  - Кастомные правила из конфига

---

### ЭТАП 4: Главный сервис синхронизации (Приоритет: 🔴 КРИТИЧНО)

#### 4.1 Класс SyncService

**Файл:** `woocommerce_connector/services/sync_service.py`

**Основные методы:**

```python
class SyncService:
    def __init__(
        self,
        wc_connector: WooCommerceConnector,
        lilu_connector: LILUConnector,
        config: SyncConfig
    ):
        """Инициализация сервиса"""
    
    def sync_order(self, order: Order) -> SyncResult:
        """Синхронизировать один заказ"""
    
    def sync_new_orders(
        self,
        status: Optional[str] = None,
        since_date: Optional[datetime] = None
    ) -> List[SyncResult]:
        """Синхронизировать новые заказы"""
    
    def sync_all_orders(self) -> List[SyncResult]:
        """Синхронизировать все заказы (для первоначальной загрузки)"""
```

**Логика sync_order:**
1. Проверить, не обработан ли заказ уже (SyncTracker)
2. Извлечь данные клиента (OrderProcessor)
3. Нормализовать телефон (PhoneNormalizer)
4. Найти клиента в LILU (ClientMatcher.find_by_phone)
5. Если найден:
   - Обновить теги если нужно
   - Логировать обновление
6. Если не найден:
   - Создать нового клиента с тегом "api woo"
   - Логировать создание
7. Отметить заказ как обработанный (SyncTracker)
8. Вернуть результат (SyncResult)

---

### ЭТАП 5: Конфигурация (Приоритет: 🟡 ВАЖНО)

#### 5.1 Настройки синхронизации

**Файл:** `.env` (добавить секцию)

```env
# Sync Configuration
SYNC_ENABLED=true
SYNC_DEFAULT_TAG=api woo
SYNC_ADDITIONAL_TAGS=vip,completed
SYNC_PHONE_COUNTRY_CODE=RU
SYNC_TRACKER_STORAGE=json
SYNC_TRACKER_FILE=data/sync_tracker.json
```

#### 5.2 Класс SyncConfig

**Файл:** `woocommerce_connector/config/sync_config.py`

**Параметры:**
- `default_tag: str` - базовый тег ("api woo")
- `additional_tags: List[str]` - дополнительные теги
- `phone_country_code: str` - код страны по умолчанию
- `tracker_storage: str` - тип хранилища (json, sqlite)
- `auto_sync_enabled: bool` - автоматическая синхронизация

---

### ЭТАП 6: Скрипты и CLI (Приоритет: 🟡 ВАЖНО)

#### 6.1 Скрипт синхронизации

**Файл:** `scripts/sync_orders.py`

**Функционал:**
- Синхронизация новых заказов
- Синхронизация всех заказов (первоначальная загрузка)
- Синхронизация конкретного заказа по ID
- Статистика синхронизации

**Пример использования:**
```bash
# Синхронизировать новые заказы
python scripts/sync_orders.py --new

# Синхронизировать все заказы
python scripts/sync_orders.py --all

# Синхронизировать конкретный заказ
python scripts/sync_orders.py --order-id 12345

# Статистика
python scripts/sync_orders.py --stats
```

#### 6.2 Планировщик (опционально)

**Файл:** `scripts/sync_scheduler.py`

**Функционал:**
- Автоматический запуск синхронизации по расписанию
- Использование cron или schedule библиотеки
- Уведомления об ошибках

---

### ЭТАП 7: Обработка ошибок и логирование (Приоритет: 🔴 КРИТИЧНО)

#### 7.1 Типы ошибок

- `PhoneNotFoundError` - телефон не найден в заказе
- `PhoneNormalizationError` - не удалось нормализовать телефон
- `ClientSearchError` - ошибка при поиске клиента
- `ClientCreationError` - ошибка при создании клиента
- `SyncError` - общая ошибка синхронизации

#### 7.2 Логирование

**Уровни:**
- `INFO` - успешная синхронизация
- `WARNING` - пропущен заказ (нет телефона)
- `ERROR` - ошибка синхронизации
- `DEBUG` - детальная информация

**Формат логов:**
```
[2026-01-27 10:30:15] INFO: Order #12345 synced → Client created (ID: 69660055fb13db648fc58795)
[2026-01-27 10:30:16] WARNING: Order #12346 skipped (no phone number)
[2026-01-27 10:30:17] ERROR: Order #12347 sync failed: ClientCreationError(...)
```

---

## 🔄 Сценарии использования

### Сценарий 1: Новый заказ → Новый клиент

1. Заказ #12345 создан в WooCommerce
2. Телефон: `8 (999) 123-45-67`
3. Нормализация: `+79991234567`
4. Поиск в LILU: не найден
5. Создание клиента:
   - name: "Иван Иванов" (из заказа)
   - phone: "+79991234567"
   - email: "ivan@example.com" (если есть)
   - tags: ["api woo"]
6. Результат: ✅ Клиент создан (ID: 69660055fb13db648fc58795)

### Сценарий 2: Новый заказ → Существующий клиент

1. Заказ #12346 создан в WooCommerce
2. Телефон: `+7 999 123 45 67`
3. Нормализация: `+79991234567`
4. Поиск в LILU: найден (ID: 69660055fb13db648fc58795)
5. Проверка тегов: есть "api woo" → ничего не делаем
6. Результат: ✅ Клиент уже существует, теги актуальны

### Сценарий 3: Новый заказ → Обновление тегов

1. Заказ #12347 создан (сумма > 10000)
2. Телефон: `+79991234567`
3. Поиск: найден клиент
4. Текущие теги: ["api woo"]
5. Определение новых тегов: ["api woo", "vip"]
6. Обновление: добавляем тег "vip"
7. Результат: ✅ Теги обновлены

### Сценарий 4: Заказ без телефона

1. Заказ #12348 создан
2. Телефон: отсутствует
3. Результат: ⚠️ Пропущен (нет телефона для поиска/создания)

---

## 📊 Структура данных

### SyncResult

```python
@dataclass
class SyncResult:
    order_id: int
    success: bool
    action: str  # "created" | "updated" | "skipped" | "error"
    lilu_client_id: Optional[str] = None
    error_message: Optional[str] = None
    tags_added: List[str] = field(default_factory=list)
    processed_at: datetime = field(default_factory=datetime.now)
```

### CustomerData

```python
@dataclass
class CustomerData:
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    order_id: int
    order_date: str
    order_total: str
```

---

## 🧪 Тестирование

### Unit тесты

- `test_phone_normalizer.py` - нормализация телефонов
- `test_client_matcher.py` - поиск/создание клиентов
- `test_order_processor.py` - извлечение данных
- `test_sync_tracker.py` - отслеживание заказов

### Integration тесты

- `test_sync_service.py` - полный цикл синхронизации
- Тесты с моками API
- Тесты с реальными API (опционально)

---

## 📝 Чеклист реализации

### Фаза 1: Базовая функциональность
- [ ] PhoneNormalizer
- [ ] SyncTracker (базовая версия с JSON)
- [ ] Метод find_client_by_phone в LILUConnector
- [ ] OrderProcessor.extract_customer_data
- [ ] SyncService.sync_order (базовая версия)

### Фаза 2: Расширенная функциональность
- [ ] Определение тегов на основе заказа
- [ ] Обновление тегов существующих клиентов
- [ ] SyncService.sync_new_orders
- [ ] Скрипт sync_orders.py

### Фаза 3: Полировка
- [ ] Обработка всех edge cases
- [ ] Подробное логирование
- [ ] Статистика и отчеты
- [ ] Документация

---

## 🚀 Приоритеты внедрения

1. **🔴 КРИТИЧНО:** Базовая синхронизация (создание клиентов)
2. **🟡 ВАЖНО:** Поиск существующих клиентов
3. **🟡 ВАЖНО:** Обновление тегов
4. **🟢 ЖЕЛАТЕЛЬНО:** Автоматическая синхронизация по расписанию
5. **🟢 ЖЕЛАТЕЛЬНО:** Расширенная статистика

---

*План создан: 2026-01-27*
*Статус: В разработке*
