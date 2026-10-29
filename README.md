# Clothing Shop

A small online clothing store built with Flask and SQLite.

## Features

- Product listing with photos, search, and a detail page for each product
- Shopping cart with quantities, subtotals, and a live total
- Checkout form that saves orders to a database
- Admin area with a password login: add and delete products, view orders, mark orders as shippedd

## Built with

Python, Flask, SQLite, HTML, CSS

## Run it locally

1. Clone the repo and open the folder.
2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install the packages:
   ```
   python -m pip install -r requirements.txt
   ```
4. Create a `.env` file with your own values:
   ```
   SECRET_KEY=some-long-random-text
   ADMIN_PASSWORD=your-password
   ```
5. Start the app:
   ```
   python main.py
   ```
6. Open http://127.0.0.1:5000, then go to `/login` to reach the admin page and add products.

## What I learned

Routes, templates, sessions, SQL (create, read, update, delete), forms, login protection, environment variables, and Git.
