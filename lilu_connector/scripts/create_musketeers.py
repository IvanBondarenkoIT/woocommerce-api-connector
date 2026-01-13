"""
Скрипт для создания тестовых клиентов - мушкетеров.

Создает 4 клиента с именами мушкетеров и вымышленными данными.

Использование:
    python -m lilu_connector.scripts.create_musketeers
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


def create_musketeers():
    """Создать 4 клиентов-мушкетеров"""
    
    print("=" * 80)
    print("СОЗДАНИЕ ТЕСТОВЫХ КЛИЕНТОВ - МУШКЕТЕРЫ")
    print("=" * 80)
    print()
    
    # Данные мушкетеров
    musketeers = [
        {
            'name': "Д'Артаньян",
            'email': 'dartagnan.musketeer@example.com',
            'phone': '+33123456789',
            'tags': ['мушкетер', 'лидер', 'тестовый'],
            'metadata': {
                'character': 'D\'Artagnan',
                'role': 'Musketeer',
                'created_by': 'test_script',
                'created_at': datetime.now().isoformat(),
                'test': True
            }
        },
        {
            'name': 'Атос',
            'email': 'athos.musketeer@example.com',
            'phone': '+33123456790',
            'tags': ['мушкетер', 'аристократ', 'тестовый'],
            'metadata': {
                'character': 'Athos',
                'role': 'Musketeer',
                'created_by': 'test_script',
                'created_at': datetime.now().isoformat(),
                'test': True
            }
        },
        {
            'name': 'Портос',
            'email': 'porthos.musketeer@example.com',
            'phone': '+33123456791',
            'tags': ['мушкетер', 'силач', 'тестовый'],
            'metadata': {
                'character': 'Porthos',
                'role': 'Musketeer',
                'created_by': 'test_script',
                'created_at': datetime.now().isoformat(),
                'test': True
            }
        },
        {
            'name': 'Арамис',
            'email': 'aramis.musketeer@example.com',
            'phone': '+33123456792',
            'tags': ['мушкетер', 'священник', 'тестовый'],
            'metadata': {
                'character': 'Aramis',
                'role': 'Musketeer',
                'created_by': 'test_script',
                'created_at': datetime.now().isoformat(),
                'test': True
            }
        }
    ]
    
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
        
        created_clients = []
        failed_clients = []
        
        print("📋 Создание клиентов-мушкетеров...")
        print()
        
        for i, musketeer_data in enumerate(musketeers, 1):
            print(f"   {i}. Создание клиента: {musketeer_data['name']}...", end=" ")
            
            try:
                new_client = connector.create_client(musketeer_data)
                created_clients.append(new_client)
                print("✅ Успешно")
                print(f"      ID: {new_client.id}")
                print(f"      Email: {new_client.email}")
                print(f"      Телефон: {new_client.phone}")
                if new_client.tags:
                    print(f"      Теги: {', '.join(new_client.tags)}")
                print()
            except LILUAPIError as e:
                failed_clients.append((musketeer_data['name'], str(e)))
                print(f"❌ Ошибка: {e}")
                print()
            except Exception as e:
                failed_clients.append((musketeer_data['name'], str(e)))
                print(f"❌ Неожиданная ошибка: {e}")
                print()
        
        print("=" * 80)
        print("📊 РЕЗУЛЬТАТЫ СОЗДАНИЯ")
        print("=" * 80)
        print()
        
        print(f"✅ Успешно создано: {len(created_clients)} клиентов")
        if created_clients:
            print()
            print("📋 Созданные клиенты:")
            for i, client in enumerate(created_clients, 1):
                print(f"   {i}. {client.name}")
                print(f"      ID: {client.id}")
                print(f"      Email: {client.email or 'не указан'}")
                print(f"      Телефон: {client.phone or 'не указан'}")
                print()
        
        if failed_clients:
            print(f"❌ Не удалось создать: {len(failed_clients)} клиентов")
            print()
            print("📋 Ошибки:")
            for name, error in failed_clients:
                print(f"   - {name}: {error}")
            print()
        
        print("=" * 80)
        print("✅ ОПЕРАЦИЯ ЗАВЕРШЕНА")
        print("=" * 80)
        
        connector.close()
        
        return created_clients
    
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
    create_musketeers()
