import sqlite3

conn = sqlite3.connect("shop.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    image TEXT NOT NULL
)
""")

cur.execute("SELECT COUNT(*) FROM products")
if cur.fetchone()[0] == 0:
    cur.executemany(
        "INSERT INTO products (name, price, image) VALUES (?, ?, ?)",
        [
            ("Black Hoodie", 45, "b.jpg"),
            ("Blue Jeans", 60, "front_n.jpg"),
            ("White T-Shirt", 20, "n.jpg"),
        ],
    )

conn.commit()
conn.close()
print("Database ready")