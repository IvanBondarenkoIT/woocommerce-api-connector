"""
Модель заказа WooCommerce.

Этот модуль содержит dataclass для представления заказа из WooCommerce API.
Заказ содержит информацию о покупке: клиент, товары, суммы, статус и т.д.

Этот модуль подготовлен для будущей фичи работы с заказами.
Пока не используется, но структура готова для быстрого внедрения.

Пример использования (когда будет реализовано):
    >>> from woocommerce_connector.models import Order
    >>> order_data = {
    ...     "id": 123,
    ...     "status": "completed",
    ...     "total": "99.99",
    ...     "line_items": [...]
    ... }
    >>> order = Order.from_dict(order_data)
    >>> print(order.total)
    99.99
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Order:
    """
    Модель заказа WooCommerce.
    
    Содержит всю информацию о заказе: клиент, товары, оплата, доставка.
    Будет использоваться для анализа заказов и извлечения клиентов.
    
    Attributes:
        id: Уникальный идентификатор заказа
        status: Статус заказа (pending, processing, completed, cancelled и т.д.)
        currency: Валюта заказа
        date_created: Дата создания заказа
        date_modified: Дата последнего изменения
        discount_total: Общая сумма скидок
        discount_tax: Налог на скидки
        shipping_total: Стоимость доставки
        shipping_tax: Налог на доставку
        cart_tax: Налог на корзину
        total: Общая сумма заказа
        total_tax: Общий налог
        customer_id: ID клиента
        customer_note: Примечание от клиента
        billing: Данные для выставления счета (dict)
        shipping: Данные доставки (dict)
        payment_method: Способ оплаты
        payment_method_title: Название способа оплаты
        transaction_id: ID транзакции
        line_items: Список товаров в заказе
        tax_lines: Список налогов
        shipping_lines: Список доставок
        fee_lines: Список дополнительных сборов
        coupon_lines: Список использованных купонов
        refunds: Список возвратов
        meta_data: Дополнительные метаданные
    """
    # Основная информация
    id: int
    status: str = "pending"
    currency: str = "GEL"
    
    # Даты
    date_created: Optional[str] = None
    date_modified: Optional[str] = None
    
    # Суммы
    discount_total: str = "0"
    discount_tax: str = "0"
    shipping_total: str = "0"
    shipping_tax: str = "0"
    cart_tax: str = "0"
    total: str = "0"
    total_tax: str = "0"
    
    # Клиент
    customer_id: int = 0
    customer_note: str = ""
    
    # Адреса
    billing: Dict[str, Any] = field(default_factory=dict)
    shipping: Dict[str, Any] = field(default_factory=dict)
    
    # Оплата
    payment_method: str = ""
    payment_method_title: str = ""
    transaction_id: str = ""
    
    # Элементы заказа
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    tax_lines: List[Dict[str, Any]] = field(default_factory=list)
    shipping_lines: List[Dict[str, Any]] = field(default_factory=list)
    fee_lines: List[Dict[str, Any]] = field(default_factory=list)
    coupon_lines: List[Dict[str, Any]] = field(default_factory=list)
    refunds: List[Dict[str, Any]] = field(default_factory=list)
    meta_data: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """
        Создать объект Order из словаря API.
        
        Args:
            data: Словарь с данными заказа из WooCommerce API
        
        Returns:
            Order: Объект заказа
        """
        return cls(
            id=data.get('id', 0),
            status=data.get('status', 'pending'),
            currency=data.get('currency', 'GEL'),
            date_created=data.get('date_created'),
            date_modified=data.get('date_modified'),
            discount_total=data.get('discount_total', '0'),
            discount_tax=data.get('discount_tax', '0'),
            shipping_total=data.get('shipping_total', '0'),
            shipping_tax=data.get('shipping_tax', '0'),
            cart_tax=data.get('cart_tax', '0'),
            total=data.get('total', '0'),
            total_tax=data.get('total_tax', '0'),
            customer_id=data.get('customer_id', 0),
            customer_note=data.get('customer_note', ''),
            billing=data.get('billing', {}),
            shipping=data.get('shipping', {}),
            payment_method=data.get('payment_method', ''),
            payment_method_title=data.get('payment_method_title', ''),
            transaction_id=data.get('transaction_id', ''),
            line_items=data.get('line_items', []),
            tax_lines=data.get('tax_lines', []),
            shipping_lines=data.get('shipping_lines', []),
            fee_lines=data.get('fee_lines', []),
            coupon_lines=data.get('coupon_lines', []),
            refunds=data.get('refunds', []),
            meta_data=data.get('meta_data', []),
        )
    
    def to_dict(self) -> dict:
        """Преобразовать объект Order в словарь для API"""
        return {
            'id': self.id,
            'status': self.status,
            'currency': self.currency,
            'date_created': self.date_created,
            'date_modified': self.date_modified,
            'discount_total': self.discount_total,
            'discount_tax': self.discount_tax,
            'shipping_total': self.shipping_total,
            'shipping_tax': self.shipping_tax,
            'cart_tax': self.cart_tax,
            'total': self.total,
            'total_tax': self.total_tax,
            'customer_id': self.customer_id,
            'customer_note': self.customer_note,
            'billing': self.billing,
            'shipping': self.shipping,
            'payment_method': self.payment_method,
            'payment_method_title': self.payment_method_title,
            'transaction_id': self.transaction_id,
            'line_items': self.line_items,
            'tax_lines': self.tax_lines,
            'shipping_lines': self.shipping_lines,
            'fee_lines': self.fee_lines,
            'coupon_lines': self.coupon_lines,
            'refunds': self.refunds,
            'meta_data': self.meta_data,
        }
    
    def __str__(self) -> str:
        """Строковое представление заказа"""
        return f"Order(id={self.id}, status='{self.status}', total='{self.total}')"
    
    @property
    def customer_email(self) -> Optional[str]:
        """Получить email клиента из данных billing"""
        return self.billing.get('email') if self.billing else None
    
    @property
    def customer_name(self) -> str:
        """Получить имя клиента из данных billing"""
        if not self.billing:
            return ""
        first_name = self.billing.get('first_name', '')
        last_name = self.billing.get('last_name', '')
        return f"{first_name} {last_name}".strip()
    
    @property
    def item_count(self) -> int:
        """Получить количество товаров в заказе"""
        return len(self.line_items)
