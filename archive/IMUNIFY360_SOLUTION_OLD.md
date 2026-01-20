# Решение проблемы "Access denied by Imunify360 bot-protection"

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

### Решение 1: Whitelist IP адреса (РЕКОМЕНДУЕТСЯ)

**Самый надежный способ** - добавить IP адрес вашего сервера/приложения в whitelist Imunify360.

#### Через веб-интерфейс Imunify360:
1. Войдите в панель управления Imunify360
2. Перейдите в **Firewall → White List**
3. Добавьте IP адрес вашего сервера/приложения
4. Сохраните изменения

#### Через командную строку (SSH):
```bash
# Добавить IP в whitelist
imunify360-agent ip-list local add --purpose white <YOUR_IP_ADDRESS>

# Перезагрузить списки
imunify360-agent reload-lists
```

#### Через файл whitelist:
```bash
# Создать/отредактировать файл
sudo nano /etc/imunify360/whitelist/ext.txt

# Добавить IP (по одному на строку)
123.45.67.89
98.76.54.32

# Перезагрузить
imunify360-agent reload-lists
```

### Решение 2: Добавить User-Agent (ВРЕМЕННОЕ РЕШЕНИЕ)

Добавлен User-Agent в код для имитации браузера. Это может помочь, но не гарантирует обход защиты.

#### Настройка через .env:
```env
WC_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

Или используйте стандартный User-Agent браузера.

### Решение 3: Whitelist домена

Если запросы идут через домен:
```bash
imunify360-agent whitelist domain add dimkava.ge
```

### Решение 4: Настройка через код (уже реализовано)

Код автоматически устанавливает User-Agent при инициализации API клиента:

```python
from woocommerce_connector import WooCommerceConnector

# User-Agent будет установлен автоматически из .env или по умолчанию
connector = WooCommerceConnector()
products = connector.get_all_products()
```

## Как узнать свой IP адрес

### Если приложение работает на сервере:
```bash
# Узнать внешний IP сервера
curl ifconfig.me
# или
curl ipinfo.io/ip
```

### Если приложение работает локально:
1. Откройте https://whatismyipaddress.com/
2. Скопируйте ваш IP адрес
3. Добавьте его в whitelist Imunify360

### Если используете облачный сервис:
- AWS: проверьте Elastic IP или Public IP в консоли EC2
- Google Cloud: проверьте External IP в консоли
- Azure: проверьте Public IP в портале

## Проверка решения

После добавления IP в whitelist, проверьте:

```bash
python scripts/test_connection_and_products.py
```

Должно работать без ошибок.

## Дополнительные настройки

### Если IP меняется (динамический IP):

1. **Используйте диапазон IP (CIDR):**
   ```bash
   imunify360-agent ip-list local add --purpose white 192.168.1.0/24
   ```

2. **Или используйте сервис с фиксированным IP:**
   - VPS с фиксированным IP
   - Облачный сервис с Elastic IP

### Если используете прокси/CDN:

Убедитесь, что Imunify360 видит правильный IP. Может потребоваться:
- Настройка X-Forwarded-For заголовков
- Whitelist IP прокси/CDN

## Важные замечания

1. **User-Agent не гарантирует обход защиты** - это только имитация браузера
2. **Whitelist IP - самое надежное решение** - рекомендуется для production
3. **Проверьте логи Imunify360** - там будет видно, какой IP блокируется
4. **Не отключайте защиту полностью** - это снизит безопасность сервера

## Структура .env файла

```env
# Основные настройки
WC_URL=https://dimkava.ge
WC_CONSUMER_KEY=ck_...
WC_CONSUMER_SECRET=cs_...
WC_API_VERSION=wc/v3
WC_TIMEOUT=30

# Опционально: User-Agent для обхода бот-защиты
WC_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

## Если ничего не помогает

1. **Проверьте логи Imunify360:**
   ```bash
   tail -f /var/log/imunify360/imunify360.log
   ```

2. **Проверьте, что IP действительно в whitelist:**
   ```bash
   imunify360-agent ip-list local list --purpose white
   ```

3. **Временно отключите WebShield для тестирования:**
   ```bash
   # ТОЛЬКО ДЛЯ ТЕСТИРОВАНИЯ!
   imunify360-agent config update '{"WEBSHIELD": {"enabled": false}}'
   ```

4. **Свяжитесь с администратором сервера** для добавления IP в whitelist

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
        print(f"Ваш IP: {get_your_ip()}")  # Нужно реализовать функцию
    else:
        print(f"Ошибка API: {e}")
```

## Контакты для помощи

Если нужна помощь с настройкой Imunify360:
- Документация: https://docs.imunify360.com/
- Поддержка: через панель управления хостингом
