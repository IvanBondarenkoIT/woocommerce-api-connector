"""
Шаблон для создания новой модели данных.

Для Junior разработчиков:
Этот файл - шаблон для создания новой модели данных.
Скопируйте этот код, замените комментарии на реальные значения
и создайте новый файл в models/.

ИНСТРУКЦИЯ:
1. Скопируйте этот код
2. Создайте новый файл models/your_model.py
3. Замените все TODO комментарии на реальные значения
4. Добавьте импорт в models/__init__.py
5. Используйте модель в connector.py
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class YourModel:  # TODO: Замените YourModel на реальное имя модели
    """
    Модель элемента из LILU API.
    
    Для Junior: Опишите, что представляет эта модель.
    
    Attributes:
        id: Уникальный идентификатор
        name: Название элемента
        # TODO: Добавьте все поля, которые возвращает API
        created_at: Дата создания
        updated_at: Дата последнего обновления
        metadata: Дополнительные данные (опционально)
    
    Пример использования:
        >>> item_data = {
        ...     'id': 1,
        ...     'name': 'Item Name',
        ...     'description': 'Item Description'
        ... }
        >>> item = YourModel.from_dict(item_data)
        >>> print(item.name)
        Item Name
    """
    
    # Обязательные поля
    id: int
    name: str
    
    # Опциональные поля
    # TODO: Добавьте все поля из API
    description: Optional[str] = None
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'YourModel':
        """
        Создать объект YourModel из словаря API.
        
        Для Junior: Этот метод преобразует сырые данные из API
        в типизированный объект. Это безопаснее, чем работать со словарями.
        
        Args:
            data: Словарь с данными из LILU API
        
        Returns:
            YourModel: Объект модели
        
        Пример:
            >>> api_data = {
            ...     'id': 1,
            ...     'name': 'Item Name'
            ... }
            >>> item = YourModel.from_dict(api_data)
            >>> print(item.name)
            Item Name
        """
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            # TODO: Добавьте все поля из data
            description=data.get('description'),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать объект YourModel в словарь для API.
        
        Для Junior: Этот метод нужен, когда мы хотим отправить данные
        обратно в API (например, при создании или обновлении).
        
        Returns:
            Dict[str, Any]: Словарь с данными для API
        
        Пример:
            >>> item = YourModel(id=1, name='Item Name')
            >>> data = item.to_dict()
            >>> # Отправить data в API
        """
        result = {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            # TODO: Добавьте все обязательные поля
        }
        
        # Добавляем опциональные поля, если они есть
        if self.description:
            result['description'] = self.description
        
        if self.metadata:
            result['metadata'] = self.metadata
        
        return result
    
    def __str__(self) -> str:
        """
        Строковое представление элемента.
        
        Для Junior: Этот метод вызывается, когда мы используем print().
        """
        return f"YourModel(id={self.id}, name='{self.name}')"
    
    def __repr__(self) -> str:
        """
        Представление для отладки.
        
        Для Junior: Этот метод вызывается в отладчике.
        """
        return self.__str__()
    
    @property
    def is_active(self) -> bool:
        """
        Проверить, активен ли элемент.
        
        Для Junior: @property - это способ создать "вычисляемое поле".
        Вместо метода is_active(), мы можем использовать item.is_active.
        
        Returns:
            bool: True, если элемент активен
        
        Пример:
            >>> item = YourModel(id=1, name='Item', status='active')
            >>> if item.is_active:
            ...     print("Элемент активен")
        """
        return self.status == 'active'
    
    # TODO: Добавьте другие полезные @property методы, если нужно
