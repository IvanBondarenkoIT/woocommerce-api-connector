"""
Сервис синхронизации заказов WooCommerce с LILU CRM.

Основной сервис для автоматической синхронизации заказов из WooCommerce
в CRM LILU: поиск клиентов по телефону, создание новых клиентов, обновление тегов.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from woocommerce_connector.connector import WooCommerceConnector
from woocommerce_connector.models.order import Order
from lilu_connector.connector import LILUConnector
from lilu_connector.models.client import ClientModel

from .order_processor import OrderProcessor, CustomerData
from .sync_tracker import SyncTracker
from woocommerce_connector.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SyncResult:
    """Результат синхронизации заказа."""
    order_id: int
    success: bool
    action: str  # "created" | "updated" | "skipped" | "error"
    lilu_client_id: Optional[str] = None
    client_identifier: Optional[str] = None  # fallback: email/name когда lilu_client_id пустой
    error_message: Optional[str] = None
    tags_added: List[str] = field(default_factory=list)
    processed_at: datetime = field(default_factory=datetime.now)

    def get_display_id(self) -> str:
        """Идентификатор для отображения."""
        return self.lilu_client_id or self.client_identifier or "-"
    
    def __str__(self) -> str:
        """Строковое представление результата."""
        status = "✅" if self.success else "❌"
        return f"{status} Order #{self.order_id}: {self.action}"


class SyncService:
    """
    Сервис синхронизации заказов WooCommerce с LILU CRM.
    
    Основные функции:
    - Получение заказов из WooCommerce
    - Извлечение данных клиентов
    - Поиск клиентов в LILU по телефону
    - Создание новых клиентов в LILU
    - Обновление тегов существующих клиентов
    - Отслеживание обработанных заказов
    """
    
    def __init__(
        self,
        wc_connector: WooCommerceConnector,
        lilu_connector: LILUConnector,
        default_tag: str = "api woo",
        additional_tag_rules: Optional[List[Dict[str, Any]]] = None,
        tracker_file: str = "data/sync_tracker.json",
        default_country: str = 'RU'
    ):
        """
        Инициализация сервиса синхронизации.
        
        Args:
            wc_connector: Коннектор WooCommerce
            lilu_connector: Коннектор LILU
            default_tag: Базовый тег для новых клиентов
            additional_tag_rules: Дополнительные правила для определения тегов
            tracker_file: Путь к файлу трекера
            default_country: Код страны по умолчанию для нормализации телефонов
        """
        self.wc_connector = wc_connector
        self.lilu_connector = lilu_connector
        self.default_tag = default_tag
        self.additional_tag_rules = additional_tag_rules or []
        self.tracker = SyncTracker(storage_file=tracker_file)
        self.order_processor = OrderProcessor(default_country=default_country)
        
        logger.info(f"SyncService initialized with default tag: {default_tag}")
    
    def sync_order(self, order: Order) -> SyncResult:
        """
        Синхронизировать один заказ.
        
        Основной метод синхронизации:
        1. Проверяет, не обработан ли заказ уже
        2. Извлекает данные клиента
        3. Ищет клиента в LILU по телефону
        4. Создает или обновляет клиента
        5. Отмечает заказ как обработанный
        
        Args:
            order: Заказ WooCommerce
        
        Returns:
            SyncResult: Результат синхронизации
        """
        order_id = order.id
        
        # Проверяем, не обработан ли заказ уже
        if self.tracker.is_processed(order_id):
            logger.debug(f"Order {order_id} already processed, skipping")
            return SyncResult(
                order_id=order_id,
                success=True,
                action="skipped",
                error_message="Order already processed"
            )
        
        try:
            # Извлекаем данные клиента из заказа
            customer_data = self.order_processor.extract_customer_data(order)
            
            if not customer_data:
                # Нет телефона - пропускаем
                result = SyncResult(
                    order_id=order_id,
                    success=False,
                    action="skipped",
                    error_message="No phone number in order"
                )
                self.tracker.mark_processed(
                    order_id=order_id,
                    status="skipped",
                    error_message="No phone number"
                )
                logger.warning(f"Order {order_id} skipped: no phone number")
                return result
            
            # Определяем теги для клиента
            tags = self.order_processor.determine_tags(
                order=order,
                default_tag=self.default_tag,
                additional_rules=self.additional_tag_rules
            )
            
            # Ищем клиента в LILU по телефону
            existing_client = self.lilu_connector.find_client_by_phone(customer_data.phone)
            
            if existing_client:
                # Клиент найден - обновляем теги если нужно
                logger.info(f"Found existing client in LILU: {existing_client.name} (ID: {existing_client.id})")
                
                # Проверяем, нужно ли обновить теги
                current_tags = set(existing_client.tags or [])
                new_tags = set(tags)
                
                if not new_tags.issubset(current_tags):
                    # Есть новые теги - обновляем
                    tags_to_add = list(new_tags - current_tags)
                    updated_tags = list(current_tags | new_tags)
                    
                    try:
                        updated_client = self.lilu_connector.update_client_tags(
                            client_id=existing_client.id,
                            tags=updated_tags,
                            merge=True
                        )
                        
                        result = SyncResult(
                            order_id=order_id,
                            success=True,
                            action="updated",
                            lilu_client_id=updated_client.id,
                            tags_added=tags_to_add
                        )
                        
                        self.tracker.mark_processed(
                            order_id=order_id,
                            lilu_client_id=updated_client.id,
                            status="updated",
                            tags_added=tags_to_add
                        )
                        
                        logger.info(f"Order {order_id} synced → Client updated (ID: {updated_client.id}), tags added: {tags_to_add}")
                        return result
                    
                    except Exception as e:
                        error_msg = f"Failed to update client tags: {e}"
                        logger.error(f"Order {order_id} sync error: {error_msg}")
                        
                        result = SyncResult(
                            order_id=order_id,
                            success=False,
                            action="error",
                            lilu_client_id=existing_client.id,
                            error_message=error_msg
                        )
                        
                        self.tracker.mark_processed(
                            order_id=order_id,
                            lilu_client_id=existing_client.id,
                            status="error",
                            error_message=error_msg
                        )
                        return result
                else:
                    # Теги уже актуальны
                    result = SyncResult(
                        order_id=order_id,
                        success=True,
                        action="updated",
                        lilu_client_id=existing_client.id,
                        tags_added=[]
                    )
                    
                    self.tracker.mark_processed(
                        order_id=order_id,
                        lilu_client_id=existing_client.id,
                        status="updated",
                        tags_added=[]
                    )
                    
                    logger.debug(f"Order {order_id} synced → Client exists, tags up to date (ID: {existing_client.id})")
                    return result
            
            else:
                # Клиент не найден - создаем нового
                logger.info(f"Client not found in LILU, creating new client for phone: {customer_data.phone}")
                
                # Идентификатор для отображения, когда LILU не вернул id
                fallback_id = customer_data.email or customer_data.name or customer_data.phone
                client_data = {
                    'name': customer_data.name or customer_data.phone,
                    'phone': customer_data.phone,
                    'tags': tags
                }
                if customer_data.email:
                    client_data['email'] = customer_data.email

                try:
                    new_client = self.lilu_connector.create_client(client_data)
                    lid = new_client.id if new_client.id else None

                    result = SyncResult(
                        order_id=order_id,
                        success=True,
                        action="created",
                        lilu_client_id=lid,
                        client_identifier=fallback_id if not lid else None,
                        tags_added=tags
                    )

                    self.tracker.mark_processed(
                        order_id=order_id,
                        lilu_client_id=lid,
                        client_identifier=fallback_id if not lid else None,
                        status="created",
                        tags_added=tags
                    )
                    
                    logger.info(f"Order {order_id} synced → Client created (ID: {lid or fallback_id}), tags: {tags}")
                    return result
                
                except Exception as e:
                    error_msg = f"Failed to create client: {e}"
                    logger.error(f"Order {order_id} sync error: {error_msg}")
                    
                    result = SyncResult(
                        order_id=order_id,
                        success=False,
                        action="error",
                        error_message=error_msg
                    )
                    
                    self.tracker.mark_processed(
                        order_id=order_id,
                        status="error",
                        error_message=error_msg
                    )
                    return result
        
        except Exception as e:
            error_msg = f"Unexpected error during sync: {e}"
            logger.error(f"Order {order_id} sync error: {error_msg}", exc_info=True)
            
            result = SyncResult(
                order_id=order_id,
                success=False,
                action="error",
                error_message=error_msg
            )
            
            self.tracker.mark_processed(
                order_id=order_id,
                status="error",
                error_message=error_msg
            )
            return result
    
    def sync_new_orders(
        self,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[SyncResult]:
        """
        Синхронизировать новые заказы (еще не обработанные).
        
        Args:
            status: Фильтр по статусу заказа (опционально)
            limit: Максимальное количество заказов для обработки (опционально)
        
        Returns:
            Список результатов синхронизации
        """
        logger.info(f"Starting sync of new orders (status={status}, limit={limit})")
        
        # Получаем все заказы
        all_orders_data = self.wc_connector.get_all_orders(per_page=100, status=status)
        
        results = []
        processed_count = 0
        
        for order_data in all_orders_data:
            if limit and processed_count >= limit:
                break
            
            # Пропускаем уже обработанные заказы
            order_id = order_data.get('id')
            if not order_id or self.tracker.is_processed(order_id):
                continue
            
            # Преобразуем в модель Order
            order = Order.from_dict(order_data)
            
            # Синхронизируем
            result = self.sync_order(order)
            results.append(result)
            processed_count += 1
        
        logger.info(f"Sync completed: {len(results)} orders processed")
        return results
    
    def sync_all_orders(self, status: Optional[str] = None) -> List[SyncResult]:
        """
        Синхронизировать все заказы (включая уже обработанные).
        
        Полезно для первоначальной загрузки или повторной синхронизации.
        
        Args:
            status: Фильтр по статусу заказа (опционально)
        
        Returns:
            Список результатов синхронизации
        """
        logger.info(f"Starting sync of ALL orders (status={status})")
        
        all_orders_data = self.wc_connector.get_all_orders(per_page=100, status=status)
        
        results = []
        
        for order_data in all_orders_data:
            order = Order.from_dict(order_data)
            result = self.sync_order(order)
            results.append(result)
        
        logger.info(f"Sync completed: {len(results)} orders processed")
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику синхронизации.
        
        Returns:
            Словарь со статистикой
        """
        tracker_stats = self.tracker.get_statistics()
        
        return {
            'tracker': tracker_stats,
            'default_tag': self.default_tag,
            'additional_rules_count': len(self.additional_tag_rules)
        }
