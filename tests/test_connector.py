"""
Tests for WooCommerceConnector class
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from woocommerce_connector import WooCommerceConnector


class TestWooCommerceConnector:
    """Test cases for WooCommerceConnector"""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables"""
        return {
            'WC_URL': 'https://test-store.com',
            'WC_CONSUMER_KEY': 'ck_test_key',
            'WC_CONSUMER_SECRET': 'cs_test_secret',
            'WC_API_VERSION': 'wc/v3'
        }
    
    @pytest.fixture
    def connector(self, mock_env_vars):
        """Create connector instance with mocked environment"""
        with patch.dict(os.environ, mock_env_vars):
            with patch('woocommerce_connector.API') as mock_api:
                mock_api_instance = MagicMock()
                mock_api.return_value = mock_api_instance
                connector = WooCommerceConnector()
                connector.wcapi = mock_api_instance
                return connector
    
    def test_init_success(self, mock_env_vars):
        """Test successful connector initialization"""
        with patch.dict(os.environ, mock_env_vars):
            with patch('woocommerce_connector.API') as mock_api:
                mock_api_instance = MagicMock()
                mock_api.return_value = mock_api_instance
                connector = WooCommerceConnector()
                
                assert connector.url == 'https://test-store.com'
                assert connector.consumer_key == 'ck_test_key'
                assert connector.consumer_secret == 'cs_test_secret'
                assert connector.api_version == 'wc/v3'
    
    def test_init_missing_env_vars(self):
        """Test initialization with missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables"):
                WooCommerceConnector()
    
    def test_get_products_success(self, connector):
        """Test successful product retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 1, 'name': 'Test Product', 'price': '10.00'}
        ]
        connector.wcapi.get.return_value = mock_response
        
        response = connector.get_products(per_page=10, page=1)
        
        assert response.status_code == 200
        connector.wcapi.get.assert_called_once()
    
    def test_get_products_error(self, connector):
        """Test product retrieval with error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        connector.wcapi.get.return_value = mock_response
        
        response = connector.get_products()
        
        assert response.status_code == 404
    
    def test_get_products_exception(self, connector):
        """Test product retrieval with exception"""
        connector.wcapi.get.side_effect = Exception("Connection error")
        
        response = connector.get_products()
        
        assert response is None
    
    def test_get_all_products_single_page(self, connector):
        """Test getting all products from single page"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 1, 'name': 'Product 1'},
            {'id': 2, 'name': 'Product 2'}
        ]
        connector.wcapi.get.return_value = mock_response
        
        products = connector.get_all_products(per_page=100)
        
        assert len(products) == 2
        assert products[0]['id'] == 1
    
    def test_get_all_products_multiple_pages(self, connector):
        """Test getting all products from multiple pages"""
        # First page
        mock_response_1 = Mock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = [
            {'id': i, 'name': f'Product {i}'} for i in range(1, 101)
        ]
        
        # Second page (last)
        mock_response_2 = Mock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = [
            {'id': 101, 'name': 'Product 101'}
        ]
        
        connector.wcapi.get.side_effect = [mock_response_1, mock_response_2]
        
        products = connector.get_all_products(per_page=100)
        
        assert len(products) == 101
        assert products[0]['id'] == 1
        assert products[100]['id'] == 101
    
    def test_get_all_products_empty(self, connector):
        """Test getting all products when store is empty"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        connector.wcapi.get.return_value = mock_response
        
        products = connector.get_all_products()
        
        assert len(products) == 0
    
    def test_get_product_fields_by_id(self, connector):
        """Test getting product fields by ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 123,
            'name': 'Test Product',
            'price': '99.99'
        }
        connector.wcapi.get.return_value = mock_response
        
        product = connector.get_product_fields(product_id=123)
        
        assert product['id'] == 123
        assert product['name'] == 'Test Product'
    
    def test_get_product_fields_first_product(self, connector):
        """Test getting first product fields"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 1, 'name': 'First Product'}
        ]
        connector.wcapi.get.return_value = mock_response
        
        product = connector.get_product_fields()
        
        assert product['id'] == 1
        assert product['name'] == 'First Product'
    
    def test_display_products_summary(self, connector, capsys):
        """Test displaying products summary"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 1,
                'name': 'Product 1',
                'sku': 'SKU1',
                'price': '10.00',
                'status': 'publish',
                'stock_status': 'instock',
                'categories': [{'name': 'Category 1'}]
            }
        ]
        connector.wcapi.get.return_value = mock_response
        
        connector.display_products_summary(limit=1)
        
        captured = capsys.readouterr()
        assert 'Product 1' in captured.out
        assert 'SKU1' in captured.out
    
    def test_display_products_summary_no_products(self, connector, capsys):
        """Test displaying summary when no products"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        connector.wcapi.get.return_value = mock_response
        
        connector.display_products_summary()
        
        captured = capsys.readouterr()
        assert 'No products found' in captured.out
    
    def test_check_api_version(self, connector):
        """Test API version checking"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        connector.wcapi.get.return_value = mock_response
        
        version = connector.check_api_version()
        
        # Should return a working version or None
        assert version is None or isinstance(version, str)



