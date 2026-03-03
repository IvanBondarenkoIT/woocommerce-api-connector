# Маппинг категорий товаров WooCommerce → теги LILU

## Где хранятся категории в WooCommerce

- **В заказе (line_items):** Только `product_id`. Категорий в line_item нет.
- **В продукте:** `GET /products/{id}` → поле `categories`:
  ```json
  "categories": [
    {"id": 107, "name": "Coffee accessories", "slug": "coffee-accessories"},
    {"id": 144, "name": "Cleaners", "slug": "cleaners"}
  ]
  ```
- **Список всех категорий:** `GET /products/categories`

## Как получаем группы товаров заказа

1. Для каждого `product_id` из `line_items` вызываем `GET /products/{product_id}`
2. Собираем уникальные категории (по `id`) из полей `categories`
3. В итоге получаем список: `[{"id": 107, "name": "...", "slug": "..."}, ...]`

## Маппинг на теги LILU

Файл: `woocommerce_connector/services/order_product_groups.py`

Словарь `CATEGORY_TO_LILU_TAG`:
- **Ключ:** `slug` категории WooCommerce (напр. `coffee-accessories`, `cleaners`)
- **Значение:** тег LILU (напр. `аксессуары кофе`, `чистящие`)

Пример:
```python
CATEGORY_TO_LILU_TAG = {
    "automatic-coffee-machines": "кофеварки",
    "coffee-accessories": "аксессуары кофе",
    "cleaners": "чистящие",
    "capsules": "капсулы",
}
```

Если в заказе товары из `coffee-accessories` и `cleaners` — клиенту добавят оба тега.

## Категории в вашем магазине (примеры)

| ID | slug | name |
|----|------|------|
| 100 | automatic-coffee-machines | Automatic-coffee-machines |
| 123 | coffee-beans | Beans |
| 428 | capsule-coffee-makers | Capsule coffee makers |
| 107 | coffee-accessories | Coffee accessories |
| 144 | cleaners | Cleaners |
| ... | ... | ... |

## Что нужно сделать

1. Экспортировать/получить полный список категорий WooCommerce (slug, name)
2. Определить соответствующие теги в LILU
3. Заполнить `CATEGORY_TO_LILU_TAG` в `order_product_groups.py`
4. Подключить `category_slugs_to_lilu_tags()` в SyncService при экспорте
