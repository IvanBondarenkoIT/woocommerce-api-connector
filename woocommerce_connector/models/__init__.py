"""
Модели данных для WooCommerce Connector.

Этот модуль содержит модели данных (dataclasses) для представления
сущностей WooCommerce: товары, категории, заказы, клиенты.

Пример использования:
    >>> from woocommerce_connector.models import Product, Category
    >>> product = Product.from_dict(api_data)
    >>> print(product.name)
"""

from .product import Product
from .category import Category

# Модели для будущих фич (готовы к использованию, но пока не используются)
from .order import Order
from .customer import Customer

__all__ = [
    "Product",
    "Category",
    "Order",  # Готово для Этапа 5 (работа с заказами)
    "Customer",  # Готово для Этапа 5 (работа с клиентами)
]
