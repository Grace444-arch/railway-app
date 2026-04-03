from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# 🔹 DATABASE CONNECTION (RAILWAY or LOCAL fallback)
# Set DATABASE_URL in Railway's Variables tab, or in a .env file locally
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:yourpassword@localhost:5432/railway_app"  # ← replace for local dev
)

def get_db():
    return psycopg2.connect(DATABASE_URL)

# 🔹 CREATE TABLE IF NOT EXISTS
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialized successfully.")

# 🔹 HOME PAGE (VIEW ALL USERS)
@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users ORDER BY id DESC")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", users=users)

# 🔹 REGISTER FORM PAGE
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    return render_template("register.html")

# 🔹 DELETE USER
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

# 🔹 EDIT USER
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        cur.execute(
            "UPDATE users SET name=%s, email=%s WHERE id=%s",
            (name, email, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    cur.execute("SELECT * FROM users WHERE id=%s", (id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit.html", user=user)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)