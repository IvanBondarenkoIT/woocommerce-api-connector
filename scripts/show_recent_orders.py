"""
Быстрый просмотр последних заказов из WooCommerce
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from woocommerce_connector.connector import WooCommerceConnector
from woocommerce_connector.api.exceptions import ConfigurationError, APIResponseError


def format_date(date_str: str) -> str:
    """Форматирует дату для отображения"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return date_str


def main():
    """Показать последние заказы"""
    try:
        print("\n" + "=" * 80)
        print("ПОСЛЕДНИЕ ЗАКАЗЫ ИЗ WOOCOMMERCE")
        print("=" * 80 + "\n")
        
        connector = WooCommerceConnector()
        
        # Получаем последние 20 заказов
        print("Загрузка последних заказов...")
        response = connector.get_orders(per_page=20, page=1)
        
        if not response or response.status_code != 200:
            print(f"❌ Ошибка получения заказов: {response.status_code if response else 'No response'}")
            return
        
        orders = response.json()
        
        if not orders:
            print("⚠️  Заказов не найдено")
            return
        
        print(f"✅ Найдено заказов: {len(orders)}\n")
        print("-" * 80)
        
        for order in orders:
            order_id = order.get('id', 'N/A')
            status = order.get('status', 'N/A')
            total = order.get('total', '0')
            currency = order.get('currency', 'GEL')
            date_created = format_date(order.get('date_created', ''))
            
            billing = order.get('billing', {})
            customer_name = f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip()
            customer_email = billing.get('email', 'N/A')
            customer_phone = billing.get('phone', 'N/A')
            
            line_items = order.get('line_items', [])
            items_summary = []
            for item in line_items[:2]:  # Первые 2 товара
                name = item.get('name', 'N/A')
                qty = item.get('quantity', 0)
                items_summary.append(f"{name} (x{qty})")
            
            items_text = ", ".join(items_summary)
            if len(line_items) > 2:
                items_text += f" + еще {len(line_items) - 2}"
            
            # Статус с цветом (в консоли)
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄',
                'completed': '✅',
                'cancelled': '❌',
                'refunded': '↩️',
                'on-hold': '⏸️'
            }.get(status, '❓')
            
            print(f"\n📦 Заказ #{order_id} {status_emoji} [{status.upper()}]")
            print(f"   💰 {total} {currency} | 📅 {date_created}")
            print(f"   👤 {customer_name or 'Без имени'}")
            print(f"   📧 {customer_email}")
            if customer_phone and customer_phone != 'N/A':
                print(f"   📞 {customer_phone}")
            print(f"   🛒 {items_text}")
            print("-" * 80)
        
        # Статистика по статусам
        status_counts = {}
        for order in orders:
            status = order.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("\n📊 Статистика по статусам:")
        for status, count in sorted(status_counts.items()):
            emoji = {
                'pending': '⏳',
                'processing': '🔄',
                'completed': '✅',
                'cancelled': '❌',
                'refunded': '↩️',
                'on-hold': '⏸️'
            }.get(status, '❓')
            print(f"   {emoji} {status}: {count}")
        
        print("\n" + "=" * 80)
        
    except ConfigurationError as e:
        print(f"\n❌ Ошибка конфигурации: {e}")
    except APIResponseError as e:
        print(f"\n❌ Ошибка API: {e}")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
