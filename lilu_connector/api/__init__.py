"""
API слой для работы с LILU API.

Для Junior разработчиков:
API слой - это часть кода, которая отвечает только за HTTP запросы.
Она не знает о бизнес-логике, только отправляет запросы и получает ответы.
"""

from .client import LILUClient
from .exceptions import (
    LILUAPIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIResponseError,
    NetworkError,
)

__all__ = [
    "LILUClient",
    "LILUAPIError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "APIResponseError",
    "NetworkError",
]
