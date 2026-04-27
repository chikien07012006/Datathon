import pandas as pd
import sqlite3
import os

conn = sqlite3.connect("datathon.db")

query1 = """
WITH order_gaps AS (
    SELECT
        customer_id,
        julianday(order_date) - julianday(
            LAG(order_date) OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            )
        ) AS gap_days
    FROM orders
),
valid_gaps AS (
    SELECT gap_days
    FROM order_gaps
    WHERE gap_days IS NOT NULL
)
SELECT AVG(gap_days) AS median_gap
FROM (
    SELECT gap_days
    FROM valid_gaps
    ORDER BY gap_days
    LIMIT 2 - (SELECT COUNT(*) FROM valid_gaps) % 2
    OFFSET (SELECT (COUNT(*) - 1) / 2 FROM valid_gaps)
);
"""
query2 = """
SELECT 
    segment,
    AVG((price - cogs) * 1.0 / price) AS avg_margin
FROM products
GROUP BY segment
ORDER BY avg_margin DESC;
"""

query3 = """
SELECT 
    r.return_reason,
    COUNT(*) AS cnt
FROM returns r
JOIN products p 
    ON r.product_id = p.product_id
WHERE p.category = 'Streetwear'
GROUP BY r.return_reason
ORDER BY cnt DESC;
"""
query4 = """
WITH daily_conversion AS (
    SELECT
        w.traffic_source,
        w.date,
        COUNT(o.order_id) * 1.0 / w.sessions AS conversion_rate
    FROM web_traffic w
    LEFT JOIN orders o
        ON w.date = o.order_date
        AND w.traffic_source = o.order_source
    GROUP BY w.traffic_source, w.date, w.sessions
)

SELECT
    traffic_source,
    AVG(conversion_rate) AS avg_conversion_rate
FROM daily_conversion
GROUP BY traffic_source
ORDER BY avg_conversion_rate DESC;
"""
query5 = """
SELECT 
    100.0 * COUNT(promo_id) / COUNT(*) AS promo_percentage
FROM order_items;
"""
query6 = """
WITH orders_per_customer AS (
    SELECT 
        c.customer_id,
        c.age_group,
        COUNT(o.order_id) AS num_orders
    FROM customers c
    LEFT JOIN orders o
        ON c.customer_id = o.customer_id
    WHERE c.age_group IS NOT NULL
    GROUP BY c.customer_id, c.age_group
)

SELECT 
    age_group,
    AVG(num_orders) AS avg_orders_per_customer
FROM orders_per_customer
GROUP BY age_group
ORDER BY avg_orders_per_customer DESC;
"""
query7 = """
SELECT
    g.region,
    SUM(s.Revenue) AS total_revenue
FROM sales s
JOIN orders o
    ON s.Date = o.order_date
JOIN geography g 
    ON g.zip = o.zip
GROUP BY g.region
ORDER BY total_revenue DESC;
"""
query8 = """
SELECT 
    payment_method,
    COUNT(*) AS cnt
FROM orders
WHERE order_status = 'cancelled'
GROUP BY payment_method
ORDER BY cnt DESC;
"""
query9 = """
WITH returns_count AS (
    SELECT 
        p.size,
        COUNT(*) AS return_cnt
    FROM returns r
    JOIN products p 
        ON r.product_id = p.product_id
    GROUP BY p.size
),
orders_count AS (
    SELECT 
        p.size,
        COUNT(*) AS order_cnt
    FROM order_items oi
    JOIN products p 
        ON oi.product_id = p.product_id
    GROUP BY p.size
)

SELECT 
    r.size,
    1.0 * r.return_cnt / o.order_cnt AS return_rate
FROM returns_count r
JOIN orders_count o
    ON r.size = o.size
ORDER BY return_rate DESC;
"""
query10 = """
SELECT 
    installments,
    AVG(payment_value) AS avg_payment
FROM payments
GROUP BY installments
ORDER BY avg_payment DESC;
"""

results = pd.read_sql(query10, conn)

print(results)
conn.close()