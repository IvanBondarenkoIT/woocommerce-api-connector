"""
GUI компоненты приложения.

Этот модуль будет содержать компоненты графического интерфейса
после рефакторинга. Пока оставляем пустым, чтобы избежать
конфликтов с woocommerce_connector/gui.py.

После рефакторинга:
- MainWindow - главное окно
- ProductListView - список товаров
- ProductDetailsView - детали товара
- Widgets - переиспользуемые виджеты
"""

# Пока пусто - GUI импортируется напрямую из gui.py
# После рефакторинга здесь будут новые компоненты

__all__ = ["main"]


def main():
    """Прокси к main() из gui.py (файл перекрыт пакетом gui/)."""
    import importlib.util
    import sys
    from pathlib import Path
    _gui_path = Path(__file__).resolve().parent.parent / "gui.py"
    _spec = importlib.util.spec_from_file_location("woocommerce_connector._gui_app", _gui_path)
    _mod = importlib.util.module_from_spec(_spec)
    _mod.__package__ = "woocommerce_connector"
    sys.modules["woocommerce_connector._gui_app"] = _mod
    _spec.loader.exec_module(_mod)
    _mod.main()
