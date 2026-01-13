"""
LILU API Connector Package

A Python package for connecting to LILU (Servus Ululu) API.
This connector follows the same architectural patterns as WooCommerce connector
but is specifically designed for LILU API integration.

Для junior разработчиков:
Этот модуль экспортирует основные классы и функции, которые можно использовать
в других частях приложения. Это точка входа в пакет LILU connector.

Пример использования:
    >>> from lilu_connector import LILUConnector
    >>> connector = LILUConnector()
    >>> products = connector.get_products()
"""

from .connector import LILUConnector

__version__ = "1.0.0"
__author__ = "Development Team"

__all__ = [
    "LILUConnector",
]
