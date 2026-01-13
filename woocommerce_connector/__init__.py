"""
WooCommerce API Connector Package

A Python package for connecting to WooCommerce stores via REST API
and managing products with a modern GUI interface.
"""

from .connector import WooCommerceConnector, check_api_version_standalone
# GUI импортируем напрямую из модуля для обратной совместимости
from .gui import WooCommerceGUI

__version__ = "1.0.0"
__author__ = "Ivan Bondarenko"
__email__ = ""

__all__ = [
    "WooCommerceConnector",
    "WooCommerceGUI",
    "check_api_version_standalone",
]



