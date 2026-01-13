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
BASE_URL = "https://api.leeloo.ai"

# Таймаут для HTTP запросов (в секундах)
REQUEST_TIMEOUT = 30

# Максимальное количество повторных попыток при ошибке
MAX_RETRIES = 3

# Интервал между повторными попытками (в секундах)
RETRY_DELAY = 1

# Endpoints API
# Для Junior: endpoint - это путь относительно base_url
# base_url уже содержит /api/v2, поэтому endpoints начинаются без /api/v2
# Например: base_url = https://api.servus-ululu.com/api/v2, endpoint = /clients
# Результат: https://api.servus-ululu.com/api/v2/clients
ENDPOINTS = {
    # Клиенты (подписчики) - в LILU API называются "people"
    'clients': '/people',  # Получить список подписчиков
    'client': '/people/{client_id}',  # Получить конкретного подписчика
    'people': '/people',  # Альтернативное название
    'person': '/people/{client_id}',  # Альтернативное название
    
    # Продукты
    'products': '/products',
    'product': '/products/{product_id}',
    
    # Заказы
    'orders': '/orders',
    'order': '/orders/{order_id}',
    
    # Аутентификация
    'auth': '/auth',
    'refresh_token': '/auth/refresh',
    
    # Статус API
    'health': '/health',
    'status': '/status',
    
    # Шаблоны сообщений
    'template_categories': '/categories/templates',
    'templates': '/templates',
    'template': '/templates/{template_id}',
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
