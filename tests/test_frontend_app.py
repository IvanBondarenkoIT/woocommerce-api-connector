"""
Тесты для FastAPI веб-приложения (frontend).

Используются моки для изоляции от WooCommerce и LILU API.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

# Минимальные env для инициализации (startup не упадёт без .env)
os.environ.setdefault('LILU_API_TOKEN', 'test-token')
os.environ.setdefault('WOOCOMMERCE_URL', 'https://test.example.com')
os.environ.setdefault('WOOCOMMERCE_CONSUMER_KEY', 'ck_test')
os.environ.setdefault('WOOCOMMERCE_CONSUMER_SECRET', 'cs_test')


@pytest.fixture
def mock_sync_service():
    """Мок SyncService с трекером."""
    mock = MagicMock()
    mock.tracker.get_processed_order.return_value = None
    mock.tracker.unmark_processed = MagicMock()
    mock.get_statistics.return_value = {}
    return mock


@pytest.fixture
def mock_lilu_connector():
    """Мок LILUConnector."""
    mock = MagicMock()
    mock.delete_client.return_value = True
    return mock


@pytest.fixture
def mock_wc_connector():
    """Мок WooCommerceConnector."""
    return MagicMock()


@pytest.fixture
def client(mock_sync_service, mock_lilu_connector, mock_wc_connector):
    """FastAPI TestClient с замоканными коннекторами и сервисом."""
    from fastapi.testclient import TestClient

    with (
        patch('frontend.app.WooCommerceConnector', return_value=mock_wc_connector),
        patch('frontend.app.LILUConnector', return_value=mock_lilu_connector),
        patch('frontend.app.SyncService', return_value=mock_sync_service),
    ):
        from frontend.app import app
        with TestClient(app) as c:
            yield c


class TestUnsyncEndpoint:
    """Тесты для POST /api/orders/{order_id}/unsync."""

    def test_unsync_success_with_lilu_client_id(
        self, client, mock_sync_service, mock_lilu_connector
    ):
        """Успешная отмена синхронизации с удалением клиента из LILU."""
        mock_processed = MagicMock()
        mock_processed.lilu_client_id = "69660055fb13db648fc58795"

        mock_sync_service.tracker.get_processed_order.return_value = mock_processed
        mock_lilu_connector.delete_client.return_value = True

        response = client.post("/api/orders/12345/unsync")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "удалён" in data["message"].lower() or "удален" in data["message"].lower()
        mock_sync_service.tracker.get_processed_order.assert_called_once_with(12345)
        mock_lilu_connector.delete_client.assert_called_once_with("69660055fb13db648fc58795")
        mock_sync_service.tracker.unmark_processed.assert_called_once_with(12345)

    def test_unsync_success_without_lilu_client_id(
        self, client, mock_sync_service, mock_lilu_connector
    ):
        """Отмена синхронизации когда lilu_client_id пустой (только unmark)."""
        mock_processed = MagicMock()
        mock_processed.lilu_client_id = None

        mock_sync_service.tracker.get_processed_order.return_value = mock_processed

        response = client.post("/api/orders/12345/unsync")

        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_lilu_connector.delete_client.assert_not_called()
        mock_sync_service.tracker.unmark_processed.assert_called_once_with(12345)

    def test_unsync_order_not_processed(self, client, mock_sync_service):
        """Запрос unsync для несинхронизированного заказа — 400."""
        mock_sync_service.tracker.get_processed_order.return_value = None

        response = client.post("/api/orders/99999/unsync")

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        mock_sync_service.tracker.unmark_processed.assert_not_called()

    def test_unsync_lilu_delete_fails_returns_500(
        self, client, mock_sync_service, mock_lilu_connector
    ):
        """Если LILU delete выбрасывает ошибку — 500."""
        mock_processed = MagicMock()
        mock_processed.lilu_client_id = "abc123"
        mock_sync_service.tracker.get_processed_order.return_value = mock_processed
        mock_lilu_connector.delete_client.side_effect = Exception("Connection refused")

        response = client.post("/api/orders/12345/unsync")

        assert response.status_code == 500
        mock_sync_service.tracker.unmark_processed.assert_not_called()


class TestHealthEndpoint:
    """Тесты для GET /api/health."""

    def test_health_ok(self, client):
        """Эндпоинт здоровья возвращает 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "wc_connector" in data
        assert "lilu_connector" in data
        assert "sync_service" in data


class TestSyncStatusEndpoint:
    """Тесты для GET /api/sync/status."""

    def test_sync_status_returns_stats(self, client, mock_sync_service):
        """Эндпоинт статистики возвращает данные трекера."""
        mock_sync_service.get_statistics.return_value = {
            "total_processed": 10,
            "created": 5,
            "updated": 3,
            "skipped": 1,
            "errors": 1,
        }

        response = client.get("/api/sync/status")

        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 10
        assert data["created"] == 5
