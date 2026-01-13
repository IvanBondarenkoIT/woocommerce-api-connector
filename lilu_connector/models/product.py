"""
Модель продукта LILU API.

Для Junior разработчиков:
Этот класс представляет продукт из LILU API.
Структура похожа на ClientModel, но содержит поля, специфичные для продуктов.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class ProductModel:
    """
    Модель продукта из LILU API.
    
    Attributes:
        id: Уникальный идентификатор продукта
        name: Название продукта
        sku: Артикул продукта
        price: Цена продукта
        description: Описание продукта
        category: Категория продукта
        stock_quantity: Количество на складе
        status: Статус продукта (active, inactive, out_of_stock)
        created_at: Дата создания
        updated_at: Дата последнего обновления
        metadata: Дополнительные данные
    """
    
    id: int
    name: str
    sku: Optional[str] = None
    price: float = 0.0
    description: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: int = 0
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductModel':
        """
        Создать объект ProductModel из словаря API.
        
        Args:
            data: Словарь с данными продукта из LILU API
        
        Returns:
            ProductModel: Объект продукта
        """
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            sku=data.get('sku'),
            price=float(data.get('price', 0.0)),
            description=data.get('description'),
            category=data.get('category'),
            stock_quantity=int(data.get('stock_quantity', 0)),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать объект ProductModel в словарь для API.
        
        Returns:
            Dict[str, Any]: Словарь с данными продукта для API
        """
        result = {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock_quantity': self.stock_quantity,
            'status': self.status,
        }
        
        if self.sku:
            result['sku'] = self.sku
        
        if self.description:
            result['description'] = self.description
        
        if self.category:
            result['category'] = self.category
        
        if self.metadata:
            result['metadata'] = self.metadata
        
        return result
    
    def __str__(self) -> str:
        """Строковое представление продукта"""
        return f"Product(id={self.id}, name='{self.name}', price={self.price})"
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return self.__str__()
    
    @property
    def is_in_stock(self) -> bool:
        """
        Проверить, есть ли продукт на складе.
        
        Returns:
            bool: True, если продукт есть на складе
        """
        return self.stock_quantity > 0 and self.status == 'active'
    
    @property
    def is_available(self) -> bool:
        """
        Проверить, доступен ли продукт для заказа.
        
        Returns:
            bool: True, если продукт доступен
        """
        return self.status == 'active' and self.is_in_stock
