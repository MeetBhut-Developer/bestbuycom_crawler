# bestbuycom_crawler
Web Scraping as well as database management



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
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX IF NOT EXISTS idx_product_id ON products_2024_11_14 (product_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON products_2024_11_14 (timestamp);
CREATE INDEX IF NOT EXISTS idx_price ON products_2024_11_14 (price);
CREATE INDEX IF NOT EXISTS idx_review_count ON products_2024_11_14 (review_count);

