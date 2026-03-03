# 🌐 Веб-интерфейс синхронизации WooCommerce → LILU

## 📋 Описание

Веб-интерфейс для просмотра заказов из WooCommerce и ручной синхронизации их в LILU CRM.

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск сервера

```bash
# Из корневой директории проекта
cd frontend
python app.py

# Или через uvicorn напрямую
uvicorn frontend.app:app --reload --host 0.0.0.0 --port 8000
```

### 3. Открыть в браузере

```
http://localhost:8000
```

## 📁 Структура

```
frontend/
├── app.py                 # FastAPI приложение
├── templates/             # HTML шаблоны
│   ├── base.html         # Базовый шаблон
│   ├── orders.html       # Список заказов
│   └── order_detail.html # Детали заказа
├── static/               # Статические файлы
│   ├── css/
│   │   └── style.css    # Стили
│   └── js/
│       └── main.js      # JavaScript утилиты
└── README.md            # Этот файл
```

## 🔌 API Endpoints

### Frontend Routes
- `GET /` - Главная страница (список заказов)
- `GET /orders/{order_id}` - Страница деталей заказа

### API Routes
- `GET /api/orders` - Список заказов (JSON)
- `GET /api/orders/{order_id}` - Детали заказа (JSON)
- `POST /api/orders/{order_id}/sync` - Синхронизировать заказ
- `GET /api/sync/status` - Статистика синхронизации
- `GET /api/health` - Проверка здоровья приложения

## 💻 Использование

1. Откройте http://localhost:8000
2. Просмотрите список заказов
3. Нажмите "Синхронизировать" для нужного заказа
4. Проверьте результат синхронизации

## 🎨 Особенности

- Современный и чистый дизайн
- Адаптивный интерфейс
- AJAX запросы (без перезагрузки страницы)
- Уведомления об успехе/ошибке
- Статус синхронизации в реальном времени

## 🔧 Настройка

Порт и хост можно изменить в `app.py`:

```python
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,  # Измените порт здесь
        reload=True
    )
```

## 📚 Документация

- [План интеграции](../docs/development/SYNC_INTEGRATION_PLAN_V2.md)
- [Руководство по синхронизации](../docs/guides/SYNC_GUIDE.md)
