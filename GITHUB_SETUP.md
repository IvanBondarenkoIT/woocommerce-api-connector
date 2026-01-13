# Инструкция по публикации на GitHub

## Шаг 1: Инициализация Git (если еще не сделано)

```bash
git init
```

## Шаг 2: Добавление всех файлов

```bash
git add .
```

## Шаг 3: Первый коммит

```bash
git commit -m "Initial commit: WooCommerce API Connector with GUI and Excel export"
```

## Шаг 4: Подключение к удаленному репозиторию

```bash
git remote add origin https://github.com/IvanBondarenkoIT/woocommerce-api-connector.git
```

## Шаг 5: Переименование ветки в main (если нужно)

```bash
git branch -M main
```

## Шаг 6: Push на GitHub

```bash
git push -u origin main
```

## Если репозиторий уже существует и не пустой

Если в репозитории уже есть файлы (например, README), нужно сначала сделать pull:

```bash
git pull origin main --allow-unrelated-histories
```

Затем разрешить конфликты (если есть) и сделать push:

```bash
git push -u origin main
```

## Проверка статуса

```bash
# Проверить статус
git status

# Посмотреть историю коммитов
git log --oneline

# Проверить удаленный репозиторий
git remote -v
```

## Дальнейшие обновления

После изменений:

```bash
git add .
git commit -m "Описание изменений"
git push
```





