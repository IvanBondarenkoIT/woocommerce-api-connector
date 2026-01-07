# WooCommerce API Connector

[![Tests](https://github.com/IvanBondarenkoIT/woocommerce-api-connector/actions/workflows/tests.yml/badge.svg)](https://github.com/IvanBondarenkoIT/woocommerce-api-connector/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Python project to connect to WordPress WooCommerce store via REST API and fetch product data. Features a modern GUI for viewing and managing products, with Excel export functionality.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3a. Install as Package (Optional)

You can also install the package in development mode:

```bash
pip install -e .
```

This allows you to use the package from anywhere and access CLI commands.

### 4. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your WooCommerce API credentials:
   ```
   WC_URL=https://your-store.com
   WC_CONSUMER_KEY=ck_your_consumer_key_here
   WC_CONSUMER_SECRET=cs_your_consumer_secret_here
   WC_API_VERSION=wc/v3
   ```
   
   **Note:** API version should be `wc/v3` (not just `v3`)

### 5. Get WooCommerce API Credentials

1. Go to your WordPress admin panel
2. Navigate to: **WooCommerce → Settings → Advanced → REST API**
3. Click **Add Key**
4. Set permissions to **Read/Write**
5. Copy the **Consumer Key** and **Consumer Secret**

## Usage

### Option 1: GUI Application (Recommended)

Run the modern GUI application:

```bash
# Using Python module
python -m woocommerce_connector.gui

# Or using the script
python scripts/run_gui.py

# Or after installation
woocommerce-gui
```

**Features:**
- 🎨 Modern dark theme interface
- 📦 View all products in a scrollable list
- 🔍 Search products by name or SKU
- 📊 Detailed product information view
- 💰 Price and stock status display
- 📋 Full product data in JSON format
- 📊 **Export to Excel** - Export all products grouped by categories
  - Each category = separate Excel sheet (вкладка)
  - All product attributes as columns
  - Auto-formatted headers and column widths
- ✏️ Edit functionality (coming soon)

### Option 2: Command Line

Run the main script:

```bash
# Using Python module
python -m woocommerce_connector.connector

# Or using the script
python scripts/run_connector.py

# Or after installation
woocommerce-connector
```

This will:
- Connect to your WooCommerce store
- Fetch product data
- Display all available product fields
- Show a summary of products

### Check API Version

To check which API version works with your store:

```bash
python -m woocommerce_connector.connector --check-version
# Or
python scripts/run_connector.py --check-version
```

## Project Structure

```
woocommerce-api-connector/
├── woocommerce_connector/    # Main package
│   ├── __init__.py          # Package initialization and exports
│   ├── connector.py         # Core API connector class
│   └── gui.py               # Modern GUI application
├── tests/                    # Test suite
│   ├── test_connector.py
│   ├── test_excel_export.py
│   └── test_api_version_check.py
├── scripts/                  # Utility scripts
│   ├── run_gui.py
│   └── run_connector.py
├── .github/workflows/        # CI/CD workflows
├── requirements.txt          # Python dependencies
├── setup.py                 # Package setup script
├── pytest.ini               # Pytest configuration
├── .env.example             # Template for .env
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
├── CONTRIBUTING.md          # Contribution guidelines
└── README.md                # This file
```

## Features

### Core Functionality
- ✅ Connect to WooCommerce REST API
- ✅ Fetch products with pagination
- ✅ Display all available product fields
- ✅ Error handling and validation
- ✅ Environment variable configuration
- ✅ API version checking

### GUI Application
- ✅ Modern dark theme interface (CustomTkinter)
- ✅ Product list with search functionality
- ✅ Detailed product view
- ✅ Real-time stock and price information
- ✅ Category display
- ✅ Full JSON data viewer
- ✅ **Export to Excel** - Export all products with categories as separate sheets
- 🔜 Product editing (coming soon)
- 🔜 Save changes to store (coming soon)

## Testing

### Run Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=woocommerce_connector --cov=woocommerce_gui --cov-report=html

# Run specific test file
pytest tests/test_connector.py

# Run with verbose output
pytest -v
```

### Test Coverage

The project includes comprehensive tests for:
- ✅ WooCommerce API connection
- ✅ Product retrieval (single and paginated)
- ✅ Excel export functionality
- ✅ API version checking
- ✅ Error handling

## Development

### Project Structure

```
.
├── woocommerce_connector.py  # Core API connector class
├── woocommerce_gui.py        # Modern GUI application
├── tests/                    # Test suite
│   ├── test_connector.py
│   ├── test_excel_export.py
│   └── test_api_version_check.py
├── requirements.txt          # Python dependencies
├── pytest.ini               # Pytest configuration
├── .github/workflows/       # CI/CD workflows
└── README.md                # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Running Tests Locally

```bash
# Install all dependencies including test packages
pip install -r requirements.txt

# Run tests
pytest

# Run tests with coverage report
pytest --cov --cov-report=html
```

## Next Steps

- [x] Export products to Excel (with categories as sheets)
- [x] Comprehensive test suite
- [x] CI/CD with GitHub Actions
- [ ] Add product editing in GUI
- [ ] Save edited products to WooCommerce
- [ ] Import products from Excel (update from file)
- [ ] Sync products to local database
- [ ] Bulk operations (update multiple products)
- [ ] Product image display

