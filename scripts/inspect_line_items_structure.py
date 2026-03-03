"""
Скрипт для проверки структуры line_items в заказах WooCommerce.
Проверяем, есть ли в line_items информация о категориях товаров.
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from woocommerce_connector.connector import WooCommerceConnector
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 70)
    print("Структура line_items и категории товаров в WooCommerce")
    print("=" * 70)
    
    wc = WooCommerceConnector()
    
    # Получаем один заказ с товарами
    response = wc.get_orders(per_page=1, page=1)
    if not response or response.status_code != 200:
        print("Ошибка получения заказов")
        return
    
    orders = response.json()
    if not orders:
        print("Нет заказов")
        return
    
    order = orders[0]
    order_id = order['id']
    line_items = order.get('line_items', [])
    
    print(f"\nЗаказ #{order_id}, товаров: {len(line_items)}")
    print("\n--- Структура первого line_item (все поля) ---\n")
    
    if line_items:
        item = line_items[0]
        print(json.dumps(item, indent=2, ensure_ascii=False))
        
        product_id = item.get('product_id')
        print(f"\n--- Получение категорий товара product_id={product_id} ---\n")
        
        # Получаем полные данные товара
        try:
            product = wc.get_product_fields(product_id)
            if product:
                print("Продукт:", product.get('name'))
                print("Категории:", product.get('categories', []))
        except Exception as e:
            print("Ошибка:", e)
    
    # Проверим WooCommerce products/categories API
    print("\n" + "=" * 70)
    print("Категории товаров в магазине (GET /products/categories)")
    print("=" * 70)
    
    try:
        cat_response = wc.wcapi.get('products/categories', params={'per_page': 20})
        if cat_response.status_code == 200:
            categories = cat_response.json()
            for c in categories[:15]:
                print(f"  ID={c.get('id')}  slug={c.get('slug')}  name={c.get('name')}")
        else:
            print(f"Ошибка: {cat_response.status_code}")
    except Exception as e:
        print("Ошибка:", e)

if __name__ == "__main__":
    main()
