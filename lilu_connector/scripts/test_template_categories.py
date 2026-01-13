"""
Тестовый скрипт для проверки получения категорий шаблонов сообщений.

Использование:
    python -m lilu_connector.scripts.test_template_categories
"""

import sys
import os
import codecs

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
    NotFoundError,
)
from lilu_connector.config.settings import LILUSettings
import json


def test_template_categories():
    """Проверить получение категорий шаблонов"""
    
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ПОЛУЧЕНИЯ КАТЕГОРИЙ ШАБЛОНОВ СООБЩЕНИЙ")
    print("=" * 80)
    print()
    
    try:
        print("📋 Шаг 1: Инициализация коннектора...")
        try:
            connector = LILUConnector()
        except ValueError as e:
            raise ConfigurationError(str(e))
        
        print("✅ Коннектор инициализирован")
        print(f"   URL: {connector.settings.api_url}")
        print(f"   Версия API: {connector.settings.api_version}")
        print()
        
        print("📋 Шаг 2: Получение категорий шаблонов сообщений...")
        print("   Endpoint: /api/v2/categories/templates")
        print()
        
        try:
            categories = connector.get_template_categories()
            
            print(f"✅ Успешно получено категорий: {len(categories)}")
            print()
            
            if categories:
                print("📊 Список категорий:")
                print()
                
                for i, category in enumerate(categories, 1):
                    if isinstance(category, dict):
                        name = category.get('name', 'Без названия')
                        category_id = category.get('id', 'N/A')
                        description = category.get('description', '')
                        
                        print(f"   {i}. {name}")
                        print(f"      ID: {category_id}")
                        if description:
                            print(f"      Описание: {description}")
                        
                        other_fields = {k: v for k, v in category.items() 
                                      if k not in ['name', 'id', 'description']}
                        if other_fields:
                            print(f"      Другие поля: {list(other_fields.keys())}")
                    else:
                        print(f"   {i}. {category}")
                    print()
                
                output_file = os.path.join(project_root, "data", "output", "template_categories.json")
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(categories, f, ensure_ascii=False, indent=2)
                
                print(f"💾 Данные сохранены в: {output_file}")
            else:
                print("⚠️  Категории не найдены")
            
            print()
            print("=" * 80)
            print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
            print("=" * 80)
            
            connector.close()
            
        except NotFoundError:
            print("❌ Endpoint не найден (404)")
            print("💡 Возможно, endpoint изменился или требуется другая версия API")
        except Exception as e:
            print(f"❌ Ошибка при получении категорий: {e}")
            import traceback
            traceback.print_exc()
    
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
        sys.exit(1)
    
    except Exception as e:
        print("❌ НЕОЖИДАННАЯ ОШИБКА:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_template_categories()
