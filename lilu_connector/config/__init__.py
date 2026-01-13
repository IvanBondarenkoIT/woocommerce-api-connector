"""
Конфигурация для LILU Connector.

Этот модуль экспортирует настройки и константы для работы с LILU API.
"""

from .settings import LILUSettings
from .constants import ENDPOINTS, API_VERSION

__all__ = [
    "LILUSettings",
    "ENDPOINTS",
    "API_VERSION",
]
