#!/usr/bin/env python
"""
Скрипт для определения вашего IP адреса.

Нужен для добавления IP в whitelist Imunify360.
"""

import requests
import sys

def get_my_ip():
    """Получить внешний IP адрес."""
    services = [
        'https://api.ipify.org',
        'https://ifconfig.me',
        'https://ipinfo.io/ip',
        'https://icanhazip.com'
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                ip = response.text.strip()
                return ip
        except:
            continue
    
    return None

if __name__ == "__main__":
    print("Определение вашего IP адреса...")
    print("=" * 50)
    
    ip = get_my_ip()
    
    if ip:
        print(f"Ваш IP адрес: {ip}")
        print()
        print("Добавьте этот IP в whitelist Imunify360:")
        print(f"  imunify360-agent ip-list local add --purpose white {ip}")
        print()
        print("Или через веб-интерфейс:")
        print("  Firewall -> White List -> Add IP")
    else:
        print("Не удалось определить IP адрес")
        print("Проверьте подключение к интернету")
        sys.exit(1)
