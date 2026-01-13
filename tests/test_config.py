"""
Тесты для конфигурации WooCommerce Connector.

Эти тесты проверяют корректность работы с WooCommerceConfig:
- Загрузка из переменных окружения
- Валидация конфигурации
- Обработка ошибок
- Значения по умолчанию
"""

import pytest
import os
from unittest.mock import patch
from woocommerce_connector.config import WooCommerceConfig
from woocommerce_connector.api.exceptions import ConfigurationError


class TestWooCommerceConfig:
    """Тесты для класса WooCommerceConfig"""
    
    @pytest.fixture
    def valid_env_vars(self):
        """Фикстура с валидными переменными окружения"""
        return {
            'WC_URL': 'https://test-store.com',
            'WC_CONSUMER_KEY': 'ck_test_key_12345',
            'WC_CONSUMER_SECRET': 'cs_test_secret_67890',
            'WC_API_VERSION': 'wc/v3',
            'WC_TIMEOUT': '30'
        }
    
    def test_from_env_success(self, valid_env_vars):
        """Тест успешной загрузки конфигурации из переменных окружения"""
        with patch.dict(os.environ, valid_env_vars):
            config = WooCommerceConfig.from_env()
            
            assert config.url == 'https://test-store.com'
            assert config.consumer_key == 'ck_test_key_12345'
            assert config.consumer_secret == 'cs_test_secret_67890'
            assert config.api_version == 'wc/v3'
            assert config.timeout == 30
            assert config.query_string_auth == True
    
    def test_from_env_with_defaults(self):
        """Тест загрузки с значениями по умолчанию"""
        env_vars = {
            'WC_URL': 'https://store.com',
            'WC_CONSUMER_KEY': 'ck_key',
            'WC_CONSUMER_SECRET': 'cs_secret'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = WooCommerceConfig.from_env()
            
            # Проверяем значения по умолчанию
            assert config.api_version == 'wc/v3'  # default
            assert config.timeout == 30  # default
            assert config.query_string_auth == True  # default
    
    def test_from_env_removes_trailing_slash(self):
        """Тест удаления завершающего слеша из URL"""
        env_vars = {
            'WC_URL': 'https://store.com/',
            'WC_CONSUMER_KEY': 'ck_key',
            'WC_CONSUMER_SECRET': 'cs_secret'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = WooCommerceConfig.from_env()
            
            assert config.url == 'https://store.com'  # Без слеша
    
    def test_from_env_timeout_as_string(self):
        """Тест преобразования таймаута из строки в число"""
        env_vars = {
            'WC_URL': 'https://store.com',
            'WC_CONSUMER_KEY': 'ck_key',
            'WC_CONSUMER_SECRET': 'cs_secret',
            'WC_TIMEOUT': '60'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = WooCommerceConfig.from_env()
            
            assert config.timeout == 60
            assert isinstance(config.timeout, int)
    
    def test_from_env_invalid_timeout(self):
        """Тест обработки невалидного таймаута"""
        env_vars = {
            'WC_URL': 'https://store.com',
            'WC_CONSUMER_KEY': 'ck_key',
            'WC_CONSUMER_SECRET': 'cs_secret',
            'WC_TIMEOUT': 'invalid'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = WooCommerceConfig.from_env()
            
            # Должен использовать значение по умолчанию
            assert config.timeout == 30
    
    def test_validate_success(self, valid_env_vars):
        """Тест успешной валидации конфигурации"""
        with patch.dict(os.environ, valid_env_vars):
            config = WooCommerceConfig.from_env()
            
            # Не должно быть исключения
            config.validate()
    
    def test_validate_missing_url(self):
        """Тест валидации при отсутствии URL"""
        config = WooCommerceConfig(
            url='',
            consumer_key='ck_key',
            consumer_secret='cs_secret'
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert 'WC_URL is required' in str(exc_info.value)
    
    def test_validate_missing_consumer_key(self):
        """Тест валидации при отсутствии Consumer Key"""
        config = WooCommerceConfig(
            url='https://store.com',
            consumer_key='',
            consumer_secret='cs_secret'
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert 'WC_CONSUMER_KEY is required' in str(exc_info.value)
    
    def test_validate_missing_consumer_secret(self):
        """Тест валидации при отсутствии Consumer Secret"""
        config = WooCommerceConfig(
            url='https://store.com',
            consumer_key='ck_key',
            consumer_secret=''
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert 'WC_CONSUMER_SECRET is required' in str(exc_info.value)
    
    def test_validate_invalid_url_format(self):
        """Тест валидации невалидного формата URL"""
        config = WooCommerceConfig(
            url='invalid-url',  # Без http:// или https://
            consumer_key='ck_key',
            consumer_secret='cs_secret'
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert 'WC_URL must start with http:// or https://' in str(exc_info.value)
    
    def test_validate_invalid_consumer_key_format(self):
        """Тест валидации невалидного формата Consumer Key"""
        config = WooCommerceConfig(
            url='https://store.com',
            consumer_key='invalid_key',  # Должен начинаться с ck_
            consumer_secret='cs_secret'
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "WC_CONSUMER_KEY should start with 'ck_'" in str(exc_info.value)
    
    def test_validate_invalid_consumer_secret_format(self):
        """Тест валидации невалидного формата Consumer Secret"""
        config = WooCommerceConfig(
            url='https://store.com',
            consumer_key='ck_key',
            consumer_secret='invalid_secret'  # Должен начинаться с cs_
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        assert "WC_CONSUMER_SECRET should start with 'cs_'" in str(exc_info.value)
    
    def test_validate_multiple_errors(self):
        """Тест валидации с несколькими ошибками"""
        config = WooCommerceConfig(
            url='',
            consumer_key='',
            consumer_secret=''
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()
        
        error_message = str(exc_info.value)
        # Должны быть все три ошибки
        assert 'WC_URL is required' in error_message
        assert 'WC_CONSUMER_KEY is required' in error_message
        assert 'WC_CONSUMER_SECRET is required' in error_message
    
    def test_str_representation(self, valid_env_vars):
        """Тест строкового представления конфигурации"""
        with patch.dict(os.environ, valid_env_vars):
            config = WooCommerceConfig.from_env()
            
            str_repr = str(config)
            
            # Должен содержать URL и версию API, но НЕ секреты
            assert 'https://test-store.com' in str_repr
            assert 'wc/v3' in str_repr
            assert 'ck_test_key' not in str_repr  # Секреты не должны быть в строке
            assert 'cs_test_secret' not in str_repr
    
    def test_repr_representation(self, valid_env_vars):
        """Тест представления для отладки"""
        with patch.dict(os.environ, valid_env_vars):
            config = WooCommerceConfig.from_env()
            
            repr_str = repr(config)
            
            # Должен быть таким же как str
            assert repr_str == str(config)
