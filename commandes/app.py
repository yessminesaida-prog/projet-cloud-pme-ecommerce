import sqlite3
import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.getenv("DB_PATH", "/data/commandes.db")
CATALOGUE_URL = os.getenv("CATALOGUE_URL", "http://catalogue:5001")
NOTIFICATIONS_URL = os.getenv("NOTIFICATIONS_URL", "http://notifications:5003")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            customer_email TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/orders", methods=["GET"])
def list_orders():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    customer_email = data.get("customer_email", "client@exemple.tn")

    # 1. Appel inter-service vers Catalogue
    resp = requests.get(f"{CATALOGUE_URL}/products/{product_id}", timeout=5)
    if resp.status_code != 200:
        return jsonify({"error": "Produit inexistant dans Catalogue"}), 404

    product = resp.json()
    total_price = product["price"] * quantity

    # 2. Enregistrement local dans commandes.db
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (product_id, quantity, total_price, customer_email, status) VALUES (?, ?, ?, ?, ?)",
        (product_id, quantity, total_price, customer_email, "CONFIRMEE"),
    )
    conn.commit()
    order_id = c.lastrowid
    conn.close()

    # 3. Appel inter-service vers Notifications
    notif_payload = {
        "recipient": customer_email,
        "message": f"Commande #{order_id} confirmée pour '{product['name']}' (x{quantity}) - Total : {total_price} TND",
    }
    try:
        requests.post(f"{NOTIFICATIONS_URL}/notify", json=notif_payload, timeout=5)
    except requests.RequestException:
        pass

    return jsonify({
        "order_id": order_id,
        "product_name": product["name"],
        "quantity": quantity,
        "total_price": total_price,
        "status": "CONFIRMEE",
        "notification": "Envoyée",
    }), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5002)