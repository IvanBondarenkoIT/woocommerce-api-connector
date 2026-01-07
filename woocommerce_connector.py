"""
WooCommerce API Connector
Connects to WordPress WooCommerce store and fetches product data
"""

import os
import json
import sys
from dotenv import load_dotenv
from woocommerce import API

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables
load_dotenv()


class WooCommerceConnector:
    """Class to handle WooCommerce API connections"""
    
    def __init__(self):
        """Initialize WooCommerce API connection"""
        self.url = os.getenv('WC_URL', '').rstrip('/')  # Remove trailing slash
        self.consumer_key = os.getenv('WC_CONSUMER_KEY')
        self.consumer_secret = os.getenv('WC_CONSUMER_SECRET')
        self.api_version = os.getenv('WC_API_VERSION', 'wc/v3')
        
        if not all([self.url, self.consumer_key, self.consumer_secret]):
            raise ValueError(
                "Missing required environment variables. "
                "Please check your .env file."
            )
        
        # Initialize WooCommerce API
        # Try with query_string_auth=True if OAuth fails
        self.wcapi = API(
            url=self.url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version=self.api_version,
            timeout=30,
            query_string_auth=True  # Use query string auth instead of OAuth
        )
    
    def get_products(self, per_page=10, page=1):
        """
        Fetch products from WooCommerce store
        
        Args:
            per_page: Number of products per page (default: 10)
            page: Page number (default: 1)
        
        Returns:
            dict: API response with products
        """
        try:
            response = self.wcapi.get(
                'products',
                params={
                    'per_page': per_page,
                    'page': page
                }
            )
            if response.status_code != 200:
                print(f"API Error: Status {response.status_code}")
                print(f"Response: {response.text}")
            return response
        except Exception as e:
            print(f"Error fetching products: {str(e)}")
            return None
    
    def get_all_products(self, per_page=100):
        """
        Fetch ALL products from WooCommerce store with pagination
        
        Args:
            per_page: Number of products per page (default: 100, max recommended)
        
        Returns:
            list: List of all products
        """
        all_products = []
        page = 1
        
        while True:
            try:
                response = self.get_products(per_page=per_page, page=page)
                
                if not response or response.status_code != 200:
                    break
                
                products = response.json()
                
                if not products:
                    break
                
                all_products.extend(products)
                
                # Check if there are more pages
                # WooCommerce API returns empty list when no more products
                if len(products) < per_page:
                    break
                
                page += 1
                
            except Exception as e:
                print(f"Error fetching page {page}: {str(e)}")
                break
        
        return all_products
    
    def get_product_fields(self, product_id=None):
        """
        Get product data and display available fields
        
        Args:
            product_id: Specific product ID (optional)
        
        Returns:
            dict: Product data with all fields
        """
        try:
            if product_id:
                response = self.wcapi.get(f'products/{product_id}')
            else:
                # Get first product to see fields
                response = self.get_products(per_page=1, page=1)
                if response and response.status_code == 200:
                    products = response.json()
                    if products:
                        return products[0]
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error fetching product: {str(e)}")
            return None
    
    def display_product_fields(self, product=None):
        """
        Display all available fields from a product
        
        Args:
            product: Product dictionary (optional, will fetch if not provided)
        """
        if not product:
            product = self.get_product_fields()
        
        if not product:
            print("No product data available")
            return
        
        print("\n" + "="*80)
        print("WOOCOMMERCE PRODUCT FIELDS")
        print("="*80)
        print(f"\nProduct ID: {product.get('id', 'N/A')}")
        print(f"Product Name: {product.get('name', 'N/A')}")
        print("\n" + "-"*80)
        print("ALL AVAILABLE FIELDS:")
        print("-"*80)
        
        # Display all fields in a structured way
        for key, value in product.items():
            if isinstance(value, (dict, list)):
                print(f"\n{key}:")
                print(json.dumps(value, indent=2, ensure_ascii=False))
            else:
                print(f"{key}: {value}")
        
        print("\n" + "="*80)
    
    def display_products_summary(self, limit=10):
        """
        Display a summary of products
        
        Args:
            limit: Number of products to display
        """
        response = self.get_products(per_page=limit)
        
        if not response:
            print("Failed to fetch products: No response")
            return
            
        if response.status_code != 200:
            print(f"Failed to fetch products: Status {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        products = response.json()
        
        if not products:
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
    
    def check_api_version(self):
        """
        Check which WooCommerce API version is available
        Returns the working API version
        """
        print("\n" + "="*80)
        print("CHECKING WOOCOMMERCE API VERSION")
        print("="*80)
        
        # Common API versions to test
        versions_to_test = ['wc/v3', 'v3', 'wc/v2', 'v2', 'wc/v1', 'v1']
        
        working_version = None
        
        for version in versions_to_test:
            try:
                print(f"\nTesting version: {version}...", end=" ")
                
                # Create temporary API instance with this version
                test_api = API(
                    url=self.url,
                    consumer_key=self.consumer_key,
                    consumer_secret=self.consumer_secret,
                    version=version,
                    timeout=10,
                    query_string_auth=True
                )
                
                # Try to get system status or products
                response = test_api.get('system_status')
                if response.status_code == 200:
                    print("[OK] - Working!")
                    working_version = version
                    break
                elif response.status_code == 404:
                    # Try products endpoint instead
                    response = test_api.get('products', params={'per_page': 1})
                    if response.status_code == 200:
                        print("[OK] - Working!")
                        working_version = version
                        break
                    else:
                        print(f"[FAILED] - Status {response.status_code}")
                else:
                    print(f"[FAILED] - Status {response.status_code}")
                    
            except Exception as e:
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
            return None
    
    def get_store_info(self):
        """
        Get WooCommerce store information
        """
        try:
            response = self.wcapi.get('system_status')
            if response.status_code == 200:
                return response.json()
            else:
                # Try alternative endpoint
                response = self.wcapi.get('')
                if response.status_code == 200:
                    return response.json()
            return None
        except Exception as e:
            print(f"Error getting store info: {str(e)}")
            return None


def check_api_version_standalone():
    """
    Standalone function to check API version without full initialization
    """
    import os
    from dotenv import load_dotenv
    from woocommerce import API
    
    load_dotenv()
    
    url = os.getenv('WC_URL', '').rstrip('/')
    consumer_key = os.getenv('WC_CONSUMER_KEY')
    consumer_secret = os.getenv('WC_CONSUMER_SECRET')
    
    if not all([url, consumer_key, consumer_secret]):
        print("Error: Missing environment variables in .env file")
        return None
    
    print("\n" + "="*80)
    print("CHECKING WOOCOMMERCE API VERSION")
    print("="*80)
    print(f"Store URL: {url}\n")
    
    # Common API versions to test
    versions_to_test = ['wc/v3', 'v3', 'wc/v2', 'v2']
    
    working_versions = []
    
    for version in versions_to_test:
        try:
            print(f"Testing version: {version:10} ... ", end="")
            
            test_api = API(
                url=url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                version=version,
                timeout=10,
                query_string_auth=True
            )
            
            # Try products endpoint (most common)
            response = test_api.get('products', params={'per_page': 1})
            
            if response.status_code == 200:
                print("[OK] - Working!")
                working_versions.append(version)
            elif response.status_code == 401:
                print("[AUTH ERROR] - Check credentials")
            elif response.status_code == 404:
                print("[NOT FOUND] - Version not available")
            else:
                print(f"[FAILED] - Status {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] - {str(e)[:50]}")
    
    print(f"\n{'='*80}")
    if working_versions:
        print(f"WORKING VERSIONS: {', '.join(working_versions)}")
        print(f"RECOMMENDED: {working_versions[0]}")
        print(f"{'='*80}\n")
        return working_versions[0]
    else:
        print("WARNING: No working API versions found!")
        print("Please check your credentials and store URL")
        print(f"{'='*80}\n")
        return None


def main():
    """Main function to test the connection"""
    try:
        print("Initializing WooCommerce connection...")
        connector = WooCommerceConnector()
        print("[OK] Connection initialized successfully!")
        
        # Display product fields
        print("\nFetching product data to see available fields...")
        connector.display_product_fields()
        
        # Display products summary
        print("\n\nFetching products summary...")
        connector.display_products_summary(limit=5)
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease create a .env file based on .env.example")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    import sys
    
    # Check if user wants to check API version only
    if len(sys.argv) > 1 and sys.argv[1] == '--check-version':
        check_api_version_standalone()
    else:
        main()

