import sqlite3
import os
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.getenv("DB_PATH", "/data/notifications.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/notify", methods=["POST"])
def send_notification():
    data = request.get_json()
    recipient = data.get("recipient", "client@exemple.tn")
    message = data.get("message", "Notification envoyée")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO notifications (recipient, message) VALUES (?, ?)",
        (recipient, message),
    )
    conn.commit()
    notif_id = c.lastrowid
    conn.close()

    print(f"[NOTIFICATION #{notif_id}] -> {recipient} : {message}", flush=True)
    return jsonify({"id": notif_id, "status": "sent", "recipient": recipient}), 201

@app.route("/notifications", methods=["GET"])
def get_notifications():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM notifications").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5003)