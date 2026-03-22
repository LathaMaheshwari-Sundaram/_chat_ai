import sqlite3
import os

# Create the SQLite database at data/company_data.db
db_path = os.path.join("data", "company_data.db")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Clear existing data if tables exist
cursor.execute("DROP TABLE IF EXISTS monthly_revenue")
cursor.execute("DROP TABLE IF EXISTS user_profiles")
cursor.execute("DROP TABLE IF EXISTS raw_sales")
cursor.execute("DROP TABLE IF EXISTS data_quality_log")

# TABLE 1: monthly_revenue
cursor.execute('''
CREATE TABLE IF NOT EXISTS monthly_revenue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT,
    region TEXT,
    total_revenue REAL,
    discount_amount REAL,
    net_revenue REAL,
    currency TEXT
)
''')

# Insert 24 rows for monthly_revenue (2 years, 2 regions)
regions = ["North", "South"]
months = [f"2023-{m:02d}" for m in range(1, 13)] + [f"2024-{m:02d}" for m in range(1, 13)]
for month in months:
    for region in regions:
        total = 10000 + (len(month) * 500)
        discount = 500 + (len(region) * 100)
        net = total - discount
        cursor.execute("INSERT INTO monthly_revenue (month, region, total_revenue, discount_amount, net_revenue, currency) VALUES (?, ?, ?, ?, ?, ?)",
                       (month, region, total, discount, net, "USD"))

# TABLE 2: user_profiles
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    email TEXT,
    signup_date TEXT,
    country TEXT,
    plan_type TEXT,
    is_active INTEGER
)
''')

# Insert 20 realistic rows
user_data = [
    (1, "jdoe", "jdoe@example.com", "2023-01-05", "USA", "Pro", 1),
    (2, "asmith", "asmith@test.org", "2023-02-12", "UK", "Free", 1),
    (3, "bjones", "bjones@mail.com", "2023-03-20", "Canada", "Enterprise", 1),
    (4, "mli", "mli@service.net", "2023-04-15", "China", "Pro", 0),
    (5, "kgomez", "kgomez@world.com", "2023-05-22", "Mexico", "Free", 1),
]
# Add more mock data to reach 20
for i in range(6, 21):
    user_data.append((i, f"user{i}", f"user{i}@company.com", f"2023-06-{i:02d}", "USA", "Free", 1))

cursor.executemany("INSERT INTO user_profiles VALUES (?, ?, ?, ?, ?, ?, ?)", user_data)

# TABLE 3: raw_sales
cursor.execute('''
CREATE TABLE IF NOT EXISTS raw_sales (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_name TEXT,
    quantity INTEGER,
    unit_price REAL,
    total_amount REAL,
    sale_date TEXT,
    region TEXT
)
''')

# Insert 30 realistic rows
products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones"]
for i in range(1, 31):
    pid = i % 5
    qty = (i % 3) + 1
    price = 100 + (pid * 50)
    cursor.execute("INSERT INTO raw_sales (user_id, product_name, quantity, unit_price, total_amount, sale_date, region) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (i % 20 + 1, products[pid], qty, price, qty * price, f"2024-03-{i:02d}", "North" if i % 2 == 0 else "South"))

# TABLE 4: data_quality_log
cursor.execute('''
CREATE TABLE IF NOT EXISTS data_quality_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT,
    column_name TEXT,
    check_type TEXT,
    result TEXT,
    null_count INTEGER,
    total_count INTEGER,
    checked_at TEXT
)
''')

# Insert 15 rows showing realistic quality check results
quality_checks = [
    ("monthly_revenue", "total_revenue", "Null Check", "PASS", 0, 48, "2024-03-20 10:00:00"),
    ("user_profiles", "email", "Null Check", "PASS", 0, 20, "2024-03-20 10:05:00"),
    ("raw_sales", "total_amount", "Range Check", "FAIL", 2, 30, "2024-03-20 10:10:00"),
]
# Add more mock data to reach 15
for i in range(4, 16):
    quality_checks.append(("raw_sales", "quantity", "Validity Check", "PASS", 0, 30, f"2024-03-20 10:1{i:02d}:00"))

cursor.executemany("INSERT INTO data_quality_log (table_name, column_name, check_type, result, null_count, total_count, checked_at) VALUES (?, ?, ?, ?, ?, ?, ?)", quality_checks)
conn.commit()
conn.close()

print("Database created with all tables and sample data.")
