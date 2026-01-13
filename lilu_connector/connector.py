"""
Главный класс для работы с LILU API.

Для Junior разработчиков:
Этот класс - это главный интерфейс для работы с LILU API.
Он объединяет все части: HTTP клиент, модели, обработку ошибок.

Пример использования:
    >>> from lilu_connector import LILUConnector
    >>> connector = LILUConnector()
    >>> clients = connector.get_clients()
    >>> for client in clients:
    ...     print(client.name)
"""

from typing import List, Optional, Dict, Any

from .config.settings import LILUSettings
from .config.constants import ENDPOINTS
from .api.client import LILUClient
from .api.exceptions import (
    LILUAPIError,
    AuthenticationError,
    NotFoundError,
    NetworkError,
)
from .models.client import ClientModel
from .models.product import ProductModel
from .models.order import OrderModel
from .utils.logger import get_logger

logger = get_logger(__name__)


class LILUConnector:
    """
    Главный класс для работы с LILU API.
    
    Для Junior разработчиков:
    Этот класс предоставляет удобные методы для работы с API.
    Внутри он использует LILUClient для HTTP запросов и преобразует
    ответы в типизированные модели.
    
    Пример использования:
        >>> connector = LILUConnector()
        >>> 
        >>> # Получить список клиентов
        >>> clients = connector.get_clients()
        >>> 
        >>> # Получить конкретного клиента
        >>> client = connector.get_client(123)
        >>> 
        >>> # Создать нового клиента
        >>> new_client = connector.create_client({
        ...     'name': 'John Doe',
        ...     'email': 'john@example.com'
        ... })
    """
    
    def __init__(self, settings: Optional[LILUSettings] = None):
        """
        Инициализация коннектора.
        
        Для Junior: __init__ - это конструктор класса. Он вызывается
        автоматически при создании объекта: connector = LILUConnector()
        
        Args:
            settings: Настройки подключения (если None, создаются автоматически)
        
        Raises:
            ConfigurationError: Если настройки неполные
        
        Пример:
            >>> # Использовать настройки из .env
            >>> connector = LILUConnector()
            >>> 
            >>> # Или передать свои настройки
            >>> settings = LILUSettings()
            >>> connector = LILUConnector(settings)
        """
        try:
            self.settings = settings or LILUSettings()
            self.client = LILUClient(self.settings)
            logger.info("LILUConnector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LILUConnector: {e}")
            raise
    
    # ==================== КЛИЕНТЫ ====================
    
    def get_clients(
        self,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[ClientModel]:
        """
        Получить список клиентов.
        
        Для Junior: этот метод делает GET запрос к API и преобразует
        ответ в список объектов ClientModel.
        
        Args:
            page: Номер страницы (для пагинации)
            limit: Количество клиентов на странице
            status: Фильтр по статусу (опционально)
        
        Returns:
            List[ClientModel]: Список клиентов
        
        Raises:
            AuthenticationError: При ошибке аутентификации
            NetworkError: При проблемах с сетью
            LILUAPIError: При других ошибках API
        
        Пример:
            >>> connector = LILUConnector()
            >>> clients = connector.get_clients(page=1, limit=50)
            >>> for client in clients:
            ...     print(f"{client.name} - {client.email}")
        """
        try:
            endpoint = ENDPOINTS['clients']
            # Для LILU API используем offset и limit вместо page
            # offset = (page - 1) * limit
            offset = (page - 1) * limit
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            if status:
                params['status'] = status
            
            logger.debug(f"Fetching clients: page={page}, limit={limit}, offset={offset}, status={status}")
            response = self.client.get(endpoint, params=params)
            data = response.json()
            
            # LILU API возвращает данные в формате {data: [...], meta: {...}, status: 1}
            if isinstance(data, dict):
                if 'data' in data:
                    data_obj = data['data']
                    # Если data - это список (стандартный формат LILU)
                    if isinstance(data_obj, list):
                        data = data_obj
                    # Если data содержит people (альтернативный формат)
                    elif isinstance(data_obj, dict) and 'people' in data_obj:
                        people_list = data_obj['people']
                        data = people_list if isinstance(people_list, list) else [people_list]
                    # Если data - это объект (один человек)
                    else:
                        data = [data_obj] if data_obj else []
                elif 'people' in data:
                    people_list = data['people']
                    data = people_list if isinstance(people_list, list) else [people_list]
            
            # Преобразуем список словарей в список ClientModel
            # Для Junior: list comprehension - это способ создать список
            # в одну строку. Эквивалентно:
            # clients = []
            # for item in data:
            #     clients.append(ClientModel.from_dict(item))
            clients = [ClientModel.from_dict(item) for item in data] if isinstance(data, list) else []
            
            logger.info(f"Retrieved {len(clients)} clients")
            return clients
        
        except AuthenticationError:
            logger.error("Authentication failed while fetching clients")
            raise
        except NetworkError:
            logger.error("Network error while fetching clients")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching clients: {e}")
            raise LILUAPIError(f"Failed to fetch clients: {e}")
    
    def get_client(self, client_id: int) -> ClientModel:
        """
        Получить информацию о конкретном клиенте.
        
        Args:
            client_id: ID клиента
        
        Returns:
            ClientModel: Объект клиента
        
        Raises:
            NotFoundError: Если клиент не найден
            AuthenticationError: При ошибке аутентификации
            NetworkError: При проблемах с сетью
        
        Пример:
            >>> connector = LILUConnector()
            >>> client = connector.get_client(123)
            >>> print(f"Клиент: {client.name}, Email: {client.email}")
        """
        try:
            endpoint = ENDPOINTS['client'].format(client_id=client_id)
            logger.debug(f"Fetching client: {client_id}")
            
            response = self.client.get(endpoint)
            data = response.json()
            
            client = ClientModel.from_dict(data)
            logger.info(f"Retrieved client: {client.name}")
            return client
        
        except NotFoundError:
            logger.warning(f"Client {client_id} not found")
            raise
        except AuthenticationError:
            logger.error("Authentication failed while fetching client")
            raise
        except NetworkError:
            logger.error("Network error while fetching client")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching client: {e}")
            raise LILUAPIError(f"Failed to fetch client: {e}")
    
    def create_client(self, client_data: Dict[str, Any]) -> ClientModel:
        """
        Создать нового клиента.
        
        Args:
            client_data: Словарь с данными клиента
                Обязательные поля: name, email
                Опциональные: phone, status, metadata
        
        Returns:
            ClientModel: Созданный клиент
        
        Raises:
            AuthenticationError: При ошибке аутентификации
            NetworkError: При проблемах с сетью
            LILUAPIError: При других ошибках API
        
        Пример:
            >>> connector = LILUConnector()
            >>> new_client = connector.create_client({
            ...     'name': 'John Doe',
            ...     'email': 'john@example.com',
            ...     'phone': '+1234567890'
            ... })
            >>> print(f"Создан клиент с ID: {new_client.id}")
        """
        try:
            endpoint = ENDPOINTS['clients']
            logger.debug(f"Creating client: {client_data.get('name')}")
            
            response = self.client.post(endpoint, json=client_data)
            data = response.json()
            
            # LILU API возвращает данные в формате {data: {...}, status: 1}
            if isinstance(data, dict) and 'data' in data:
                data = data['data']
            
            client = ClientModel.from_dict(data)
            logger.info(f"Created client: {client.name} (ID: {client.id})")
            return client
        
        except AuthenticationError:
            logger.error("Authentication failed while creating client")
            raise
        except NetworkError:
            logger.error("Network error while creating client")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating client: {e}")
            raise LILUAPIError(f"Failed to create client: {e}")
    
    # ==================== ПРОДУКТЫ ====================
    
    def get_products(
        self,
        page: int = 1,
        limit: int = 50,
        category: Optional[str] = None
    ) -> List[ProductModel]:
        """
        Получить список продуктов.
        
        Args:
            page: Номер страницы
            limit: Количество продуктов на странице
            category: Фильтр по категории (опционально)
        
        Returns:
            List[ProductModel]: Список продуктов
        
        Пример:
            >>> connector = LILUConnector()
            >>> products = connector.get_products(category='electronics')
            >>> for product in products:
            ...     print(f"{product.name} - {product.price}")
        """
        try:
            endpoint = ENDPOINTS['products']
            params = {
                'page': page,
                'limit': limit
            }
            
            if category:
                params['category'] = category
            
            logger.debug(f"Fetching products: page={page}, limit={limit}, category={category}")
            response = self.client.get(endpoint, params=params)
            data = response.json()
            
            products = [ProductModel.from_dict(item) for item in data]
            logger.info(f"Retrieved {len(products)} products")
            return products
        
        except Exception as e:
            logger.error(f"Error while fetching products: {e}")
            raise LILUAPIError(f"Failed to fetch products: {e}")
    
    def get_product(self, product_id: int) -> ProductModel:
        """
        Получить информацию о конкретном продукте.
        
        Args:
            product_id: ID продукта
        
        Returns:
            ProductModel: Объект продукта
        
        Raises:
            NotFoundError: Если продукт не найден
        """
        try:
            endpoint = ENDPOINTS['product'].format(product_id=product_id)
            logger.debug(f"Fetching product: {product_id}")
            
            response = self.client.get(endpoint)
            data = response.json()
            
            product = ProductModel.from_dict(data)
            logger.info(f"Retrieved product: {product.name}")
            return product
        
        except NotFoundError:
            logger.warning(f"Product {product_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error while fetching product: {e}")
            raise LILUAPIError(f"Failed to fetch product: {e}")
    
    # ==================== ЗАКАЗЫ ====================
    
    def get_orders(
        self,
        page: int = 1,
        limit: int = 50,
        client_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[OrderModel]:
        """
        Получить список заказов.
        
        Args:
            page: Номер страницы
            limit: Количество заказов на странице
            client_id: Фильтр по ID клиента (опционально)
            status: Фильтр по статусу (опционально)
        
        Returns:
            List[OrderModel]: Список заказов
        """
        try:
            endpoint = ENDPOINTS['orders']
            params = {
                'page': page,
                'limit': limit
            }
            
            if client_id:
                params['client_id'] = client_id
            
            if status:
                params['status'] = status
            
            logger.debug(f"Fetching orders: page={page}, limit={limit}")
            response = self.client.get(endpoint, params=params)
            data = response.json()
            
            orders = [OrderModel.from_dict(item) for item in data]
            logger.info(f"Retrieved {len(orders)} orders")
            return orders
        
        except Exception as e:
            logger.error(f"Error while fetching orders: {e}")
            raise LILUAPIError(f"Failed to fetch orders: {e}")
    
    def get_order(self, order_id: int) -> OrderModel:
        """
        Получить информацию о конкретном заказе.
        
        Args:
            order_id: ID заказа
        
        Returns:
            OrderModel: Объект заказа
        
        Raises:
            NotFoundError: Если заказ не найден
        """
        try:
            endpoint = ENDPOINTS['order'].format(order_id=order_id)
            logger.debug(f"Fetching order: {order_id}")
            
            response = self.client.get(endpoint)
            data = response.json()
            
            order = OrderModel.from_dict(data)
            logger.info(f"Retrieved order: {order.id}")
            return order
        
        except NotFoundError:
            logger.warning(f"Order {order_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error while fetching order: {e}")
            raise LILUAPIError(f"Failed to fetch order: {e}")
    
    # ==================== УТИЛИТЫ ====================
    
    def health_check(self) -> bool:
        """
        Проверить доступность API.
        
        Returns:
            bool: True, если API доступен
        
        Пример:
            >>> connector = LILUConnector()
            >>> if connector.health_check():
            ...     print("API доступен")
            ... else:
            ...     print("API недоступен")
        """
        try:
            endpoint = ENDPOINTS['health']
            response = self.client.get(endpoint)
            logger.info("Health check passed")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    def get_template_categories(self) -> List[Dict[str, Any]]:
        """
        Получить список категорий шаблонов сообщений.
        
        Args:
            None
        
        Returns:
            List[Dict[str, Any]]: Список категорий шаблонов
        
        Пример:
            >>> connector = LILUConnector()
            >>> categories = connector.get_template_categories()
            >>> for category in categories:
            ...     print(category['name'])
        """
        try:
            endpoint = ENDPOINTS['template_categories']
            logger.debug("Fetching template categories")
            
            response = self.client.get(endpoint)
            data = response.json()
            
            # Логируем сырой ответ для отладки
            logger.debug(f"Raw response: {type(data)}, keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            
            # Проверяем, не является ли ответ ошибкой
            if isinstance(data, dict) and 'error' in data:
                error_msg = data.get('error', 'Unknown error')
                status = data.get('status', 'Unknown')
                logger.error(f"API returned error: status={status}, error={error_msg}")
                raise LILUAPIError(f"API error: {error_msg} (status: {status})")
            
            # Если ответ - список, проверяем структуру
            if isinstance(data, list):
                # Если первый элемент содержит 'categories', извлекаем их
                if data and len(data) > 0 and isinstance(data[0], dict) and 'categories' in data[0]:
                    categories = data[0]['categories']
                    if isinstance(categories, list):
                        logger.info(f"Retrieved {len(categories)} template categories")
                        return categories
                    else:
                        logger.info(f"Retrieved 1 template category")
                        return [categories] if categories else []
                else:
                    logger.info(f"Retrieved {len(data)} template categories")
                    return data
            # Если ответ - объект с данными
            elif isinstance(data, dict):
                # Проверяем различные возможные ключи
                if 'data' in data:
                    data_obj = data['data']
                    # Если data содержит categories
                    if isinstance(data_obj, dict) and 'categories' in data_obj:
                        categories = data_obj['categories']
                        if isinstance(categories, list):
                            logger.info(f"Retrieved {len(categories)} template categories")
                            return categories
                        else:
                            return [categories] if categories else []
                    # Если data - это список
                    elif isinstance(data_obj, list):
                        logger.info(f"Retrieved {len(data_obj)} template categories")
                        return data_obj
                    # Если data - это объект (одна категория)
                    else:
                        logger.info(f"Retrieved 1 template category")
                        return [data_obj] if data_obj else []
                elif 'categories' in data:
                    categories = data['categories']
                    if isinstance(categories, list):
                        logger.info(f"Retrieved {len(categories)} template categories")
                        return categories
                    else:
                        logger.info(f"Retrieved 1 template category")
                        return [categories] if categories else []
                elif 'results' in data:
                    categories = data['results']
                    logger.info(f"Retrieved {len(categories)} template categories")
                    return categories if isinstance(categories, list) else [categories]
                else:
                    # Возможно, сам объект и есть категория, или это другой формат
                    logger.warning(f"Unexpected response format. Keys: {list(data.keys())}")
                    # Возвращаем весь объект как список из одного элемента для анализа
                    return [data]
            else:
                logger.warning(f"Unexpected response type: {type(data)}")
                return []
        
        except Exception as e:
            logger.error(f"Error while fetching template categories: {e}")
            raise LILUAPIError(f"Failed to fetch template categories: {e}")
    
    def close(self):
        """
        Закрыть соединение и освободить ресурсы.
        
        Для Junior: важно закрывать соединения, чтобы не тратить ресурсы.
        Обычно это делается в конце работы или в блоке finally.
        
        Пример:
            >>> connector = LILUConnector()
            >>> try:
            ...     clients = connector.get_clients()
            ... finally:
            ...     connector.close()
        """
        if hasattr(self, 'client'):
            self.client.close()
        logger.info("LILUConnector closed")
