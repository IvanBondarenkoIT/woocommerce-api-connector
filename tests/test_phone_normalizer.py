"""
Тесты для нормализации телефонных номеров.
"""

import pytest
from woocommerce_connector.utils.phone_normalizer import (
    PhoneNormalizer,
    normalize_phone,
    is_valid_phone
)


class TestPhoneNormalizer:
    """Тесты для класса PhoneNormalizer."""
    
    def test_normalize_russian_format_8(self):
        """Тест нормализации российского формата с 8."""
        normalizer = PhoneNormalizer(default_country='RU')
        assert normalizer.normalize("8 (999) 123-45-67") == "+79991234567"
        assert normalizer.normalize("8-999-123-45-67") == "+79991234567"
        assert normalizer.normalize("8 999 123 45 67") == "+79991234567"
    
    def test_normalize_international_format(self):
        """Тест нормализации международного формата."""
        normalizer = PhoneNormalizer(default_country='RU')
        assert normalizer.normalize("+7 999 123 45 67") == "+79991234567"
        assert normalizer.normalize("+79991234567") == "+79991234567"
    
    def test_normalize_without_code(self):
        """Тест нормализации без кода страны."""
        normalizer = PhoneNormalizer(default_country='RU')
        assert normalizer.normalize("9991234567") == "+79991234567"
    
    def test_normalize_with_7_prefix(self):
        """Тест нормализации с префиксом 7."""
        normalizer = PhoneNormalizer(default_country='RU')
        assert normalizer.normalize("79991234567") == "+79991234567"
    
    def test_normalize_empty_string(self):
        """Тест нормализации пустой строки."""
        normalizer = PhoneNormalizer(default_country='RU')
        assert normalizer.normalize("") is None
        assert normalizer.normalize(None) is None
    
    def test_normalize_invalid_format(self):
        """Тест нормализации невалидного формата."""
        normalizer = PhoneNormalizer(default_country='RU')
        # Слишком короткий номер
        assert normalizer.normalize("123") is None or len(normalizer.normalize("123") or "") < 10
    
    def test_is_valid(self):
        """Тест проверки валидности телефона."""
        normalizer = PhoneNormalizer(default_country='RU')
        assert normalizer.is_valid("+79991234567") is True
        assert normalizer.is_valid("8 (999) 123-45-67") is True
        assert normalizer.is_valid("") is False
        assert normalizer.is_valid(None) is False
        assert normalizer.is_valid("123") is False
    
    def test_different_countries(self):
        """Тест нормализации для разных стран."""
        # Украина
        normalizer_ua = PhoneNormalizer(default_country='UA')
        assert normalizer_ua.normalize("380991234567") == "+380991234567"
        
        # Грузия
        normalizer_ge = PhoneNormalizer(default_country='GE')
        assert normalizer_ge.normalize("995123456789") == "+995123456789"


class TestNormalizePhoneFunction:
    """Тесты для функции normalize_phone."""
    
    def test_function_normalize(self):
        """Тест функции normalize_phone."""
        assert normalize_phone("8 (999) 123-45-67") == "+79991234567"
        assert normalize_phone("+7 999 123 45 67") == "+79991234567"
        assert normalize_phone("9991234567") == "+79991234567"
    
    def test_function_is_valid(self):
        """Тест функции is_valid_phone."""
        assert is_valid_phone("+79991234567") is True
        assert is_valid_phone("8 (999) 123-45-67") is True
        assert is_valid_phone("") is False
