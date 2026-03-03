# Полное руководство по решению проблемы Imunify360

## Проблема

При попытке получить товары через WooCommerce API возникает ошибка:
```
Access denied by Imunify360 bot-protection. IPs used for automation should be whitelisted
```

## Причина

Imunify360 - это система защиты сервера, которая блокирует автоматизированные запросы (боты). Она определяет ботов по:
- Отсутствию или подозрительному User-Agent
- Поведению запросов (слишком быстро, слишком много)
- IP адресу (не в whitelist)

## Решения

### Решение 1: Whitelist IP адреса (РЕКОМЕНДУЕТСЯ для production)

**Самый надежный способ** - добавить IP адрес вашего сервера/приложения в whitelist Imunify360.

#### Шаг 1: Узнайте ваш IP адрес

**На вашем локальном компьютере или сервере, откуда делаются запросы:**

```bash
# Windows PowerShell
Invoke-WebRequest -Uri "https://api.ipify.org" | Select-Object -ExpandProperty Content

# Linux/Mac
curl https://api.ipify.org

# Или используйте скрипт
python scripts/get_my_ip.py
```

**Если используете облачный сервис:**
- **AWS EC2:** Консоль AWS → EC2 → Instances → Ваш инстанс → Public IPv4 address
- **Google Cloud:** Консоль GCP → Compute Engine → VM instances → External IP
- **Azure:** Портал Azure → Virtual machines → Public IP address
- **VPS/Shared Hosting:** Проверьте в панели управления хостингом

#### Шаг 2: Добавьте IP в whitelist

**Вариант A: Через SSH (командная строка на сервере)**

1. Подключитесь к серверу:
   ```bash
   ssh username@your-server-ip
   # или
   ssh username@dimkava.ge
   ```

2. Выполните команду:
   ```bash
   sudo imunify360-agent ip-list local add --purpose white YOUR_IP
   
   # Например:
   sudo imunify360-agent ip-list local add --purpose white 123.45.67.89
   ```

3. Перезагрузите списки:
   ```bash
   sudo imunify360-agent reload-lists
   ```

4. Проверьте:
   ```bash
   sudo imunify360-agent ip-list local list --purpose white
   ```

**Вариант B: Через веб-интерфейс**

**cPanel:**
1. Войдите в **cPanel**
2. Найдите раздел **Imunify360** или **Security**
3. Перейдите в **Firewall → White List**
4. Нажмите **Add IP** или **Добавить IP**
5. Введите ваш IP адрес
6. Выберите **Purpose: White**
7. Сохраните

**Imunify360 Dashboard:**
1. Войдите в **Imunify360 Dashboard**
2. Перейдите в **Firewall → White List**
3. Нажмите **+ Add IP**
4. Введите IP адрес
5. Выберите **Purpose: White**
6. Сохраните

**Plesk:**
1. Войдите в **Plesk**
2. Перейдите в **Extensions → Imunify360**
3. Откройте **Firewall → White List**
4. Добавьте IP адрес

**Вариант C: Через файл whitelist**

```bash
# Создать или отредактировать файл
sudo nano /etc/imunify360/whitelist/ext.txt

# Добавить IP (по одному на строку)
123.45.67.89
98.76.54.32

# Сохранить (Ctrl+O, Enter, Ctrl+X)
# Перезагрузить
sudo imunify360-agent reload-lists
```

**Вариант D: Если нет доступа к серверу**

Свяжитесь с администратором сервера или хостинг-провайдером и попросите добавить ваш IP в whitelist Imunify360.

### Решение 2: Установить User-Agent (ВРЕМЕННОЕ РЕШЕНИЕ)

**Всегда устанавливайте User-Agent**, чтобы запросы выглядели как от браузера.

#### В коде (автоматически в этом проекте):

```python
from woocommerce_connector import WooCommerceConnector

# User-Agent устанавливается автоматически из .env или по умолчанию
connector = WooCommerceConnector()
products = connector.get_all_products()
```

#### Настройка через .env:

```env
WC_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

#### Или вручную через requests:

```python
import requests
from requests.auth import HTTPBasicAuth

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
}

response = requests.get(
    'https://your-store.com/wp-json/wc/v3/products',
    params={'per_page': 100, 'page': 1},
    auth=HTTPBasicAuth(consumer_key, consumer_secret),
    headers=headers,
    timeout=30
)
```

### Решение 3: Whitelist домена

Если запросы идут через домен:
```bash
imunify360-agent whitelist domain add dimkava.ge
```

## Проверка решения

После добавления IP в whitelist или установки User-Agent:

```bash
python scripts/test_connection_and_products.py
```

Должно работать без ошибки "Access denied by Imunify360".

## Дополнительные настройки

### Если IP меняется (динамический IP)

1. **Используйте диапазон IP (CIDR):**
   ```bash
   imunify360-agent ip-list local add --purpose white 192.168.1.0/24
   ```

2. **Или используйте сервис с фиксированным IP:**
   - VPS с фиксированным IP
   - Облачный сервис с Elastic IP

### Если используете прокси/CDN

Убедитесь, что Imunify360 видит правильный IP. Может потребоваться:
- Настройка X-Forwarded-For заголовков
- Whitelist IP прокси/CDN

## Важные замечания

1. **User-Agent не гарантирует обход защиты** - это только имитация браузера
2. **Whitelist IP - самое надежное решение** - рекомендуется для production
3. **Проверьте логи Imunify360** - там будет видно, какой IP блокируется
4. **Не отключайте защиту полностью** - это снизит безопасность сервера

## Частые вопросы

### Q: Нужны ли права sudo?

**A:** Да, обычно нужны права администратора (sudo или root).

### Q: Как добавить несколько IP?

**A:** 
```bash
# По одному
sudo imunify360-agent ip-list local add --purpose white IP1
sudo imunify360-agent ip-list local add --purpose white IP2

# Или через файл (см. Вариант C выше)
```

### Q: Как удалить IP из whitelist?

**A:**
```bash
sudo imunify360-agent ip-list local remove --purpose white YOUR_IP
```

### Q: IP меняется каждый раз (динамический IP)

**A:** 
- Используйте диапазон IP (CIDR): `192.168.1.0/24`
- Или получите статический IP у провайдера
- Или используйте VPN/прокси с фиксированным IP

### Q: Не знаю, как подключиться по SSH

**A:**
- Свяжитесь с администратором сервера
- Или используйте веб-интерфейс (cPanel/Plesk)
- Или попросите администратора добавить IP за вас

## Пример полного процесса

```bash
# 1. На вашем компьютере - узнайте IP
python scripts/get_my_ip.py
# Вывод: Ваш IP адрес: 123.45.67.89

# 2. Подключитесь к серверу
ssh admin@dimkava.ge

# 3. На сервере - добавьте IP в whitelist
sudo imunify360-agent ip-list local add --purpose white 123.45.67.89

# 4. Перезагрузите списки
sudo imunify360-agent reload-lists

# 5. Проверьте
sudo imunify360-agent ip-list local list --purpose white

# 6. Вернитесь на ваш компьютер и проверьте API
python scripts/test_connection_and_products.py
```

## Если ничего не помогает

1. **Проверьте логи Imunify360:**
   ```bash
   sudo tail -f /var/log/imunify360/imunify360.log
   ```

2. **Убедитесь, что IP действительно добавлен:**
   ```bash
   sudo imunify360-agent ip-list local list --purpose white | grep YOUR_IP
   ```

3. **Временно отключите WebShield для тестирования (ТОЛЬКО ДЛЯ ТЕСТИРОВАНИЯ!):**
   ```bash
   imunify360-agent config update '{"WEBSHIELD": {"enabled": false}}'
   ```

4. **Свяжитесь с поддержкой хостинга или администратором сервера**

## Пример кода с обработкой ошибки

```python
from woocommerce_connector import WooCommerceConnector
from woocommerce_connector.api.exceptions import APIResponseError

try:
    connector = WooCommerceConnector()
    products = connector.get_all_products()
    print(f"Получено {len(products)} товаров")
except APIResponseError as e:
    if "Imunify360" in str(e) or "bot-protection" in str(e).lower():
        print("ОШИБКА: Imunify360 блокирует запросы")
        print("РЕШЕНИЕ: Добавьте ваш IP адрес в whitelist Imunify360")
        print("Ваш IP можно узнать: python scripts/get_my_ip.py")
    else:
        print(f"Ошибка API: {e}")
```

## Контакты для помощи

Если нужна помощь с настройкой Imunify360:
- Документация: https://docs.imunify360.com/
- Поддержка: через панель управления хостингом
