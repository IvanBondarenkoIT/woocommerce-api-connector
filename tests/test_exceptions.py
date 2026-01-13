"""
Тесты для кастомных исключений WooCommerce API.

Эти тесты проверяют корректность работы всех типов исключений:
- Создание исключений
- Сообщения об ошибках
- Наследование от базового класса
- Специфичные атрибуты
"""

import pytest
from woocommerce_connector.api.exceptions import (
    WooCommerceAPIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIResponseError,
    ConfigurationError,
    NetworkError,
)


class TestWooCommerceAPIError:
    """Тесты для базового исключения WooCommerceAPIError"""
    
    def test_base_exception_creation(self):
        """Тест создания базового исключения"""
        error = WooCommerceAPIError("Test error")
        
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_base_exception_inheritance(self):
        """Тест что все исключения наследуются от базового"""
        errors = [
            AuthenticationError(),
            NotFoundError("resource", "123"),
            RateLimitError(),
            APIResponseError(404, "Not found"),
            ConfigurationError(),
            NetworkError(),
        ]
        
        for error in errors:
            assert isinstance(error, WooCommerceAPIError)
            assert isinstance(error, Exception)


class TestAuthenticationError:
    """Тесты для AuthenticationError"""
    
    def test_authentication_error_default_message(self):
        """Тест создания с сообщением по умолчанию"""
        error = AuthenticationError()
        
        assert str(error) == "Authentication failed"
        assert error.message == "Authentication failed"
    
    def test_authentication_error_custom_message(self):
        """Тест создания с кастомным сообщением"""
        error = AuthenticationError("Invalid credentials")
        
        assert str(error) == "Invalid credentials"
        assert error.message == "Invalid credentials"
    
    def test_authentication_error_inheritance(self):
        """Тест наследования от WooCommerceAPIError"""
        error = AuthenticationError()
        
        assert isinstance(error, WooCommerceAPIError)
        assert isinstance(error, Exception)


class TestNotFoundError:
    """Тесты для NotFoundError"""
    
    def test_not_found_error_with_id(self):
        """Тест создания с ID ресурса"""
        error = NotFoundError("Product", "123")
        
        assert str(error) == "Product with ID 123 not found"
        assert error.message == "Product with ID 123 not found"
    
    def test_not_found_error_without_id(self):
        """Тест создания без ID ресурса"""
        error = NotFoundError("Product")
        
        assert str(error) == "Product not found"
        assert error.message == "Product not found"
    
    def test_not_found_error_inheritance(self):
        """Тест наследования от WooCommerceAPIError"""
        error = NotFoundError("Product", "123")
        
        assert isinstance(error, WooCommerceAPIError)


class TestRateLimitError:
    """Тесты для RateLimitError"""
    
    def test_rate_limit_error_default_message(self):
        """Тест создания с сообщением по умолчанию"""
        error = RateLimitError()
        
        assert str(error) == "Rate limit exceeded"
        assert error.message == "Rate limit exceeded"
    
    def test_rate_limit_error_custom_message(self):
        """Тест создания с кастомным сообщением"""
        error = RateLimitError("Too many requests. Please wait.")
        
        assert str(error) == "Too many requests. Please wait."
        assert error.message == "Too many requests. Please wait."


class TestAPIResponseError:
    """Тесты для APIResponseError"""
    
    def test_api_response_error_basic(self):
        """Тест создания базового APIResponseError"""
        error = APIResponseError(404, "Not found")
        
        assert error.status_code == 404
        assert error.message == "Not found"
        assert "404" in str(error)
        assert "Not found" in str(error)
    
    def test_api_response_error_with_response_text(self):
        """Тест создания с текстом ответа"""
        error = APIResponseError(500, "Internal error", "Server crashed")
        
        assert error.status_code == 500
        assert error.message == "Internal error"
        assert error.response_text == "Server crashed"
        assert "500" in str(error)
        assert "Internal error" in str(error)
        assert "Server crashed" in str(error)
    
    def test_api_response_error_inheritance(self):
        """Тест наследования от WooCommerceAPIError"""
        error = APIResponseError(404, "Not found")
        
        assert isinstance(error, WooCommerceAPIError)


class TestConfigurationError:
    """Тесты для ConfigurationError"""
    
    def test_configuration_error_default_message(self):
        """Тест создания с сообщением по умолчанию"""
        error = ConfigurationError()
        
        assert str(error) == "Configuration error"
        assert error.message == "Configuration error"
    
    def test_configuration_error_custom_message(self):
        """Тест создания с кастомным сообщением"""
        error = ConfigurationError("WC_URL is required")
        
        assert str(error) == "WC_URL is required"
        assert error.message == "WC_URL is required"
    
    def test_configuration_error_multiline_message(self):
        """Тест создания с многострочным сообщением"""
        error = ConfigurationError("Configuration errors:\n  - Error 1\n  - Error 2")
        
        assert "Error 1" in str(error)
        assert "Error 2" in str(error)


class TestNetworkError:
    """Тесты для NetworkError"""
    
    def test_network_error_default_message(self):
        """Тест создания с сообщением по умолчанию"""
        error = NetworkError()
        
        assert str(error) == "Network error"
        assert error.message == "Network error"
    
    def test_network_error_custom_message(self):
        """Тест создания с кастомным сообщением"""
        error = NetworkError("Connection timeout")
        
        assert str(error) == "Connection timeout"
        assert error.message == "Connection timeout"
    
    def test_network_error_inheritance(self):
        """Тест наследования от WooCommerceAPIError"""
        error = NetworkError()
        
        assert isinstance(error, WooCommerceAPIError)


class TestExceptionUsage:
    """Тесты использования исключений в реальных сценариях"""
    
    def test_catching_base_exception(self):
        """Тест перехвата всех API ошибок через базовый класс"""
        errors = [
            AuthenticationError(),
            NotFoundError("Product", "123"),
            RateLimitError(),
            APIResponseError(500, "Error"),
        ]
        
        for error in errors:
            try:
                raise error
            except WooCommerceAPIError as e:
                # Все исключения должны перехватываться
                assert isinstance(e, WooCommerceAPIError)
            except Exception:
                pytest.fail("Should be caught by WooCommerceAPIError")
    
    def test_specific_error_handling(self):
        """Тест обработки специфичных ошибок"""
        try:
            raise AuthenticationError("Invalid credentials")
        except AuthenticationError as e:
            assert str(e) == "Invalid credentials"
        except WooCommerceAPIError:
            pytest.fail("Should be caught by AuthenticationError first")
    
    def test_error_hierarchy(self):
        """Тест иерархии исключений"""
        error = APIResponseError(404, "Not found")
        
        # Должно перехватываться и базовым, и специфичным
        try:
            raise error
        except APIResponseError:
            pass  # OK
        
        try:
            raise error
        except WooCommerceAPIError:
            pass  # OK
        
        try:
            raise error
        except Exception:
            pass  # OK
