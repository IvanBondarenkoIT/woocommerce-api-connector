"""
Скрипт для создания тестового клиента в LILU API.

Для Junior разработчиков:
Этот скрипт создаёт тестового клиента в системе LILU.
Используйте его для проверки работы API.

Использование:
    python -m lilu_connector.scripts.create_client
"""

import sys
import os
import codecs
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Добавляем корневую директорию проекта в путь для импорта
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

# Загружаем .env файл из корня проекта
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


def create_test_client():
    """Создать тестового клиента"""
    
    print("=" * 80)
    print("СОЗДАНИЕ ТЕСТОВОГО КЛИЕНТА В LILU API")
    print("=" * 80)
    print()
    
    try:
        print("📋 Инициализация коннектора...")
        try:
            connector = LILUConnector()
        except ValueError as e:
            raise ConfigurationError(str(e))
        
        print("✅ Коннектор инициализирован")
        print()
        
        print("📋 Проверка подключения к API...")
        if not connector.health_check():
            print("⚠️  API недоступен, но продолжаем...")
        else:
            print("✅ API доступен")
        print()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        client_data = {
            'name': f'Тестовый клиент {timestamp}',
            'email': f'test_client_{timestamp}@example.com',
            'phone': '+79991234567',
            'status': 'active',
            'metadata': {
                'created_by': 'test_script',
                'created_at': datetime.now().isoformat(),
                'test': True
            }
        }
        
        print("📋 Данные тестового клиента:")
        print(f"   Имя: {client_data['name']}")
        print(f"   Email: {client_data['email']}")
        print(f"   Телефон: {client_data['phone']}")
        print(f"   Статус: {client_data['status']}")
        print()
        
        print("📋 Создание клиента в системе LILU...")
        try:
            new_client = connector.create_client(client_data)
            
            print("✅ КЛИЕНТ УСПЕШНО СОЗДАН!")
            print()
            print("📊 Информация о созданном клиенте:")
            print(f"   ID: {new_client.id}")
            print(f"   Имя: {new_client.name}")
            print(f"   Email: {new_client.email or 'не указан'}")
            print(f"   Телефон: {new_client.phone or 'не указан'}")
            print(f"   Активен: {'Да' if new_client.is_active else 'Нет'}")
            if new_client.tags:
                print(f"   Теги: {', '.join(new_client.tags)}")
            
            if new_client.created_at:
                print(f"   Создан: {new_client.created_at}")
            
            print()
            print("=" * 80)
            print("✅ ОПЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
            print("=" * 80)
            print()
            print(f"💡 Вы можете использовать ID {new_client.id} для дальнейшей работы с клиентом")
            
            connector.close()
            
            return new_client
        
        except LILUAPIError as e:
            print(f"❌ ОШИБКА ПРИ СОЗДАНИИ КЛИЕНТА:")
            print(f"   {e}")
            print()
            print("💡 Возможные причины:")
            print("   1. Клиент с таким email уже существует")
            print("   2. Неверный формат данных")
            print("   3. Недостаточно прав для создания клиентов")
            print("   4. Проблема на стороне API")
            sys.exit(1)
    
    except ConfigurationError as e:
        print("❌ ОШИБКА КОНФИГУРАЦИИ:")
        print(f"   {e}")
        print()
        print("💡 Решение:")
        print("   1. Убедитесь, что файл .env существует")
        print("   2. Проверьте, что в .env есть LILU_API_URL, LILU_API_KEY и LILU_API_SECRET")
        sys.exit(1)
    
    except AuthenticationError as e:
        print("❌ ОШИБКА АУТЕНТИФИКАЦИИ:")
        print(f"   {e}")
        print()
        print("💡 Решение:")
        print("   1. Проверьте правильность LILU_API_KEY и LILU_API_SECRET в .env")
        print("   2. Убедитесь, что ключи активны")
        sys.exit(1)
    
    except NetworkError as e:
        print("❌ ОШИБКА СЕТИ:")
        print(f"   {e}")
        print()
        print("💡 Решение:")
        print("   1. Проверьте интернет-соединение")
        print("   2. Проверьте правильность LILU_API_URL")
        sys.exit(1)
    
    except Exception as e:
        print("❌ НЕОЖИДАННАЯ ОШИБКА:")
        print(f"   {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    create_test_client()
