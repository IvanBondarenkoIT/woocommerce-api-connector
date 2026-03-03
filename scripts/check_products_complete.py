#!/usr/bin/env python
"""
Полная проверка всех товаров, включая вариации и все статусы.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from woocommerce_connector.connector import WooCommerceConnector

def check_all_products_complete():
    """Полная проверка всех товаров."""
    print("=" * 80)
    print("ПОЛНАЯ ПРОВЕРКА ВСЕХ ТОВАРОВ")
    print("=" * 80)
    print()
    
    connector = WooCommerceConnector()
    wcapi = connector.wcapi
    
    # 1. Проверяем все статусы
    print("1. Проверка товаров по статусам:")
    statuses_to_check = ['publish', 'draft', 'pending', 'private', 'any']
    
    for status in statuses_to_check:
        try:
            response = wcapi.get('products', params={
                'per_page': 1,
                'page': 1,
                'status': status
            })
            if response.status_code == 200:
                total = response.headers.get('X-WP-Total', 'N/A')
                print(f"   status={status:10} -> X-WP-Total: {total}")
        except Exception as e:
            print(f"   status={status:10} -> Ошибка: {e}")
    
    print()
    
    # 2. Получаем ВСЕ товары со статусом 'any'
    print("2. Получение ВСЕХ товаров (status=any):")
    all_products = []
    page = 1
    per_page = 100
    
    while True:
        response = wcapi.get('products', params={
            'per_page': per_page,
            'page': page,
            'status': 'any'
        })
        
        if response.status_code != 200:
            print(f"   Ошибка на странице {page}: {response.status_code}")
            break
        
        products = response.json()
        if not products:
            break
        
        all_products.extend(products)
        total_pages = int(response.headers.get('X-WP-TotalPages', 0))
        print(f"   Страница {page}/{total_pages}: {len(products)} товаров (всего: {len(all_products)})")
        
        if page >= total_pages or len(products) < per_page:
            break
        
        page += 1
    
    print(f"   Всего товаров: {len(all_products)}")
    print()
    
    # 3. Проверяем вариации товаров
    print("3. Проверка вариаций товаров:")
    variable_products = [p for p in all_products if p.get('type') == 'variable']
    print(f"   Товаров типа 'variable': {len(variable_products)}")
    
    # Получаем вариации для каждого variable продукта
    total_variations = 0
    for product in variable_products[:5]:  # Проверяем первые 5 для примера
        product_id = product.get('id')
        variations = product.get('variations', [])
        if variations:
            print(f"   Товар ID {product_id} ({product.get('name', 'N/A')}): {len(variations)} вариаций")
            total_variations += len(variations)
    
    print(f"   Всего вариаций (примерно): {total_variations}+")
    print()
    
    # 4. Проверяем через админку WooCommerce (если есть доступ)
    print("4. Сравнение с админкой WooCommerce:")
    print("   В админке WooCommerce может показываться:")
    print(f"   - Простые товары: {len([p for p in all_products if p.get('type') == 'simple'])}")
    print(f"   - Вариативные товары: {len(variable_products)}")
    print(f"   - Группированные товары: {len([p for p in all_products if p.get('type') == 'grouped'])}")
    print(f"   - Внешние товары: {len([p for p in all_products if p.get('type') == 'external'])}")
    print()
    print("   ⚠ ВАЖНО: В админке WooCommerce может показываться общее количество")
    print("   включая вариации. API возвращает только родительские товары.")
    print()
    
    # 5. Статистика по типам
    print("5. Статистика по типам товаров:")
    types = {}
    for product in all_products:
        ptype = product.get('type', 'unknown')
        types[ptype] = types.get(ptype, 0) + 1
    
    for ptype, count in sorted(types.items()):
        print(f"   - {ptype}: {count}")
    print()
    
    # 6. Проверяем, может быть есть товары, которые не возвращаются
    print("6. Проверка через разные endpoints:")
    
    # Проверяем общее количество через system_status (если доступно)
    try:
        response = wcapi.get('system_status')
        if response.status_code == 200:
            data = response.json()
            # Ищем информацию о товарах в system_status
            print("   system_status endpoint доступен")
    except:
        print("   system_status endpoint недоступен")
    
    print()
    print("=" * 80)
    print("ВЫВОД:")
    print("=" * 80)
    print(f"API возвращает: {len(all_products)} товаров")
    print("Это включает все статусы (publish, draft, pending, private)")
    print()
    print("Если в админке показывается ~500 товаров, возможно:")
    print("1. Считаются вариации отдельно (API возвращает только родительские товары)")
    print("2. Есть товары, которые не возвращаются через API (проверьте права доступа)")
    print("3. В админке показывается другое число (например, включая удаленные)")
    print()
    print("Для получения вариаций нужно делать отдельные запросы:")
    print("  GET /wp-json/wc/v3/products/{id}/variations")

if __name__ == "__main__":
    check_all_products_complete()
