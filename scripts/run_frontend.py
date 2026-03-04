"""
Скрипт для запуска веб-интерфейса синхронизации.

Использование:
    python scripts/run_frontend.py

Imunify360: для обхода блокировки с residential IP:
    - railway run python scripts/run_frontend.py   # запросы с IP Railway
    - или WC_HTTPS_PROXY=http://proxy:port в .env
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn


def _use_railway_run() -> bool:
    """Проверить, нужно ли запускать через railway run (Imunify360 bypass)."""
    if os.getenv("RAILWAY_ENVIRONMENT"):
        return False  # уже внутри Railway
    if os.getenv("WC_HTTPS_PROXY") or os.getenv("HTTPS_PROXY"):
        return False  # прокси задан — обычный запуск
    railway = shutil.which("railway")
    return bool(railway)


def main():
    print("\n" + "=" * 80)
    print("Запуск веб-интерфейса синхронизации WooCommerce -> LILU")
    print("=" * 80)

    if _use_railway_run():
        print("\n[Imunify360] railway в PATH — запуск через railway run (datacenter IP)")
        print("Запросы к WooCommerce пойдут с IP Railway (обход блокировки).\n")
        cmd = ["railway", "run", sys.executable, "-m", "uvicorn", "frontend.app:app",
               "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]
        subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        return

    proxy = os.getenv("WC_HTTPS_PROXY") or os.getenv("HTTPS_PROXY")
    if proxy:
        print(f"\n[Imunify360] Прокси: {proxy[:50]}...")
    print("\nОткройте в браузере: http://localhost:8000")
    print("Для остановки нажмите Ctrl+C\n")

    uvicorn.run(
        "frontend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
