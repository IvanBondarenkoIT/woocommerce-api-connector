"""
Обработчик заказов WooCommerce.

Извлекает данные клиента из заказов для синхронизации с LILU.
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from woocommerce_connector.models.order import Order
from woocommerce_connector.utils.logger import get_logger
from woocommerce_connector.utils.phone_normalizer import PhoneNormalizer

logger = get_logger(__name__)


@dataclass
class CustomerData:
    """Данные клиента, извлеченные из заказа."""
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    order_id: int = 0
    order_date: Optional[str] = None
    order_total: str = "0"
    order_status: str = ""


class OrderProcessor:
    """
    Обработчик заказов для извлечения данных клиента.
    
    Извлекает телефон, имя, email и другую информацию из заказов WooCommerce
    для последующей синхронизации с LILU.
    """
    
    def __init__(self, default_country: str = 'RU'):
        """
        Инициализация обработчика.
        
        Args:
            default_country: Код страны по умолчанию для нормализации телефонов
        """
        self.phone_normalizer = PhoneNormalizer(default_country=default_country)
        logger.debug(f"OrderProcessor initialized with default country: {default_country}")
    
    def extract_customer_data(self, order: Order) -> Optional[CustomerData]:
        """
        Извлечь данные клиента из заказа.
        
        Args:
            order: Заказ WooCommerce
        
        Returns:
            CustomerData если удалось извлечь данные, None если нет телефона
        
        Raises:
            ValueError: Если заказ не содержит необходимых данных
        """
        # Извлекаем телефон из billing данных
        phone_raw = None
        if order.billing:
            phone_raw = order.billing.get('phone', '')
        
        # Нормализуем телефон
        phone = self.phone_normalizer.normalize(phone_raw)
        
        if not phone:
            logger.warning(f"Order {order.id} has no valid phone number, skipping")
            return None
        
        # Извлекаем имя
        name = order.customer_name
        if not name and order.billing:
            first_name = order.billing.get('first_name', '')
            last_name = order.billing.get('last_name', '')
            name = f"{first_name} {last_name}".strip() or None
        
        # Извлекаем email
        email = order.customer_email
        if not email and order.billing:
            email = order.billing.get('email', '') or None
        
        # Если нет имени, используем телефон как имя
        if not name:
            name = phone
        
        customer_data = CustomerData(
            phone=phone,
            name=name,
            email=email,
            order_id=order.id,
            order_date=order.date_created,
            order_total=order.total,
            order_status=order.status
        )
        
        logger.debug(f"Extracted customer data from order {order.id}: phone={phone}, name={name}")
        return customer_data
    
    def determine_tags(
        self,
        order: Order,
        default_tag: str = "api woo",
        additional_rules: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Определить теги для клиента на основе заказа.
        
        Args:
            order: Заказ WooCommerce
            default_tag: Базовый тег (всегда добавляется)
            additional_rules: Дополнительные правила для определения тегов
        
        Returns:
            Список тегов для клиента
        """
        tags = [default_tag]  # Базовый тег всегда
        
        if not additional_rules:
            return tags
        
        # Применяем дополнительные правила
        for rule in additional_rules:
            tag = rule.get('tag')
            condition = rule.get('condition')
            
            if not tag or not condition:
                continue
            
            # Проверяем условие
            if self._check_condition(order, condition):
                if tag not in tags:
                    tags.append(tag)
        
        logger.debug(f"Determined tags for order {order.id}: {tags}")
        return tags

    def format_order_products(self, order: Order) -> str:
        """
        Форматировать перечень товаров заказа для отображения/комментария.

        Args:
            order: Заказ WooCommerce

        Returns:
            Строка вида "Товар 1 x2, Товар 2 x1" или пустая строка
        """
        if not order.line_items:
            return ""
        parts = []
        for item in order.line_items:
            name = item.get("name", "—")
            qty = item.get("quantity", 1)
            if isinstance(qty, (int, float)):
                parts.append(f"{name} x{int(qty)}")
            else:
                parts.append(str(name))
        return ", ".join(parts)

    def format_order_summary_for_message(
        self, order: Order, customer_data: Optional[CustomerData] = None
    ) -> str:
        """
        Форматировать полное описание заказа для стартового сообщения в переписку.

        Args:
            order: Заказ WooCommerce
            customer_data: Данные клиента (опционально)

        Returns:
            Текст сообщения с информацией о заказе
        """
        from datetime import datetime

        lines = [
            f"Заказ WooCommerce #{order.id}",
            f"Дата: {order.date_created or '—'}",
            f"Сумма: {order.total} {order.currency}",
            f"Статус: {order.status}",
        ]
        products = self.format_order_products(order)
        if products:
            lines.append(f"Товары: {products}")
        if customer_data and customer_data.order_id:
            lines.append(f"Телефон клиента: {customer_data.phone}")
        return "\n".join(lines)

    def _check_condition(self, order: Order, condition: Dict[str, Any]) -> bool:
        """
        Проверить условие для определения тега.
        
        Args:
            order: Заказ
            condition: Условие в формате {"field": "total", "operator": ">", "value": 10000}
        
        Returns:
            True если условие выполнено
        """
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        if not all([field, operator, value]):
            return False
        
        # Получаем значение поля из заказа
        order_value = None
        if field == 'total':
            order_value = float(order.total) if order.total else 0
        elif field == 'status':
            order_value = order.status
        elif field == 'item_count':
            order_value = order.item_count
        
        if order_value is None:
            return False
        
        # Применяем оператор
        if operator == '>':
            return order_value > value
        elif operator == '>=':
            return order_value >= value
        elif operator == '<':
            return order_value < value
        elif operator == '<=':
            return order_value <= value
        elif operator == '==':
            return order_value == value
        elif operator == '!=':
            return order_value != value
        elif operator == 'in':
            return order_value in value if isinstance(value, list) else False
        
        return False
