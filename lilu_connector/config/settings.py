"""
Настройки подключения к LILU API.

Для Junior разработчиков:
Этот класс читает настройки из переменных окружения (.env файл).
Переменные окружения - это способ хранить секретные данные (API ключи)
вне кода, чтобы не коммитить их в Git.

Пример .env файла:
    LILU_API_URL=https://api.servus-ululu.com
    LILU_API_KEY=your_key_here
    LILU_API_SECRET=your_secret_here
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class LILUSettings:
    """
    Настройки для подключения к LILU API.
    
    Этот класс хранит все настройки, необходимые для работы с API:
    - URL сервера
    - API ключи
    - Версия API
    - Таймауты и т.д.
    
    Пример использования:
        >>> settings = LILUSettings()
        >>> print(settings.api_url)
        https://api.servus-ululu.com
    """
    
    def __init__(self):
        """
        Инициализация настроек из переменных окружения.
        
        Если переменная не найдена, используется значение по умолчанию
        или выбрасывается ошибка (для обязательных полей).
        """
        # Базовый URL API
        # os.getenv() читает переменную из окружения
        # Второй параметр - значение по умолчанию, если переменная не найдена
        self.api_url: str = os.getenv(
            'LILU_API_URL',
            'https://api.servus-ululu.com'
        ).rstrip('/')  # Убираем слеш в конце, если есть
        
        # API ключ (обязательный)
        self.api_key: Optional[str] = os.getenv('LILU_API_KEY')
        
        # API секрет (обязательный)
        self.api_secret: Optional[str] = os.getenv('LILU_API_SECRET')
        
        # Версия API
        self.api_version: str = os.getenv('LILU_API_VERSION', 'v2')
        
        # Таймаут для запросов (в секундах)
        self.timeout: int = int(os.getenv('LILU_TIMEOUT', '30'))
        
        # Максимальное количество повторных попыток
        self.max_retries: int = int(os.getenv('LILU_MAX_RETRIES', '3'))
        
        # Интервал между повторными попытками (в секундах)
        self.retry_delay: int = int(os.getenv('LILU_RETRY_DELAY', '1'))
        
        # Проверяем обязательные поля
        self._validate()
    
    def _validate(self) -> None:
        """
        Проверка, что все обязательные настройки заполнены.
        
        Если какое-то обязательное поле отсутствует,
        выбрасывается ValueError с понятным сообщением.
        
        Raises:
            ValueError: Если отсутствуют обязательные настройки
        """
        if not self.api_key:
            raise ValueError(
                "LILU_API_KEY is required. "
                "Please set it in your .env file."
            )
        
        if not self.api_secret:
            raise ValueError(
                "LILU_API_SECRET is required. "
                "Please set it in your .env file."
            )
        
        if not self.api_url:
            raise ValueError(
                "LILU_API_URL is required. "
                "Please set it in your .env file."
            )
    
    def get_base_url(self) -> str:
        """
        Получить полный базовый URL API.
        
        Returns:
            str: Полный URL, например: https://api.servus-ululu.com/api/v2
        """
        return f"{self.api_url}/api/{self.api_version}"
    
    def __repr__(self) -> str:
        """
        Строковое представление настроек (без секретных данных).
        
        Returns:
            str: Информация о настройках
        """
        return (
            f"LILUSettings("
            f"api_url={self.api_url}, "
            f"api_version={self.api_version}, "
            f"timeout={self.timeout}, "
            f"api_key={'***' if self.api_key else 'None'}, "
            f"api_secret={'***' if self.api_secret else 'None'}"
            f")"
        )
