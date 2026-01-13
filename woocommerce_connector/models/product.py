"""
Модель товара WooCommerce.

Этот модуль содержит dataclass для представления товара из WooCommerce API.
Товар содержит всю информацию о продукте: цены, наличие, категории и т.д.

Пример использования:
    >>> from woocommerce_connector.models import Product, Category
    >>> product_data = {
    ...     "id": 1,
    ...     "name": "Coffee",
    ...     "price": "29.99",
    ...     "categories": [{"id": 1, "name": "Beverages"}]
    ... }
    >>> product = Product.from_dict(product_data)
    >>> print(product.name)
    Coffee
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from .category import Category


@dataclass
class Product:
    """
    Модель товара WooCommerce.
    
    Содержит все основные поля товара из WooCommerce API.
    Используется для типизированной работы с данными товаров.
    
    Attributes:
        id: Уникальный идентификатор товара
        name: Название товара
        slug: URL-friendly идентификатор товара
        permalink: Полная ссылка на товар
        date_created: Дата создания товара
        date_modified: Дата последнего изменения
        type: Тип товара (simple, variable, grouped, external)
        status: Статус товара (draft, pending, private, publish)
        featured: Является ли товар рекомендуемым
        catalog_visibility: Видимость в каталоге
        description: Полное описание товара
        short_description: Краткое описание
        sku: Артикул товара
        price: Текущая цена (строка)
        regular_price: Обычная цена
        sale_price: Цена со скидкой (если есть)
        on_sale: Есть ли скидка
        purchasable: Можно ли купить товар
        total_sales: Количество продаж
        virtual: Виртуальный товар (не требует доставки)
        downloadable: Можно ли скачать товар
        downloads: Список файлов для скачивания
        download_limit: Лимит скачиваний
        download_expiry: Срок действия скачивания
        external_url: Внешняя ссылка (для внешних товаров)
        button_text: Текст кнопки (для внешних товаров)
        tax_status: Статус налогообложения
        tax_class: Класс налога
        manage_stock: Управлять ли складом
        stock_quantity: Количество на складе
        stock_status: Статус наличия (instock, outofstock, onbackorder)
        backorders: Разрешить ли предзаказы
        backorders_allowed: Разрешены ли предзаказы
        backordered: Есть ли предзаказы
        sold_individually: Продавать ли поштучно
        weight: Вес товара
        dimensions: Размеры товара (dict с width, height, length)
        shipping_required: Требуется ли доставка
        shipping_taxable: Облагается ли доставка налогом
        shipping_class: Класс доставки
        shipping_class_id: ID класса доставки
        reviews_allowed: Разрешены ли отзывы
        average_rating: Средний рейтинг
        rating_count: Количество оценок
        related_ids: ID связанных товаров
        upsell_ids: ID товаров для перекрестных продаж
        cross_sell_ids: ID товаров для дополнительных продаж
        parent_id: ID родительского товара (для вариаций)
        purchase_note: Примечание к покупке
        categories: Список категорий товара
        tags: Список тегов товара
        images: Список изображений товара
        attributes: Атрибуты товара
        default_attributes: Атрибуты по умолчанию
        variations: Вариации товара (для variable products)
        grouped_products: Группированные товары
        menu_order: Порядок сортировки
        meta_data: Дополнительные метаданные
    """
    # Основная информация
    id: int
    name: str
    slug: str = ""
    permalink: str = ""
    type: str = "simple"
    status: str = "publish"
    featured: bool = False
    catalog_visibility: str = "visible"
    
    # Описание
    description: str = ""
    short_description: str = ""
    
    # Цены
    sku: Optional[str] = None
    price: str = "0"
    regular_price: str = "0"
    sale_price: Optional[str] = None
    on_sale: bool = False
    purchasable: bool = True
    
    # Продажи
    total_sales: int = 0
    
    # Тип товара
    virtual: bool = False
    downloadable: bool = False
    downloads: List[dict] = field(default_factory=list)
    download_limit: int = -1
    download_expiry: int = -1
    external_url: str = ""
    button_text: str = ""
    
    # Налоги
    tax_status: str = "taxable"
    tax_class: str = ""
    
    # Склад
    manage_stock: bool = False
    stock_quantity: Optional[int] = None
    stock_status: str = "instock"
    backorders: str = "no"
    backorders_allowed: bool = False
    backordered: bool = False
    sold_individually: bool = False
    
    # Доставка
    weight: str = ""
    dimensions: dict = field(default_factory=dict)
    shipping_required: bool = True
    shipping_taxable: bool = True
    shipping_class: str = ""
    shipping_class_id: int = 0
    
    # Отзывы
    reviews_allowed: bool = True
    average_rating: str = "0"
    rating_count: int = 0
    
    # Связи
    related_ids: List[int] = field(default_factory=list)
    upsell_ids: List[int] = field(default_factory=list)
    cross_sell_ids: List[int] = field(default_factory=list)
    parent_id: int = 0
    
    # Дополнительно
    purchase_note: str = ""
    categories: List[Category] = field(default_factory=list)
    tags: List[dict] = field(default_factory=list)
    images: List[dict] = field(default_factory=list)
    attributes: List[dict] = field(default_factory=list)
    default_attributes: List[dict] = field(default_factory=list)
    variations: List[int] = field(default_factory=list)
    grouped_products: List[int] = field(default_factory=list)
    menu_order: int = 0
    meta_data: List[dict] = field(default_factory=list)
    
    # Даты
    date_created: Optional[str] = None
    date_modified: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """
        Создать объект Product из словаря API.
        
        Этот метод преобразует сырые данные из WooCommerce API
        в типизированный объект Product.
        
        Args:
            data: Словарь с данными товара из WooCommerce API
        
        Returns:
            Product: Объект товара
        
        Example:
            >>> api_data = {
            ...     "id": 1,
            ...     "name": "Coffee",
            ...     "price": "29.99",
            ...     "categories": [{"id": 1, "name": "Beverages", "slug": "beverages"}]
            ... }
            >>> product = Product.from_dict(api_data)
            >>> print(product.name)
            Coffee
        """
        # Преобразуем категории в объекты Category
        categories = []
        if 'categories' in data and isinstance(data['categories'], list):
            categories = [Category.from_dict(cat) for cat in data['categories']]
        
        return cls(
            # Основная информация
            id=data.get('id', 0),
            name=data.get('name', ''),
            slug=data.get('slug', ''),
            permalink=data.get('permalink', ''),
            type=data.get('type', 'simple'),
            status=data.get('status', 'publish'),
            featured=data.get('featured', False),
            catalog_visibility=data.get('catalog_visibility', 'visible'),
            
            # Описание
            description=data.get('description', ''),
            short_description=data.get('short_description', ''),
            
            # Цены
            sku=data.get('sku'),
            price=data.get('price', '0'),
            regular_price=data.get('regular_price', '0'),
            sale_price=data.get('sale_price'),
            on_sale=data.get('on_sale', False),
            purchasable=data.get('purchasable', True),
            
            # Продажи
            total_sales=data.get('total_sales', 0),
            
            # Тип товара
            virtual=data.get('virtual', False),
            downloadable=data.get('downloadable', False),
            downloads=data.get('downloads', []),
            download_limit=data.get('download_limit', -1),
            download_expiry=data.get('download_expiry', -1),
            external_url=data.get('external_url', ''),
            button_text=data.get('button_text', ''),
            
            # Налоги
            tax_status=data.get('tax_status', 'taxable'),
            tax_class=data.get('tax_class', ''),
            
            # Склад
            manage_stock=data.get('manage_stock', False),
            stock_quantity=data.get('stock_quantity'),
            stock_status=data.get('stock_status', 'instock'),
            backorders=data.get('backorders', 'no'),
            backorders_allowed=data.get('backorders_allowed', False),
            backordered=data.get('backordered', False),
            sold_individually=data.get('sold_individually', False),
            
            # Доставка
            weight=data.get('weight', ''),
            dimensions=data.get('dimensions', {}),
            shipping_required=data.get('shipping_required', True),
            shipping_taxable=data.get('shipping_taxable', True),
            shipping_class=data.get('shipping_class', ''),
            shipping_class_id=data.get('shipping_class_id', 0),
            
            # Отзывы
            reviews_allowed=data.get('reviews_allowed', True),
            average_rating=str(data.get('average_rating', '0')),
            rating_count=data.get('rating_count', 0),
            
            # Связи
            related_ids=data.get('related_ids', []),
            upsell_ids=data.get('upsell_ids', []),
            cross_sell_ids=data.get('cross_sell_ids', []),
            parent_id=data.get('parent_id', 0),
            
            # Дополнительно
            purchase_note=data.get('purchase_note', ''),
            categories=categories,
            tags=data.get('tags', []),
            images=data.get('images', []),
            attributes=data.get('attributes', []),
            default_attributes=data.get('default_attributes', []),
            variations=data.get('variations', []),
            grouped_products=data.get('grouped_products', []),
            menu_order=data.get('menu_order', 0),
            meta_data=data.get('meta_data', []),
            
            # Даты
            date_created=data.get('date_created'),
            date_modified=data.get('date_modified'),
        )
    
    def to_dict(self) -> dict:
        """
        Преобразовать объект Product в словарь для API.
        
        Этот метод преобразует объект Product обратно в формат,
        который ожидает WooCommerce API.
        
        Returns:
            dict: Словарь с данными товара для API
        
        Example:
            >>> product = Product(id=1, name="Coffee", price="29.99")
            >>> data = product.to_dict()
            >>> print(data['name'])
            Coffee
        """
        result = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'type': self.type,
            'status': self.status,
            'featured': self.featured,
            'catalog_visibility': self.catalog_visibility,
            'description': self.description,
            'short_description': self.short_description,
            'sku': self.sku,
            'price': self.price,
            'regular_price': self.regular_price,
            'sale_price': self.sale_price,
            'on_sale': self.on_sale,
            'purchasable': self.purchasable,
            'total_sales': self.total_sales,
            'virtual': self.virtual,
            'downloadable': self.downloadable,
            'downloads': self.downloads,
            'download_limit': self.download_limit,
            'download_expiry': self.download_expiry,
            'external_url': self.external_url,
            'button_text': self.button_text,
            'tax_status': self.tax_status,
            'tax_class': self.tax_class,
            'manage_stock': self.manage_stock,
            'stock_quantity': self.stock_quantity,
            'stock_status': self.stock_status,
            'backorders': self.backorders,
            'backorders_allowed': self.backorders_allowed,
            'backordered': self.backordered,
            'sold_individually': self.sold_individually,
            'weight': self.weight,
            'dimensions': self.dimensions,
            'shipping_required': self.shipping_required,
            'shipping_taxable': self.shipping_taxable,
            'shipping_class': self.shipping_class,
            'shipping_class_id': self.shipping_class_id,
            'reviews_allowed': self.reviews_allowed,
            'average_rating': self.average_rating,
            'rating_count': self.rating_count,
            'related_ids': self.related_ids,
            'upsell_ids': self.upsell_ids,
            'cross_sell_ids': self.cross_sell_ids,
            'parent_id': self.parent_id,
            'purchase_note': self.purchase_note,
            'categories': [cat.to_dict() for cat in self.categories],
            'tags': self.tags,
            'images': self.images,
            'attributes': self.attributes,
            'default_attributes': self.default_attributes,
            'variations': self.variations,
            'grouped_products': self.grouped_products,
            'menu_order': self.menu_order,
            'meta_data': self.meta_data,
        }
        
        # Удаляем None значения для опциональных полей
        return {k: v for k, v in result.items() if v is not None}
    
    def __str__(self) -> str:
        """Строковое представление товара"""
        return f"Product(id={self.id}, name='{self.name}', price='{self.price}')"
    
    def __repr__(self) -> str:
        """Представление для отладки"""
        return self.__str__()
    
    @property
    def is_in_stock(self) -> bool:
        """Проверить, есть ли товар в наличии"""
        return self.stock_status == 'instock'
    
    @property
    def has_discount(self) -> bool:
        """Проверить, есть ли скидка на товар"""
        return self.on_sale and self.sale_price is not None
    
    @property
    def discount_percentage(self) -> Optional[float]:
        """Вычислить процент скидки"""
        if not self.has_discount:
            return None
        
        try:
            regular = float(self.regular_price)
            sale = float(self.sale_price) if self.sale_price else 0
            if regular > 0:
                return round(((regular - sale) / regular) * 100, 2)
        except (ValueError, TypeError):
            pass
        
        return None
