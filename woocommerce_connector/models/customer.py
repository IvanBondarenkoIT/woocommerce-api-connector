"""
Модель клиента WooCommerce.

Этот модуль содержит dataclass для представления клиента из WooCommerce API.
Клиент содержит информацию о покупателе: контакты, адреса, статистику и т.д.

Этот модуль подготовлен для будущей фичи работы с клиентами.
Пока не используется, но структура готова для быстрого внедрения.

Пример использования (когда будет реализовано):
    >>> from woocommerce_connector.models import Customer
    >>> customer_data = {
    ...     "id": 1,
    ...     "email": "customer@example.com",
    ...     "first_name": "John",
    ...     "last_name": "Doe"
    ... }
    >>> customer = Customer.from_dict(customer_data)
    >>> print(customer.full_name)
    John Doe
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class Customer:
    """
    Модель клиента WooCommerce.
    
    Содержит информацию о клиенте: контакты, адреса, статистику покупок.
    Будет использоваться для анализа клиентской базы и синхронизации
    с внешними сервисами.
    
    Attributes:
        id: Уникальный идентификатор клиента
        email: Email адрес клиента
        username: Имя пользователя (если зарегистрирован)
        first_name: Имя
        last_name: Фамилия
        role: Роль пользователя (customer, administrator и т.д.)
        date_created: Дата регистрации
        date_modified: Дата последнего изменения
        billing: Данные для выставления счета
        shipping: Данные доставки
        is_paying_customer: Является ли платящим клиентом
        avatar_url: URL аватара
        meta_data: Дополнительные метаданные
    """
    # Основная информация
    id: int
    email: str = ""
    username: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    role: str = "customer"
    
    # Даты
    date_created: Optional[str] = None
    date_modified: Optional[str] = None
    
    # Адреса
    billing: Dict[str, Any] = field(default_factory=dict)
    shipping: Dict[str, Any] = field(default_factory=dict)
    
    # Статус
    is_paying_customer: bool = False
    avatar_url: str = ""
    meta_data: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        """
        Создать объект Customer из словаря API.
        
        Args:
            data: Словарь с данными клиента из WooCommerce API
        
        Returns:
            Customer: Объект клиента
        """
        return cls(
            id=data.get('id', 0),
            email=data.get('email', ''),
            username=data.get('username'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', 'customer'),
            date_created=data.get('date_created'),
            date_modified=data.get('date_modified'),
            billing=data.get('billing', {}),
            shipping=data.get('shipping', {}),
            is_paying_customer=data.get('is_paying_customer', False),
            avatar_url=data.get('avatar_url', ''),
            meta_data=data.get('meta_data', []),
        )
    
    def to_dict(self) -> dict:
        """Преобразовать объект Customer в словарь для API"""
        result = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'billing': self.billing,
            'shipping': self.shipping,
            'is_paying_customer': self.is_paying_customer,
            'avatar_url': self.avatar_url,
            'meta_data': self.meta_data,
        }
        
        if self.username:
            result['username'] = self.username
        if self.date_created:
            result['date_created'] = self.date_created
        if self.date_modified:
            result['date_modified'] = self.date_modified
        
        return result
    
    def __str__(self) -> str:
        """Строковое представление клиента"""
        return f"Customer(id={self.id}, email='{self.email}', name='{self.full_name}')"
    
    @property
    def full_name(self) -> str:
        """Получить полное имя клиента"""
        name_parts = [self.first_name, self.last_name]
        return " ".join(filter(None, name_parts)) or self.email
    
    @property
    def phone(self) -> Optional[str]:
        """Получить телефон клиента из данных billing"""
        return self.billing.get('phone') if self.billing else None
    
    @property
    def billing_address(self) -> str:
        """Получить полный адрес для выставления счета"""
        if not self.billing:
            return ""
        
        parts = [
            self.billing.get('address_1', ''),
            self.billing.get('address_2', ''),
            self.billing.get('city', ''),
            self.billing.get('state', ''),
            self.billing.get('postcode', ''),
            self.billing.get('country', ''),
        ]
        return ", ".join(filter(None, parts))
