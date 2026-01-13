"""
Модель заказа LILU API.

Для Junior разработчиков:
Этот класс представляет заказ из LILU API.
Заказ связывает клиента с продуктами и содержит информацию о доставке.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class OrderItem:
    """
    Элемент заказа (продукт в заказе).
    
    Attributes:
        product_id: ID продукта
        product_name: Название продукта
        quantity: Количество
        price: Цена за единицу
        total: Общая стоимость (quantity * price)
    """
    product_id: int
    product_name: str
    quantity: int
    price: float
    total: float = 0.0
    
    def __post_init__(self):
        """Вычислить общую стоимость после инициализации"""
        if self.total == 0.0:
            self.total = self.quantity * self.price
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderItem':
        """Создать OrderItem из словаря"""
        return cls(
            product_id=data.get('product_id', 0),
            product_name=data.get('product_name', ''),
            quantity=int(data.get('quantity', 1)),
            price=float(data.get('price', 0.0)),
            total=float(data.get('total', 0.0))
        )


@dataclass
class OrderModel:
    """
    Модель заказа из LILU API.
    
    Attributes:
        id: Уникальный идентификатор заказа
        client_id: ID клиента
        client_name: Имя клиента
        items: Список элементов заказа
        total_amount: Общая сумма заказа
        status: Статус заказа (pending, processing, completed, cancelled)
        shipping_address: Адрес доставки
        created_at: Дата создания
        updated_at: Дата последнего обновления
        metadata: Дополнительные данные
    """
    
    id: int
    client_id: int
    client_name: str
    items: List[OrderItem] = field(default_factory=list)
    total_amount: float = 0.0
    status: str = "pending"
    shipping_address: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderModel':
        """
        Создать объект OrderModel из словаря API.
        
        Args:
            data: Словарь с данными заказа из LILU API
        
        Returns:
            OrderModel: Объект заказа
        """
        # Преобразуем элементы заказа
        items = []
        if 'items' in data and isinstance(data['items'], list):
            items = [OrderItem.from_dict(item) for item in data['items']]
        
        return cls(
            id=data.get('id', 0),
            client_id=data.get('client_id', 0),
            client_name=data.get('client_name', ''),
            items=items,
            total_amount=float(data.get('total_amount', 0.0)),
            status=data.get('status', 'pending'),
            shipping_address=data.get('shipping_address'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать объект OrderModel в словарь для API.
        
        Returns:
            Dict[str, Any]: Словарь с данными заказа для API
        """
        result = {
            'id': self.id,
            'client_id': self.client_id,
            'client_name': self.client_name,
            'items': [item.__dict__ for item in self.items],
            'total_amount': self.total_amount,
            'status': self.status,
        }
        
        if self.shipping_address:
            result['shipping_address'] = self.shipping_address
        
        if self.metadata:
            result['metadata'] = self.metadata
        
        return result
    
    def __str__(self) -> str:
        """Строковое представление заказа"""
        return f"Order(id={self.id}, client='{self.client_name}', total={self.total_amount})"
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return self.__str__()
    
    @property
    def is_completed(self) -> bool:
        """Проверить, завершён ли заказ"""
        return self.status == 'completed'
    
    @property
    def is_cancelled(self) -> bool:
        """Проверить, отменён ли заказ"""
        return self.status == 'cancelled'
    
    @property
    def items_count(self) -> int:
        """Получить количество элементов в заказе"""
        return len(self.items)
