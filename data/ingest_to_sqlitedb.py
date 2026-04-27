import pandas as pd
import sqlite3
import os

DATA_PATH = "D:\Datathon\data"  
DB_NAME = "datathon.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

files = [
    "products.csv",
    "customers.csv",
    "promotions.csv",
    "geography.csv",
    "orders.csv",
    "order_items.csv",
    "payments.csv",
    "shipments.csv",
    "returns.csv",
    "reviews.csv",
    "sales.csv",
    "inventory.csv",
    "web_traffic.csv"
]

for file in files:
    file_path = os.path.join(DATA_PATH, file)
    table_name = file.replace(".csv", "")
    
    print(f"Loading {file}...")
    
    df = pd.read_csv(file_path)
    
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    
    print(f"Done: {table_name}")

print("All tables loaded!")

indexes = [
    "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);",
    
    "CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);",
    "CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);",
    
    "CREATE INDEX IF NOT EXISTS idx_returns_order ON returns(order_id);",
    "CREATE INDEX IF NOT EXISTS idx_products_product ON products(product_id);",
    
    "CREATE INDEX IF NOT EXISTS idx_customers_id ON customers(customer_id);"
]

for idx in indexes:
    cursor.execute(idx)

conn.commit()
print("Indexes created!")

query = """
SELECT COUNT(*) as total_orders FROM orders;
"""

result = pd.read_sql(query, conn)
print(result)

conn.close()