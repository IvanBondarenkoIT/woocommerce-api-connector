"""
Тесты для обработчика заказов.
"""

import pytest
from woocommerce_connector.services.order_processor import OrderProcessor, CustomerData
from woocommerce_connector.models.order import Order


class TestOrderProcessor:
    """Тесты для класса OrderProcessor."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.processor = OrderProcessor(default_country='RU')
    
    def test_extract_customer_data_with_phone(self):
        """Тест извлечения данных клиента с телефоном."""
        order_data = {
            'id': 12345,
            'status': 'completed',
            'total': '1000.00',
            'date_created': '2026-01-27T10:00:00',
            'billing': {
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'phone': '8 (999) 123-45-67',
                'email': 'ivan@example.com'
            }
        }
        order = Order.from_dict(order_data)
        
        customer_data = self.processor.extract_customer_data(order)
        
        assert customer_data is not None
        assert customer_data.phone == "+79991234567"
        assert customer_data.name == "Иван Иванов"
        assert customer_data.email == "ivan@example.com"
        assert customer_data.order_id == 12345
    
    def test_extract_customer_data_without_phone(self):
        """Тест извлечения данных без телефона."""
        order_data = {
            'id': 12346,
            'status': 'completed',
            'total': '1000.00',
            'billing': {
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'email': 'ivan@example.com'
            }
        }
        order = Order.from_dict(order_data)
        
        customer_data = self.processor.extract_customer_data(order)
        
        assert customer_data is None
    
    def test_extract_customer_data_name_from_phone(self):
        """Тест использования телефона как имени, если имя отсутствует."""
        order_data = {
            'id': 12347,
            'status': 'completed',
            'total': '1000.00',
            'billing': {
                'phone': '+79991234567'
            }
        }
        order = Order.from_dict(order_data)
        
        customer_data = self.processor.extract_customer_data(order)
        
        assert customer_data is not None
        assert customer_data.name == "+79991234567"  # Используется телефон как имя
    
    def test_determine_tags_default(self):
        """Тест определения тегов по умолчанию."""
        order_data = {
            'id': 12348,
            'status': 'pending',
            'total': '500.00'
        }
        order = Order.from_dict(order_data)
        
        tags = self.processor.determine_tags(order, default_tag="api woo")
        
        assert "api woo" in tags
        assert len(tags) == 1
    
    def test_determine_tags_with_rules(self):
        """Тест определения тегов с правилами."""
        order_data = {
            'id': 12349,
            'status': 'completed',
            'total': '15000.00'  # Больше 10000
        }
        order = Order.from_dict(order_data)
        
        rules = [
            {
                'tag': 'vip',
                'condition': {
                    'field': 'total',
                    'operator': '>',
                    'value': 10000
                }
            },
            {
                'tag': 'completed',
                'condition': {
                    'field': 'status',
                    'operator': '==',
                    'value': 'completed'
                }
            }
        ]
        
        tags = self.processor.determine_tags(
            order,
            default_tag="api woo",
            additional_rules=rules
        )
        
        assert "api woo" in tags
        assert "vip" in tags
        assert "completed" in tags
        assert len(tags) == 3
    
    def test_determine_tags_rule_not_met(self):
        """Тест когда правило не выполняется."""
        order_data = {
            'id': 12350,
            'status': 'pending',
            'total': '500.00'  # Меньше 10000
        }
        order = Order.from_dict(order_data)
        
        rules = [
            {
                'tag': 'vip',
                'condition': {
                    'field': 'total',
                    'operator': '>',
                    'value': 10000
                }
            }
        ]
        
        tags = self.processor.determine_tags(
            order,
            default_tag="api woo",
            additional_rules=rules
        )
        
        assert "api woo" in tags
        assert "vip" not in tags
        assert len(tags) == 1
