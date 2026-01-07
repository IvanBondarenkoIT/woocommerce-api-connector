# 🚀 Инструкция по публикации на GitHub

## Быстрый старт

### 1. Проверка текущего состояния

```bash
# Проверить статус Git
git status

# Проверить, есть ли уже remote
git remote -v
```

### 2. Инициализация Git (если нужно)

```bash
git init
```

### 3. Добавление всех файлов

```bash
git add .
```

**Важно:** Убедитесь, что `.env` файл в `.gitignore` (он там уже есть)

### 4. Первый коммит

```bash
git commit -m "Initial commit: WooCommerce API Connector

- Modern GUI with CustomTkinter
- Excel export with category grouping
- Comprehensive test suite
- CI/CD with GitHub Actions
- Full WooCommerce API integration"
```

### 5. Подключение к GitHub

```bash
# Добавить remote репозиторий
git remote add origin https://github.com/IvanBondarenkoIT/woocommerce-api-connector.git

# Проверить
git remote -v
```

### 6. Push на GitHub

```bash
# Переименовать ветку в main (если нужно)
git branch -M main

# Push с установкой upstream
git push -u origin main
```

## Если репозиторий не пустой

Если в репозитории уже есть файлы (например, README от GitHub):

```bash
# Сначала pull с merge
git pull origin main --allow-unrelated-histories

# Разрешить конфликты (если есть)
# Затем push
git push -u origin main
```

## Проверка после публикации

1. Откройте https://github.com/IvanBondarenkoIT/woocommerce-api-connector
2. Проверьте, что все файлы загружены
3. Проверьте, что GitHub Actions запустились (вкладка Actions)

## Дальнейшие обновления

После изменений в коде:

```bash
git add .
git commit -m "Описание изменений"
git push
```

## Структура проекта на GitHub

После публикации структура должна быть:

```
woocommerce-api-connector/
├── .github/
│   └── workflows/
│       ├── tests.yml
│       └── lint.yml
├── tests/
│   ├── __init__.py
│   ├── test_connector.py
│   ├── test_excel_export.py
│   └── test_api_version_check.py
├── woocommerce_connector.py
├── woocommerce_gui.py
├── requirements.txt
├── pytest.ini
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── .gitignore
└── .env.example
```

## Полезные команды

```bash
# Посмотреть историю коммитов
git log --oneline

# Посмотреть изменения
git diff

# Отменить последний коммит (локально)
git reset --soft HEAD~1

# Проверить, какие файлы будут закоммичены
git status
```



