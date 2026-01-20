# Руководство по подключению к WooCommerce API и получению товаров

## Как работает подключение

### 1. Инициализация API клиента

```python
from woocommerce import API

wcapi = API(
    url="https://your-store.com",           # URL магазина (без слеша в конце)
    consumer_key="ck_...",                  # Consumer Key
    consumer_secret="cs_...",               # Consumer Secret
    version="wc/v3",                        # Версия API (обычно wc/v3)
    timeout=30,                             # Таймаут в секундах
    query_string_auth=True                  # Использовать query string auth
)
```

### 2. Получение товаров

#### Метод 1: Одна страница товаров

```python
response = wcapi.get(
    'products',
    params={
        'per_page': 10,  # Количество товаров на странице (макс 100)
        'page': 1        # Номер страницы
    }
)

if response.status_code == 200:
    products = response.json()  # Список товаров
```

#### Метод 2: Все товары с пагинацией

```python
all_products = []
page = 1
per_page = 100  # Максимум

while True:
    response = wcapi.get('products', params={'per_page': per_page, 'page': page})
    
    if response.status_code != 200:
        break
    
    products = response.json()
    
    if not products:  # Если список пустой - конец
        break
    
    all_products.extend(products)
    
    # Если получили меньше товаров, чем per_page - это последняя страница
    if len(products) < per_page:
        break
    
    page += 1
```

## Как это реализовано в проекте

### Класс WooCommerceConnector

**Файл:** `woocommerce_connector/connector.py`

#### Метод `get_products(per_page=10, page=1)`
- Получает одну страницу товаров
- Возвращает Response объект
- Обрабатывает ошибки (401, 404, и т.д.)

#### Метод `get_all_products(per_page=100)`
- Автоматически получает ВСЕ товары
- Обрабатывает пагинацию
- Возвращает `List[Dict[str, Any]]` со всеми товарами
- Останавливается когда:
  - Получен пустой список
  - Получено меньше товаров, чем `per_page`
  - Произошла ошибка

## Типичные ошибки и их решения

### 0. ⚠️ Ошибка Imunify360 - "Access denied by Imunify360 bot-protection"

**Причина:** Imunify360 блокирует автоматизированные запросы

**Решение:** 
- См. подробное руководство: [IMUNIFY360_GUIDE.md](IMUNIFY360_GUIDE.md)
- Кратко: добавьте IP в whitelist или установите User-Agent

### 1. Ошибка 401 - Authentication Error

**Причина:** Неправильные учетные данные или отсутствие прав доступа

**Решение:**
- Проверьте Consumer Key и Consumer Secret
- Убедитесь, что API ключ имеет права Read или Read/Write
- Проверьте формат ключей (должны начинаться с `ck_` и `cs_`)

### 2. Ошибка 404 - Not Found

**Причина:** Неправильный URL или версия API

**Решение:**
- Проверьте URL магазина (должен быть без слеша в конце)
- Проверьте версию API (обычно `wc/v3`)
- Убедитесь, что WooCommerce REST API включен

### 3. Ошибка таймаута

**Причина:** Медленное соединение или большой объем данных

**Решение:**
- Увеличьте timeout: `timeout=60`
- Уменьшите `per_page` (например, 50 вместо 100)
- Добавьте задержки между запросами

### 4. Ошибка "Empty response" или пустой список

**Причина:** 
- В магазине нет товаров
- Товары на других страницах
- Фильтры скрывают товары

**Решение:**
- Проверьте количество товаров в админке WooCommerce
- Попробуйте запросить разные страницы
- Проверьте статус товаров (должны быть "publish")

### 5. Ошибка пагинации (бесконечный цикл)

**Причина:** Неправильная логика определения последней страницы

**Решение:**
- Всегда проверяйте: `if not products: break`
- Проверяйте: `if len(products) < per_page: break`
- Добавьте максимальное количество страниц для безопасности

### 6. Ошибка кодировки (кириллица/спецсимволы)

**Причина:** Проблемы с кодировкой UTF-8

**Решение:**
- Убедитесь, что используется UTF-8
- В Windows: `sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')`

## Пример правильной реализации

```python
import os
from woocommerce import API
from dotenv import load_dotenv

load_dotenv()

# Инициализация
wcapi = API(
    url=os.getenv('WC_URL'),
    consumer_key=os.getenv('WC_CONSUMER_KEY'),
    consumer_secret=os.getenv('WC_CONSUMER_SECRET'),
    version=os.getenv('WC_API_VERSION', 'wc/v3'),
    timeout=30,
    query_string_auth=True
)

# Получение всех товаров
def get_all_products():
    all_products = []
    page = 1
    per_page = 100
    
    while True:
        try:
            response = wcapi.get(
                'products',
                params={'per_page': per_page, 'page': page}
            )
            
            if response.status_code != 200:
                print(f"Error: Status {response.status_code}")
                print(f"Response: {response.text}")
                break
            
            products = response.json()
            
            if not products:
                break
            
            all_products.extend(products)
            print(f"Page {page}: {len(products)} products (total: {len(all_products)})")
            
            if len(products) < per_page:
                break
            
            page += 1
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
    
    return all_products

# Использование
products = get_all_products()
print(f"Total products: {len(products)}")
```

## Проверка подключения

Запустите тестовый скрипт:

```bash
python scripts/test_connection_and_products.py
```

Скрипт проверит:
1. Конфигурацию (.env файл)
2. Подключение к API
3. Получение первой страницы товаров
4. Получение всех товаров с пагинацией
5. Выведет статистику и примеры товаров

## Структура ответа API

Каждый товар содержит:

```python
{
    'id': 123,
    'name': 'Product Name',
    'sku': 'SKU123',
    'price': '29.99',
    'regular_price': '29.99',
    'sale_price': '24.99',  # Если есть скидка
    'stock_quantity': 10,
    'stock_status': 'instock',  # instock, outofstock, onbackorder
    'manage_stock': True,
    'description': 'Product description',
    'short_description': 'Short description',
    'categories': [{'id': 1, 'name': 'Category'}],
    'status': 'publish',  # publish, draft, pending, private
    # ... и много других полей
}
```

## Важные замечания

1. **Максимум товаров на странице:** 100 (рекомендуется использовать 100 для эффективности)

2. **Пагинация:** WooCommerce использует стандартную пагинацию с параметрами `page` и `per_page`

3. **Rate Limiting:** Некоторые серверы могут ограничивать количество запросов. Добавьте задержки если нужно:
   ```python
   import time
   time.sleep(0.5)  # Задержка 0.5 секунды между запросами
   ```

4. **Обработка ошибок:** Всегда обрабатывайте ошибки и проверяйте status_code

5. **Пустые ответы:** Пустой список `[]` означает, что страница пустая или достигнут конец

## Если возникла ошибка в другом проекте

Пришлите:
1. Текст ошибки (полный traceback)
2. Код, который вызывает ошибку
3. Версию Python
4. Версию библиотеки `woocommerce`
5. Настройки .env (без секретов, только структуру)

И я помогу разобраться!
