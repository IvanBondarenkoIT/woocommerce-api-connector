"""
API слой для работы с WooCommerce REST API.

Этот модуль содержит классы для работы с WooCommerce API:
- WooCommerceAPIClient - базовый клиент для API запросов
- ProductsRepository - репозиторий для работы с товарами
- OrdersRepository - репозиторий для работы с заказами (будущее)
- CustomersRepository - репозиторий для работы с клиентами (будущее)

Пример использования:
    >>> from woocommerce_connector.api import WooCommerceAPIClient, ProductsRepository
    >>> client = WooCommerceAPIClient(config)
    >>> repo = ProductsRepository(client)
    >>> products = repo.get_all()
"""

# Будет добавлено после реализации
# from .client import WooCommerceAPIClient
# from .products import ProductsRepository
# from .exceptions import WooCommerceAPIError, AuthenticationError

__all__ = [
    # "WooCommerceAPIClient",
    # "ProductsRepository",
    # "WooCommerceAPIError",
    # "AuthenticationError",
]
