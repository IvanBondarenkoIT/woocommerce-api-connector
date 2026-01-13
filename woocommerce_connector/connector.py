"""
WooCommerce API Connector
Connects to WordPress WooCommerce store and fetches product data
"""

import json
import sys
from typing import Optional, List, Dict, Any
from woocommerce import API

# Импортируем новые компоненты
from .config import WooCommerceConfig
from .utils.logger import setup_logger
from .api.exceptions import (
    ConfigurationError,
    AuthenticationError,
    NotFoundError,
    APIResponseError,
    NetworkError,
)

# Настраиваем logger для модуля
logger = setup_logger(__name__)

# Fix encoding for Windows console (оставляем для обратной совместимости)
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class WooCommerceConnector:
    """
    Класс для работы с WooCommerce API.
    
    Предоставляет методы для подключения к WooCommerce магазину
    и получения данных о товарах, заказах и другой информации.
    
    Example:
        >>> from woocommerce_connector import WooCommerceConnector
        >>> connector = WooCommerceConnector()
        >>> products = connector.get_all_products()
    """
    
    def __init__(self, config: Optional[WooCommerceConfig] = None):
        """
        Инициализация подключения к WooCommerce API.
        
        Args:
            config: Объект конфигурации WooCommerceConfig.
                   Если не указан, загружается из переменных окружения.
        
        Raises:
            ConfigurationError: Если конфигурация невалидна или отсутствует
        
        Example:
            >>> # Использование конфигурации по умолчанию (из .env)
            >>> connector = WooCommerceConnector()
            >>> 
            >>> # Использование кастомной конфигурации
            >>> from woocommerce_connector.config import WooCommerceConfig
            >>> config = WooCommerceConfig(
            ...     url="https://store.com",
            ...     consumer_key="ck_...",
            ...     consumer_secret="cs_..."
            ... )
            >>> connector = WooCommerceConnector(config)
        """
        # Загружаем конфигурацию
        if config is None:
            try:
                config = WooCommerceConfig.from_env()
                config.validate()
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}", exc_info=True)
                raise ConfigurationError(f"Failed to load configuration: {e}")
        
        self.config = config
        self.url = config.url
        self.consumer_key = config.consumer_key
        self.consumer_secret = config.consumer_secret
        self.api_version = config.api_version
        
        logger.info(f"Initializing WooCommerce connection to {self.url}")
        
        # Initialize WooCommerce API
        try:
            self.wcapi = API(
                url=self.url,
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                version=self.api_version,
                timeout=config.timeout,
                query_string_auth=config.query_string_auth
            )
            logger.info("WooCommerce API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WooCommerce API: {e}", exc_info=True)
            raise ConfigurationError(f"Failed to initialize API client: {e}")
    
    def get_products(self, per_page: int = 10, page: int = 1) -> Optional[Any]:
        """
        Получить товары из WooCommerce магазина.
        
        Args:
            per_page: Количество товаров на странице (по умолчанию 10)
            page: Номер страницы (по умолчанию 1)
        
        Returns:
            Response объект с товарами или None в случае ошибки
        
        Raises:
            APIResponseError: При ошибке API запроса
            NetworkError: При проблемах с сетью
        
        Example:
            >>> response = connector.get_products(per_page=20, page=1)
            >>> if response and response.status_code == 200:
            ...     products = response.json()
        """
        try:
            logger.debug(f"Fetching products: page={page}, per_page={per_page}")
            response = self.wcapi.get(
                'products',
                params={
                    'per_page': per_page,
                    'page': page
                }
            )
            
            if response.status_code != 200:
                error_msg = f"API Error: Status {response.status_code}"
                logger.error(f"{error_msg} - Response: {response.text}")
                
                # Определяем тип ошибки по статусу
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API credentials")
                elif response.status_code == 404:
                    raise NotFoundError("Products endpoint")
                else:
                    raise APIResponseError(
                        response.status_code,
                        error_msg,
                        response.text
                    )
            
            logger.debug(f"Successfully fetched {len(response.json())} products from page {page}")
            return response
            
        except (AuthenticationError, NotFoundError, APIResponseError):
            raise  # Пробрасываем наши исключения дальше
        except Exception as e:
            logger.error(f"Error fetching products: {e}", exc_info=True)
            raise NetworkError(f"Network error while fetching products: {e}")
    
    def get_all_products(self, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Получить ВСЕ товары из WooCommerce магазина с пагинацией.
        
        Автоматически обрабатывает пагинацию и загружает все страницы товаров.
        
        Args:
            per_page: Количество товаров на странице (по умолчанию 100, максимум рекомендуется)
        
        Returns:
            Список всех товаров
        
        Raises:
            APIResponseError: При ошибке API запроса
            NetworkError: При проблемах с сетью
        
        Example:
            >>> all_products = connector.get_all_products()
            >>> print(f"Total products: {len(all_products)}")
        """
        all_products = []
        page = 1
        
        logger.info(f"Starting to fetch all products (per_page={per_page})")
        
        while True:
            try:
                response = self.get_products(per_page=per_page, page=page)
                
                if not response or response.status_code != 200:
                    logger.warning(f"Failed to fetch page {page}, stopping pagination")
                    break
                
                products = response.json()
                
                if not products:
                    logger.debug(f"No products on page {page}, stopping pagination")
                    break
                
                all_products.extend(products)
                logger.debug(f"Fetched page {page}: {len(products)} products (total: {len(all_products)})")
                
                # Проверяем есть ли еще страницы
                if len(products) < per_page:
                    logger.debug("Last page reached")
                    break
                
                page += 1
                
            except (AuthenticationError, NotFoundError, APIResponseError, NetworkError):
                # Пробрасываем наши исключения
                raise
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}", exc_info=True)
                raise NetworkError(f"Error during pagination: {e}")
        
        logger.info(f"Successfully fetched {len(all_products)} products from {page} page(s)")
        return all_products
    
    def get_product_fields(self, product_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Получить данные товара и отобразить доступные поля.
        
        Args:
            product_id: ID конкретного товара (опционально)
        
        Returns:
            Словарь с данными товара или None в случае ошибки
        
        Raises:
            NotFoundError: Если товар не найден
            APIResponseError: При ошибке API запроса
        """
        try:
            if product_id:
                logger.debug(f"Fetching product with ID: {product_id}")
                response = self.wcapi.get(f'products/{product_id}')
            else:
                # Получаем первый товар для просмотра полей
                logger.debug("Fetching first product to see available fields")
                response = self.get_products(per_page=1, page=1)
                if response and response.status_code == 200:
                    products = response.json()
                    if products:
                        return products[0]
                return None
            
            if response.status_code == 200:
                product = response.json()
                logger.debug(f"Successfully fetched product: {product.get('name', 'Unknown')}")
                return product
            elif response.status_code == 404:
                raise NotFoundError("Product", str(product_id))
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise APIResponseError(response.status_code, error_msg, response.text)
                
        except (NotFoundError, APIResponseError):
            raise
        except Exception as e:
            logger.error(f"Error fetching product: {e}", exc_info=True)
            raise NetworkError(f"Error fetching product: {e}")
    
    def display_product_fields(self, product: Optional[Dict[str, Any]] = None) -> None:
        """
        Отобразить все доступные поля товара.
        
        Args:
            product: Словарь с данными товара (опционально, будет получен если не указан)
        
        Note:
            Этот метод использует print() для обратной совместимости с CLI.
            Для программного использования лучше использовать get_product_fields().
        """
        if not product:
            product = self.get_product_fields()
        
        if not product:
            logger.warning("No product data available to display")
            print("No product data available")
            return
        
        logger.debug("Displaying product fields")
        print("\n" + "="*80)
        print("WOOCOMMERCE PRODUCT FIELDS")
        print("="*80)
        print(f"\nProduct ID: {product.get('id', 'N/A')}")
        print(f"Product Name: {product.get('name', 'N/A')}")
        print("\n" + "-"*80)
        print("ALL AVAILABLE FIELDS:")
        print("-"*80)
        
        # Отображаем все поля структурированно
        for key, value in product.items():
            if isinstance(value, (dict, list)):
                print(f"\n{key}:")
                print(json.dumps(value, indent=2, ensure_ascii=False))
            else:
                print(f"{key}: {value}")
        
        print("\n" + "="*80)
    
    def display_products_summary(self, limit: int = 10) -> None:
        """
        Отобразить краткую сводку по товарам.
        
        Args:
            limit: Количество товаров для отображения
        
        Note:
            Этот метод использует print() для обратной совместимости с CLI.
        """
        logger.info(f"Displaying products summary (limit={limit})")
        response = self.get_products(per_page=limit)
        
        if not response:
            logger.warning("Failed to fetch products: No response")
            print("Failed to fetch products: No response")
            return
            
        if response.status_code != 200:
            error_msg = f"Failed to fetch products: Status {response.status_code}"
            logger.error(f"{error_msg} - Response: {response.text}")
            print(error_msg)
            print(f"Response: {response.text}")
            return
        
        products = response.json()
        
        if not products:
            logger.info("No products found in the store")
            print("No products found in the store")
            return
        
        print("\n" + "="*80)
        print(f"PRODUCTS SUMMARY (Showing {len(products)} products)")
        print("="*80)
        
        for idx, product in enumerate(products, 1):
            print(f"\n{idx}. {product.get('name', 'N/A')}")
            print(f"   ID: {product.get('id', 'N/A')}")
            print(f"   SKU: {product.get('sku', 'N/A')}")
            print(f"   Price: {product.get('price', 'N/A')}")
            print(f"   Status: {product.get('status', 'N/A')}")
            print(f"   Stock Status: {product.get('stock_status', 'N/A')}")
            if product.get('categories'):
                categories = [cat.get('name') for cat in product.get('categories', [])]
                print(f"   Categories: {', '.join(categories)}")
        
        print("\n" + "="*80)
        logger.debug(f"Displayed summary for {len(products)} products")
    
    def check_api_version(self) -> Optional[str]:
        """
        Проверить какая версия WooCommerce API доступна.
        
        Returns:
            Рабочую версию API или None если не удалось определить
        
        Note:
            Этот метод использует print() для обратной совместимости с CLI.
        """
        logger.info("Checking WooCommerce API version")
        print("\n" + "="*80)
        print("CHECKING WOOCOMMERCE API VERSION")
        print("="*80)
        
        # Версии API для проверки
        from .config.constants import APIConstants
        versions_to_test = APIConstants.SUPPORTED_VERSIONS
        
        working_version = None
        
        for version in versions_to_test:
            try:
                logger.debug(f"Testing API version: {version}")
                print(f"\nTesting version: {version}...", end=" ")
                
                # Создаем временный API экземпляр с этой версией
                test_api = API(
                    url=self.url,
                    consumer_key=self.consumer_key,
                    consumer_secret=self.consumer_secret,
                    version=version,
                    timeout=10,
                    query_string_auth=True
                )
                
                # Пробуем получить system_status или products
                response = test_api.get('system_status')
                if response.status_code == 200:
                    print("[OK] - Working!")
                    working_version = version
                    logger.info(f"Found working API version: {version}")
                    break
                elif response.status_code == 404:
                    # Пробуем products endpoint
                    response = test_api.get('products', params={'per_page': 1})
                    if response.status_code == 200:
                        print("[OK] - Working!")
                        working_version = version
                        logger.info(f"Found working API version: {version}")
                        break
                    else:
                        print(f"[FAILED] - Status {response.status_code}")
                else:
                    print(f"[FAILED] - Status {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"Error testing version {version}: {e}")
                print(f"[ERROR] - {str(e)}")
        
        if working_version:
            print(f"\n{'='*80}")
            print(f"RECOMMENDED API VERSION: {working_version}")
            print(f"{'='*80}")
            return working_version
        else:
            print(f"\n{'='*80}")
            print("WARNING: Could not determine API version automatically")
            print("Current version in .env might be incorrect")
            print(f"{'='*80}")
            logger.warning("Could not determine working API version")
            return None
    
    def get_store_info(self) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о WooCommerce магазине.
        
        Returns:
            Словарь с информацией о магазине или None в случае ошибки
        """
        try:
            logger.debug("Fetching store information")
            response = self.wcapi.get('system_status')
            if response.status_code == 200:
                store_info = response.json()
                logger.info("Successfully fetched store information")
                return store_info
            else:
                # Пробуем альтернативный endpoint
                response = self.wcapi.get('')
                if response.status_code == 200:
                    logger.info("Successfully fetched store information (alternative endpoint)")
                    return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting store info: {e}", exc_info=True)
            return None


def check_api_version_standalone() -> Optional[str]:
    """
    Автономная функция для проверки версии API без полной инициализации.
    
    Returns:
        Рабочую версию API или None если не удалось определить
    
    Note:
        Используется для CLI команды --check-version
    """
    try:
        config = WooCommerceConfig.from_env()
        config.validate()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        print("Error: Missing environment variables in .env file")
        return None
    
    logger.info("Standalone API version check")
    print("\n" + "="*80)
    print("CHECKING WOOCOMMERCE API VERSION")
    print("="*80)
    print(f"Store URL: {config.url}\n")
    
    from .config.constants import APIConstants
    versions_to_test = APIConstants.SUPPORTED_VERSIONS
    
    working_versions = []
    
    for version in versions_to_test:
        try:
            logger.debug(f"Testing version: {version}")
            print(f"Testing version: {version:10} ... ", end="")
            
            test_api = API(
                url=config.url,
                consumer_key=config.consumer_key,
                consumer_secret=config.consumer_secret,
                version=version,
                timeout=10,
                query_string_auth=True
            )
            
            # Пробуем products endpoint (самый распространенный)
            response = test_api.get('products', params={'per_page': 1})
            
            if response.status_code == 200:
                print("[OK] - Working!")
                working_versions.append(version)
                logger.info(f"Found working version: {version}")
            elif response.status_code == 401:
                print("[AUTH ERROR] - Check credentials")
                logger.warning("Authentication error while checking version")
            elif response.status_code == 404:
                print("[NOT FOUND] - Version not available")
            else:
                print(f"[FAILED] - Status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error testing version {version}: {e}")
            print(f"[ERROR] - {str(e)[:50]}")
    
    print(f"\n{'='*80}")
    if working_versions:
        print(f"WORKING VERSIONS: {', '.join(working_versions)}")
        print(f"RECOMMENDED: {working_versions[0]}")
        print(f"{'='*80}\n")
        logger.info(f"Recommended API version: {working_versions[0]}")
        return working_versions[0]
    else:
        print("WARNING: No working API versions found!")
        print("Please check your credentials and store URL")
        print(f"{'='*80}\n")
        logger.warning("No working API versions found")
        return None


def main() -> None:
    """Главная функция для тестирования подключения"""
    try:
        logger.info("Starting WooCommerce connector test")
        print("Initializing WooCommerce connection...")
        connector = WooCommerceConnector()
        print("[OK] Connection initialized successfully!")
        logger.info("Connection initialized successfully")
        
        # Отображаем поля товара
        print("\nFetching product data to see available fields...")
        connector.display_product_fields()
        
        # Отображаем сводку по товарам
        print("\n\nFetching products summary...")
        connector.display_products_summary(limit=5)
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration Error: {e}")
        print("\nPlease create a .env file based on .env.example")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    import sys
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1 and sys.argv[1] == '--check-version':
        check_api_version_standalone()
    else:
        main()
