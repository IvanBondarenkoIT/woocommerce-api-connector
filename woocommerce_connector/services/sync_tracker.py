"""
Система отслеживания обработанных заказов.

Хранит информацию о заказах, которые уже были синхронизированы,
чтобы избежать дублирования при повторных запусках синхронизации.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from woocommerce_connector.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessedOrder:
    """Информация об обработанном заказе."""
    order_id: int
    processed_at: str
    lilu_client_id: Optional[str] = None
    client_identifier: Optional[str] = None  # fallback: email или name, когда lilu_client_id пустой
    status: str = "processed"  # "created" | "updated" | "skipped" | "error"
    tags_added: list = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.tags_added is None:
            self.tags_added = []
    
    def get_display_id(self) -> str:
        """Идентификатор для отображения: lilu_client_id или client_identifier."""
        if self.lilu_client_id:
            return self.lilu_client_id
        return self.client_identifier or "-"


class SyncTracker:
    """
    Отслеживание обработанных заказов.
    
    Хранит информацию о заказах, которые уже были синхронизированы.
    Поддерживает хранение в JSON файле (можно расширить для SQLite/PostgreSQL).
    """
    
    def __init__(self, storage_file: str = "data/sync_tracker.json"):
        """
        Инициализация трекера.
        
        Args:
            storage_file: Путь к файлу для хранения данных
        """
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Dict[str, Any]] = {}
        self._load()
        logger.debug(f"SyncTracker initialized with storage: {self.storage_file}")
    
    def _load(self) -> None:
        """Загрузить данные из файла."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                logger.debug(f"Loaded {len(self._data)} processed orders from tracker")
            except Exception as e:
                logger.warning(f"Failed to load tracker data: {e}, starting fresh")
                self._data = {}
        else:
            self._data = {}
    
    def _save(self) -> None:
        """Сохранить данные в файл."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved {len(self._data)} processed orders to tracker")
        except Exception as e:
            logger.error(f"Failed to save tracker data: {e}")
            raise
    
    def is_processed(self, order_id: int) -> bool:
        """
        Проверить, был ли заказ уже обработан.
        
        Args:
            order_id: ID заказа
        
        Returns:
            True если заказ уже обработан
        """
        return str(order_id) in self._data
    
    def mark_processed(
        self,
        order_id: int,
        lilu_client_id: Optional[str] = None,
        client_identifier: Optional[str] = None,
        status: str = "processed",
        tags_added: Optional[list] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Отметить заказ как обработанный.
        
        Args:
            order_id: ID заказа
            lilu_client_id: ID клиента в LILU (если был создан/найден)
            client_identifier: Fallback идентификатор (email или name), когда lilu_client_id пустой
            status: Статус обработки ("created" | "updated" | "skipped" | "error")
            tags_added: Список добавленных тегов
            error_message: Сообщение об ошибке (если была)
        """
        processed_order = ProcessedOrder(
            order_id=order_id,
            processed_at=datetime.now().isoformat(),
            lilu_client_id=lilu_client_id or None,
            client_identifier=client_identifier,
            status=status,
            tags_added=tags_added or [],
            error_message=error_message
        )
        
        self._data[str(order_id)] = asdict(processed_order)
        self._save()
        logger.debug(f"Marked order {order_id} as processed (status: {status})")
    
    def unmark_processed(self, order_id: int) -> None:
        """
        Удалить заказ из списка обработанных (отменить синхронизацию).
        
        Args:
            order_id: ID заказа
        """
        key = str(order_id)
        if key in self._data:
            del self._data[key]
            self._save()
            logger.info(f"Unmarked order {order_id} from sync tracker")

    def get_processed_order(self, order_id: int) -> Optional[ProcessedOrder]:
        """
        Получить информацию об обработанном заказе.
        
        Args:
            order_id: ID заказа
        
        Returns:
            ProcessedOrder если заказ был обработан, None иначе
        """
        order_data = self._data.get(str(order_id))
        if order_data:
            kwargs = {k: v for k, v in order_data.items()
                      if k in ('order_id', 'processed_at', 'lilu_client_id', 'client_identifier', 'status', 'tags_added', 'error_message')}
            kwargs.setdefault('client_identifier', None)
            return ProcessedOrder(**kwargs)
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику по обработанным заказам.
        
        Returns:
            Словарь со статистикой
        """
        total = len(self._data)
        created = sum(1 for o in self._data.values() if o.get('status') == 'created')
        updated = sum(1 for o in self._data.values() if o.get('status') == 'updated')
        skipped = sum(1 for o in self._data.values() if o.get('status') == 'skipped')
        errors = sum(1 for o in self._data.values() if o.get('status') == 'error')
        
        return {
            'total_processed': total,
            'created': created,
            'updated': updated,
            'skipped': skipped,
            'errors': errors
        }
    
    def clear(self) -> None:
        """Очистить все данные трекера."""
        self._data = {}
        self._save()
        logger.info("SyncTracker cleared")
