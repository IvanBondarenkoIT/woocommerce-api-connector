"""
Константы для WooCommerce Connector.

Этот модуль содержит все константы, используемые в приложении:
лимиты API, форматы данных, значения по умолчанию и т.д.

Пример использования:
    >>> from woocommerce_connector.config.constants import APIConstants
    >>> per_page = APIConstants.DEFAULT_PER_PAGE
"""


class APIConstants:
    """
    Константы для работы с WooCommerce API.
    
    Содержит значения по умолчанию и лимиты для API запросов.
    """
    # Пагинация
    DEFAULT_PER_PAGE: int = 100
    MAX_PER_PAGE: int = 100
    MIN_PER_PAGE: int = 1
    
    # Таймауты
    DEFAULT_TIMEOUT: int = 30
    MIN_TIMEOUT: int = 5
    MAX_TIMEOUT: int = 300
    
    # Версии API
    DEFAULT_API_VERSION: str = "wc/v3"
    SUPPORTED_VERSIONS: list = ['wc/v3', 'wc/v2', 'v3', 'v2']
    
    # Retry настройки
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1  # секунды


class ExcelConstants:
    """
    Константы для экспорта в Excel.
    
    Содержит настройки для форматирования Excel файлов.
    """
    # Имена листов
    MAX_SHEET_NAME_LENGTH: int = 31
    INVALID_SHEET_CHARS: list = ['\\', '/', '*', '?', ':', '[', ']']
    DEFAULT_SHEET_NAME: str = "Products"
    
    # Форматирование
    DEFAULT_COLUMN_WIDTH: int = 50
    HEADER_COLOR: str = "366092"
    HEADER_FONT_COLOR: str = "FFFFFF"
    HEADER_FONT_SIZE: int = 12
    HEADER_FONT_BOLD: bool = True
    
    # Файлы
    DEFAULT_FILENAME_PREFIX: str = "woocommerce_"
    FILE_EXTENSION: str = ".xlsx"


class ProductConstants:
    """
    Константы для работы с товарами.
    
    Содержит значения по умолчанию и статусы товаров.
    """
    # Статусы товаров
    STATUS_PUBLISH: str = "publish"
    STATUS_DRAFT: str = "draft"
    STATUS_PENDING: str = "pending"
    STATUS_PRIVATE: str = "private"
    
    # Статусы наличия
    STOCK_IN_STOCK: str = "instock"
    STOCK_OUT_OF_STOCK: str = "outofstock"
    STOCK_ON_BACKORDER: str = "onbackorder"
    
    # Типы товаров
    TYPE_SIMPLE: str = "simple"
    TYPE_VARIABLE: str = "variable"
    TYPE_GROUPED: str = "grouped"
    TYPE_EXTERNAL: str = "external"


class OrderConstants:
    """
    Константы для работы с заказами.
    
    Содержит статусы заказов и другие константы.
    """
    # Статусы заказов
    STATUS_PENDING: str = "pending"
    STATUS_PROCESSING: str = "processing"
    STATUS_ON_HOLD: str = "on-hold"
    STATUS_COMPLETED: str = "completed"
    STATUS_CANCELLED: str = "cancelled"
    STATUS_REFUNDED: str = "refunded"
    STATUS_FAILED: str = "failed"
