"""
Скрипт для проверки созданных клиентов-мушкетеров.

Использование:
    python -m lilu_connector.scripts.check_musketeers
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

from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from lilu_connector import LILUConnector

connector = LILUConnector()

# Ищем мушкетеров по email
print("Поиск клиентов-мушкетеров...")
print()

all_clients = connector.get_clients(limit=100)
musketeers = [c for c in all_clients if c.email and 'musketeer' in c.email.lower()]

print(f"Найдено мушкетеров: {len(musketeers)}")
print()

if musketeers:
    names = ['Д\'Артаньян', 'Атос', 'Портос', 'Арамис']
    for i, client in enumerate(musketeers[:4], 1):
        name = names[i-1] if i <= len(names) else 'Неизвестный'
        print(f"{i}. {name} ({client.name})")
        print(f"   ID: {client.id}")
        print(f"   Email: {client.email}")
        print(f"   Телефон: {client.phone or 'не указан'}")
        if client.tags:
            print(f"   Теги: {', '.join(client.tags)}")
        print()
else:
    print("Мушкетеры не найдены")

connector.close()
