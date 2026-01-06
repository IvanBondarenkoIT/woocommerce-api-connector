# WooCommerce API Connection

Python project to connect to WordPress WooCommerce store via REST API and fetch product data.

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
   WC_API_VERSION=v3
   ```

### 5. Get WooCommerce API Credentials

1. Go to your WordPress admin panel
2. Navigate to: **WooCommerce → Settings → Advanced → REST API**
3. Click **Add Key**
4. Set permissions to **Read/Write**
5. Copy the **Consumer Key** and **Consumer Secret**

## Usage

### Run the main script:

```bash
python woocommerce_connector.py
```

This will:
- Connect to your WooCommerce store
- Fetch product data
- Display all available product fields
- Show a summary of products

## Project Structure

```
.
├── woocommerce_connector.py  # Main script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── .env.example             # Template for .env
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Features

- ✅ Connect to WooCommerce REST API
- ✅ Fetch products with pagination
- ✅ Display all available product fields
- ✅ Error handling and validation
- ✅ Environment variable configuration

## Next Steps

- Add product filtering and search
- Export products to CSV/JSON
- Sync products to local database
- Create web interface for displaying products

