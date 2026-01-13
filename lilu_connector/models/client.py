"""
Модель клиента LILU API.

Для Junior разработчиков:
Этот класс представляет клиента из LILU API.
Вместо работы со словарём, мы используем типизированный класс.
Это даёт нам:
1. Автодополнение в IDE
2. Проверку типов
3. Документацию полей
4. Методы для преобразования данных
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class ClientModel:
    """
    Модель клиента из LILU API.
    
    Для Junior: @dataclass - это декоратор Python, который автоматически
    создаёт методы __init__, __repr__, __eq__ и другие для класса.
    Это экономит много кода!
    
    Attributes:
        id: Уникальный идентификатор клиента
        name: Имя клиента
        email: Email адрес
        phone: Номер телефона (опционально)
        status: Статус клиента (active, inactive, etc.)
        created_at: Дата создания
        updated_at: Дата последнего обновления
        metadata: Дополнительные данные (опционально)
    
    Пример использования:
        >>> client_data = {
        ...     'id': 1,
        ...     'name': 'John Doe',
        ...     'email': 'john@example.com',
        ...     'phone': '+1234567890',
        ...     'status': 'active'
        ... }
        >>> client = ClientModel.from_dict(client_data)
        >>> print(client.name)
        John Doe
    """
    
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientModel':
        """
        Создать объект ClientModel из словаря API.
        
        Для Junior: classmethod - это метод, который можно вызывать
        на классе, а не на объекте. Например: ClientModel.from_dict(data)
        вместо client.from_dict(data).
        
        Этот метод преобразует сырые данные из API в типизированный объект.
        
        Args:
            data: Словарь с данными клиента из LILU API
        
        Returns:
            ClientModel: Объект клиента
        
        Пример:
            >>> api_data = {
            ...     'id': 1,
            ...     'name': 'John Doe',
            ...     'email': 'john@example.com'
            ... }
            >>> client = ClientModel.from_dict(api_data)
            >>> print(client.name)
            John Doe
        """
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone'),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать объект ClientModel в словарь для API.
        
        Для Junior: этот метод нужен, когда мы хотим отправить данные
        обратно в API (например, при создании или обновлении клиента).
        
        Returns:
            Dict[str, Any]: Словарь с данными клиента для API
        
        Пример:
            >>> client = ClientModel(id=1, name='John', email='john@example.com')
            >>> data = client.to_dict()
            >>> # Отправить data в API
        """
        result = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'status': self.status,
        }
        
        # Добавляем опциональные поля, если они есть
        if self.phone:
            result['phone'] = self.phone
        
        if self.metadata:
            result['metadata'] = self.metadata
        
        return result
    
    def __str__(self) -> str:
        """
        Строковое представление клиента.
        
        Для Junior: этот метод вызывается, когда мы используем print() или str().
        """
        return f"Client(id={self.id}, name='{self.name}', email='{self.email}')"
    
    def __repr__(self) -> str:
        """
        Представление для отладки.
        
        Для Junior: этот метод вызывается в отладчике и при выводе в консоль.
        """
        return self.__str__()
    
    @property
    def is_active(self) -> bool:
        """
        Проверить, активен ли клиент.
        
        Для Junior: @property - это способ создать "вычисляемое поле".
        Вместо метода is_active(), мы можем использовать client.is_active
        (без скобок).
        
        Returns:
            bool: True, если клиент активен
        
        Пример:
            >>> client = ClientModel(id=1, name='John', email='john@example.com', status='active')
            >>> if client.is_active:
            ...     print("Клиент активен")
        """
        return self.status == 'active'
    
    @property
    def display_name(self) -> str:
        """
        Получить отображаемое имя клиента.
        
        Returns:
            str: Имя клиента или email, если имя пустое
        
        Пример:
            >>> client = ClientModel(id=1, name='', email='john@example.com')
            >>> print(client.display_name)
            john@example.com
        """
        return self.name if self.name else self.email
