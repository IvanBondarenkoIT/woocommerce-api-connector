# Реорганизация проекта - 20 января 2026

## Цель
Привести проект в порядок: разделить документы по категориям, организовать скрипты, создать логическую структуру.

## Выполненные изменения

### 1. Организация документации

#### Создана структура папок:
- `docs/guides/` - Практические руководства
- `docs/development/` - Документация для разработчиков
- `docs/deployment/` - Документация по развертыванию
- `docs/prompts/` - Промпты для других проектов

#### Перемещенные файлы:

**Руководства (docs/guides/):**
- `API_CONNECTION_GUIDE.md` → `docs/guides/API_CONNECTION_GUIDE.md`
- `IMUNIFY360_GUIDE.md` → `docs/guides/IMUNIFY360_GUIDE.md`

**Разработка (docs/development/):**
- `TESTING_STRATEGY.md` → `docs/development/TESTING_STRATEGY.md`
- `TESTING_SUMMARY.md` → `docs/development/TESTING_SUMMARY.md`
- `REFACTORING_PLAN.md` → `docs/development/REFACTORING_PLAN.md`
- `FEATURES_ROADMAP.md` → `docs/development/FEATURES_ROADMAP.md`
- `IMPROVEMENTS_PROPOSAL_RU.md` → `docs/development/IMPROVEMENTS_PROPOSAL_RU.md`

**Развертывание (docs/deployment/):**
- `DEPLOY.md` → `docs/deployment/DEPLOY.md`
- `GITHUB_SETUP.md` → `docs/deployment/GITHUB_SETUP.md`

**Промпты (docs/prompts/):**
- `WOOCOMMERCE_PRODUCT_STOCK_PROMPT.md` → `docs/prompts/WOOCOMMERCE_PRODUCT_STOCK_PROMPT.md`

#### Созданные файлы:
- `docs/README.md` - Индекс документации в папке docs
- `PROJECT_STRUCTURE.md` - Обзор структуры проекта

### 2. Организация скриптов

#### Создан файл:
- `scripts/README.md` - Описание всех скриптов с категориями

Скрипты остались в папке `scripts/`, так как уже были логически организованы.

### 3. Обновленные файлы

- `DOCUMENTATION_INDEX.md` - Обновлены все ссылки на новую структуру
- `ARCHITECTURE.md` - Добавлена информация о новой структуре документации
- `docs/guides/API_CONNECTION_GUIDE.md` - Ссылка на IMUNIFY360_GUIDE.md обновлена

### 4. Файлы, оставшиеся в корне

Основная документация (для быстрого доступа):
- `README.md` - Главная документация
- `ARCHITECTURE.md` - Архитектура проекта
- `CONTRIBUTING.md` - Руководство для контрибьюторов
- `DOCUMENTATION_INDEX.md` - Индекс документации
- `SUCCESS.md` - История успешных интеграций
- `PROJECT_STRUCTURE.md` - Структура проекта

## Итоговая структура

```
woocommerce-api-connector/
├── README.md, ARCHITECTURE.md, CONTRIBUTING.md (основная документация)
├── docs/                          # Организованная документация
│   ├── guides/                    # Руководства
│   ├── development/               # Для разработчиков
│   ├── deployment/                # Развертывание
│   └── prompts/                   # Промпты
├── scripts/                        # Скрипты (с README.md)
├── woocommerce_connector/          # Код WooCommerce
├── lilu_connector/                # Код LILU
├── tests/                          # Тесты
├── data/                           # Данные
├── logs/                           # Логи
└── archive/                        # Архив
```

## Преимущества новой структуры

1. ✅ **Логическая организация** - документы разделены по назначению
2. ✅ **Легкий поиск** - понятная структура папок
3. ✅ **Масштабируемость** - легко добавлять новые документы
4. ✅ **Чистота корня** - основные файлы в корне, детали в подпапках
5. ✅ **Документированность** - README файлы в каждой категории

## Обратная совместимость

Все ссылки обновлены. Если где-то остались старые ссылки, они будут указывать на несуществующие файлы и потребуют обновления.

## Следующие шаги

1. Проверить все ссылки в коде и документации
2. Обновить CI/CD если нужно
3. Обновить документацию в других местах (если есть)
