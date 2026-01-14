"""
Проверка конкретных заказов из уведомлений Telegram бота
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from woocommerce_connector.connector import WooCommerceConnector
from woocommerce_connector.api.exceptions import ConfigurationError, APIResponseError, NotFoundError


def format_date(date_str: str) -> str:
    """Форматирует дату для отображения"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d %B %Y, %I:%M %p")
    except:
        return date_str


def check_order(connector, order_id: int):
    """Проверить конкретный заказ"""
    try:
        print(f"\n{'='*80}")
        print(f"ПРОВЕРКА ЗАКАЗА #{order_id}")
        print(f"{'='*80}\n")
        
        order = connector.get_order_by_id(order_id)
        
        if not order:
            print(f"❌ Заказ #{order_id} не найден")
            return
        
        # Основная информация
        status = order.get('status', 'N/A')
        total = order.get('total', '0')
        currency = order.get('currency', 'GEL')
        date_created = format_date(order.get('date_created', ''))
        
        # Информация о клиенте
        billing = order.get('billing', {})
        customer_name = f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip()
        customer_email = billing.get('email', 'N/A')
        customer_phone = billing.get('phone', 'N/A')
        
        # Способ оплаты
        payment_method = order.get('payment_method_title', 'N/A')
        payment_status = "Paid" if order.get('date_paid') else "NOT Paid"
        
        # Товары
        line_items = order.get('line_items', [])
        
        print(f"📦 Заказ #{order.get('id', 'N/A')}")
        print(f"   Статус: {status.upper()}")
        print(f"   Дата создания: {date_created}")
        print(f"   Сумма: {total} {currency}")
        print(f"   Оплата: {payment_status} ({payment_method})")
        print()
        print(f"👤 Клиент:")
        print(f"   Имя: {customer_name}")
        print(f"   Email: {customer_email}")
        print(f"   Телефон: {customer_phone}")
        print()
        print(f"🛒 Товары ({len(line_items)} шт.):")
        print("   " + "-" * 76)
        
        total_items = 0
        for item in line_items:
            name = item.get('name', 'N/A')
            qty = item.get('quantity', 0)
            price = item.get('price', '0')
            subtotal = item.get('subtotal', '0')
            total_items += qty
            
            print(f"   {qty} x {name}")
            print(f"      Цена за единицу: {price} {currency}")
            print(f"      Сумма: {subtotal} {currency}")
            print()
        
        print(f"   Всего товаров: {total_items} шт.")
        print("   " + "-" * 76)
        
        # Доставка
        shipping = order.get('shipping', {})
        shipping_address = shipping.get('address_1', '')
        shipping_total = order.get('shipping_total', '0')
        
        if shipping_address:
            print(f"\n🚚 Доставка:")
            print(f"   Адрес: {shipping_address}")
            if shipping_total and float(shipping_total) > 0:
                print(f"   Стоимость доставки: {shipping_total} {currency}")
        
        # Дополнительная информация
        customer_id = order.get('customer_id', 0)
        if customer_id > 0:
            print(f"\n📊 Дополнительно:")
            print(f"   Customer ID: {customer_id}")
        
        print(f"\n{'='*80}")
        
        return order
        
    except NotFoundError as e:
        print(f"❌ Заказ #{order_id} не найден: {e}")
    except Exception as e:
        print(f"❌ Ошибка при получении заказа #{order_id}: {e}")


def main():
    """Проверить конкретные заказы"""
    try:
        print("\n" + "="*80)
        print("ПРОВЕРКА ЗАКАЗОВ ИЗ TELEGRAM УВЕДОМЛЕНИЙ")
        print("="*80)
        
        connector = WooCommerceConnector()
        
        # Заказы из уведомлений
        order_ids = [7848, 7840, 7833]
        
        for order_id in order_ids:
            check_order(connector, order_id)
        
        print("\n✅ Проверка завершена!")
        print("="*80 + "\n")
        
    except ConfigurationError as e:
        print(f"\n❌ Ошибка конфигурации: {e}")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
