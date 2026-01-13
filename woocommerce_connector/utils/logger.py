"""
Модуль для настройки логирования в приложении.

Этот модуль предоставляет функцию setup_logger для настройки
логирования с записью в консоль и файлы.

Пример использования:
    >>> from woocommerce_connector.utils.logger import setup_logger
    >>> logger = setup_logger(__name__)
    >>> logger.info("Application started")
    >>> logger.error("Something went wrong", exc_info=True)
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_dir: Optional[str] = None,
    log_to_file: bool = True
) -> logging.Logger:
    """
    Настроить logger для модуля.
    
    Создает logger с двумя обработчиками:
    - Console handler: выводит логи в консоль (INFO и выше)
    - File handler: записывает логи в файл (DEBUG и выше)
    
    Args:
        name: Имя logger (обычно __name__ модуля)
        level: Уровень логирования (по умолчанию INFO)
        log_dir: Директория для логов (по умолчанию "logs")
        log_to_file: Записывать ли логи в файл (по умолчанию True)
    
    Returns:
        logging.Logger: Настроенный logger
    
    Example:
        >>> # В начале модуля
        >>> from woocommerce_connector.utils.logger import setup_logger
        >>> logger = setup_logger(__name__)
        >>> 
        >>> # Использование
        >>> logger.debug("Debug message")
        >>> logger.info("Info message")
        >>> logger.warning("Warning message")
        >>> logger.error("Error message", exc_info=True)
    """
    logger = logging.getLogger(name)
    
    # Не добавлять обработчики, если они уже есть
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler - выводит в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler - записывает в файл
    if log_to_file:
        if log_dir is None:
            log_dir = "logs"
        
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Имя файла на основе имени модуля
        log_file = log_path / f"{name.replace('.', '_')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # В файл пишем все логи
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Получить существующий logger или создать новый.
    
    Удобная функция для получения logger без явной настройки.
    Если logger еще не настроен, создаст его с настройками по умолчанию.
    
    Args:
        name: Имя logger (обычно __name__ модуля)
    
    Returns:
        logging.Logger: Logger
    
    Example:
        >>> from woocommerce_connector.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Message")
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        return setup_logger(name)
    
    return logger
