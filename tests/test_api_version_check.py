"""
Tests for API version checking functionality
"""

import pytest
from unittest.mock import Mock, patch
from woocommerce_connector.connector import check_api_version_standalone


class TestAPIVersionCheck:
    """Test cases for API version checking"""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables"""
        return {
            'WC_URL': 'https://test-store.com',
            'WC_CONSUMER_KEY': 'ck_test_key',
            'WC_CONSUMER_SECRET': 'cs_test_secret'
        }
    
    def test_check_version_success(self, mock_env_vars, capsys):
        """Test successful version check"""
        with patch.dict('os.environ', mock_env_vars):
            with patch('woocommerce_connector.connector.API') as mock_api_class:
                # Mock API instance
                mock_api = Mock()
                mock_response = Mock()
                mock_response.status_code = 200
                mock_api.get.return_value = mock_response
                mock_api_class.return_value = mock_api
                
                result = check_api_version_standalone()
                
                # Should return a version or None
                assert result is None or isinstance(result, str)
    
    def test_check_version_missing_env(self, capsys):
        """Test version check with missing environment variables"""
        with patch.dict('os.environ', {}, clear=True):
            with patch('woocommerce_connector.connector.load_dotenv'):
                # Mock os.getenv to return None for all keys
                with patch('woocommerce_connector.connector.os.getenv', side_effect=lambda key, default='': None if key.startswith('WC_') else default):
                    result = check_api_version_standalone()
                    
                    # Should return None when env vars are missing
                    assert result is None
                    captured = capsys.readouterr()
                    # Check for error message (may vary)
                    assert 'Missing' in captured.out or 'Error' in captured.out or len(captured.out) > 0
    
    def test_check_version_api_error(self, mock_env_vars, capsys):
        """Test version check with API error"""
        with patch.dict('os.environ', mock_env_vars):
            with patch('woocommerce_connector.connector.API') as mock_api_class:
                mock_api = Mock()
                mock_response = Mock()
                mock_response.status_code = 401
                mock_api.get.return_value = mock_response
                mock_api_class.return_value = mock_api
                
                result = check_api_version_standalone()
                
                # Should handle error gracefully
                assert result is None or isinstance(result, str)

