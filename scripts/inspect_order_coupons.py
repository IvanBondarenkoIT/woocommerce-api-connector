"""
Скрипт для проверки структуры coupon_lines в ответе WooCommerce API.

Показывает заказы с купонами и структуру данных купонов.
Использование:
    python scripts/inspect_order_coupons.py
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from woocommerce_connector.connector import WooCommerceConnector
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 60)
    print("Инспекция coupon_lines в заказах WooCommerce")
    print("=" * 60)
    
    wc = WooCommerceConnector()
    
    # Получаем последние 50 заказов
    response = wc.get_orders(per_page=50, page=1)
    if not response or response.status_code != 200:
        print("Ошибка получения заказов")
        return
    
    orders = response.json()
    orders_with_coupons = [o for o in orders if o.get('coupon_lines')]
    
    print(f"\nВсего заказов: {len(orders)}")
    print(f"Заказов с купонами: {len(orders_with_coupons)}")
    
    if not orders_with_coupons:
        print("\nКупонов не найдено в последних заказах.")
        return
    
    print("\n" + "-" * 60)
    print("ПРИМЕРЫ СТРУКТУРЫ coupon_lines:")
    print("-" * 60)
    
    for i, order in enumerate(orders_with_coupons[:5]):  # Показать первые 5
        order_id = order.get('id')
        coupon_lines = order.get('coupon_lines', [])
        
        print(f"\n--- Заказ #{order_id} ---")
        print(f"  discount_total: {order.get('discount_total')}")
        print(f"  coupon_lines ({len(coupon_lines)} шт):")
        
        for j, cl in enumerate(coupon_lines):
            print(f"    [{j}] {json.dumps(cl, indent=6, ensure_ascii=False)}")
    
    print("\n" + "=" * 60)
    print("ВЫВОД: Как вычленить заказы с купоном -15%:")
    print("=" * 60)
    print("""
Варианты фильтрации:

1. По coupon_lines:
   - Если coupon_lines не пустой - заказ со скидкой
   - В каждом элементе может быть:
     * code - код купона (например "first_order_15")
     * meta_data - метаданные, могут содержать discount_type, nominal_amount

2. По discount_total:
   - discount_total > "0" - заказ со скидкой

3. Комбинация: coupon_lines не пустой И discount_total > 0

Для фильтра "-15%" нужно проверить:
   - code содержит "15" или похожий идентификатор
   - ИЛИ в meta_data nominal_amount/discount_type указывает на 15%
   - ИЛИ discount_total показывает скидку ~15% от суммы заказа
""")


if __name__ == "__main__":
    main()
