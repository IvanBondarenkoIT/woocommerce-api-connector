#!/usr/bin/env python
"""
Script to run WooCommerce connector CLI
"""

import sys
from woocommerce_connector.connector import main, check_api_version_standalone

if __name__ == "__main__":
    # Check if user wants to check API version only
    if len(sys.argv) > 1 and sys.argv[1] == '--check-version':
        check_api_version_standalone()
    else:
        main()



