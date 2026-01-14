"""
Скрипт для тестирования получения заказов из WooCommerce
"""
import sys
import json
from datetime import datetime
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from woocommerce_connector.connector import WooCommerceConnector
from woocommerce_connector.api.exceptions import (
    ConfigurationError,
    APIResponseError,
    NetworkError
)


def main():
    """Тестирование получения заказов"""
    try:
        print("=" * 80)
        print("ТЕСТИРОВАНИЕ ПОЛУЧЕНИЯ ЗАКАЗОВ ИЗ WOOCOMMERCE")
        print("=" * 80)
        print()
        
        # Инициализация подключения
        print("1. Инициализация подключения...")
        connector = WooCommerceConnector()
        print("   ✅ Подключение установлено")
        print()
        
        # Получаем последние заказы
        print("2. Получение последних заказов...")
        response = connector.get_orders(per_page=10, page=1)
        
        if not response or response.status_code != 200:
            print(f"   ❌ Ошибка: {response.status_code if response else 'No response'}")
            return
        
        orders = response.json()
        print(f"   ✅ Получено заказов: {len(orders)}")
        print()
        
        if not orders:
            print("   ⚠️  Заказов не найдено. Создайте несколько заказов в WooCommerce для тестирования.")
            return
        
        # Отображаем информацию о заказах
        print("3. Информация о заказах:")
        print("=" * 80)
        
        for idx, order in enumerate(orders, 1):
            order_id = order.get('id', 'N/A')
            status = order.get('status', 'N/A')
            total = order.get('total', '0')
            currency = order.get('currency', 'GEL')
            date_created = order.get('date_created', 'N/A')
            
            # Информация о клиенте
            customer_id = order.get('customer_id', 0)
            billing = order.get('billing', {})
            customer_name = billing.get('first_name', '') + ' ' + billing.get('last_name', '')
            customer_email = billing.get('email', 'N/A')
            
            # Количество товаров
            line_items = order.get('line_items', [])
            items_count = len(line_items)
            
            print(f"\n{idx}. Заказ #{order_id}")
            print(f"   Статус: {status}")
            print(f"   Дата создания: {date_created}")
            print(f"   Сумма: {total} {currency}")
            print(f"   Клиент ID: {customer_id}")
            print(f"   Имя: {customer_name.strip() or 'N/A'}")
            print(f"   Email: {customer_email}")
            print(f"   Товаров в заказе: {items_count}")
            
            # Список товаров
            if line_items:
                print("   Товары:")
                for item in line_items[:3]:  # Показываем первые 3 товара
                    item_name = item.get('name', 'N/A')
                    item_qty = item.get('quantity', 0)
                    item_price = item.get('price', '0')
                    print(f"      - {item_name} (x{item_qty}) - {item_price} {currency}")
                if len(line_items) > 3:
                    print(f"      ... и еще {len(line_items) - 3} товаров")
        
        print("\n" + "=" * 80)
        
        # Сохраняем в JSON для детального анализа
        output_dir = Path(__file__).parent.parent / "data" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"orders_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)
        
        print(f"4. Данные сохранены в: {output_file}")
        print()
        
        # Получаем все заказы (если нужно)
        print("5. Получение всех заказов (может занять время)...")
        try:
            all_orders = connector.get_all_orders(per_page=100)
            print(f"   ✅ Всего заказов в магазине: {len(all_orders)}")
            
            # Сохраняем все заказы
            all_orders_file = output_dir / f"all_orders_{timestamp}.json"
            with open(all_orders_file, 'w', encoding='utf-8') as f:
                json.dump(all_orders, f, indent=2, ensure_ascii=False)
            print(f"   ✅ Все заказы сохранены в: {all_orders_file}")
        except Exception as e:
            print(f"   ⚠️  Ошибка при получении всех заказов: {e}")
        
        print("\n" + "=" * 80)
        print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 80)
        
    except ConfigurationError as e:
        print(f"\n❌ Ошибка конфигурации: {e}")
        print("\nПроверьте файл .env и убедитесь, что все переменные установлены.")
    except APIResponseError as e:
        print(f"\n❌ Ошибка API: {e}")
    except NetworkError as e:
        print(f"\n❌ Ошибка сети: {e}")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
