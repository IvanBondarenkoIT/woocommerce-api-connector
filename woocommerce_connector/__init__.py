"""
WooCommerce API Connector Package

A Python package for connecting to WooCommerce stores via REST API
and managing products with a modern GUI interface.
"""

from .connector import WooCommerceConnector, check_api_version_standalone

# GUI импортируем лениво для избежания конфликтов с папкой gui/
# и проблемами с customtkinter при импорте в тестах
def __getattr__(name):
    """Ленивый импорт для GUI"""
    if name == 'WooCommerceGUI':
        try:
            # Импортируем напрямую из модуля gui.py
            # Используем абсолютный импорт для обхода конфликта с папкой gui/
            import importlib
            # Создаем специальный loader для gui.py
            import sys
            from pathlib import Path
            
            # Импортируем через sys.modules обход
            if 'woocommerce_connector.gui_module' not in sys.modules:
                # Загружаем gui.py как отдельный модуль
                gui_path = Path(__file__).parent / "gui.py"
                spec = importlib.util.spec_from_file_location(
                    "woocommerce_connector.gui_module", 
                    gui_path
                )
                gui_module = importlib.util.module_from_spec(spec)
                # Устанавливаем правильный parent для относительных импортов
                gui_module.__package__ = 'woocommerce_connector'
                spec.loader.exec_module(gui_module)
                sys.modules['woocommerce_connector.gui_module'] = gui_module
            else:
                gui_module = sys.modules['woocommerce_connector.gui_module']
            
            return gui_module.WooCommerceGUI
        except Exception:
            # Если не удалось импортировать, возвращаем None
            return None
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

import importlib.util

__version__ = "1.0.0"
__author__ = "Ivan Bondarenko"
__email__ = ""

__all__ = [
    "WooCommerceConnector",
    "WooCommerceGUI",
    "check_api_version_standalone",
]



