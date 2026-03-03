"""
Сервисы для бизнес-логики приложения.

Этот модуль содержит сервисы, которые инкапсулируют бизнес-логику:
- SyncService - синхронизация заказов WooCommerce с LILU CRM
- OrderProcessor - обработка заказов и извлечение данных клиентов
- SyncTracker - отслеживание обработанных заказов
- ProductService - работа с товарами (будущее)
- ExportService - экспорт данных

Пример использования:
    >>> from woocommerce_connector.services import SyncService
    >>> from woocommerce_connector.connector import WooCommerceConnector
    >>> from lilu_connector.connector import LILUConnector
    >>> 
    >>> wc = WooCommerceConnector()
    >>> lilu = LILUConnector()
    >>> sync = SyncService(wc, lilu)
    >>> results = sync.sync_new_orders()
"""

from .sync_service import SyncService, SyncResult
from .order_processor import OrderProcessor, CustomerData
from .sync_tracker import SyncTracker, ProcessedOrder

__all__ = [
    "SyncService",
    "SyncResult",
    "OrderProcessor",
    "CustomerData",
    "SyncTracker",
    "ProcessedOrder",
]
