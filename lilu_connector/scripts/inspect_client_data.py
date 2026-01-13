"""
Скрипт для анализа структуры данных клиентов из LILU API.

Сохраняет сырой ответ API в файл для анализа.
"""

import sys
import os
import codecs
import json

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

from lilu_connector.api.client import LILUClient
from lilu_connector.config.settings import LILUSettings

settings = LILUSettings()
client = LILUClient(settings)

print("Получение данных клиента из API...")
response = client.get('/people', params={'limit': 1})
data = response.json()

output_file = os.path.join(project_root, "data", "output", "raw_client_data.json")
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Данные сохранены в: {output_file}")
print(f"\nСтруктура ответа:")
print(f"  Тип: {type(data)}")
if isinstance(data, dict):
    print(f"  Ключи: {list(data.keys())}")
    if 'data' in data:
        print(f"  data тип: {type(data['data'])}")
        if isinstance(data['data'], dict):
            print(f"  data ключи: {list(data['data'].keys())}")
            if 'people' in data['data']:
                people = data['data']['people']
                print(f"  people тип: {type(people)}")
                if isinstance(people, list) and len(people) > 0:
                    print(f"  Первый клиент ключи: {list(people[0].keys())}")

client.close()
