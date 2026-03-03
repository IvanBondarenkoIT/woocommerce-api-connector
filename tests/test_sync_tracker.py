"""
Тесты для системы отслеживания обработанных заказов.
"""

import pytest
import json
import tempfile
from pathlib import Path
from woocommerce_connector.services.sync_tracker import SyncTracker, ProcessedOrder


class TestSyncTracker:
    """Тесты для класса SyncTracker."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        # Создаем временный файл для каждого теста
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.tracker = SyncTracker(storage_file=self.temp_file.name)
    
    def teardown_method(self):
        """Очистка после каждого теста."""
        # Удаляем временный файл
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_is_processed_false(self):
        """Тест проверки необработанного заказа."""
        assert self.tracker.is_processed(12345) is False
    
    def test_mark_processed(self):
        """Тест отметки заказа как обработанного."""
        self.tracker.mark_processed(
            order_id=12345,
            lilu_client_id="69660055fb13db648fc58795",
            status="created",
            tags_added=["api woo"]
        )
        
        assert self.tracker.is_processed(12345) is True
    
    def test_get_processed_order(self):
        """Тест получения информации об обработанном заказе."""
        self.tracker.mark_processed(
            order_id=12345,
            lilu_client_id="69660055fb13db648fc58795",
            status="created",
            tags_added=["api woo", "vip"]
        )
        
        processed = self.tracker.get_processed_order(12345)
        
        assert processed is not None
        assert processed.order_id == 12345
        assert processed.lilu_client_id == "69660055fb13db648fc58795"
        assert processed.status == "created"
        assert "api woo" in processed.tags_added
        assert "vip" in processed.tags_added
    
    def test_get_statistics(self):
        """Тест получения статистики."""
        # Создаем несколько заказов
        self.tracker.mark_processed(12345, status="created")
        self.tracker.mark_processed(12346, status="updated")
        self.tracker.mark_processed(12347, status="skipped")
        self.tracker.mark_processed(12348, status="error")
        
        stats = self.tracker.get_statistics()
        
        assert stats['total_processed'] == 4
        assert stats['created'] == 1
        assert stats['updated'] == 1
        assert stats['skipped'] == 1
        assert stats['errors'] == 1
    
    def test_persistence(self):
        """Тест сохранения и загрузки данных."""
        # Создаем заказ
        self.tracker.mark_processed(
            order_id=12345,
            lilu_client_id="69660055fb13db648fc58795",
            status="created"
        )
        
        # Создаем новый трекер с тем же файлом
        new_tracker = SyncTracker(storage_file=self.temp_file.name)
        
        # Проверяем, что заказ сохранился
        assert new_tracker.is_processed(12345) is True
        processed = new_tracker.get_processed_order(12345)
        assert processed.lilu_client_id == "69660055fb13db648fc58795"
    
    def test_clear(self):
        """Тест очистки трекера."""
        self.tracker.mark_processed(12345, status="created")
        self.tracker.mark_processed(12346, status="created")
        
        assert self.tracker.get_statistics()['total_processed'] == 2
        
        self.tracker.clear()
        
        assert self.tracker.get_statistics()['total_processed'] == 0
        assert self.tracker.is_processed(12345) is False

    def test_unmark_processed(self):
        """Тест отмены синхронизации (удаление из трекера)."""
        self.tracker.mark_processed(
            order_id=12345,
            lilu_client_id="69660055fb13db648fc58795",
            status="created"
        )
        assert self.tracker.is_processed(12345) is True

        self.tracker.unmark_processed(12345)

        assert self.tracker.is_processed(12345) is False
        assert self.tracker.get_processed_order(12345) is None
        assert self.tracker.get_statistics()['total_processed'] == 0

    def test_unmark_processed_not_exists(self):
        """Тест unmark_processed для несуществующего заказа не падает."""
        assert self.tracker.is_processed(99999) is False
        self.tracker.unmark_processed(99999)
        assert self.tracker.is_processed(99999) is False

    def test_unmark_processed_persistence(self):
        """Тест что unmark_processed сохраняется на диск."""
        self.tracker.mark_processed(12345, lilu_client_id="abc123", status="created")
        self.tracker.unmark_processed(12345)

        new_tracker = SyncTracker(storage_file=self.temp_file.name)
        assert new_tracker.is_processed(12345) is False
