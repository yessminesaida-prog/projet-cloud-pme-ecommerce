import sqlite3
import os
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.getenv("DB_PATH", "/data/catalogue.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    if c.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            [
                ("Poterie de Sejnane", 45, 20),
                ("Tapis berbère artisanal", 320, 8),
                ("Coffret huile d'olive & bois d'olivier", 60, 15),
            ],
        )
    conn.commit()
    conn.close()

@app.route("/products", methods=["GET"])
def get_products():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Produit introuvable"}), 404
    return jsonify(dict(row))

@app.route("/products", methods=["POST"])
def add_product():
    data = request.get_json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        (data["name"], data["price"], data.get("stock", 10)),
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return jsonify({"id": new_id, "status": "created"}), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001)