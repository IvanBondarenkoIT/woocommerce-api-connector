"""
Модели данных для LILU API.

Для Junior разработчиков:
Модели - это структуры данных, которые представляют объекты из API.
Вместо работы со словарями (dict), мы используем типизированные классы.
Это делает код более безопасным и понятным.

Пример:
    # Плохо (работа со словарями):
    client = {'id': 1, 'name': 'John', 'email': 'john@example.com'}
    print(client['name'])  # Опечатка в ключе не будет обнаружена
    
    # Хорошо (работа с моделями):
    client = ClientModel(id=1, name='John', email='john@example.com')
    print(client.name)  # IDE подскажет правильное поле
"""

from .client import ClientModel
from .product import ProductModel
from .order import OrderModel

__all__ = [
    "ClientModel",
    "ProductModel",
    "OrderModel",
]
