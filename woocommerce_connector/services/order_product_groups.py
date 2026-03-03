"""
Сервис получения групп товаров (категорий) для заказа.

Категории товаров в WooCommerce хранятся в продукте, не в line_item.
Для каждого product_id из line_items нужно запросить продукт и получить categories.
"""

from typing import List, Dict, Any, Optional, Set
from functools import lru_cache

from woocommerce_connector.connector import WooCommerceConnector
from woocommerce_connector.utils.logger import get_logger

logger = get_logger(__name__)

# Маппинг: slug категории WooCommerce -> тег LILU
# TODO: Заполнить таблицу сопоставления от пользователя
CATEGORY_TO_LILU_TAG: Dict[str, str] = {
    # Примеры (заменить на реальные):
    # "automatic-coffee-machines": "кофеварки",
    # "coffee-accessories": "аксессуары кофе",
    # "cleaners": "чистящие",
    # "capsules": "капсулы",
}


def get_order_product_categories(
    wc_connector: WooCommerceConnector,
    line_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Получить уникальные категории товаров из заказа.
    
    Для каждого product_id в line_items запрашивается продукт и извлекаются
    категории (id, name, slug).
    
    Args:
        wc_connector: Коннектор WooCommerce
        line_items: Список line_items из заказа
    
    Returns:
        Список уникальных категорий: [{"id": 107, "name": "...", "slug": "..."}, ...]
    """
    seen: Set[int] = set()
    categories_list: List[Dict[str, Any]] = []
    
    for item in line_items or []:
        if not isinstance(item, dict):
            continue
        product_id = item.get("product_id") or item.get("productId")
        if not product_id or product_id in seen:
            continue
        seen.add(product_id)

        try:
            product = wc_connector.get_product_fields(product_id)
            if not product or not isinstance(product, dict):
                continue
            cats = product.get("categories") or []
            for c in cats:
                if not isinstance(c, dict):
                    continue
                cat_id = c.get("id")
                if cat_id is None:
                    continue
                # Добавляем только если ещё не было
                if not any(x.get("id") == cat_id for x in categories_list):
                    categories_list.append({
                        "id": cat_id,
                        "name": c.get("name", ""),
                        "slug": c.get("slug", ""),
                    })
        except Exception as e:
            logger.warning(f"Failed to get categories for product {product_id}: {e}")
            continue
    
    return categories_list


def get_order_product_group_slugs(
    wc_connector: WooCommerceConnector,
    line_items: List[Dict[str, Any]],
) -> List[str]:
    """
    Получить список slug категорий товаров в заказе (уникальные).
    
    Returns:
        ["coffee-accessories", "cleaners", ...]
    """
    cats = get_order_product_categories(wc_connector, line_items)
    return [c["slug"] for c in cats if c.get("slug")]


def category_slugs_to_lilu_tags(category_slugs: List[str]) -> List[str]:
    """
    Преобразовать slug категорий WooCommerce в теги LILU по маппингу.
    
    Args:
        category_slugs: Список slug категорий из заказа
    
    Returns:
        Список тегов LILU для добавления клиенту
    """
    tags: List[str] = []
    for slug in category_slugs:
        tag = CATEGORY_TO_LILU_TAG.get(slug)
        if tag and tag not in tags:
            tags.append(tag)
    return tags
