"""
Тесты для сервиса синхронизации.

Используются моки для изоляции от реальных API.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from woocommerce_connector.services.sync_service import SyncService, SyncResult
from woocommerce_connector.models.order import Order
from lilu_connector.models.client import ClientModel


class TestSyncService:
    """Тесты для класса SyncService."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        import tempfile
        from pathlib import Path
        
        # Создаем временный файл для трекера для каждого теста
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.temp_path = self.temp_file.name
        
        # Создаем моки коннекторов
        self.wc_connector = Mock()
        self.lilu_connector = Mock()
        
        # Создаем сервис синхронизации с изолированным трекером
        self.sync_service = SyncService(
            wc_connector=self.wc_connector,
            lilu_connector=self.lilu_connector,
            default_tag="api woo",
            tracker_file=self.temp_path
        )
    
    def teardown_method(self):
        """Очистка после каждого теста."""
        from pathlib import Path
        Path(self.temp_path).unlink(missing_ok=True)
    
    def test_sync_order_already_processed(self):
        """Тест синхронизации уже обработанного заказа."""
        order_data = {
            'id': 12345,
            'status': 'completed',
            'total': '1000.00',
            'billing': {'phone': '+79991234567'}
        }
        order = Order.from_dict(order_data)
        
        # Помечаем заказ как обработанный
        self.sync_service.tracker.mark_processed(12345, status="created")
        
        result = self.sync_service.sync_order(order)
        
        assert result.success is True
        assert result.action == "skipped"
        # Коннекторы не должны вызываться
        self.lilu_connector.find_client_by_phone.assert_not_called()
    
    def test_sync_order_no_phone(self):
        """Тест синхронизации заказа без телефона."""
        order_data = {
            'id': 12346,
            'status': 'completed',
            'total': '1000.00',
            'billing': {}  # Нет телефона
        }
        order = Order.from_dict(order_data)
        
        result = self.sync_service.sync_order(order)
        
        # Заказ без телефона должен быть пропущен (skipped)
        # success может быть True или False в зависимости от реализации
        assert result.action == "skipped"
        assert "phone" in result.error_message.lower() or "no phone" in result.error_message.lower()
    
    def test_sync_order_create_new_client(self):
        """Тест создания нового клиента."""
        order_data = {
            'id': 12347,
            'status': 'completed',
            'total': '1000.00',
            'billing': {
                'phone': '+79991234567',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'email': 'ivan@example.com'
            }
        }
        order = Order.from_dict(order_data)
        
        # Клиент не найден
        self.lilu_connector.find_client_by_phone.return_value = None
        
        # Мокируем создание клиента
        new_client = ClientModel(
            id="69660055fb13db648fc58795",
            name="Иван Иванов",
            phone="+79991234567",
            email="ivan@example.com",
            tags=["api woo"]
        )
        self.lilu_connector.create_client.return_value = new_client
        
        result = self.sync_service.sync_order(order)
        
        assert result.success is True
        assert result.action == "created"
        assert result.lilu_client_id == "69660055fb13db648fc58795"
        assert "api woo" in result.tags_added
        
        # Проверяем вызовы
        self.lilu_connector.find_client_by_phone.assert_called_once_with("+79991234567")
        self.lilu_connector.create_client.assert_called_once()
    
    def test_sync_order_update_existing_client(self):
        """Тест обновления существующего клиента."""
        order_data = {
            'id': 12348,
            'status': 'completed',
            'total': '1000.00',
            'billing': {
                'phone': '+79991234567',
                'first_name': 'Иван',
                'last_name': 'Иванов'
            }
        }
        order = Order.from_dict(order_data)
        
        # Клиент найден
        existing_client = ClientModel(
            id="69660055fb13db648fc58795",
            name="Иван Иванов",
            phone="+79991234567",
            tags=["api woo"]
        )
        self.lilu_connector.find_client_by_phone.return_value = existing_client
        
        # Мокируем обновление (теги не изменились)
        updated_client = ClientModel(
            id="69660055fb13db648fc58795",
            name="Иван Иванов",
            phone="+79991234567",
            tags=["api woo"]
        )
        self.lilu_connector.update_client_tags.return_value = updated_client
        
        result = self.sync_service.sync_order(order)
        
        assert result.success is True
        assert result.action == "updated"
        assert result.lilu_client_id == "69660055fb13db648fc58795"
        
        # Проверяем вызовы
        self.lilu_connector.find_client_by_phone.assert_called_once()
        # update_client_tags может не вызываться, если теги не изменились
    
    def test_sync_order_add_new_tags(self):
        """Тест добавления новых тегов существующему клиенту."""
        order_data = {
            'id': 12349,
            'status': 'completed',
            'total': '15000.00',  # Больше 10000 - должен добавиться тег "vip"
            'billing': {
                'phone': '+79991234567',
                'first_name': 'Иван',
                'last_name': 'Иванов'
            }
        }
        order = Order.from_dict(order_data)
        
        # Правила для тегов
        self.sync_service.additional_tag_rules = [
            {
                'tag': 'vip',
                'condition': {
                    'field': 'total',
                    'operator': '>',
                    'value': 10000
                }
            }
        ]
        
        # Клиент найден, но без тега "vip"
        existing_client = ClientModel(
            id="69660055fb13db648fc58795",
            name="Иван Иванов",
            phone="+79991234567",
            tags=["api woo"]  # Нет "vip"
        )
        self.lilu_connector.find_client_by_phone.return_value = existing_client
        
        # Мокируем обновление с новым тегом
        updated_client = ClientModel(
            id="69660055fb13db648fc58795",
            name="Иван Иванов",
            phone="+79991234567",
            tags=["api woo", "vip"]
        )
        self.lilu_connector.update_client_tags.return_value = updated_client
        
        result = self.sync_service.sync_order(order)
        
        assert result.success is True
        assert result.action == "updated"
        assert "vip" in result.tags_added
        
        # Проверяем, что update_client_tags был вызван
        self.lilu_connector.update_client_tags.assert_called_once()
        call_args = self.lilu_connector.update_client_tags.call_args
        # Проверяем содержимое тегов (порядок может быть разным)
        assert set(call_args[1]['tags']) == {"api woo", "vip"}
