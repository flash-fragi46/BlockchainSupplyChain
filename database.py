import sqlite3

conn = sqlite3.connect("database/supplychain.db")
cursor = conn.cursor()

# ---------------- PRODUCTS ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    farmer_name TEXT,
    harvest_date TEXT,
    quantity TEXT
)
""")

# ---------------- DISTRIBUTOR ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS distributor(
    product_id TEXT,
    distributor_name TEXT,
    dispatch_date TEXT,
    transport_method TEXT,
    destination TEXT
)
""")

# ---------------- RETAILER ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS retailer(
    product_id TEXT,
    retailer_name TEXT,
    store_name TEXT,
    location TEXT,
    arrival_date TEXT
)
""")

# ---------------- BLOCKCHAIN TRANSACTIONS ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT,
    sender TEXT,
    receiver TEXT,
    location TEXT,
    timestamp TEXT,
    hash TEXT,
    previous_hash TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")