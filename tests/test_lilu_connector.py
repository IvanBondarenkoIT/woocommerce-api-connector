"""
Тесты для LILUConnector.

Используются моки для изоляции от реального LILU API.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from lilu_connector.api.exceptions import NotFoundError


class TestLILUConnectorDeleteClient:
    """Тесты для метода delete_client."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.mock_client = MagicMock()

    @patch('lilu_connector.connector.LILUClient')
    @patch('lilu_connector.connector.LILUSettings')
    def test_delete_client_success_204(self, mock_settings_cls, mock_client_cls):
        """Успешное удаление клиента (204 No Content)."""
        mock_client_cls.return_value = self.mock_client
        mock_response = Mock()
        mock_response.status_code = 204
        self.mock_client.delete.return_value = mock_response

        from lilu_connector.connector import LILUConnector
        connector = LILUConnector()

        result = connector.delete_client("69660055fb13db648fc58795")

        assert result is True
        self.mock_client.delete.assert_called_once()
        call_endpoint = self.mock_client.delete.call_args[0][0]
        assert "69660055fb13db648fc58795" in call_endpoint

    @patch('lilu_connector.connector.LILUClient')
    @patch('lilu_connector.connector.LILUSettings')
    def test_delete_client_success_200(self, mock_settings_cls, mock_client_cls):
        """Успешное удаление клиента (200 OK)."""
        mock_client_cls.return_value = self.mock_client
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_client.delete.return_value = mock_response

        from lilu_connector.connector import LILUConnector
        connector = LILUConnector()

        result = connector.delete_client("abc123")

        assert result is True

    @patch('lilu_connector.connector.LILUClient')
    @patch('lilu_connector.connector.LILUSettings')
    def test_delete_client_not_found_returns_true(self, mock_settings_cls, mock_client_cls):
        """Если клиент не найден (404), считаем что удалён — возвращаем True."""
        mock_client_cls.return_value = self.mock_client
        self.mock_client.delete.side_effect = NotFoundError("Resource", "123")

        from lilu_connector.connector import LILUConnector
        connector = LILUConnector()

        result = connector.delete_client("69660055fb13db648fc58795")

        assert result is True

    @patch('lilu_connector.connector.LILUClient')
    @patch('lilu_connector.connector.LILUSettings')
    def test_delete_client_empty_id_returns_false(self, mock_settings_cls, mock_client_cls):
        """Пустой client_id возвращает False, API не вызывается."""
        mock_client_cls.return_value = self.mock_client

        from lilu_connector.connector import LILUConnector
        connector = LILUConnector()

        assert connector.delete_client("") is False
        assert connector.delete_client("   ") is False
        assert connector.delete_client(None) is False
        self.mock_client.delete.assert_not_called()

    @patch('lilu_connector.connector.LILUClient')
    @patch('lilu_connector.connector.LILUSettings')
    def test_delete_client_other_status_returns_false(self, mock_settings_cls, mock_client_cls):
        """Статус отличный от 200/204 возвращает False."""
        mock_client_cls.return_value = self.mock_client
        mock_response = Mock()
        mock_response.status_code = 500
        self.mock_client.delete.return_value = mock_response

        from lilu_connector.connector import LILUConnector
        connector = LILUConnector()

        result = connector.delete_client("abc123")

        assert result is False
