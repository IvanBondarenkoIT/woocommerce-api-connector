"""
Скрипт для запуска веб-интерфейса синхронизации.

Использование:
    python scripts/run_frontend.py
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Запуск веб-интерфейса синхронизации WooCommerce -> LILU")
    print("=" * 80)
    print("\nОткройте в браузере: http://localhost:8000")
    print("Для остановки нажмите Ctrl+C\n")
    
    uvicorn.run(
        "frontend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
