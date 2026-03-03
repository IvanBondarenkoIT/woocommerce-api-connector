"""
Ручной тест синхронизации (для проверки в реальных условиях).

Этот скрипт позволяет протестировать синхронизацию с реальными API
на небольшом количестве заказов.
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from woocommerce_connector.connector import WooCommerceConnector
from lilu_connector.connector import LILUConnector
from woocommerce_connector.services import SyncService
from woocommerce_connector.models.order import Order
from woocommerce_connector.utils.logger import get_logger

logger = get_logger(__name__)


def test_phone_normalization():
    """Тест нормализации телефонов."""
    print("\n" + "=" * 80)
    print("ТЕСТ НОРМАЛИЗАЦИИ ТЕЛЕФОНОВ")
    print("=" * 80 + "\n")
    
    from woocommerce_connector.utils.phone_normalizer import normalize_phone
    
    test_cases = [
        "8 (999) 123-45-67",
        "+7 999 123 45 67",
        "79991234567",
        "9991234567",
        "+79991234567"
    ]
    
    for phone in test_cases:
        normalized = normalize_phone(phone)
        print(f"  {phone:25} → {normalized}")
    
    print("\n✅ Тест нормализации завершен\n")


def test_single_order_sync():
    """Тест синхронизации одного заказа."""
    print("\n" + "=" * 80)
    print("ТЕСТ СИНХРОНИЗАЦИИ ОДНОГО ЗАКАЗА")
    print("=" * 80 + "\n")
    
    try:
        # Инициализация
        print("1. Инициализация коннекторов...")
        wc_connector = WooCommerceConnector()
        lilu_connector = LILUConnector()
        print("   ✅ Коннекторы инициализированы\n")
        
        # Получаем последний заказ
        print("2. Получение последнего заказа из WooCommerce...")
        response = wc_connector.get_orders(per_page=1, page=1)
        
        if not response or response.status_code != 200:
            print(f"   ❌ Ошибка получения заказов: {response.status_code if response else 'No response'}")
            return
        
        orders = response.json()
        if not orders:
            print("   ⚠️  Заказов не найдено")
            return
        
        order_data = orders[0]
        order = Order.from_dict(order_data)
        print(f"   ✅ Получен заказ #{order.id}\n")
        
        # Показываем информацию о заказе
        print("3. Информация о заказе:")
        print(f"   ID: {order.id}")
        print(f"   Статус: {order.status}")
        print(f"   Сумма: {order.total}")
        if order.billing:
            print(f"   Телефон: {order.billing.get('phone', 'не указан')}")
            print(f"   Имя: {order.customer_name}")
            print(f"   Email: {order.customer_email}")
        print()
        
        # Создаем сервис синхронизации
        print("4. Создание сервиса синхронизации...")
        sync_service = SyncService(
            wc_connector=wc_connector,
            lilu_connector=lilu_connector,
            default_tag="api woo"
        )
        print("   ✅ Сервис создан\n")
        
        # Синхронизируем
        print("5. Синхронизация заказа...")
        result = sync_service.sync_order(order)
        
        print(f"\n   Результат: {result}")
        if result.success:
            if result.action == "created":
                print(f"   ✅ Клиент создан в LILU")
            elif result.action == "updated":
                print(f"   ✅ Клиент обновлен в LILU")
            elif result.action == "skipped":
                print(f"   ⚠️  Заказ пропущен")
            
            if result.lilu_client_id:
                print(f"   LILU Client ID: {result.lilu_client_id}")
            if result.tags_added:
                print(f"   Добавлены теги: {', '.join(result.tags_added)}")
        else:
            print(f"   ❌ Ошибка: {result.error_message}")
        
        print("\n✅ Тест завершен\n")
    
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}", exc_info=True)
        print(f"\n❌ Ошибка: {e}\n")


def test_find_client_by_phone():
    """Тест поиска клиента по телефону."""
    print("\n" + "=" * 80)
    print("ТЕСТ ПОИСКА КЛИЕНТА ПО ТЕЛЕФОНУ")
    print("=" * 80 + "\n")
    
    try:
        lilu_connector = LILUConnector()
        
        # Тестовый телефон (замените на реальный из вашей базы)
        test_phone = input("Введите телефон для поиска (или нажмите Enter для пропуска): ").strip()
        
        if not test_phone:
            print("   ⚠️  Тест пропущен")
            return
        
        print(f"\nПоиск клиента с телефоном: {test_phone}")
        client = lilu_connector.find_client_by_phone(test_phone)
        
        if client:
            print(f"   ✅ Клиент найден:")
            print(f"      ID: {client.id}")
            print(f"      Имя: {client.name}")
            print(f"      Email: {client.email}")
            print(f"      Телефон: {client.phone}")
            print(f"      Теги: {', '.join(client.tags) if client.tags else 'нет'}")
        else:
            print(f"   ⚠️  Клиент не найден")
        
        print("\n✅ Тест завершен\n")
    
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}", exc_info=True)
        print(f"\n❌ Ошибка: {e}\n")


def main():
    """Главная функция."""
    print("\n" + "=" * 80)
    print("РУЧНОЕ ТЕСТИРОВАНИЕ СИНХРОНИЗАЦИИ")
    print("=" * 80)
    
    print("\nДоступные тесты:")
    print("1. Тест нормализации телефонов")
    print("2. Тест синхронизации одного заказа")
    print("3. Тест поиска клиента по телефону")
    print("4. Все тесты")
    
    choice = input("\nВыберите тест (1-4): ").strip()
    
    if choice == "1":
        test_phone_normalization()
    elif choice == "2":
        test_single_order_sync()
    elif choice == "3":
        test_find_client_by_phone()
    elif choice == "4":
        test_phone_normalization()
        test_single_order_sync()
        test_find_client_by_phone()
    else:
        print("Неверный выбор")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        print(f"\n❌ Критическая ошибка: {e}\n")
        sys.exit(1)
