"""
Модель категории товара WooCommerce.

Этот модуль содержит dataclass для представления категории товара.
Категория содержит информацию о категории из WooCommerce API.

Пример использования:
    >>> from woocommerce_connector.models import Category
    >>> category_data = {"id": 1, "name": "Coffee", "slug": "coffee"}
    >>> category = Category.from_dict(category_data)
    >>> print(category.name)
    Coffee
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    """
    Модель категории товара WooCommerce.
    
    Attributes:
        id: Уникальный идентификатор категории
        name: Название категории
        slug: URL-friendly идентификатор категории
        parent: ID родительской категории (если есть)
        description: Описание категории (опционально)
        count: Количество товаров в категории (опционально)
    """
    id: int
    name: str
    slug: str
    parent: Optional[int] = None
    description: Optional[str] = None
    count: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Category':
        """
        Создать объект Category из словаря API.
        
        Args:
            data: Словарь с данными категории из WooCommerce API
        
        Returns:
            Category: Объект категории
        
        Example:
            >>> data = {"id": 1, "name": "Coffee", "slug": "coffee"}
            >>> category = Category.from_dict(data)
        """
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            slug=data.get('slug', ''),
            parent=data.get('parent', None),
            description=data.get('description', None),
            count=data.get('count', None)
        )
    
    def to_dict(self) -> dict:
        """
        Преобразовать объект Category в словарь для API.
        
        Returns:
            dict: Словарь с данными категории
        
        Example:
            >>> category = Category(id=1, name="Coffee", slug="coffee")
            >>> data = category.to_dict()
        """
        result = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug
        }
        
        if self.parent is not None:
            result['parent'] = self.parent
        
        if self.description:
            result['description'] = self.description
        
        if self.count is not None:
            result['count'] = self.count
        
        return result
    
    def __str__(self) -> str:
        """Строковое представление категории"""
        return f"Category(id={self.id}, name='{self.name}')"
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return self.__str__()
