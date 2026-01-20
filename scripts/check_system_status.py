#!/usr/bin/env python
"""
Проверка system_status для получения точной информации о количестве товаров.
"""

import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from woocommerce_connector.connector import WooCommerceConnector

def check_system_status():
    """Проверка system_status."""
    print("=" * 80)
    print("ПРОВЕРКА SYSTEM_STATUS")
    print("=" * 80)
    print()
    
    connector = WooCommerceConnector()
    wcapi = connector.wcapi
    
    try:
        response = wcapi.get('system_status')
        if response.status_code == 200:
            data = response.json()
            
            print("Информация из system_status:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
            print()
            
            # Ищем информацию о товарах
            if 'database' in data:
                db_info = data['database']
                print("Информация о базе данных:")
                for key, value in db_info.items():
                    if 'product' in key.lower() or 'post' in key.lower():
                        print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("ПРОВЕРКА ЧЕРЕЗ ПРЯМОЙ SQL ЗАПРОС (если доступно)")
    print("=" * 80)
    print()
    print("Если у вас есть доступ к базе данных, выполните:")
    print("  SELECT COUNT(*) FROM wp_posts WHERE post_type = 'product';")
    print("  SELECT COUNT(*) FROM wp_posts WHERE post_type = 'product' AND post_status = 'publish';")
    print("  SELECT COUNT(*) FROM wp_posts WHERE post_type = 'product_variation';")

if __name__ == "__main__":
    check_system_status()
