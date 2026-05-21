-- ============================================================
-- BLINKIT ANALYTICS PROJECT - Complete SQL Analysis Script
-- Author: Data Analytics Portfolio Project
-- Dataset: blinkit_dataset.csv (13,000 records, 25 columns)
-- ============================================================

-- ============================================================
-- SECTION 1: TABLE CREATION
-- ============================================================

CREATE TABLE IF NOT EXISTS blinkit_products (
    product_id          INT PRIMARY KEY,
    product_name        VARCHAR(200),
    category            VARCHAR(100),
    brand               VARCHAR(100),
    price               DECIMAL(10,2),
    discount_pct        INT,
    final_price         DECIMAL(10,2),
    rating              DECIMAL(3,1),
    num_reviews         INT,
    delivery_time_min   INT,
    city                VARCHAR(100),
    seller              VARCHAR(100),
    stock               INT,
    sold_quantity       INT,
    profit_margin_pct   DECIMAL(5,2),
    is_organic          BOOLEAN,
    packaging_type      VARCHAR(50),
    weight_g            INT,
    shelf_life_days     INT,
    reorder_level       INT,
    demand_index        INT,
    date_added          DATE,
    expiry_date         DATE,
    offer_type          VARCHAR(100),
    delivery_status     VARCHAR(50)
);

-- ============================================================
-- SECTION 2: DATA CLEANING
-- ============================================================

-- 2a. Check for nulls across all columns
SELECT
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END)          AS null_product_id,
    SUM(CASE WHEN product_name IS NULL THEN 1 ELSE 0 END)        AS null_product_name,
    SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END)            AS null_category,
    SUM(CASE WHEN brand IS NULL THEN 1 ELSE 0 END)               AS null_brand,
    SUM(CASE WHEN price IS NULL THEN 1 ELSE 0 END)               AS null_price,
    SUM(CASE WHEN final_price IS NULL THEN 1 ELSE 0 END)         AS null_final_price,
    SUM(CASE WHEN rating IS NULL THEN 1 ELSE 0 END)              AS null_rating,
    SUM(CASE WHEN city IS NULL THEN 1 ELSE 0 END)                AS null_city,
    SUM(CASE WHEN offer_type IS NULL THEN 1 ELSE 0 END)          AS null_offer_type,
    SUM(CASE WHEN delivery_status IS NULL THEN 1 ELSE 0 END)     AS null_delivery_status
FROM blinkit_products;

-- 2b. Check for duplicates
SELECT product_id, product_name, COUNT(*) AS cnt
FROM blinkit_products
GROUP BY product_id, product_name
HAVING COUNT(*) > 1;

-- 2c. Standardize offer_type nulls to 'No Offer'
UPDATE blinkit_products
SET offer_type = 'No Offer'
WHERE offer_type IS NULL;

-- 2d. Validate price consistency (final_price should be <= price)
SELECT product_id, product_name, price, discount_pct, final_price
FROM blinkit_products
WHERE final_price > price;

-- 2e. Check for out-of-range ratings
SELECT COUNT(*) AS invalid_ratings
FROM blinkit_products
WHERE rating < 0 OR rating > 5;

-- 2f. Check for negative stocks or sold quantities
SELECT COUNT(*) AS negative_stock_or_sales
FROM blinkit_products
WHERE stock < 0 OR sold_quantity < 0;

-- ============================================================
-- SECTION 3: CORE ANALYSIS QUERIES
-- ============================================================

-- 3a. Total Sales Revenue by Category
SELECT
    category,
    COUNT(*)                                  AS total_products,
    SUM(sold_quantity)                        AS total_units_sold,
    ROUND(SUM(final_price * sold_quantity), 2) AS total_revenue,
    ROUND(AVG(final_price), 2)                AS avg_price,
    ROUND(AVG(rating), 2)                     AS avg_rating
FROM blinkit_products
GROUP BY category
ORDER BY total_revenue DESC;

-- 3b. Outlet / City Performance
SELECT
    city,
    COUNT(DISTINCT seller)                     AS num_sellers,
    COUNT(*)                                   AS num_products,
    SUM(sold_quantity)                         AS total_units_sold,
    ROUND(SUM(final_price * sold_quantity), 2) AS total_revenue,
    ROUND(AVG(delivery_time_min), 1)           AS avg_delivery_min,
    ROUND(SUM(CASE WHEN delivery_status = 'On-Time' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS ontime_delivery_pct
FROM blinkit_products
GROUP BY city
ORDER BY total_revenue DESC;

-- 3c. Top 20 Products by Revenue
SELECT
    product_id,
    product_name,
    category,
    brand,
    city,
    sold_quantity,
    final_price,
    ROUND(final_price * sold_quantity, 2)      AS revenue,
    rating,
    num_reviews
FROM blinkit_products
ORDER BY revenue DESC
LIMIT 20;

-- 3d. Low Performing Products (bottom 20 by revenue)
SELECT
    product_id,
    product_name,
    category,
    brand,
    city,
    sold_quantity,
    final_price,
    ROUND(final_price * sold_quantity, 2)      AS revenue,
    rating,
    stock
FROM blinkit_products
ORDER BY revenue ASC
LIMIT 20;

-- 3e. Location Tier Analysis
SELECT
    city,
    CASE
        WHEN SUM(final_price * sold_quantity) >= 5000000 THEN 'Tier 1 - High Revenue'
        WHEN SUM(final_price * sold_quantity) >= 2000000 THEN 'Tier 2 - Medium Revenue'
        ELSE 'Tier 3 - Low Revenue'
    END AS city_tier,
    ROUND(SUM(final_price * sold_quantity), 2)  AS total_revenue,
    COUNT(*)                                    AS product_count,
    ROUND(AVG(rating), 2)                       AS avg_rating
FROM blinkit_products
GROUP BY city
ORDER BY total_revenue DESC;

-- 3f. Category Contribution Analysis (% of total revenue)
WITH category_revenue AS (
    SELECT
        category,
        SUM(final_price * sold_quantity) AS revenue
    FROM blinkit_products
    GROUP BY category
),
total AS (
    SELECT SUM(revenue) AS grand_total FROM category_revenue
)
SELECT
    cr.category,
    ROUND(cr.revenue, 2)                                   AS category_revenue,
    ROUND(cr.revenue * 100.0 / t.grand_total, 2)          AS revenue_share_pct,
    ROUND(SUM(cr.revenue) OVER (ORDER BY cr.revenue DESC) * 100.0 / t.grand_total, 2) AS cumulative_share_pct
FROM category_revenue cr, total t
ORDER BY cr.revenue DESC;

-- 3g. Product Ranking Using Window Functions
SELECT
    product_id,
    product_name,
    category,
    city,
    ROUND(final_price * sold_quantity, 2)           AS revenue,
    RANK()       OVER (ORDER BY final_price * sold_quantity DESC)                    AS overall_rank,
    RANK()       OVER (PARTITION BY category ORDER BY final_price * sold_quantity DESC) AS category_rank,
    RANK()       OVER (PARTITION BY city     ORDER BY final_price * sold_quantity DESC) AS city_rank,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY rating DESC)                  AS rating_rank_in_category,
    NTILE(4)     OVER (ORDER BY final_price * sold_quantity DESC)                   AS revenue_quartile
FROM blinkit_products
ORDER BY overall_rank;

-- 3h. Product Segmentation Using CASE WHEN
SELECT
    product_id,
    product_name,
    category,
    final_price,
    sold_quantity,
    rating,
    demand_index,
    profit_margin_pct,
    CASE
        WHEN final_price < 100                            THEN 'Budget'
        WHEN final_price BETWEEN 100 AND 300             THEN 'Mid-Range'
        WHEN final_price BETWEEN 300 AND 600             THEN 'Premium'
        ELSE 'Luxury'
    END AS price_segment,
    CASE
        WHEN demand_index >= 75                          THEN 'High Demand'
        WHEN demand_index BETWEEN 40 AND 74             THEN 'Medium Demand'
        ELSE 'Low Demand'
    END AS demand_segment,
    CASE
        WHEN rating >= 4.5                               THEN 'Excellent'
        WHEN rating >= 3.5                               THEN 'Good'
        WHEN rating >= 2.5                               THEN 'Average'
        ELSE 'Poor'
    END AS rating_segment,
    CASE
        WHEN stock <= reorder_level                      THEN 'Reorder Needed'
        WHEN stock <= reorder_level * 1.5               THEN 'Low Stock'
        ELSE 'Adequate Stock'
    END AS stock_status
FROM blinkit_products
ORDER BY product_id;

-- 3i. Advanced CTE: Seller Performance Dashboard
WITH seller_stats AS (
    SELECT
        seller,
        city,
        COUNT(*)                                        AS total_products,
        SUM(sold_quantity)                              AS total_units_sold,
        ROUND(SUM(final_price * sold_quantity), 2)      AS total_revenue,
        ROUND(AVG(profit_margin_pct), 2)                AS avg_profit_margin,
        ROUND(AVG(rating), 2)                           AS avg_rating,
        SUM(CASE WHEN delivery_status = 'On-Time' THEN 1 ELSE 0 END) AS ontime_deliveries,
        COUNT(*)                                        AS total_deliveries
    FROM blinkit_products
    GROUP BY seller, city
),
seller_ranked AS (
    SELECT *,
        ROUND(ontime_deliveries * 100.0 / total_deliveries, 1) AS ontime_pct,
        RANK() OVER (ORDER BY total_revenue DESC)               AS revenue_rank,
        RANK() OVER (ORDER BY avg_rating DESC)                  AS rating_rank
    FROM seller_stats
)
SELECT *
FROM seller_ranked
ORDER BY revenue_rank
LIMIT 50;

-- 3j. Advanced CTE: Discount Impact Analysis
WITH discount_buckets AS (
    SELECT
        CASE
            WHEN discount_pct = 0            THEN 'No Discount'
            WHEN discount_pct BETWEEN 1 AND 10  THEN '1-10%'
            WHEN discount_pct BETWEEN 11 AND 20 THEN '11-20%'
            WHEN discount_pct BETWEEN 21 AND 30 THEN '21-30%'
            ELSE '30%+'
        END AS discount_bucket,
        sold_quantity,
        final_price * sold_quantity         AS revenue,
        profit_margin_pct,
        rating
    FROM blinkit_products
)
SELECT
    discount_bucket,
    COUNT(*)                                AS product_count,
    ROUND(AVG(sold_quantity), 1)            AS avg_units_sold,
    ROUND(SUM(revenue), 2)                  AS total_revenue,
    ROUND(AVG(profit_margin_pct), 2)        AS avg_profit_margin,
    ROUND(AVG(rating), 2)                   AS avg_rating
FROM discount_buckets
GROUP BY discount_bucket
ORDER BY total_revenue DESC;

-- 3k. Advanced CTE: Organic vs Non-Organic Performance
WITH organic_analysis AS (
    SELECT
        category,
        is_organic,
        COUNT(*)                                        AS product_count,
        ROUND(AVG(final_price), 2)                      AS avg_price,
        ROUND(AVG(rating), 2)                           AS avg_rating,
        ROUND(AVG(profit_margin_pct), 2)                AS avg_margin,
        SUM(sold_quantity)                              AS total_sold,
        ROUND(SUM(final_price * sold_quantity), 2)      AS total_revenue
    FROM blinkit_products
    GROUP BY category, is_organic
)
SELECT *,
    ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (PARTITION BY category), 2) AS category_share_pct
FROM organic_analysis
ORDER BY category, is_organic;

-- 3l. Advanced CTE: Delivery Time & Status Performance
WITH delivery_perf AS (
    SELECT
        city,
        delivery_status,
        CASE
            WHEN delivery_time_min <= 15 THEN 'Express (<15 min)'
            WHEN delivery_time_min <= 30 THEN 'Fast (15-30 min)'
            WHEN delivery_time_min <= 45 THEN 'Standard (30-45 min)'
            ELSE 'Slow (45+ min)'
        END AS delivery_speed_bucket,
        COUNT(*)                    AS orders,
        ROUND(AVG(rating), 2)       AS avg_rating,
        ROUND(AVG(delivery_time_min), 1) AS avg_delivery_min
    FROM blinkit_products
    GROUP BY city, delivery_status,
        CASE
            WHEN delivery_time_min <= 15 THEN 'Express (<15 min)'
            WHEN delivery_time_min <= 30 THEN 'Fast (15-30 min)'
            WHEN delivery_time_min <= 45 THEN 'Standard (30-45 min)'
            ELSE 'Slow (45+ min)'
        END
)
SELECT *,
    RANK() OVER (PARTITION BY city ORDER BY orders DESC) AS speed_rank_in_city
FROM delivery_perf
ORDER BY city, avg_delivery_min;

-- 3m. Month-over-Month Sales Trend
SELECT
    DATE_FORMAT(date_added, '%Y-%m')         AS month,
    COUNT(*)                                 AS products_added,
    SUM(sold_quantity)                       AS total_units_sold,
    ROUND(SUM(final_price * sold_quantity), 2) AS monthly_revenue,
    ROUND(AVG(rating), 2)                    AS avg_rating
FROM blinkit_products
GROUP BY DATE_FORMAT(date_added, '%Y-%m')
ORDER BY month;

-- 3n. Stock Risk Analysis
SELECT
    product_id,
    product_name,
    category,
    city,
    stock,
    reorder_level,
    sold_quantity,
    demand_index,
    ROUND(sold_quantity * 1.0 / NULLIF(stock, 0), 2) AS sell_through_rate,
    CASE
        WHEN stock = 0                    THEN 'OUT OF STOCK'
        WHEN stock < reorder_level        THEN 'CRITICAL - REORDER NOW'
        WHEN stock < reorder_level * 1.5  THEN 'LOW - REORDER SOON'
        ELSE 'HEALTHY'
    END AS stock_alert
FROM blinkit_products
WHERE stock <= reorder_level * 1.5
ORDER BY stock ASC;

-- 3o. Top Brands by Category
WITH brand_rank AS (
    SELECT
        category,
        brand,
        COUNT(*)                                        AS product_count,
        ROUND(SUM(final_price * sold_quantity), 2)     AS total_revenue,
        ROUND(AVG(rating), 2)                          AS avg_rating,
        RANK() OVER (PARTITION BY category ORDER BY SUM(final_price * sold_quantity) DESC) AS brand_rank
    FROM blinkit_products
    GROUP BY category, brand
)
SELECT *
FROM brand_rank
WHERE brand_rank <= 3
ORDER BY category, brand_rank;
