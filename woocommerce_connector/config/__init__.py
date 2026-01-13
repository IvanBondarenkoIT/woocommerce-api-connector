"""
Модуль конфигурации WooCommerce Connector.

Содержит классы и константы для настройки приложения.
"""

# Импортируем WooCommerceConfig из родительского модуля
# config.py находится в woocommerce_connector/, а мы в woocommerce_connector/config/
from ..config import WooCommerceConfig
from .constants import (
    APIConstants,
    ExcelConstants,
    ProductConstants,
    OrderConstants,
)

__all__ = [
    "WooCommerceConfig",
    "APIConstants",
    "ExcelConstants",
    "ProductConstants",
    "OrderConstants",
]
