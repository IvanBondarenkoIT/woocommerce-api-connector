"""
Скрипт для проверки настроек .env файла.

Проверяет, что все необходимые переменные установлены правильно.
"""

import sys
import os
import codecs

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Определяем путь к .env файлу в корне проекта
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
env_path = os.path.join(project_root, '.env')

from dotenv import dotenv_values

print("=" * 80)
print("ПРОВЕРКА НАСТРОЕК .ENV ФАЙЛА")
print("=" * 80)
print()
print(f"📁 Путь к .env: {env_path}")
print()

env = dotenv_values(env_path)

# Проверяем обязательные переменные
required_vars = {
    'LILU_API_URL': 'URL API сервера',
    'LILU_API_KEY': 'API ключ',
    'LILU_API_SECRET': 'API секрет',
}

print("📋 Проверка обязательных переменных:")
print()

all_ok = True

for var_name, description in required_vars.items():
    value = env.get(var_name, '')
    
    if not value:
        print(f"❌ {var_name} - НЕ УСТАНОВЛЕН")
        print(f"   Описание: {description}")
        all_ok = False
    elif 'your_' in value.lower() or 'here' in value.lower():
        print(f"⚠️  {var_name} - содержит заглушку")
        print(f"   Текущее значение: {value[:50]}...")
        print(f"   Описание: {description}")
        print(f"   💡 Замените на реальное значение!")
        all_ok = False
    else:
        masked = value[:10] + '...' + value[-5:] if len(value) > 15 else '***'
        print(f"✅ {var_name} - установлен")
        print(f"   Значение: {masked}")
        print(f"   Длина: {len(value)} символов")

print()

# Проверяем опциональные переменные
optional_vars = {
    'LILU_API_VERSION': 'v2',
    'LILU_TIMEOUT': '30',
    'LILU_MAX_RETRIES': '3',
    'LILU_RETRY_DELAY': '1',
}

print("📋 Опциональные переменные:")
print()

for var_name, default in optional_vars.items():
    value = env.get(var_name, default)
    print(f"   {var_name}: {value}")

print()
print("=" * 80)

if all_ok:
    print("✅ ВСЕ НАСТРОЙКИ В ПОРЯДКЕ")
    print()
    print("💡 Следующий шаг: запустите тестовое подключение")
    print("   python -m lilu_connector.scripts.test_connection")
else:
    print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
    print()
    print("💡 Решение:")
    print("   1. Откройте файл .env в корне проекта")
    print("   2. Замените заглушки на реальные значения")
    print("   3. Убедитесь, что нет лишних пробелов")
    print("   4. Сохраните файл")

print("=" * 80)
