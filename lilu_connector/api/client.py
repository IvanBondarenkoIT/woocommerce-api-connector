"""
HTTP клиент для работы с LILU API.

Для Junior разработчиков:
HTTP клиент - это класс, который делает HTTP запросы (GET, POST, PUT, DELETE)
к API серверу. Он инкапсулирует всю логику работы с HTTP:
- Формирование URL
- Добавление заголовков
- Обработка ошибок
- Повторные попытки при ошибках

Пример использования:
    >>> client = LILUClient(settings)
    >>> response = client.get('/api/v2/clients')
    >>> data = response.json()
"""

import time
import requests
from typing import Dict, Optional, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config.settings import LILUSettings
from ..config.constants import (
    DEFAULT_HEADERS,
    SUCCESS_STATUS_CODES,
    RETRY_STATUS_CODES,
    AUTH_ERROR_STATUS_CODES,
    NOT_FOUND_STATUS_CODES,
    REQUEST_TIMEOUT,
)
from .exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIResponseError,
    NetworkError,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LILUClient:
    """
    HTTP клиент для работы с LILU API.
    
    Этот класс инкапсулирует всю логику HTTP запросов:
    - Аутентификация через API ключи
    - Обработка ошибок
    - Повторные попытки при временных ошибках
    - Логирование запросов
    
    Пример использования:
        >>> settings = LILUSettings()
        >>> client = LILUClient(settings)
        >>> response = client.get('/api/v2/clients')
        >>> clients = response.json()
    """
    
    def __init__(self, settings: LILUSettings):
        """
        Инициализация HTTP клиента.
        
        Args:
            settings: Настройки подключения к API
        
        Raises:
            ConfigurationError: Если настройки неполные
        """
        self.settings = settings
        self.base_url = settings.get_base_url()
        
        # Создаём сессию requests для переиспользования соединений
        # Для Junior: Session позволяет сохранять настройки между запросами
        self.session = requests.Session()
        
        # Настраиваем повторные попытки
        retry_strategy = Retry(
            total=settings.max_retries,
            backoff_factor=settings.retry_delay,
            status_forcelist=RETRY_STATUS_CODES,
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Устанавливаем заголовки по умолчанию
        self.session.headers.update(DEFAULT_HEADERS)
        
        # Добавляем аутентификацию
        # Для Junior: API ключи передаются в заголовках
        self.session.headers.update({
            'X-API-Key': settings.api_key,
            'X-API-Secret': settings.api_secret,
        })
        
        logger.info(f"LILUClient initialized for {self.base_url}")
    
    def _build_url(self, endpoint: str) -> str:
        """
        Построить полный URL для запроса.
        
        Для Junior: endpoint - это путь, например '/api/v2/clients'
        Метод объединяет базовый URL и endpoint в полный URL.
        
        Args:
            endpoint: Путь к endpoint (может содержать {placeholders})
        
        Returns:
            str: Полный URL
        
        Пример:
            >>> client._build_url('/api/v2/clients')
            'https://api.servus-ululu.com/api/v2/clients'
        """
        # Убираем начальный слеш, если есть
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _format_endpoint(self, endpoint: str, **kwargs) -> str:
        """
        Форматировать endpoint с подстановкой параметров.
        
        Для Junior: это позволяет использовать шаблоны типа '/api/v2/clients/{client_id}'
        и заменять {client_id} на реальное значение.
        
        Args:
            endpoint: Шаблон endpoint с {placeholders}
            **kwargs: Значения для подстановки
        
        Returns:
            str: Отформатированный endpoint
        
        Пример:
            >>> client._format_endpoint('/api/v2/clients/{client_id}', client_id=123)
            '/api/v2/clients/123'
        """
        return endpoint.format(**kwargs)
    
    def _handle_response(self, response: requests.Response) -> requests.Response:
        """
        Обработать ответ от API и выбросить исключение при ошибке.
        
        Для Junior: этот метод проверяет статус ответа и выбрасывает
        соответствующее исключение, если что-то пошло не так.
        
        Args:
            response: Объект ответа от requests
        
        Returns:
            requests.Response: Ответ, если всё в порядке
        
        Raises:
            AuthenticationError: При ошибке аутентификации (401, 403)
            NotFoundError: При отсутствии ресурса (404)
            RateLimitError: При превышении лимита (429)
            APIResponseError: При других ошибках API
        """
        status_code = response.status_code
        
        # Успешный ответ
        if status_code in SUCCESS_STATUS_CODES:
            return response
        
        # Ошибка аутентификации
        if status_code in AUTH_ERROR_STATUS_CODES:
            logger.error(f"Authentication error: {status_code}")
            raise AuthenticationError(
                f"Authentication failed with status {status_code}: {response.text}"
            )
        
        # Ресурс не найден
        if status_code in NOT_FOUND_STATUS_CODES:
            logger.warning(f"Resource not found: {status_code}")
            raise NotFoundError("Resource", "")
        
        # Превышен лимит запросов
        if status_code == 429:
            retry_after = response.headers.get('Retry-After', '60')
            logger.warning(f"Rate limit exceeded. Retry after {retry_after} seconds")
            raise RateLimitError(
                f"Rate limit exceeded. Please retry after {retry_after} seconds"
            )
        
        # Другие ошибки API
        logger.error(f"API error {status_code}: {response.text}")
        raise APIResponseError(
            status_code,
            f"API returned error status {status_code}",
            response.text
        )
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Выполнить GET запрос к API.
        
        Для Junior: GET запрос используется для получения данных.
        Например, получить список клиентов или информацию о клиенте.
        
        Args:
            endpoint: Путь к endpoint (может содержать {placeholders})
            params: Параметры запроса (будут добавлены в URL как ?key=value)
            **kwargs: Параметры для форматирования endpoint
        
        Returns:
            requests.Response: Ответ от API
        
        Raises:
            NetworkError: При проблемах с сетью
            AuthenticationError: При ошибке аутентификации
            NotFoundError: При отсутствии ресурса
            APIResponseError: При других ошибках API
        
        Пример:
            >>> # Получить список клиентов
            >>> response = client.get('/api/v2/clients')
            >>> 
            >>> # Получить конкретного клиента
            >>> response = client.get('/api/v2/clients/{client_id}', client_id=123)
            >>> 
            >>> # С параметрами
            >>> response = client.get('/api/v2/clients', params={'page': 1, 'limit': 50})
        """
        url = self._build_url(self._format_endpoint(endpoint, **kwargs))
        
        logger.debug(f"GET {url} with params: {params}")
        
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.settings.timeout
            )
            return self._handle_response(response)
        
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            raise NetworkError(f"Request timeout after {self.settings.timeout} seconds")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise NetworkError(f"Connection error: {str(e)}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {url} - {e}")
            raise NetworkError(f"Request error: {str(e)}")
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Выполнить POST запрос к API.
        
        Для Junior: POST запрос используется для создания новых ресурсов.
        Например, создать нового клиента или заказ.
        
        Args:
            endpoint: Путь к endpoint
            data: Данные для отправки (form-data)
            json: JSON данные для отправки
            **kwargs: Параметры для форматирования endpoint
        
        Returns:
            requests.Response: Ответ от API
        
        Пример:
            >>> # Создать нового клиента
            >>> client_data = {'name': 'John Doe', 'email': 'john@example.com'}
            >>> response = client.post('/api/v2/clients', json=client_data)
        """
        url = self._build_url(self._format_endpoint(endpoint, **kwargs))
        
        logger.debug(f"POST {url} with json: {json}")
        
        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                timeout=self.settings.timeout
            )
            return self._handle_response(response)
        
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            raise NetworkError(f"Request timeout after {self.settings.timeout} seconds")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise NetworkError(f"Connection error: {str(e)}")
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Выполнить PUT запрос к API.
        
        Для Junior: PUT запрос используется для полного обновления ресурса.
        
        Args:
            endpoint: Путь к endpoint
            data: Данные для отправки
            json: JSON данные для отправки
            **kwargs: Параметры для форматирования endpoint
        
        Returns:
            requests.Response: Ответ от API
        """
        url = self._build_url(self._format_endpoint(endpoint, **kwargs))
        
        logger.debug(f"PUT {url} with json: {json}")
        
        try:
            response = self.session.put(
                url,
                data=data,
                json=json,
                timeout=self.settings.timeout
            )
            return self._handle_response(response)
        
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            raise NetworkError(f"Request timeout after {self.settings.timeout} seconds")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise NetworkError(f"Connection error: {str(e)}")
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Выполнить DELETE запрос к API.
        
        Для Junior: DELETE запрос используется для удаления ресурсов.
        
        Args:
            endpoint: Путь к endpoint
            **kwargs: Параметры для форматирования endpoint
        
        Returns:
            requests.Response: Ответ от API
        """
        url = self._build_url(self._format_endpoint(endpoint, **kwargs))
        
        logger.debug(f"DELETE {url}")
        
        try:
            response = self.session.delete(
                url,
                timeout=self.settings.timeout
            )
            return self._handle_response(response)
        
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            raise NetworkError(f"Request timeout after {self.settings.timeout} seconds")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise NetworkError(f"Connection error: {str(e)}")
    
    def close(self):
        """
        Закрыть сессию и освободить ресурсы.
        
        Для Junior: важно закрывать соединения, чтобы не тратить ресурсы.
        """
        self.session.close()
        logger.debug("LILUClient session closed")
