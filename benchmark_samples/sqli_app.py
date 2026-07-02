"""SQL Injection vulnerable app — benchmark sample."""
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = "users.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn


@app.route("/user/<user_id>")
def get_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    # VULN: SQLi via f-string interpolation
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"id": row[0], "name": row[1], "email": row[2]})
    return jsonify({"error": "User not found"}), 404


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    conn = get_db()
    cursor = conn.cursor()
    # VULN: SQLi in login
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"token": "fake-jwt-token"})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/users", methods=["GET"])
def list_users():
    conn = get_db()
    cursor = conn.cursor()
    # VULN: No auth check, exposes all users
    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "email": r[2]} for r in rows])


if __name__ == "__main__":
    app.run(debug=True)
