"""
Кастомные исключения для работы с LILU API.

Для Junior разработчиков:
Исключения (exceptions) - это способ обработать ошибки в Python.
Вместо того чтобы возвращать None или -1 при ошибке, мы выбрасываем исключение.
Это делает код более понятным и безопасным.

Пример использования:
    >>> try:
    ...     client = connector.get_client(123)
    ... except NotFoundError:
    ...     print("Клиент не найден")
    ... except AuthenticationError:
    ...     print("Ошибка аутентификации")
"""


class LILUAPIError(Exception):
    """
    Базовое исключение для всех ошибок LILU API.
    
    Все остальные исключения наследуются от этого класса.
    Это позволяет перехватывать все API ошибки одним блоком:
    
    Пример:
        >>> try:
        ...     # API операция
        ... except LILUAPIError as e:
        ...     print(f"Ошибка API: {e}")
    """
    pass


class AuthenticationError(LILUAPIError):
    """
    Ошибка аутентификации.
    
    Возникает при неправильном API токене (401 или 403 статус).
    Обычно означает, что LILU_API_TOKEN неверен или истёк.
    
    Пример:
        >>> raise AuthenticationError("Invalid API token")
    """
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(LILUAPIError):
    """
    Ресурс не найден.
    
    Возникает при попытке получить несуществующий ресурс (404 статус).
    Например, клиент или заказ с указанным ID не существует.
    
    Пример:
        >>> raise NotFoundError("Client", "123")
        # Выведет: "Client with ID 123 not found"
    """
    def __init__(self, resource: str, resource_id: str = ""):
        if resource_id:
            self.message = f"{resource} with ID {resource_id} not found"
        else:
            self.message = f"{resource} not found"
        super().__init__(self.message)


class RateLimitError(LILUAPIError):
    """
    Превышен лимит запросов.
    
    Возникает при превышении лимита запросов к API (429 статус).
    API может ограничивать количество запросов в единицу времени.
    
    Пример:
        >>> raise RateLimitError("Too many requests. Please wait 60 seconds.")
    """
    def __init__(self, message: str = "Rate limit exceeded"):
        self.message = message
        super().__init__(self.message)


class APIResponseError(LILUAPIError):
    """
    Ошибка ответа API.
    
    Возникает при неожиданном статусе ответа от API (не 200).
    Содержит информацию о статусе и теле ответа.
    
    Attributes:
        status_code: HTTP статус код ответа (например, 500)
        message: Сообщение об ошибке
        response_text: Текст ответа от сервера
    
    Пример:
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


class ConfigurationError(LILUAPIError):
    """
    Ошибка конфигурации.
    
    Возникает при отсутствии или неправильной настройке
    необходимых параметров (URL, ключи и т.д.).
    
    Пример:
        >>> raise ConfigurationError("LILU_API_URL is required")
    """
    def __init__(self, message: str = "Configuration error"):
        self.message = message
        super().__init__(self.message)


class NetworkError(LILUAPIError):
    """
    Ошибка сети.
    
    Возникает при проблемах с сетевым соединением:
    таймауты, недоступность сервера и т.д.
    
    Пример:
        >>> raise NetworkError("Connection timeout after 30 seconds")
    """
    def __init__(self, message: str = "Network error"):
        self.message = message
        super().__init__(self.message)
