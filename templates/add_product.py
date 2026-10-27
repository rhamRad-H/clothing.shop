import sqlite3

conn = sqlite3.connect("shop.db")
conn.execute(
    "INSERT INTO products (name, price, image) VALUES (?, ?, ?)",
    ("Grey Cap", 25, "n.jpg"),
)
conn.commit()
conn.close()
print("Product added")