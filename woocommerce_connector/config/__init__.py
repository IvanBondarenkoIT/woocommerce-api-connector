"""
Модуль конфигурации WooCommerce Connector.

Содержит классы и константы для настройки приложения.
"""

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
