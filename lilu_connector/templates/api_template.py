"""
Шаблон для создания нового API endpoint.

Для Junior разработчиков:
Этот файл - шаблон для добавления нового метода в LILUConnector.
Скопируйте этот код, замените комментарии на реальные значения
и добавьте метод в connector.py.

ИНСТРУКЦИЯ:
1. Скопируйте этот код
2. Вставьте в connector.py
3. Замените все TODO комментарии на реальные значения
4. Добавьте endpoint в config/constants.py
5. Создайте модель в models/ (если нужно)
6. Напишите тесты
"""

from typing import List, Optional, Dict, Any
from .models.your_model import YourModel  # TODO: Замените на реальную модель
from .config.constants import ENDPOINTS
from .api.exceptions import LILUAPIError, NotFoundError
from .utils.logger import get_logger

logger = get_logger(__name__)


# TODO: Добавьте endpoint в config/constants.py:
# 'your_endpoint': '/api/v2/your_endpoint',
# 'your_item': '/api/v2/your_endpoint/{item_id}',


def get_your_items(
    self,
    page: int = 1,
    limit: int = 50,
    filter_param: Optional[str] = None  # TODO: Замените на реальные параметры
) -> List[YourModel]:  # TODO: Замените YourModel на реальную модель
    """
    Получить список элементов.
    
    Для Junior: Опишите, что делает этот метод.
    
    Args:
        page: Номер страницы (для пагинации)
        limit: Количество элементов на странице
        filter_param: Параметр фильтрации (опционально)
    
    Returns:
        List[YourModel]: Список элементов
    
    Raises:
        AuthenticationError: При ошибке аутентификации
        NetworkError: При проблемах с сетью
        LILUAPIError: При других ошибках API
    
    Пример:
        >>> connector = LILUConnector()
        >>> items = connector.get_your_items(page=1, limit=50)
        >>> for item in items:
        ...     print(item.name)
    """
    try:
        # TODO: Замените 'your_endpoint' на реальный endpoint
        endpoint = ENDPOINTS['your_endpoint']
        
        # Параметры запроса
        params = {
            'page': page,
            'limit': limit
        }
        
        # Добавляем опциональные параметры
        if filter_param:
            params['filter'] = filter_param  # TODO: Замените на реальное имя параметра
        
        logger.debug(f"Fetching items: page={page}, limit={limit}")
        response = self.client.get(endpoint, params=params)
        data = response.json()
        
        # Преобразуем список словарей в список моделей
        items = [YourModel.from_dict(item) for item in data]
        
        logger.info(f"Retrieved {len(items)} items")
        return items
    
    except AuthenticationError:
        logger.error("Authentication failed while fetching items")
        raise
    except NetworkError:
        logger.error("Network error while fetching items")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching items: {e}")
        raise LILUAPIError(f"Failed to fetch items: {e}")


def get_your_item(self, item_id: int) -> YourModel:
    """
    Получить информацию о конкретном элементе.
    
    Args:
        item_id: ID элемента
    
    Returns:
        YourModel: Объект элемента
    
    Raises:
        NotFoundError: Если элемент не найден
        AuthenticationError: При ошибке аутентификации
        NetworkError: При проблемах с сетью
    
    Пример:
        >>> connector = LILUConnector()
        >>> item = connector.get_your_item(123)
        >>> print(item.name)
    """
    try:
        # TODO: Замените 'your_item' на реальный endpoint
        endpoint = ENDPOINTS['your_item'].format(item_id=item_id)
        logger.debug(f"Fetching item: {item_id}")
        
        response = self.client.get(endpoint)
        data = response.json()
        
        item = YourModel.from_dict(data)
        logger.info(f"Retrieved item: {item.name}")
        return item
    
    except NotFoundError:
        logger.warning(f"Item {item_id} not found")
        raise
    except AuthenticationError:
        logger.error("Authentication failed while fetching item")
        raise
    except NetworkError:
        logger.error("Network error while fetching item")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching item: {e}")
        raise LILUAPIError(f"Failed to fetch item: {e}")


def create_your_item(self, item_data: Dict[str, Any]) -> YourModel:
    """
    Создать новый элемент.
    
    Args:
        item_data: Словарь с данными элемента
            Обязательные поля: TODO - укажите обязательные поля
            Опциональные: TODO - укажите опциональные поля
    
    Returns:
        YourModel: Созданный элемент
    
    Raises:
        AuthenticationError: При ошибке аутентификации
        NetworkError: При проблемах с сетью
        LILUAPIError: При других ошибках API
    
    Пример:
        >>> connector = LILUConnector()
        >>> new_item = connector.create_your_item({
        ...     'name': 'Item Name',
        ...     'description': 'Item Description'
        ... })
        >>> print(f"Создан элемент с ID: {new_item.id}")
    """
    try:
        # TODO: Замените 'your_endpoint' на реальный endpoint
        endpoint = ENDPOINTS['your_endpoint']
        logger.debug(f"Creating item: {item_data.get('name')}")
        
        response = self.client.post(endpoint, json=item_data)
        data = response.json()
        
        item = YourModel.from_dict(data)
        logger.info(f"Created item: {item.name} (ID: {item.id})")
        return item
    
    except AuthenticationError:
        logger.error("Authentication failed while creating item")
        raise
    except NetworkError:
        logger.error("Network error while creating item")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating item: {e}")
        raise LILUAPIError(f"Failed to create item: {e}")
