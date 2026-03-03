"""
FastAPI приложение для веб-интерфейса синхронизации заказов.

Предоставляет веб-интерфейс для:
- Просмотра заказов из WooCommerce
- Ручной синхронизации заказов в LILU CRM
- Мониторинга статуса синхронизации
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any
import time
import uvicorn

from woocommerce_connector.connector import WooCommerceConnector
from woocommerce_connector.models.order import Order
from lilu_connector.connector import LILUConnector
from woocommerce_connector.services import SyncService, SyncResult
from woocommerce_connector.services.order_product_groups import (
    get_order_product_categories,
    get_order_product_group_slugs,
)
from woocommerce_connector.utils.logger import get_logger

logger = get_logger(__name__)


def _get_order_product_categories(order: Order) -> List[Dict[str, Any]]:
    """Получить категории товаров в заказе (для отображения групп)."""
    if not wc_connector:
        return []
    return get_order_product_categories(wc_connector, order.line_items)

# Инициализация FastAPI
app = FastAPI(
    title="WooCommerce → LILU Sync",
    description="Веб-интерфейс для синхронизации заказов WooCommerce с LILU CRM",
    version="1.0.0"
)

# Настройка шаблонов и статических файлов
# Используем абсолютный путь для надежности
frontend_dir = Path(__file__).parent
templates = Jinja2Templates(directory=str(frontend_dir / "templates"))
app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")

# Инициализация коннекторов (глобально, один раз при старте)
wc_connector: Optional[WooCommerceConnector] = None
lilu_connector: Optional[LILUConnector] = None
sync_service: Optional[SyncService] = None


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения."""
    global wc_connector, lilu_connector, sync_service
    
    try:
        logger.info("Initializing connectors...")
        wc_connector = WooCommerceConnector()
        lilu_connector = LILUConnector()
        
        sync_service = SyncService(
            wc_connector=wc_connector,
            lilu_connector=lilu_connector,
            default_tag="api woo"
        )
        
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении приложения."""
    logger.info("Application shutting down")


# ==================== FRONTEND ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница - список заказов."""
    return templates.TemplateResponse("orders.html", {"request": request})


@app.get("/orders/{order_id}", response_class=HTMLResponse)
async def order_detail(request: Request, order_id: int):
    """Страница деталей заказа."""
    return templates.TemplateResponse("order_detail.html", {
        "request": request,
        "order_id": order_id
    })


# ==================== API ROUTES ====================

def _has_coupon_code(order_data: dict, coupon_code: str) -> bool:
    """Проверить, есть ли в заказе купон с указанным кодом."""
    if not isinstance(order_data, dict):
        return False
    coupon_lines = order_data.get("coupon_lines") or []
    for cl in coupon_lines:
        if isinstance(cl, dict) and cl.get("code") == coupon_code:
            return True
    return False


@app.get("/api/orders")
async def get_orders(
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    search: Optional[str] = None,
    coupon_code: Optional[str] = None,
    load_product_groups: Optional[str] = "0",
) -> JSONResponse:
    """
    Получить список заказов.
    
    Args:
        page: Номер страницы
        per_page: Количество заказов на странице
        status: Фильтр по статусу
        search: Поиск по ID или имени клиента
        coupon_code: Фильтр по коду купона (например "-15%" для скидки на первый заказ)
        load_product_groups: Загружать группы товаров (категории) — медленно при многих заказах
    
    Returns:
        JSONResponse: Список заказов с метаданными
    """
    if not wc_connector:
        raise HTTPException(status_code=500, detail="WooCommerce connector not initialized")
    
    t0 = time.perf_counter()
    logger.info(f"get_orders: page={page}, per_page={per_page}, status={status}, coupon_code={coupon_code}")
    
    try:
        # При фильтре по купону — читаем страницы WC пока не наберём нужный срез
        if coupon_code:
            fetch_per_page = 100
            wc_page = 1
            all_matching: List[Dict[str, Any]] = []
            need_count = page * per_page
            while len(all_matching) < need_count:
                response = wc_connector.get_orders(
                    per_page=fetch_per_page, page=wc_page, status=status
                )
                if not response or response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code if response else 500,
                        detail="Failed to fetch orders",
                    )
                batch = response.json()
                for o in batch if isinstance(batch, list) else []:
                    if isinstance(o, dict) and _has_coupon_code(o, coupon_code):
                        all_matching.append(o)
                if len(batch) < fetch_per_page:
                    break
                wc_page += 1
                if wc_page > 50:
                    break
            start = (page - 1) * per_page
            orders_data = all_matching[start : start + per_page]
            logger.info(f"Coupon filter '{coupon_code}': found {len(all_matching)} orders, returning {len(orders_data)}")
        else:
            response = wc_connector.get_orders(
                per_page=per_page, page=page, status=status
            )
            if not response or response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code if response else 500,
                    detail="Failed to fetch orders",
                )
            raw = response.json()
            if isinstance(raw, list):
                orders_data = raw
            elif isinstance(raw, dict):
                orders_data = raw.get('orders', raw.get('data', []))
                if not isinstance(orders_data, list):
                    orders_data = []
                if not orders_data and ('code' in raw or 'message' in raw):
                    err_msg = raw.get('message', raw.get('code', 'WooCommerce API error'))
                    logger.error(f"WooCommerce API returned error: {raw}")
                    raise HTTPException(status_code=500, detail=str(err_msg))
            else:
                orders_data = []
            logger.info(f"Fetched {len(orders_data)} orders from WooCommerce in {time.perf_counter()-t0:.1f}s")

        # Преобразуем в формат для фронтенда
        orders = []
        fetch_groups = (load_product_groups in ("1", "true", "yes")) and wc_connector and len(orders_data) <= 30
        if fetch_groups:
            logger.info(f"Loading product groups for {len(orders_data)} orders...")
        for i, order_data in enumerate(orders_data):
            if not isinstance(order_data, dict):
                continue
            order = Order.from_dict(order_data)
            
            # Проверяем статус синхронизации
            sync_status = "not_synced"
            lilu_client_id = None
            if sync_service:
                processed = sync_service.tracker.get_processed_order(order.id)
                if processed:
                    sync_status = processed.status
                    lilu_client_id = processed.lilu_client_id
            
            # Фильтр по поиску
            if search:
                search_lower = search.lower()
                if (str(order.id) != search_lower and 
                    order.customer_name.lower().find(search_lower) == -1 and
                    (order.customer_email or "").lower().find(search_lower) == -1):
                    continue
            
            # Купоны
            coupon_codes = [
                cl.get("code", "") for cl in (order.coupon_lines or [])
                if isinstance(cl, dict) and cl.get("code")
            ]
            # Группы товаров (категории)
            product_groups = []
            if fetch_groups:
                cats = get_order_product_categories(wc_connector, order.line_items)
                product_groups = [c.get("name", "") for c in cats if isinstance(c, dict) and c.get("name")]
                if (i + 1) % 5 == 0 or i == len(orders_data) - 1:
                    logger.debug(f"Product groups: {i+1}/{len(orders_data)} orders processed")

            po = sync_service.tracker.get_processed_order(order.id) if sync_service else None
            display_id = (po.get_display_id() if po else None) or lilu_client_id

            orders.append({
                "id": order.id,
                "currency": order.currency,
                "date": order.date_created,
                "customer_name": order.customer_name,
                "customer_phone": order.billing.get("phone", "") if order.billing else "",
                "customer_email": order.customer_email,
                "total": order.total,
                "status": order.status,
                "coupon_codes": coupon_codes,
                "product_groups": product_groups,
                "sync_status": sync_status,
                "lilu_client_id": lilu_client_id,
                "client_identifier": po.client_identifier if po else None,
                "display_id": display_id if display_id != "-" else None,
            })
        
        # Проверяем, есть ли ещё страницы
        has_more = len(orders_data) >= per_page
        elapsed = time.perf_counter() - t0
        logger.info(f"get_orders: done in {elapsed:.1f}s, returning {len(orders)} orders")

        return JSONResponse({
            "orders": orders,
            "page": page,
            "per_page": per_page,
            "total": len(orders),
            "has_more": has_more,
        })
    
    except Exception as e:
        logger.error(f"get_orders failed after {time.perf_counter()-t0:.1f}s: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders/{order_id}")
async def get_order_detail(order_id: int) -> JSONResponse:
    """
    Получить детали заказа.
    
    Args:
        order_id: ID заказа
    
    Returns:
        JSONResponse: Детали заказа
    """
    if not wc_connector:
        raise HTTPException(status_code=500, detail="WooCommerce connector not initialized")
    
    logger.info(f"get_order_detail: order_id={order_id}")
    try:
        order_data = wc_connector.get_order_by_id(order_id)
        
        if not order_data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = Order.from_dict(order_data)
        
        # Информация о синхронизации
        sync_info = {
            "synced": False,
            "lilu_client_id": None,
            "synced_at": None,
            "status": "not_synced",
            "tags_added": []
        }
        
        if sync_service:
            processed = sync_service.tracker.get_processed_order(order.id)
            if processed:
                sync_info = {
                    "synced": True,
                    "lilu_client_id": processed.lilu_client_id,
                    "client_identifier": processed.client_identifier,
                    "display_id": processed.get_display_id() if processed.get_display_id() != "-" else None,
                    "synced_at": processed.processed_at,
                    "status": processed.status,
                    "tags_added": processed.tags_added
                }
        
        return JSONResponse({
            "id": order.id,
            "date": order.date_created,
            "date_modified": order.date_modified,
            "status": order.status,
            "total": order.total,
            "currency": order.currency,
            "discount_total": order.discount_total,
            "shipping_total": order.shipping_total,
            "total_tax": order.total_tax,
            "customer_id": order.customer_id,
            "customer_note": order.customer_note,
            "customer": {
                "name": order.customer_name,
                "phone": order.billing.get("phone", "") if order.billing else "",
                "email": order.customer_email
            },
            "billing": order.billing,
            "shipping": order.shipping,
            "payment_method": order.payment_method,
            "payment_method_title": order.payment_method_title,
            "transaction_id": order.transaction_id,
            "items": order.line_items,
            "product_categories": _get_order_product_categories(order),
            "tax_lines": order.tax_lines,
            "shipping_lines": order.shipping_lines,
            "fee_lines": order.fee_lines,
            "coupon_lines": order.coupon_lines,
            "refunds": order.refunds,
            "meta_data": order.meta_data,
            "sync_status": sync_info
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/orders/{order_id}/sync")
async def sync_order(order_id: int) -> JSONResponse:
    """
    Синхронизировать заказ в LILU CRM.
    
    Args:
        order_id: ID заказа для синхронизации
    
    Returns:
        JSONResponse: Результат синхронизации
    """
    if not wc_connector or not sync_service:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    try:
        # Получаем заказ
        order_data = wc_connector.get_order_by_id(order_id)
        
        if not order_data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = Order.from_dict(order_data)
        
        # Синхронизируем
        result: SyncResult = sync_service.sync_order(order)
        
        # Формируем ответ
        response_data = {
            "order_id": result.order_id,
            "success": result.success,
            "action": result.action,
            "lilu_client_id": result.lilu_client_id,
            "client_identifier": result.client_identifier,
            "display_id": result.get_display_id(),
            "tags_added": result.tags_added,
            "error_message": result.error_message
        }
        
        # Сообщение для пользователя
        if result.success:
            if result.action == "created":
                response_data["message"] = f"✅ Клиент создан в LILU ({result.get_display_id()})"
            elif result.action == "updated":
                if result.tags_added:
                    response_data["message"] = f"✅ Клиент обновлен в LILU. Добавлены теги: {', '.join(result.tags_added)}"
                else:
                    response_data["message"] = f"✅ Клиент в LILU ({result.get_display_id()})"
            else:
                response_data["message"] = "⚠️ Заказ уже был обработан ранее"
        else:
            response_data["message"] = f"❌ Ошибка: {result.error_message}"
        
        status_code = 200 if result.success else 400
        return JSONResponse(content=response_data, status_code=status_code)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing order {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/orders/{order_id}/unsync")
async def unsync_order(order_id: int) -> JSONResponse:
    """
    Удалить клиента из LILU и отменить синхронизацию заказа.
    
    Args:
        order_id: ID заказа
    
    Returns:
        JSONResponse: Результат операции
    """
    if not sync_service or not lilu_connector:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    try:
        processed = sync_service.tracker.get_processed_order(order_id)
        if not processed:
            return JSONResponse(
                content={"success": False, "message": "Заказ не был синхронизирован"},
                status_code=400
            )
        
        # Удаляем клиента из LILU, если есть lilu_client_id
        if processed.lilu_client_id:
            try:
                lilu_connector.delete_client(processed.lilu_client_id)
            except Exception as e:
                logger.warning(f"Failed to delete client from LILU: {e}")
                return JSONResponse(
                    content={
                        "success": False,
                        "message": f"Ошибка удаления из LILU: {e}"
                    },
                    status_code=500
                )
        
        sync_service.tracker.unmark_processed(order_id)
        
        return JSONResponse(content={
            "success": True,
            "message": "Клиент удалён из LILU, синхронизация отменена",
            "order_id": order_id
        })
    
    except Exception as e:
        logger.error(f"Error unsyncing order {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sync/status")
async def get_sync_status() -> JSONResponse:
    """
    Получить статус синхронизации.
    
    Returns:
        JSONResponse: Статистика синхронизации
    """
    if not sync_service:
        raise HTTPException(status_code=500, detail="Sync service not initialized")
    
    try:
        stats = sync_service.get_statistics()
        return JSONResponse(stats)
    
    except Exception as e:
        logger.error(f"Error getting sync status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/product-categories")
async def get_product_categories() -> JSONResponse:
    """
    Получить список категорий товаров WooCommerce.
    Для составления маппинга категорий -> теги LILU.
    """
    if not wc_connector:
        raise HTTPException(status_code=500, detail="WooCommerce connector not initialized")
    try:
        response = wc_connector.wcapi.get(
            "products/categories", params={"per_page": 100}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch categories")
        categories = response.json()
        return JSONResponse([{"id": c.get("id"), "name": c.get("name"), "slug": c.get("slug")} for c in categories])
    except Exception as e:
        logger.error(f"Error fetching categories: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check() -> JSONResponse:
    """Проверка здоровья приложения."""
    return JSONResponse({
        "status": "ok",
        "wc_connector": wc_connector is not None,
        "lilu_connector": lilu_connector is not None,
        "sync_service": sync_service is not None
    })


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
