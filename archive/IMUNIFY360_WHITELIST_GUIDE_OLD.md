# Как добавить IP в whitelist Imunify360

## Где выполнять команду

Команда `imunify360-agent ip-list local add --purpose white YOUR_IP` выполняется **на сервере**, где установлен Imunify360, через **SSH терминал**.

## Способ 1: Через SSH (командная строка на сервере)

### Шаг 1: Подключитесь к серверу по SSH

**Windows:**
```bash
# Используйте PuTTY, Windows Terminal, или PowerShell
ssh username@your-server-ip
# или
ssh username@dimkava.ge
```

**Linux/Mac:**
```bash
ssh username@your-server-ip
```

### Шаг 2: Узнайте ваш IP адрес

**На вашем локальном компьютере или сервере, откуда делаются запросы:**

```bash
# Windows PowerShell
Invoke-WebRequest -Uri "https://api.ipify.org" | Select-Object -ExpandProperty Content

# Linux/Mac
curl https://api.ipify.org

# Или используйте скрипт
python scripts/get_my_ip.py
```

### Шаг 3: Выполните команду на сервере

**После подключения к серверу по SSH:**

```bash
# Замените YOUR_IP на ваш реальный IP адрес
sudo imunify360-agent ip-list local add --purpose white YOUR_IP

# Например:
sudo imunify360-agent ip-list local add --purpose white 123.45.67.89
```

### Шаг 4: Перезагрузите списки

```bash
sudo imunify360-agent reload-lists
```

### Шаг 5: Проверьте, что IP добавлен

```bash
sudo imunify360-agent ip-list local list --purpose white
```

## Способ 2: Через веб-интерфейс (панель управления)

Если у вас есть доступ к панели управления сервером (cPanel, Plesk, или напрямую Imunify360):

### Вариант A: Через cPanel

1. Войдите в **cPanel**
2. Найдите раздел **Imunify360** или **Security**
3. Перейдите в **Firewall** → **White List**
4. Нажмите **Add IP** или **Добавить IP**
5. Введите ваш IP адрес
6. Выберите **Purpose: White**
7. Сохраните

### Вариант B: Через Imunify360 Dashboard

1. Войдите в **Imunify360 Dashboard**
2. Перейдите в **Firewall** → **White List**
3. Нажмите **+ Add IP**
4. Введите IP адрес
5. Выберите **Purpose: White**
6. Сохраните

### Вариант C: Через Plesk

1. Войдите в **Plesk**
2. Перейдите в **Extensions** → **Imunify360**
3. Откройте **Firewall** → **White List**
4. Добавьте IP адрес

## Способ 3: Через файл whitelist (если есть доступ к файловой системе)

### Шаг 1: Подключитесь по SSH

```bash
ssh username@your-server
```

### Шаг 2: Создайте/отредактируйте файл whitelist

```bash
# Создать или отредактировать файл
sudo nano /etc/imunify360/whitelist/ext.txt
```

### Шаг 3: Добавьте IP адрес

В файле добавьте ваш IP (по одному на строку):
```
123.45.67.89
98.76.54.32
```

Сохраните файл (в nano: `Ctrl+O`, затем `Enter`, затем `Ctrl+X`)

### Шаг 4: Перезагрузите списки

```bash
sudo imunify360-agent reload-lists
```

## Способ 4: Если нет доступа к серверу

Если у вас **нет доступа к серверу** (SSH или панель управления):

1. **Свяжитесь с администратором сервера** или хостинг-провайдером
2. Попросите добавить ваш IP в whitelist Imunify360
3. Предоставьте ваш IP адрес (можно получить через `python scripts/get_my_ip.py`)

## Как узнать, какой IP нужно добавить

### Если приложение работает на вашем компьютере:

```bash
# Windows PowerShell
python scripts/get_my_ip.py

# Или в браузере откройте
https://whatismyipaddress.com/
```

### Если приложение работает на сервере/облаке:

**AWS EC2:**
- Консоль AWS → EC2 → Instances → Ваш инстанс → Public IPv4 address

**Google Cloud:**
- Консоль GCP → Compute Engine → VM instances → External IP

**Azure:**
- Портал Azure → Virtual machines → Public IP address

**VPS/Shared Hosting:**
- Проверьте в панели управления хостингом
- Или выполните на сервере: `curl https://api.ipify.org`

## Проверка после добавления

После добавления IP в whitelist, проверьте работу API:

```bash
python scripts/test_connection_and_products.py
```

Должно работать без ошибки "Access denied by Imunify360".

## Частые вопросы

### Q: Нужны ли права sudo?

**A:** Да, обычно нужны права администратора (sudo или root).

### Q: Как добавить несколько IP?

**A:** 
```bash
# По одному
sudo imunify360-agent ip-list local add --purpose white IP1
sudo imunify360-agent ip-list local add --purpose white IP2

# Или через файл (см. Способ 3)
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

1. Проверьте логи Imunify360:
   ```bash
   sudo tail -f /var/log/imunify360/imunify360.log
   ```

2. Убедитесь, что IP действительно добавлен:
   ```bash
   sudo imunify360-agent ip-list local list --purpose white | grep YOUR_IP
   ```

3. Свяжитесь с поддержкой хостинга или администратором сервера
