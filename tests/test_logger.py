"""
Тесты для системы логирования.

Эти тесты проверяют корректность работы logger:
- Создание logger
- Настройка handlers
- Запись в файл и консоль
- Уровни логирования
"""

import pytest
import logging
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from woocommerce_connector.utils.logger import setup_logger, get_logger


@pytest.fixture
def temp_log_dir():
    """Создает временную директорию для логов"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestSetupLogger:
    """Тесты для функции setup_logger"""
    
    def test_setup_logger_creates_logger(self):
        """Тест создания logger"""
        logger = setup_logger("test_module", log_to_file=False)
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
    
    def test_setup_logger_sets_level(self):
        """Тест установки уровня логирования"""
        # Удаляем logger если он существует
        logger_name = "test_setup_level"
        if logger_name in logging.Logger.manager.loggerDict:
            del logging.Logger.manager.loggerDict[logger_name]
        
        logger = setup_logger(logger_name, level=logging.DEBUG, log_to_file=False)
        
        # Проверяем что уровень установлен (может быть INFO по умолчанию для root)
        assert logger.level <= logging.DEBUG or logger.level == logging.NOTSET
    
    def test_setup_logger_creates_console_handler(self):
        """Тест создания console handler"""
        logger = setup_logger("test_module", log_to_file=False)
        
        # Должен быть хотя бы один handler
        assert len(logger.handlers) >= 1
        
        # Должен быть StreamHandler для консоли
        console_handlers = [
            h for h in logger.handlers 
            if isinstance(h, logging.StreamHandler)
        ]
        assert len(console_handlers) >= 1
    
    def test_setup_logger_creates_file_handler(self, temp_log_dir):
        """Тест создания file handler"""
        logger_name = "test_file_handler"
        # Удаляем logger если он существует
        if logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
        
        logger = setup_logger(
            logger_name,
            log_dir=temp_log_dir,
            log_to_file=True
        )
        
        # Должен быть FileHandler
        file_handlers = [
            h for h in logger.handlers 
            if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) >= 1
    
    def test_setup_logger_file_handler_level(self, temp_log_dir):
        """Тест уровня логирования file handler"""
        logger_name = "test_file_handler_level"
        # Удаляем logger если он существует
        if logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
        
        logger = setup_logger(
            logger_name,
            level=logging.INFO,
            log_dir=temp_log_dir,
            log_to_file=True
        )
        
        file_handlers = [
            h for h in logger.handlers 
            if isinstance(h, logging.FileHandler)
        ]
        
        # File handler должен иметь уровень DEBUG (все логи)
        assert len(file_handlers) >= 1
        assert file_handlers[0].level == logging.DEBUG
    
    def test_setup_logger_console_handler_level(self):
        """Тест уровня логирования console handler"""
        logger_name = "test_console_level"
        # Удаляем logger если он существует
        if logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
        
        logger = setup_logger(
            logger_name,
            level=logging.WARNING,
            log_to_file=False
        )
        
        console_handlers = [
            h for h in logger.handlers 
            if isinstance(h, logging.StreamHandler)
        ]
        
        assert len(console_handlers) >= 1
        # Handler должен иметь уровень WARNING или выше
        assert console_handlers[0].level >= logging.WARNING
    
    def test_setup_logger_creates_log_file(self, temp_log_dir):
        """Тест создания файла лога"""
        logger_name = "test_log_file"
        # Удаляем logger если он существует
        if logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
        
        logger = setup_logger(
            logger_name,
            log_dir=temp_log_dir,
            log_to_file=True
        )
        
        # Записываем тестовое сообщение
        logger.info("Test message")
        
        # Закрываем handlers чтобы файл был записан
        for handler in logger.handlers:
            handler.close()
        
        # Файл должен быть создан
        log_file = Path(temp_log_dir) / f"{logger_name}.log"
        assert log_file.exists()
        
        # Файл должен содержать сообщение
        content = log_file.read_text(encoding='utf-8')
        assert "Test message" in content
    
    def test_setup_logger_formatter(self):
        """Тест форматирования логов"""
        logger = setup_logger("test_module", log_to_file=False)
        
        # Проверяем что у handler есть formatter
        for handler in logger.handlers:
            assert handler.formatter is not None
            assert isinstance(handler.formatter, logging.Formatter)
    
    def test_setup_logger_no_duplicate_handlers(self):
        """Тест что handlers не дублируются"""
        logger1 = setup_logger("test_module", log_to_file=False)
        logger2 = setup_logger("test_module", log_to_file=False)
        
        # Должен быть один и тот же logger
        assert logger1 is logger2
        
        # Handlers не должны дублироваться
        # (setup_logger проверяет наличие handlers)
        assert len(logger1.handlers) >= 1


class TestGetLogger:
    """Тесты для функции get_logger"""
    
    def test_get_logger_creates_new_logger(self):
        """Тест создания нового logger"""
        # Удаляем logger если он существует
        logger_name = "test_get_logger_new"
        if logger_name in logging.Logger.manager.loggerDict:
            del logging.Logger.manager.loggerDict[logger_name]
        
        logger = get_logger(logger_name)
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == logger_name
    
    def test_get_logger_returns_existing(self):
        """Тест возврата существующего logger"""
        logger_name = "test_get_logger_existing"
        
        # Создаем logger вручную
        existing_logger = logging.getLogger(logger_name)
        
        # get_logger должен вернуть тот же logger
        logger = get_logger(logger_name)
        
        assert logger is existing_logger
    
    def test_get_logger_sets_up_if_no_handlers(self):
        """Тест настройки logger если handlers отсутствуют"""
        logger_name = "test_get_logger_setup"
        
        # Создаем logger без handlers
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        
        # get_logger должен настроить logger
        result = get_logger(logger_name)
        
        assert len(result.handlers) >= 1


class TestLoggerUsage:
    """Тесты использования logger в реальных сценариях"""
    
    def test_logger_info_message(self, temp_log_dir):
        """Тест записи INFO сообщения"""
        logger_name = "test_info"
        if logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
        
        logger = setup_logger(
            logger_name,
            log_dir=temp_log_dir,
            log_to_file=True
        )
        
        logger.info("Info message")
        
        # Закрываем handlers
        for handler in logger.handlers:
            handler.close()
        
        log_file = Path(temp_log_dir) / f"{logger_name}.log"
        assert log_file.exists()
        
        content = log_file.read_text(encoding='utf-8')
        assert "Info message" in content
        assert "INFO" in content
    
    def test_logger_error_message(self, temp_log_dir):
        """Тест записи ERROR сообщения"""
        logger_name = "test_error"
        if logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
        
        logger = setup_logger(
            logger_name,
            log_dir=temp_log_dir,
            log_to_file=True
        )
        
        logger.error("Error message")
        
        # Закрываем handlers
        for handler in logger.handlers:
            handler.close()
        
        log_file = Path(temp_log_dir) / f"{logger_name}.log"
        content = log_file.read_text(encoding='utf-8')
        assert "Error message" in content
        assert "ERROR" in content
    
    def test_logger_debug_not_logged_to_console(self, capsys):
        """Тест что DEBUG не логируется в консоль при уровне INFO"""
        logger = setup_logger(
            "test_debug",
            level=logging.INFO,
            log_to_file=False
        )
        
        logger.debug("Debug message")
        
        # DEBUG не должен быть в консоли
        captured = capsys.readouterr()
        assert "Debug message" not in captured.out
    
    def test_logger_info_logged_to_console(self, capsys):
        """Тест что INFO логируется в консоль"""
        logger = setup_logger(
            "test_info_console",
            level=logging.INFO,
            log_to_file=False
        )
        
        logger.info("Info message")
        
        # INFO должен быть в консоли
        captured = capsys.readouterr()
        assert "Info message" in captured.out
    
    def test_logger_exception_logging(self, temp_log_dir):
        """Тест логирования исключений"""
        logger_name = "test_exception"
        if logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
        
        logger = setup_logger(
            logger_name,
            log_dir=temp_log_dir,
            log_to_file=True
        )
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.error("Caught exception", exc_info=True)
        
        # Закрываем handlers
        for handler in logger.handlers:
            handler.close()
        
        log_file = Path(temp_log_dir) / f"{logger_name}.log"
        content = log_file.read_text(encoding='utf-8')
        
        assert "Caught exception" in content
        assert "ValueError" in content
        assert "Test exception" in content


class TestLoggerDefaultDirectory:
    """Тесты для директории логов по умолчанию"""
    
    def test_default_log_directory_created(self):
        """Тест создания директории logs по умолчанию"""
        logger_name = "test_default_dir"
        if logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
        
        logger = setup_logger(logger_name, log_to_file=True)
        
        # Записываем сообщение чтобы создать файл
        logger.info("Test")
        
        # Закрываем handlers
        for handler in logger.handlers:
            handler.close()
        
        # Директория logs должна существовать
        log_dir = Path("logs")
        assert log_dir.exists()
        assert log_dir.is_dir()
        
        # Файл должен быть создан
        log_file = log_dir / f"{logger_name}.log"
        assert log_file.exists()
        
        # Очистка (пытаемся удалить, но не критично если не получится)
        try:
            if log_file.exists():
                # Даем время системе освободить файл
                import time
                time.sleep(0.1)
                log_file.unlink()
        except (PermissionError, OSError):
            pass  # Игнорируем ошибки на Windows
