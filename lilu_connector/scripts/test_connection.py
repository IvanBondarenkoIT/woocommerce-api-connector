"""
Тестовый скрипт для проверки подключения к LILU API.

Для Junior разработчиков:
Этот скрипт проверяет, что подключение к API работает правильно.
Запустите его после настройки .env файла.

Использование:
    python -m lilu_connector.scripts.test_connection
    или из корня проекта:
    python -m lilu_connector.scripts.test_connection
"""

import sys
import os
import codecs

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Добавляем корневую директорию проекта в путь для импорта
# Скрипт находится в lilu_connector/scripts/, нужно подняться на 3 уровня вверх
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

# Загружаем .env из корня проекта
from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from lilu_connector import LILUConnector
from lilu_connector.api.exceptions import (
    AuthenticationError,
    NetworkError,
    ConfigurationError,
    LILUAPIError,
)
from lilu_connector.config.settings import LILUSettings


def test_connection():
    """Проверить подключение к LILU API"""
    
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ К LILU API")
    print("=" * 80)
    print()
    
    try:
        # Шаг 1: Инициализация коннектора
        print("📋 Шаг 1: Инициализация коннектора...")
        try:
            connector = LILUConnector()
        except ValueError as e:
            # ValueError из LILUSettings._validate() - это ConfigurationError
            raise ConfigurationError(str(e))
        
        print("✅ Коннектор успешно инициализирован")
        print(f"   URL: {connector.settings.api_url}")
        print(f"   Версия API: {connector.settings.api_version}")
        print()
        
        # Шаг 2: Проверка доступности API
        print("📋 Шаг 2: Проверка доступности API (health check)...")
        if connector.health_check():
            print("✅ API доступен и отвечает")
        else:
            print("⚠️  API недоступен или не отвечает")
        print()
        
        # Шаг 3: Получение категорий шаблонов (работающий endpoint)
        print("📋 Шаг 3: Получение категорий шаблонов сообщений...")
        try:
            categories = connector.get_template_categories()
            print(f"✅ Успешно получено категорий: {len(categories)}")
            
            if categories:
                print("\n   Первые категории:")
                for i, category in enumerate(categories[:3], 1):
                    name = category.get('name', 'Без названия') if isinstance(category, dict) else str(category)
                    print(f"   {i}. {name}")
        except Exception as e:
            print(f"⚠️  Не удалось получить категории: {e}")
        print()
        
        # Шаг 4: Получение списка клиентов
        print("📋 Шаг 4: Получение списка клиентов...")
        try:
            clients = connector.get_clients(limit=5)
            print(f"✅ Успешно получено {len(clients)} клиентов")
            
            if clients:
                print("\n   Первые клиенты:")
                for i, client in enumerate(clients[:3], 1):
                    print(f"   {i}. {client.name} ({client.email})")
            else:
                print("   ⚠️  Клиенты не найдены")
        except Exception as e:
            print(f"⚠️  Не удалось получить клиентов: {e}")
        print()
        
        # Шаг 5: Получение списка продуктов
        print("📋 Шаг 5: Получение списка продуктов...")
        try:
            products = connector.get_products(limit=5)
            print(f"✅ Успешно получено {len(products)} продуктов")
            
            if products:
                print("\n   Первые продукты:")
                for i, product in enumerate(products[:3], 1):
                    print(f"   {i}. {product.name} - {product.price} руб.")
        except Exception as e:
            print(f"⚠️  Не удалось получить продукты: {e}")
        print()
        
        print("=" * 80)
        print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
        print("=" * 80)
        
        # Закрываем соединение
        connector.close()
        
    except ConfigurationError as e:
        print("❌ ОШИБКА КОНФИГУРАЦИИ:")
        print(f"   {e}")
        print()
        print("💡 Решение:")
        print("   1. Убедитесь, что файл .env существует")
        print("   2. Проверьте, что в .env есть LILU_API_URL, LILU_API_KEY и LILU_API_SECRET")
        print("   3. Убедитесь, что значения не содержат лишних пробелов")
        sys.exit(1)
    
    except AuthenticationError as e:
        print("❌ ОШИБКА АУТЕНТИФИКАЦИИ:")
        print(f"   {e}")
        print()
        print("💡 Решение:")
        print("   1. Проверьте правильность LILU_API_KEY и LILU_API_SECRET в .env")
        print("   2. Убедитесь, что ключи активны в личном кабинете LILU")
        print("   3. Проверьте, что ключи не истёк")
        sys.exit(1)
    
    except NetworkError as e:
        print("❌ ОШИБКА СЕТИ:")
        print(f"   {e}")
        print()
        print("💡 Решение:")
        print("   1. Проверьте интернет-соединение")
        print("   2. Проверьте правильность LILU_API_URL")
        print("   3. Попробуйте увеличить LILU_TIMEOUT в .env")
        sys.exit(1)
    
    except Exception as e:
        print("❌ НЕОЖИДАННАЯ ОШИБКА:")
        print(f"   {e}")
        print()
        print("💡 Проверьте логи для получения дополнительной информации")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_connection()
