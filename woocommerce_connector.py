"""
WooCommerce API Connector
Connects to WordPress WooCommerce store and fetches product data
"""

import os
import json
from dotenv import load_dotenv
from woocommerce import API

# Load environment variables
load_dotenv()


class WooCommerceConnector:
    """Class to handle WooCommerce API connections"""
    
    def __init__(self):
        """Initialize WooCommerce API connection"""
        self.url = os.getenv('WC_URL')
        self.consumer_key = os.getenv('WC_CONSUMER_KEY')
        self.consumer_secret = os.getenv('WC_CONSUMER_SECRET')
        self.api_version = os.getenv('WC_API_VERSION', 'v3')
        
        if not all([self.url, self.consumer_key, self.consumer_secret]):
            raise ValueError(
                "Missing required environment variables. "
                "Please check your .env file."
            )
        
        # Initialize WooCommerce API
        self.wcapi = API(
            url=self.url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version=self.api_version,
            timeout=30
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
            return response
        except Exception as e:
            print(f"Error fetching products: {str(e)}")
            return None
    
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
        
        if not response or response.status_code != 200:
            print("Failed to fetch products")
            return
        
        products = response.json()
        
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


def main():
    """Main function to test the connection"""
    try:
        print("Initializing WooCommerce connection...")
        connector = WooCommerceConnector()
        print("✓ Connection initialized successfully!")
        
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
    main()

