"""
Утилиты для работы приложения.

Этот модуль содержит вспомогательные функции и классы:
- logger - настройка логирования
- validators - валидация данных

Пример использования:
    >>> from woocommerce_connector.utils.logger import setup_logger
    >>> logger = setup_logger(__name__)
    >>> logger.info("Application started")
"""

from .logger import setup_logger, get_logger
# from .validators import ProductValidator  # Будет добавлено позже

__all__ = [
    "setup_logger",
    "get_logger",
    # "ProductValidator",
]
