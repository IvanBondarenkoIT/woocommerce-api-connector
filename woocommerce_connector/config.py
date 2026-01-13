"""
Модуль конфигурации для WooCommerce Connector.

Этот модуль содержит класс WooCommerceConfig для централизованного
управления настройками подключения к WooCommerce API.

Пример использования:
    >>> from woocommerce_connector.config import WooCommerceConfig
    >>> config = WooCommerceConfig.from_env()
    >>> config.validate()
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

from .api.exceptions import ConfigurationError

# Загружаем переменные окружения
load_dotenv()


@dataclass
class WooCommerceConfig:
    """
    Конфигурация для подключения к WooCommerce API.
    
    Содержит все необходимые параметры для работы с WooCommerce REST API:
    URL магазина, ключи доступа, версия API и другие настройки.
    
    Attributes:
        url: URL магазина WooCommerce (без завершающего слеша)
        consumer_key: Consumer Key для аутентификации
        consumer_secret: Consumer Secret для аутентификации
        api_version: Версия API (по умолчанию 'wc/v3')
        timeout: Таймаут запросов в секундах (по умолчанию 30)
        query_string_auth: Использовать ли query string auth вместо OAuth
    
    Example:
        >>> # Загрузка из переменных окружения
        >>> config = WooCommerceConfig.from_env()
        >>> config.validate()
        >>> 
        >>> # Создание вручную
        >>> config = WooCommerceConfig(
        ...     url="https://store.example.com",
        ...     consumer_key="ck_...",
        ...     consumer_secret="cs_..."
        ... )
    """
    url: str
    consumer_key: str
    consumer_secret: str
    api_version: str = "wc/v3"
    timeout: int = 30
    query_string_auth: bool = True
    
    @classmethod
    def from_env(cls) -> 'WooCommerceConfig':
        """
        Загрузить конфигурацию из переменных окружения.
        
        Читает настройки из .env файла или переменных окружения:
        - WC_URL: URL магазина
        - WC_CONSUMER_KEY: Consumer Key
        - WC_CONSUMER_SECRET: Consumer Secret
        - WC_API_VERSION: Версия API (опционально, по умолчанию 'wc/v3')
        - WC_TIMEOUT: Таймаут в секундах (опционально, по умолчанию 30)
        
        Returns:
            WooCommerceConfig: Объект конфигурации
        
        Raises:
            ConfigurationError: Если отсутствуют обязательные переменные
        
        Example:
            >>> config = WooCommerceConfig.from_env()
            >>> print(config.url)
            https://store.example.com
        """
        url = (os.getenv('WC_URL') or '').rstrip('/')
        consumer_key = os.getenv('WC_CONSUMER_KEY', '')
        consumer_secret = os.getenv('WC_CONSUMER_SECRET', '')
        api_version = os.getenv('WC_API_VERSION', 'wc/v3')
        
        # Таймаут из переменной окружения или по умолчанию
        timeout_str = os.getenv('WC_TIMEOUT', '30')
        try:
            timeout = int(timeout_str)
        except ValueError:
            timeout = 30
        
        return cls(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            api_version=api_version,
            timeout=timeout,
        )
    
    def validate(self) -> None:
        """
        Валидировать конфигурацию.
        
        Проверяет, что все обязательные поля заполнены и корректны.
        
        Raises:
            ConfigurationError: Если конфигурация невалидна
        
        Example:
            >>> config = WooCommerceConfig.from_env()
            >>> try:
            ...     config.validate()
            ...     print("Configuration is valid")
            ... except ConfigurationError as e:
            ...     print(f"Invalid config: {e}")
        """
        errors = []
        
        if not self.url:
            errors.append("WC_URL is required")
        
        if not self.consumer_key:
            errors.append("WC_CONSUMER_KEY is required")
        
        if not self.consumer_secret:
            errors.append("WC_CONSUMER_SECRET is required")
        
        # Проверка формата URL
        if self.url and not (self.url.startswith('http://') or self.url.startswith('https://')):
            errors.append("WC_URL must start with http:// or https://")
        
        # Проверка формата ключей
        if self.consumer_key and not self.consumer_key.startswith('ck_'):
            errors.append("WC_CONSUMER_KEY should start with 'ck_'")
        
        if self.consumer_secret and not self.consumer_secret.startswith('cs_'):
            errors.append("WC_CONSUMER_SECRET should start with 'cs_'")
        
        if errors:
            error_message = "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ConfigurationError(error_message)
    
    def __str__(self) -> str:
        """Строковое представление конфигурации (без секретов)"""
        return (
            f"WooCommerceConfig("
            f"url='{self.url}', "
            f"api_version='{self.api_version}', "
            f"timeout={self.timeout}"
            f")"
        )
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return self.__str__()
