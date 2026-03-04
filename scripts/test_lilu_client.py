"""
Скрипт для тестирования создания и удаления клиентов в LILU.

Позволяет проверить формат данных и работу API без WooCommerce sync.

Использование:
    # Создать тестового клиента
    python scripts/test_lilu_client.py create

    # Создать с указанным телефоном
    python scripts/test_lilu_client.py create --phone +995544445523

    # Удалить клиента по ID
    python scripts/test_lilu_client.py delete --id 60a4bcd7bc45b806ac3b1a4a

    # Создать и сразу удалить (полный цикл)
    python scripts/test_lilu_client.py create --delete-after
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from lilu_connector import LILUConnector
from lilu_connector.api.exceptions import LILUAPIError, AuthenticationError, NotFoundError


def cmd_create(args):
    """Создать тестового клиента."""
    connector = LILUConnector()

    # LILU принимает только name, email, phone (формат E.164: +digits)
    phone = (args.phone or "+79991234567").strip()
    if not phone.startswith("+"):
        phone = f"+{phone}"

    client_data = {
        "name": args.name or "Тест Woo Sync",
        "email": args.email or "test-woo-sync@example.com",
        "phone": phone,
    }

    print("Отправляем в LILU:")
    for k, v in client_data.items():
        print(f"  {k}: {v!r}")
    print()

    try:
        client = connector.create_client(client_data)
        print(f"OK Создан: id={client.id}, name={client.name}")
        print(f"   phone={client.phone}, email={client.email}")

        if args.delete_after:
            print("\nУдаляем...")
            connector.delete_client(client.id)
            print("OK Удален")

        return client.id
    except LILUAPIError as e:
        print(f"ERROR LILU API: {e}")
        raise
    finally:
        connector.close()


def cmd_delete(args):
    """Удалить клиента по ID."""
    client_id = args.id
    if not client_id:
        print("ERROR: Укажите --id")
        sys.exit(1)

    connector = LILUConnector()
    try:
        ok = connector.delete_client(client_id)
        print("OK Удален" if ok else "ERROR Не удален")
    except NotFoundError:
        print("ERROR: Клиент не найден")
    except Exception as e:
        print(f"ERROR: {e}")
        raise
    finally:
        connector.close()


def main():
    parser = argparse.ArgumentParser(description="Тест создания/удаления клиентов в LILU")
    sub = parser.add_subparsers(dest="cmd", required=True)

    create_p = sub.add_parser("create", help="Создать тестового клиента")
    create_p.add_argument("--name", default="Тест Woo Sync", help="Имя")
    create_p.add_argument("--email", default="test-woo-sync@example.com", help="Email")
    create_p.add_argument("--phone", default="+79991234567", help="Телефон (E.164)")
    create_p.add_argument("--delete-after", action="store_true", help="Удалить после создания")
    create_p.set_defaults(func=cmd_create)

    delete_p = sub.add_parser("delete", help="Удалить клиента")
    delete_p.add_argument("--id", required=True, help="ID клиента в LILU")
    delete_p.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
