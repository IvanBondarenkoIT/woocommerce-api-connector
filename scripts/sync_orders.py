"""
Скрипт для синхронизации заказов WooCommerce с LILU CRM.

Использование:
    # Синхронизировать новые заказы
    python scripts/sync_orders.py --new
    
    # Синхронизировать все заказы
    python scripts/sync_orders.py --all
    
    # Синхронизировать конкретный заказ
    python scripts/sync_orders.py --order-id 12345
    
    # Показать статистику
    python scripts/sync_orders.py --stats
"""

import sys
import argparse
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from woocommerce_connector.connector import WooCommerceConnector
from lilu_connector.connector import LILUConnector
from woocommerce_connector.services.sync_service import SyncService
from woocommerce_connector.models.order import Order
from woocommerce_connector.utils.logger import get_logger

logger = get_logger(__name__)


def sync_new_orders(sync_service: SyncService, status: str = None, limit: int = None):
    """Синхронизировать новые заказы."""
    print("\n" + "=" * 80)
    print("СИНХРОНИЗАЦИЯ НОВЫХ ЗАКАЗОВ")
    print("=" * 80 + "\n")
    
    results = sync_service.sync_new_orders(status=status, limit=limit)
    
    # Статистика
    created = sum(1 for r in results if r.action == "created")
    updated = sum(1 for r in results if r.action == "updated")
    skipped = sum(1 for r in results if r.action == "skipped")
    errors = sum(1 for r in results if not r.success)
    
    print(f"\n✅ Синхронизация завершена:")
    print(f"   Создано клиентов: {created}")
    print(f"   Обновлено клиентов: {updated}")
    print(f"   Пропущено: {skipped}")
    print(f"   Ошибок: {errors}")
    print(f"   Всего обработано: {len(results)}")


def sync_all_orders(sync_service: SyncService, status: str = None):
    """Синхронизировать все заказы."""
    print("\n" + "=" * 80)
    print("СИНХРОНИЗАЦИЯ ВСЕХ ЗАКАЗОВ")
    print("=" * 80 + "\n")
    
    print("⚠️  ВНИМАНИЕ: Будут обработаны ВСЕ заказы, включая уже обработанные!")
    response = input("Продолжить? (yes/no): ")
    
    if response.lower() not in ['yes', 'y', 'да', 'д']:
        print("Отменено.")
        return
    
    results = sync_service.sync_all_orders(status=status)
    
    # Статистика
    created = sum(1 for r in results if r.action == "created")
    updated = sum(1 for r in results if r.action == "updated")
    skipped = sum(1 for r in results if r.action == "skipped")
    errors = sum(1 for r in results if not r.success)
    
    print(f"\n✅ Синхронизация завершена:")
    print(f"   Создано клиентов: {created}")
    print(f"   Обновлено клиентов: {updated}")
    print(f"   Пропущено: {skipped}")
    print(f"   Ошибок: {errors}")
    print(f"   Всего обработано: {len(results)}")


def sync_single_order(sync_service: SyncService, order_id: int):
    """Синхронизировать один заказ."""
    print(f"\nСинхронизация заказа #{order_id}...")
    
    wc_connector = sync_service.wc_connector
    order_data = wc_connector.get_order_by_id(order_id)
    
    if not order_data:
        print(f"❌ Заказ #{order_id} не найден")
        return
    
    order = Order.from_dict(order_data)
    result = sync_service.sync_order(order)
    
    print(f"\n{result}")
    if result.success:
        if result.action == "created":
            print(f"✅ Клиент создан в LILU (ID: {result.lilu_client_id})")
        elif result.action == "updated":
            print(f"✅ Клиент обновлен в LILU (ID: {result.lilu_client_id})")
        if result.tags_added:
            print(f"   Добавлены теги: {', '.join(result.tags_added)}")
    else:
        print(f"❌ Ошибка: {result.error_message}")


def show_statistics(sync_service: SyncService):
    """Показать статистику синхронизации."""
    print("\n" + "=" * 80)
    print("СТАТИСТИКА СИНХРОНИЗАЦИИ")
    print("=" * 80 + "\n")
    
    stats = sync_service.get_statistics()
    tracker_stats = stats['tracker']
    
    print(f"Всего обработано заказов: {tracker_stats['total_processed']}")
    print(f"   Создано клиентов: {tracker_stats['created']}")
    print(f"   Обновлено клиентов: {tracker_stats['updated']}")
    print(f"   Пропущено: {tracker_stats['skipped']}")
    print(f"   Ошибок: {tracker_stats['errors']}")
    print(f"\nБазовый тег: {stats['default_tag']}")
    print(f"Дополнительных правил: {stats['additional_rules_count']}")


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description='Синхронизация заказов WooCommerce с LILU CRM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python scripts/sync_orders.py --new                    # Синхронизировать новые заказы
  python scripts/sync_orders.py --all                    # Синхронизировать все заказы
  python scripts/sync_orders.py --order-id 12345         # Синхронизировать конкретный заказ
  python scripts/sync_orders.py --stats                  # Показать статистику
  python scripts/sync_orders.py --new --status completed # Только завершенные заказы
  python scripts/sync_orders.py --new --limit 10         # Только 10 новых заказов
        """
    )
    
    parser.add_argument('--new', action='store_true', help='Синхронизировать новые заказы')
    parser.add_argument('--all', action='store_true', help='Синхронизировать все заказы')
    parser.add_argument('--order-id', type=int, help='ID заказа для синхронизации')
    parser.add_argument('--stats', action='store_true', help='Показать статистику')
    parser.add_argument('--status', type=str, help='Фильтр по статусу заказа')
    parser.add_argument('--limit', type=int, help='Лимит количества заказов (только для --new)')
    
    args = parser.parse_args()
    
    # Если нет аргументов, показываем help
    if not any([args.new, args.all, args.order_id, args.stats]):
        parser.print_help()
        return
    
    try:
        # Инициализация коннекторов
        print("Инициализация коннекторов...")
        wc_connector = WooCommerceConnector()
        lilu_connector = LILUConnector()
        
        # Создание сервиса синхронизации
        # Можно добавить дополнительные правила для тегов
        additional_rules = [
            # Пример: добавлять тег "vip" для заказов больше 10000
            {
                'tag': 'vip',
                'condition': {
                    'field': 'total',
                    'operator': '>',
                    'value': 10000
                }
            },
            # Пример: добавлять тег "completed" для завершенных заказов
            {
                'tag': 'completed',
                'condition': {
                    'field': 'status',
                    'operator': '==',
                    'value': 'completed'
                }
            }
        ]

        sync_service = SyncService(
            wc_connector=wc_connector,
            lilu_connector=lilu_connector,
            default_tag="api woo",
            additional_tag_rules=additional_rules
        )
        
        print("✅ Коннекторы инициализированы\n")
        
        # Выполняем действия
        if args.stats:
            show_statistics(sync_service)
        
        if args.new:
            sync_new_orders(sync_service, status=args.status, limit=args.limit)
        
        if args.all:
            sync_all_orders(sync_service, status=args.status)
        
        if args.order_id:
            sync_single_order(sync_service, args.order_id)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ошибка при выполнении синхронизации: {e}", exc_info=True)
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
