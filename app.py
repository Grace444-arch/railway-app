from flask import Flask, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL"), sslmode="require")

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def home():
    return "Railway App is Running!"

@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("INSERT INTO items (name, description) VALUES (%s, %s) RETURNING *",
                (data["name"], data.get("description", "")))
    item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(dict(item)), 201

@app.route("/items", methods=["GET"])
def get_items():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM items")
    items = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(items)

@app.route("/items/<int:id>", methods=["GET"])
def get_item(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM items WHERE id = %s", (id,))
    item = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(dict(item)) if item else (jsonify({"error": "Not found"}), 404)

@app.route("/items/<int:id>", methods=["PUT"])
def update_item(id):
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("UPDATE items SET name=%s, description=%s WHERE id=%s RETURNING *",
                (data["name"], data.get("description", ""), id))
    item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(dict(item)) if item else (jsonify({"error": "Not found"}), 404)

@app.route("/items/<int:id>", methods=["DELETE"])
def delete_item(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Deleted successfully"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))