"""
Тесты для моделей данных (Product, Category, Order, Customer).

Эти тесты проверяют корректность работы с моделями данных:
- Создание из словарей API
- Преобразование в словари для API
- Работа со свойствами и методами
"""

import pytest
from woocommerce_connector.models import Product, Category, Order, Customer


class TestCategory:
    """Тесты для модели Category"""
    
    def test_category_from_dict(self):
        """Тест создания Category из словаря API"""
        data = {
            'id': 1,
            'name': 'Coffee',
            'slug': 'coffee',
            'parent': 0,
            'description': 'Coffee category',
            'count': 10
        }
        
        category = Category.from_dict(data)
        
        assert category.id == 1
        assert category.name == 'Coffee'
        assert category.slug == 'coffee'
        assert category.parent == 0
        assert category.description == 'Coffee category'
        assert category.count == 10
    
    def test_category_from_dict_minimal(self):
        """Тест создания Category с минимальными данными"""
        data = {
            'id': 1,
            'name': 'Coffee',
            'slug': 'coffee'
        }
        
        category = Category.from_dict(data)
        
        assert category.id == 1
        assert category.name == 'Coffee'
        assert category.slug == 'coffee'
        assert category.parent is None
        assert category.description is None
        assert category.count is None
    
    def test_category_to_dict(self):
        """Тест преобразования Category в словарь"""
        category = Category(
            id=1,
            name='Coffee',
            slug='coffee',
            parent=0,
            description='Coffee category',
            count=10
        )
        
        data = category.to_dict()
        
        assert data['id'] == 1
        assert data['name'] == 'Coffee'
        assert data['slug'] == 'coffee'
        assert data['parent'] == 0
        assert data['description'] == 'Coffee category'
        assert data['count'] == 10
    
    def test_category_to_dict_optional_fields(self):
        """Тест преобразования Category без опциональных полей"""
        category = Category(id=1, name='Coffee', slug='coffee')
        
        data = category.to_dict()
        
        assert 'id' in data
        assert 'name' in data
        assert 'slug' in data
        # Опциональные поля не должны быть в словаре, если None
        assert 'parent' not in data or data['parent'] is None
    
    def test_category_str(self):
        """Тест строкового представления Category"""
        category = Category(id=1, name='Coffee', slug='coffee')
        
        assert 'Category' in str(category)
        assert '1' in str(category)
        assert 'Coffee' in str(category)


class TestProduct:
    """Тесты для модели Product"""
    
    @pytest.fixture
    def sample_product_data(self):
        """Фикстура с примерными данными товара"""
        return {
            'id': 1,
            'name': 'Test Coffee',
            'slug': 'test-coffee',
            'type': 'simple',
            'status': 'publish',
            'featured': False,
            'description': 'Test description',
            'short_description': 'Short desc',
            'sku': 'SKU001',
            'price': '29.99',
            'regular_price': '39.99',
            'sale_price': '29.99',
            'on_sale': True,
            'stock_status': 'instock',
            'stock_quantity': 10,
            'manage_stock': True,
            'categories': [
                {'id': 1, 'name': 'Coffee', 'slug': 'coffee'}
            ]
        }
    
    def test_product_from_dict(self, sample_product_data):
        """Тест создания Product из словаря API"""
        product = Product.from_dict(sample_product_data)
        
        assert product.id == 1
        assert product.name == 'Test Coffee'
        assert product.price == '29.99'
        assert product.regular_price == '39.99'
        assert product.sale_price == '29.99'
        assert product.on_sale == True
        assert product.stock_status == 'instock'
        assert product.stock_quantity == 10
        assert len(product.categories) == 1
        assert product.categories[0].name == 'Coffee'
    
    def test_product_from_dict_minimal(self):
        """Тест создания Product с минимальными данными"""
        data = {
            'id': 1,
            'name': 'Product',
            'slug': 'product',
            'price': '10.00',
            'regular_price': '10.00'
        }
        
        product = Product.from_dict(data)
        
        assert product.id == 1
        assert product.name == 'Product'
        assert product.price == '10.00'
        assert product.categories == []
    
    def test_product_to_dict(self, sample_product_data):
        """Тест преобразования Product в словарь"""
        product = Product.from_dict(sample_product_data)
        data = product.to_dict()
        
        assert data['id'] == 1
        assert data['name'] == 'Test Coffee'
        assert data['price'] == '29.99'
        assert isinstance(data['categories'], list)
        assert len(data['categories']) == 1
    
    def test_product_is_in_stock(self):
        """Тест свойства is_in_stock"""
        product_instock = Product(
            id=1, name='Product', slug='product',
            price='10', regular_price='10',
            stock_status='instock'
        )
        product_outofstock = Product(
            id=2, name='Product', slug='product',
            price='10', regular_price='10',
            stock_status='outofstock'
        )
        
        assert product_instock.is_in_stock == True
        assert product_outofstock.is_in_stock == False
    
    def test_product_has_discount(self):
        """Тест свойства has_discount"""
        product_with_discount = Product(
            id=1, name='Product', slug='product',
            price='75', regular_price='100',
            sale_price='75', on_sale=True
        )
        product_no_discount = Product(
            id=2, name='Product', slug='product',
            price='100', regular_price='100',
            sale_price=None, on_sale=False
        )
        
        assert product_with_discount.has_discount == True
        assert product_no_discount.has_discount == False
    
    def test_product_discount_percentage(self):
        """Тест вычисления процента скидки"""
        product = Product(
            id=1, name='Product', slug='product',
            price='75', regular_price='100',
            sale_price='75', on_sale=True
        )
        
        discount = product.discount_percentage
        
        assert discount == 25.0
    
    def test_product_discount_percentage_no_discount(self):
        """Тест процента скидки для товара без скидки"""
        product = Product(
            id=1, name='Product', slug='product',
            price='100', regular_price='100',
            sale_price=None, on_sale=False
        )
        
        assert product.discount_percentage is None
    
    def test_product_discount_percentage_invalid_price(self):
        """Тест процента скидки с невалидной ценой"""
        product = Product(
            id=1, name='Product', slug='product',
            price='invalid', regular_price='invalid',
            sale_price='invalid', on_sale=True
        )
        
        # Должен вернуть None при невалидных ценах
        assert product.discount_percentage is None


class TestOrder:
    """Тесты для модели Order (для будущих фич)"""
    
    def test_order_from_dict(self):
        """Тест создания Order из словаря API"""
        data = {
            'id': 123,
            'status': 'completed',
            'currency': 'GEL',
            'total': '99.99',
            'customer_id': 1,
            'billing': {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com'
            },
            'line_items': [
                {'id': 1, 'name': 'Product 1', 'quantity': 2}
            ]
        }
        
        order = Order.from_dict(data)
        
        assert order.id == 123
        assert order.status == 'completed'
        assert order.total == '99.99'
        assert order.customer_id == 1
        assert order.billing['email'] == 'john@example.com'
        assert len(order.line_items) == 1
    
    def test_order_customer_email(self):
        """Тест получения email клиента из заказа"""
        order = Order(
            id=1, status='pending', currency='GEL', total='100',
            billing={'email': 'test@example.com'}
        )
        
        assert order.customer_email == 'test@example.com'
    
    def test_order_customer_name(self):
        """Тест получения имени клиента из заказа"""
        order = Order(
            id=1, status='pending', currency='GEL', total='100',
            billing={
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        
        assert order.customer_name == 'John Doe'
    
    def test_order_item_count(self):
        """Тест подсчета товаров в заказе"""
        order = Order(
            id=1, status='pending', currency='GEL', total='100',
            line_items=[
                {'id': 1, 'name': 'Product 1'},
                {'id': 2, 'name': 'Product 2'}
            ]
        )
        
        assert order.item_count == 2


class TestCustomer:
    """Тесты для модели Customer (для будущих фич)"""
    
    def test_customer_from_dict(self):
        """Тест создания Customer из словаря API"""
        data = {
            'id': 1,
            'email': 'customer@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'customer',
            'billing': {
                'phone': '+1234567890',
                'address_1': '123 Main St',
                'city': 'New York'
            }
        }
        
        customer = Customer.from_dict(data)
        
        assert customer.id == 1
        assert customer.email == 'customer@example.com'
        assert customer.first_name == 'John'
        assert customer.last_name == 'Doe'
        assert customer.phone == '+1234567890'
    
    def test_customer_full_name(self):
        """Тест получения полного имени клиента"""
        customer = Customer(
            id=1, email='test@example.com',
            first_name='John', last_name='Doe'
        )
        
        assert customer.full_name == 'John Doe'
    
    def test_customer_full_name_no_last_name(self):
        """Тест полного имени без фамилии"""
        customer = Customer(
            id=1, email='test@example.com',
            first_name='John', last_name=''
        )
        
        assert customer.full_name == 'John'
    
    def test_customer_full_name_fallback_to_email(self):
        """Тест полного имени с fallback на email"""
        customer = Customer(
            id=1, email='test@example.com',
            first_name='', last_name=''
        )
        
        assert customer.full_name == 'test@example.com'
