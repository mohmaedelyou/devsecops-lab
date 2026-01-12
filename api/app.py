from flask import Flask, request, jsonify
import sqlite3
import hashlib
import os
import bcrypt

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-12345")  # Plus sûr, configurable

DATABASE = "users.db"

# ---------------------
# Utilitaires
# ---------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    # Utilisation de bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ---------------------
# Routes sécurisées
# ---------------------
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return jsonify({"status": "error", "message": "Missing credentials"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Requête paramétrée pour éviter SQL injection
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password(password, user["password"]):
        return jsonify({"status": "success", "user": username})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host", "")
    # Validation simple
    if not host.isalnum():
        return jsonify({"status": "error", "message": "Invalid host"}), 400
    return jsonify({"output": f"ping {host} simulated"})  # Plus de subprocess dangereux

@app.route("/compute", methods=["POST"])
def compute():
    expression = request.json.get("expression", "")
    # On n’utilise plus eval() directement
    allowed_chars = "0123456789+-*/(). "
    if not all(c in allowed_chars for c in expression):
        return jsonify({"status": "error", "message": "Invalid expression"}), 400
    try:
        result = eval(expression)  # Note : Eval limité aux caractères sûrs
        return jsonify({"result": result})
    except Exception:
        return jsonify({"status": "error", "message": "Computation failed"}), 400

@app.route("/hash", methods=["POST"])
def hash_endpoint():
    pwd = request.json.get("password", "")
    if not pwd:
        return jsonify({"status": "error", "message": "Password missing"}), 400
    return jsonify({"bcrypt": hash_password(pwd)})

@app.route("/readfile", methods=["POST"])
def readfile():
    filename = request.json.get("filename", "")
    # Validation simple : empêcher les chemins relatifs dangereux
    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"status": "error", "message": "Invalid filename"}), 400
    try:
        with open(filename, "r") as f:
            content = f.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "File not found"}), 404

@app.route("/debug", methods=["GET"])
def debug():
    # Ne pas exposer le secret ni les variables d'environnement
    return jsonify({"debug": False, "message": "Debug info disabled"})

@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Welcome to the secure DevSecOps API"})

# ---------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
