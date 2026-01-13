"""
Константы для LILU API.

Для Junior разработчиков:
Константы - это значения, которые не меняются во время работы программы.
Мы выносим их в отдельный файл, чтобы:
1. Легко найти и изменить
2. Избежать "магических чисел" в коде
3. Использовать одно значение в разных местах

Пример "магического числа":
    response = client.get('/api/v2/clients')  # Что такое '/api/v2/clients'?

Правильный подход:
    response = client.get(ENDPOINTS['clients'])  # Понятно, что это endpoint для клиентов
"""

# Версия API
API_VERSION = "v2"

# Базовый URL API (будет переопределён из .env)
BASE_URL = "https://api.servus-ululu.com"

# Таймаут для HTTP запросов (в секундах)
REQUEST_TIMEOUT = 30

# Максимальное количество повторных попыток при ошибке
MAX_RETRIES = 3

# Интервал между повторными попытками (в секундах)
RETRY_DELAY = 1

# Endpoints API
# Для Junior: endpoint - это адрес, по которому мы обращаемся к API
# Например: https://api.servus-ululu.com/api/v2/clients
ENDPOINTS = {
    # Клиенты
    'clients': '/api/v2/clients',
    'client': '/api/v2/clients/{client_id}',  # {client_id} будет заменён на реальный ID
    
    # Продукты
    'products': '/api/v2/products',
    'product': '/api/v2/products/{product_id}',
    
    # Заказы
    'orders': '/api/v2/orders',
    'order': '/api/v2/orders/{order_id}',
    
    # Аутентификация
    'auth': '/api/v2/auth',
    'refresh_token': '/api/v2/auth/refresh',
    
    # Статус API
    'health': '/api/v2/health',
    'status': '/api/v2/status',
}

# HTTP заголовки по умолчанию
DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

# Коды статусов HTTP, которые считаются успешными
SUCCESS_STATUS_CODES = [200, 201, 204]

# Коды статусов, при которых нужно повторить запрос
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

# Коды статусов, которые означают ошибку аутентификации
AUTH_ERROR_STATUS_CODES = [401, 403]

# Коды статусов, которые означают, что ресурс не найден
NOT_FOUND_STATUS_CODES = [404]

# Лимиты пагинации (разбиение на страницы)
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# Формат даты/времени, используемый в API
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
ISO_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
