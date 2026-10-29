import sqlite3
from flask import Flask, render_template,redirect, url_for, session, request, flash, abort
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ["SECRET_KEY"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

def init_db():
    conn = sqlite3.connect("shop.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            image TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            items TEXT NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    products = search_products(q) if q else get_products()
    cart_count = len(get_valid_cart())
    return render_template("index.html", items=products, cart_count=cart_count, q=q)

def get_products():
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return rows

def search_products(query):
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM products WHERE name LIKE ?",
        (f"%{query}%",),
    ).fetchall()
    conn.close()
    return rows

def get_valid_cart():
    valid_ids = {p["id"] for p in get_products()}
    cart = [i for i in session.get("cart", []) if i in valid_ids]
    session["cart"] = cart
    return cart

def build_cart():
    products = {p["id"]: p for p in get_products()}
    counts = {}
    for i in get_valid_cart():
        counts[i] = counts.get(i, 0) + 1

    cart_items = []
    total = 0
    for product_id, qty in counts.items():
        product = products[product_id]
        subtotal = product["price"] * qty
        total += subtotal
        cart_items.append({
            "id": product_id,
            "name": product["name"],
            "price": product["price"],
            "qty": qty,
            "subtotal": subtotal,
        })
    return cart_items, total

@app.route("/cart")
def cart():
    cart_items, total = build_cart()
    return render_template("cart.html", cart_items=cart_items, total=total)


@app.route("/add/<int:item_id>")
def add_to_cart(item_id):
    cart = get_valid_cart()
    cart.append(item_id)
    session["cart"] = cart
    return redirect(request.referrer or url_for("home"))


@app.route("/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart = get_valid_cart()
    if product_id in cart:
        cart.remove(product_id)
        session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/clear")
def clear_cart():
    session["cart"] = []
    return redirect(url_for("cart"))

    
@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        image = request.form["image"]

        conn = sqlite3.connect("shop.db")
        conn.execute(
            "INSERT INTO products (name, price, image) VALUES (?, ?, ?)",
            (name, price, image),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("home"))

    return render_template("admin.html", items=get_products())

@app.route("/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    conn = sqlite3.connect("shop.db")
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin"))
        flash("Wrong password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("home"))

@app.route("/product/<int:product_id>")
def product(product_id):
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    item = conn.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    conn.close()
    if item is None:
        abort(404)
    return render_template("product.html", item=item, cart_count=len(get_valid_cart()))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items, total = build_cart()
    if not cart_items:
        return redirect(url_for("cart"))

    if request.method == "POST":
        name = request.form["name"].strip()
        address = request.form["address"].strip()
        summary = ", ".join(f"{i['name']} x{i['qty']}" for i in cart_items)

        conn = sqlite3.connect("shop.db")
        conn.execute(
            "INSERT INTO orders (name, address, items, total) VALUES (?, ?, ?, ?)",
            (name, address, summary, total),
        )
        conn.commit()
        conn.close()

        session["cart"] = []
        return render_template("order_done.html", name=name, total=total)

    return render_template("checkout.html", cart_items=cart_items, total=total)

@app.route("/orders")
@admin_required
def orders():
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("orders.html", orders=rows)

if __name__ == "__main__":
    app.run(debug=True)