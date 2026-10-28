import sqlite3
from flask import Flask, render_template,redirect, url_for, session, request, flash, abort
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ["SECRET_KEY"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    cart_count = len(get_valid_cart())
    return render_template("index.html", items=get_products(), cart_count=cart_count)

def get_products():
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return rows

def get_valid_cart():
    valid_ids = {p["id"] for p in get_products()}
    cart = [i for i in session.get("cart", []) if i in valid_ids]
    session["cart"] = cart
    return cart

@app.route("/cart")
def cart():
    products = {p["id"]: p for p in get_products()}
    cart_ids = get_valid_cart()
    cart_items = [products[i] for i in cart_ids if i in products]
    total = sum(item["price"] for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total=total)


@app.route("/add/<int:item_id>")
def add_to_cart(item_id):
    cart = session.get("cart", [])
    cart.append(item_id)
    session["cart"] = cart
    return redirect(url_for("home"))


@app.route("/remove/<int:position>")
def remove_from_cart(position):
    cart = get_valid_cart()
    if 0 <= position < len(cart):
        cart.pop(position)
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

if __name__ == "__main__":
    app.run(debug=True)