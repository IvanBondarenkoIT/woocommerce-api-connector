"""
Тесты загрузки заказов WooCommerce с учётом Imunify360.

- unit: mock API — проверка обработки ответов (в т.ч. Imunify360 в теле)
- integration: реальный запрос 1 заказа — skip если нет WC_HTTPS_PROXY/RAILWAY
  (на residential IP Imunify360 блокирует без proxy)
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from woocommerce_connector.connector import WooCommerceConnector
from woocommerce_connector.api.exceptions import APIResponseError


class TestOrdersImunifyUnit:
    """Unit-тесты с mock API."""

    @pytest.fixture
    def mock_env(self):
        return {
            "WC_URL": "https://test-store.com",
            "WC_CONSUMER_KEY": "ck_test",
            "WC_CONSUMER_SECRET": "cs_test",
            "WC_API_VERSION": "wc/v3",
        }

    @pytest.fixture
    def connector(self, mock_env):
        with patch.dict(os.environ, mock_env):
            with patch("woocommerce_connector.connector.API") as mock_api:
                with patch("woocommerce_connector.connector.patch_api_with_browser_headers"):
                    mock_api_instance = MagicMock()
                    mock_api.return_value = mock_api_instance
                    conn = WooCommerceConnector()
                    conn.wcapi = mock_api_instance
                    return conn

    def test_get_orders_success(self, connector):
        """Успешная загрузка заказов."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[{"id": 1, "total": "100"}]'
        mock_response.json.return_value = [{"id": 1, "total": "100"}]
        connector.wcapi.get.return_value = mock_response

        resp = connector.get_orders(per_page=10, page=1)
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["id"] == 1

    def test_get_orders_imunify_block_in_body(self, connector):
        """Блокировка Imunify360 в теле при status 200 — должно вызвать APIResponseError."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'Access denied by Imunify360 bot-protection'
        connector.wcapi.get.return_value = mock_response

        with pytest.raises(APIResponseError) as exc:
            connector.get_orders(per_page=10, page=1)
        assert "Imunify360" in str(exc.value)
        assert exc.value.status_code == 403

    def test_get_order_by_id_imunify_block(self, connector):
        """get_order_by_id — Imunify360 в теле."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'bot-protection Imunify360'
        connector.wcapi.get.return_value = mock_response

        with pytest.raises(APIResponseError):
            connector.get_order_by_id(1)


def _has_imunify_bypass() -> bool:
    """Есть ли обход Imunify360 (прокси или Railway)."""
    return bool(
        os.getenv("WC_HTTPS_PROXY")
        or os.getenv("HTTPS_PROXY")
        or os.getenv("RAILWAY_ENVIRONMENT")
    )


@pytest.mark.skipif(
    not _has_imunify_bypass(),
    reason="WC_HTTPS_PROXY/HTTPS_PROXY/RAILWAY нужны для real fetch (residential IP блокируется)",
)
class TestOrdersImunifyIntegration:
    """Integration: реальная загрузка 1 заказа (только при proxy/Railway)."""

    def test_fetch_one_order_real(self):
        """Загрузить один заказ с WooCommerce."""
        from woocommerce_connector.config import WooCommerceConfig

        try:
            config = WooCommerceConfig.from_env()
            config.validate()
        except Exception:
            pytest.skip("WC_* не настроены")
            return

        connector = WooCommerceConnector()
        response = connector.get_orders(per_page=1, page=1)
        assert response is not None
        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)
        # может быть пусто если нет заказов
        if orders:
            assert "id" in orders[0]
