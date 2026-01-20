#!/usr/bin/env python
"""
Скрипт для проверки получения ВСЕХ товаров через API.

Проверяет:
1. Общее количество товаров
2. Товары с разными статусами (publish, draft, etc.)
3. Товары с разными статусами остатков (instock, outofstock)
4. Сравнивает с тем, что возвращает API без фильтров
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from woocommerce_connector.connector import WooCommerceConnector
from woocommerce import API
import os
from dotenv import load_dotenv

load_dotenv()

def check_products_detailed():
    """Детальная проверка получения товаров."""
    print("=" * 80)
    print("ПРОВЕРКА ПОЛУЧЕНИЯ ВСЕХ ТОВАРОВ")
    print("=" * 80)
    print()
    
    try:
        connector = WooCommerceConnector()
        
        # 1. Получаем все товары через наш метод
        print("1. Получение товаров через get_all_products()...")
        all_products = connector.get_all_products(per_page=100)
        print(f"   Получено товаров: {len(all_products)}")
        print()
        
        # 2. Проверяем статусы товаров
        print("2. Анализ статусов товаров:")
        statuses = {}
        for product in all_products:
            status = product.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        for status, count in sorted(statuses.items()):
            print(f"   - {status}: {count}")
        print()
        
        # 3. Проверяем статусы остатков
        print("3. Анализ статусов остатков:")
        stock_statuses = {}
        for product in all_products:
            stock_status = product.get('stock_status', 'unknown')
            stock_statuses[stock_status] = stock_statuses.get(stock_status, 0) + 1
        
        for stock_status, count in sorted(stock_statuses.items()):
            print(f"   - {stock_status}: {count}")
        print()
        
        # 4. Проверяем товары с остатками > 0
        print("4. Товары с остатками:")
        in_stock_count = sum(1 for p in all_products if p.get('stock_quantity') is not None and p.get('stock_quantity', 0) > 0)
        out_of_stock_count = sum(1 for p in all_products if p.get('stock_quantity') is not None and p.get('stock_quantity', 0) == 0)
        no_stock_info = sum(1 for p in all_products if p.get('stock_quantity') is None)
        
        print(f"   - С остатками > 0: {in_stock_count}")
        print(f"   - С остатками = 0: {out_of_stock_count}")
        print(f"   - Без информации об остатках: {no_stock_info}")
        print()
        
        # 5. Пробуем получить товары с разными фильтрами напрямую через API
        print("5. Проверка через прямой API запрос с разными параметрами:")
        
        wcapi = connector.wcapi
        
        # Без фильтров
        print("   a) Без фильтров (по умолчанию):")
        response = wcapi.get('products', params={'per_page': 1, 'page': 1})
        if response.status_code == 200:
            # Проверяем заголовки для общего количества
            total_products = response.headers.get('X-WP-Total')
            total_pages = response.headers.get('X-WP-TotalPages')
            print(f"      X-WP-Total: {total_products}")
            print(f"      X-WP-TotalPages: {total_pages}")
        
        # С явным указанием status=publish
        print("   b) С фильтром status=publish:")
        response = wcapi.get('products', params={'per_page': 1, 'page': 1, 'status': 'publish'})
        if response.status_code == 200:
            total = response.headers.get('X-WP-Total')
            print(f"      X-WP-Total: {total}")
        
        # С фильтром stock_status=instock
        print("   c) С фильтром stock_status=instock:")
        response = wcapi.get('products', params={'per_page': 1, 'page': 1, 'stock_status': 'instock'})
        if response.status_code == 200:
            total = response.headers.get('X-WP-Total')
            print(f"      X-WP-Total: {total}")
        
        # Все статусы (publish, draft, pending, private)
        print("   d) Все статусы (без фильтра по status):")
        # WooCommerce по умолчанию возвращает только publish, нужно явно указать
        response = wcapi.get('products', params={'per_page': 1, 'page': 1, 'status': 'any'})
        if response.status_code == 200:
            total = response.headers.get('X-WP-Total')
            print(f"      X-WP-Total (status=any): {total}")
        
        print()
        
        # 6. Получаем ВСЕ товары включая draft, pending, private
        print("6. Получение ВСЕХ товаров (включая draft, pending, private)...")
        all_products_all_statuses = []
        page = 1
        per_page = 100
        
        while True:
            response = wcapi.get('products', params={
                'per_page': per_page,
                'page': page,
                'status': 'any'  # Получить все статусы
            })
            
            if response.status_code != 200:
                break
            
            products = response.json()
            if not products:
                break
            
            all_products_all_statuses.extend(products)
            
            total_pages = int(response.headers.get('X-WP-TotalPages', 0))
            print(f"   Страница {page}/{total_pages}: {len(products)} товаров (всего: {len(all_products_all_statuses)})")
            
            if page >= total_pages or len(products) < per_page:
                break
            
            page += 1
        
        print(f"   Всего товаров (все статусы): {len(all_products_all_statuses)}")
        print()
        
        # 7. Сравнение
        print("7. СРАВНЕНИЕ:")
        print(f"   Товаров через get_all_products(): {len(all_products)}")
        print(f"   Товаров со статусом 'any': {len(all_products_all_statuses)}")
        print(f"   Разница: {len(all_products_all_statuses) - len(all_products)}")
        print()
        
        if len(all_products_all_statuses) > len(all_products):
            print("   ⚠ ВНИМАНИЕ: Есть товары, которые не получены через get_all_products()")
            print("   Причина: get_all_products() получает только товары со статусом 'publish'")
            print("   (это стандартное поведение WooCommerce API)")
            print()
            
            # Показываем какие статусы пропущены
            all_statuses = {}
            for product in all_products_all_statuses:
                status = product.get('status', 'unknown')
                all_statuses[status] = all_statuses.get(status, 0) + 1
            
            print("   Статусы всех товаров:")
            for status, count in sorted(all_statuses.items()):
                print(f"     - {status}: {count}")
        else:
            print("   ✓ Все товары получены")
        
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_products_detailed()
