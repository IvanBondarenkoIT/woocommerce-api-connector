"""
Кастомные исключения для работы с WooCommerce API.

Этот модуль содержит специфичные исключения для различных
типов ошибок, которые могут возникнуть при работе с API.

Пример использования:
    >>> from woocommerce_connector.api.exceptions import AuthenticationError
    >>> try:
    ...     # API call
    ... except AuthenticationError as e:
    ...     logger.error(f"Auth failed: {e}")
"""


class WooCommerceAPIError(Exception):
    """
    Базовое исключение для всех ошибок WooCommerce API.
    
    Все специфичные исключения наследуются от этого класса.
    Это позволяет перехватывать все API ошибки одним блоком try/except.
    
    Example:
        >>> try:
        ...     # API operation
        ... except WooCommerceAPIError as e:
        ...     print(f"API error: {e}")
    """
    pass


class AuthenticationError(WooCommerceAPIError):
    """
    Ошибка аутентификации.
    
    Возникает при неправильных credentials (401 статус).
    Обычно означает, что consumer_key или consumer_secret неверны.
    
    Example:
        >>> raise AuthenticationError("Invalid credentials")
    """
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(WooCommerceAPIError):
    """
    Ресурс не найден.
    
    Возникает при попытке получить несуществующий ресурс (404 статус).
    Например, товар или заказ с указанным ID не существует.
    
    Example:
        >>> raise NotFoundError("Product with ID 123 not found")
    """
    def __init__(self, resource: str, resource_id: str = ""):
        if resource_id:
            self.message = f"{resource} with ID {resource_id} not found"
        else:
            self.message = f"{resource} not found"
        super().__init__(self.message)


class RateLimitError(WooCommerceAPIError):
    """
    Превышен лимит запросов.
    
    Возникает при превышении лимита запросов к API (429 статус).
    WooCommerce может ограничивать количество запросов в единицу времени.
    
    Example:
        >>> raise RateLimitError("Too many requests. Please wait.")
    """
    def __init__(self, message: str = "Rate limit exceeded"):
        self.message = message
        super().__init__(self.message)


class APIResponseError(WooCommerceAPIError):
    """
    Ошибка ответа API.
    
    Возникает при неожиданном статусе ответа от API (не 200).
    Содержит информацию о статусе и теле ответа.
    
    Attributes:
        status_code: HTTP статус код ответа
        message: Сообщение об ошибке
        response_text: Текст ответа от сервера
    
    Example:
        >>> raise APIResponseError(500, "Internal server error", "Error details")
    """
    def __init__(self, status_code: int, message: str, response_text: str = ""):
        self.status_code = status_code
        self.message = message
        self.response_text = response_text
        error_msg = f"API Error {status_code}: {message}"
        if response_text:
            error_msg += f" - {response_text}"
        super().__init__(error_msg)


class ConfigurationError(WooCommerceAPIError):
    """
    Ошибка конфигурации.
    
    Возникает при отсутствии или неправильной настройке
    необходимых параметров (URL, ключи и т.д.).
    
    Example:
        >>> raise ConfigurationError("WC_URL is required")
    """
    def __init__(self, message: str = "Configuration error"):
        self.message = message
        super().__init__(self.message)


class NetworkError(WooCommerceAPIError):
    """
    Ошибка сети.
    
    Возникает при проблемах с сетевым соединением:
    таймауты, недоступность сервера и т.д.
    
    Example:
        >>> raise NetworkError("Connection timeout")
    """
    def __init__(self, message: str = "Network error"):
        self.message = message
        super().__init__(self.message)
