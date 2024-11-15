# Best Buy Website Crawler

This project includes web scraping tools for capturing product data from the Best Buy website and managing it in a structured database. It features a full data crawling system for initial product entry, an hourly monitoring system for updating price, stock, and review data, and a tool for obtaining shipping and pickup details for specific stores based on product URLs and U.S. zip codes.

---

## Project Structure

database
   └── bestbuy.db           # SQLite database for storing product data

price_monitoring
   ── bestbuy_spider.py    # Initial full crawl for product data storage in the database
   ── hourly_crawl_spider.py # Scheduled hourly crawl for monitoring price, stock, and reviews

scraper
   └── bestbuy_scraper.py   # Scraper to retrieve shipping & pickup information using product URLs and zip codes

## Database Structure
The database consists of a master product list and a daily table to track updates in product details. For reference and ease of replication, SQLite is used in this example, but the project is compatible with other databases like MySQL or PostgreSQL.

CREATE TABLE IF NOT EXISTS master_products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    UNIQUE(product_name)
);

CREATE TABLE IF NOT EXISTS products_2024_11_14 (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    price DECIMAL(10, 4),
    discount DECIMAL(10, 4),
    rating_value INT(10),
    review_count INT(10),
    reviewer_1 JSON,
    reviewer_2 JSON,
    reviewer_3 JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES master_products(product_id)
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_product_id ON products_2024_11_14 (product_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON products_2024_11_14 (timestamp);
CREATE INDEX IF NOT EXISTS idx_price ON products_2024_11_14 (price);
CREATE INDEX IF NOT EXISTS idx_review_count ON products_2024_11_14 (review_count);

## Hourly Monitoring with Cron Job
The hourly crawler checks for updates in price, stock, and reviews and saves these in daily tables. Set up a cron job to automate this process:
0 * * * * cd /path/to/price_monitoring && python3 hourly_crawl_spider.py