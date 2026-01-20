#!/usr/bin/env python
"""
Скрипт для проверки подключения к WooCommerce API и получения всех товаров.

Этот скрипт:
1. Проверяет подключение к WooCommerce API
2. Получает весь список товаров с пагинацией
3. Выводит информацию о товарах
4. Помогает диагностировать проблемы с подключением

Использование:
    python scripts/test_connection_and_products.py
"""

import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from woocommerce_connector.connector import WooCommerceConnector
from woocommerce_connector.config import WooCommerceConfig
from woocommerce_connector.api.exceptions import (
    ConfigurationError,
    AuthenticationError,
    APIResponseError,
    NetworkError
)


def test_connection():
    """Тест подключения к WooCommerce API."""
    print("=" * 80)
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К WOOCOMMERCE API")
    print("=" * 80)
    print()
    
    try:
        # 1. Проверка конфигурации
        print("1. Проверка конфигурации...")
        try:
            config = WooCommerceConfig.from_env()
            config.validate()
            print(f"   ✓ URL: {config.url}")
            print(f"   ✓ API Version: {config.api_version}")
            print(f"   ✓ Consumer Key: {config.consumer_key[:10]}...")
            print(f"   ✓ Consumer Secret: {config.consumer_secret[:10]}...")
        except ConfigurationError as e:
            print(f"   ✗ Ошибка конфигурации: {e}")
            print("\nПроверьте .env файл:")
            print("  - WC_URL=https://your-store.com")
            print("  - WC_CONSUMER_KEY=ck_...")
            print("  - WC_CONSUMER_SECRET=cs_...")
            print("  - WC_API_VERSION=wc/v3")
            return False
        except Exception as e:
            print(f"   ✗ Неожиданная ошибка: {e}")
            return False
        
        print()
        
        # 2. Инициализация подключения
        print("2. Инициализация подключения...")
        try:
            connector = WooCommerceConnector()
            print("   ✓ Подключение инициализировано")
        except Exception as e:
            print(f"   ✗ Ошибка инициализации: {e}")
            return False
        
        print()
        
        # 3. Тест простого запроса (получение одной страницы)
        print("3. Тест простого запроса (первая страница, 10 товаров)...")
        try:
            response = connector.get_products(per_page=10, page=1)
            if response and response.status_code == 200:
                products = response.json()
                print(f"   ✓ Успешно получено {len(products)} товаров")
                if products:
                    print(f"   ✓ Пример товара: {products[0].get('name', 'N/A')}")
            else:
                print(f"   ✗ Ошибка: Status {response.status_code if response else 'No response'}")
                return False
        except AuthenticationError as e:
            print(f"   ✗ Ошибка аутентификации: {e}")
            print("\nПроверьте:")
            print("  - Правильность Consumer Key и Consumer Secret")
            print("  - Права доступа API ключа (должен быть Read или Read/Write)")
            return False
        except APIResponseError as e:
            print(f"   ✗ Ошибка API: {e}")
            return False
        except NetworkError as e:
            print(f"   ✗ Ошибка сети: {e}")
            print("\nПроверьте:")
            print("  - Подключение к интернету")
            print("  - Доступность URL магазина")
            return False
        except Exception as e:
            print(f"   ✗ Неожиданная ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print()
        
        # 4. Получение всех товаров с пагинацией
        print("4. Получение ВСЕХ товаров с пагинацией...")
        try:
            all_products = connector.get_all_products(per_page=100)
            print(f"   ✓ Всего получено товаров: {len(all_products)}")
            
            if all_products:
                # Статистика
                print("\n   Статистика:")
                print(f"     - Товаров в наличии: {sum(1 for p in all_products if p.get('stock_status') == 'instock')}")
                print(f"     - Товаров нет в наличии: {sum(1 for p in all_products if p.get('stock_status') == 'outofstock')}")
                print(f"     - Товаров со SKU: {sum(1 for p in all_products if p.get('sku'))}")
                print(f"     - Товаров с управлением складом: {sum(1 for p in all_products if p.get('manage_stock'))}")
                
                # Примеры товаров
                print("\n   Примеры товаров (первые 5):")
                for i, product in enumerate(all_products[:5], 1):
                    print(f"     {i}. {product.get('name', 'N/A')}")
                    print(f"        ID: {product.get('id')}, SKU: {product.get('sku', 'N/A')}")
                    print(f"        Остаток: {product.get('stock_quantity', 'N/A')}")
                    print(f"        Статус: {product.get('stock_status', 'N/A')}")
                    print(f"        Цена: {product.get('price', 'N/A')}")
                    if product.get('sale_price'):
                        print(f"        Цена со скидкой: {product.get('sale_price')}")
                    print()
        except Exception as e:
            print(f"   ✗ Ошибка при получении всех товаров: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print()
        print("=" * 80)
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО")
        print("=" * 80)
        return True
        
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        return False
    except Exception as e:
        print(f"\n✗ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_api_details():
    """Показать детали API подключения."""
    print("\n" + "=" * 80)
    print("ДЕТАЛИ API ПОДКЛЮЧЕНИЯ")
    print("=" * 80)
    print()
    
    try:
        config = WooCommerceConfig.from_env()
        connector = WooCommerceConnector()
        
        print("Конфигурация:")
        print(f"  URL: {config.url}")
        print(f"  API Version: {config.api_version}")
        print(f"  Timeout: {config.timeout}s")
        print(f"  Query String Auth: {config.query_string_auth}")
        print()
        
        print("Методы получения товаров:")
        print("  1. get_products(per_page=10, page=1)")
        print("     - Получает одну страницу товаров")
        print("     - Возвращает Response объект")
        print()
        print("  2. get_all_products(per_page=100)")
        print("     - Получает ВСЕ товары с автоматической пагинацией")
        print("     - Возвращает List[Dict] со всеми товарами")
        print()
        
        print("Как работает пагинация:")
        print("  - WooCommerce API возвращает максимум 100 товаров на страницу")
        print("  - get_all_products() автоматически запрашивает все страницы")
        print("  - Останавливается, когда получено меньше товаров, чем per_page")
        print()
        
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    success = test_connection()
    
    if success:
        show_api_details()
    
    sys.exit(0 if success else 1)
