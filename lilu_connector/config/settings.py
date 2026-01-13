"""
Настройки подключения к LILU API.

Для Junior разработчиков:
Этот класс читает настройки из переменных окружения (.env файл).
Переменные окружения - это способ хранить секретные данные (API токен)
вне кода, чтобы не коммитить их в Git.

Пример .env файла:
    LILU_API_URL=https://api.servus-ululu.com
    LILU_API_TOKEN=your_token_here
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные из .env файла
# Ищем .env файл в корне проекта (на 2 уровня выше от этого файла)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)
# Также пробуем загрузить из текущей директории (на случай, если запускаем из корня)
load_dotenv()


class LILUSettings:
    """
    Настройки для подключения к LILU API.
    
    Этот класс хранит все настройки, необходимые для работы с API:
    - URL сервера
    - API токен
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
            'https://api.leeloo.ai'
        ).rstrip('/')  # Убираем слеш в конце, если есть
        
        # API ключ и секрет (для аутентификации)
        # Для Junior: ключ и секрет используются для аутентификации в API
        # Поддерживаем оба варианта: токен или ключ+секрет
        self.api_token: Optional[str] = os.getenv('LILU_API_TOKEN')
        self.api_key: Optional[str] = os.getenv('LILU_API_KEY')
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
        if not self.api_url:
            raise ValueError(
                "LILU_API_URL is required. "
                "Please set it in your .env file."
            )
        
        # Проверяем, что есть либо токен, либо ключ+секрет
        if not self.api_token and not (self.api_key and self.api_secret):
            raise ValueError(
                "Either LILU_API_TOKEN or both LILU_API_KEY and LILU_API_SECRET are required. "
                "Please set them in your .env file."
            )
        
        # Если используется ключ+секрет, оба должны быть указаны
        if (self.api_key or self.api_secret) and not (self.api_key and self.api_secret):
            raise ValueError(
                "Both LILU_API_KEY and LILU_API_SECRET must be set together. "
                "Please set both in your .env file."
            )
    
    def get_base_url(self) -> str:
        """
        Получить полный базовый URL API.
        
        Returns:
            str: Полный URL, например: https://api.leeloo.ai/api/v2
        """
        # Если URL уже содержит /api, не добавляем его снова
        if '/api' in self.api_url:
            return f"{self.api_url}/{self.api_version}"
        else:
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
            f"api_token={'***' if self.api_token else 'None'}"
            f")"
        )
