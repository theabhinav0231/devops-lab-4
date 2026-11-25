"""ENSP461 Lab 4 microservice (Abhinav Kumar - 2301730191)."""
import hashlib
import os
import random
import socket
import sqlite3
from datetime import datetime, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)

APP_NAME = os.environ.get("APP_NAME", "devops-lab4-app")
APP_VERSION = os.environ.get("APP_VERSION", "4.0.0")
DEPLOYMENT_SLOT = os.environ.get("DEPLOYMENT_SLOT", "blue")
DB_PATH = os.environ.get("DB_PATH", "/tmp/lab4_app.db")
API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "")
SIMULATE_ERROR_RATE = float(os.environ.get("SIMULATE_ERROR_RATE", "0.0"))


def get_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS items ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT NOT NULL, "
        "created_at TEXT NOT NULL)"
    )
    conn.commit()
    return conn


@app.route("/")
def index():
    if SIMULATE_ERROR_RATE > 0 and random.random() < SIMULATE_ERROR_RATE:
        return jsonify(error="simulated canary fault", version=APP_VERSION, slot=DEPLOYMENT_SLOT), 500
    return jsonify(
        app=APP_NAME,
        student="Abhinav Kumar",
        version=APP_VERSION,
        slot=DEPLOYMENT_SLOT,
        hostname=socket.gethostname(),
    )


@app.route("/health")
def health():
    return jsonify(status="UP", version=APP_VERSION, slot=DEPLOYMENT_SLOT), 200


@app.route("/items", methods=["GET", "POST"])
def items():
    conn = get_db()
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        name = str(payload.get("name", "")).strip()
        if not name:
            conn.close()
            return jsonify(error="name is required"), 400
        now = datetime.now(timezone.utc).isoformat()
        cur = conn.execute("INSERT INTO items (name, created_at) VALUES (?, ?)", (name, now))
        conn.commit()
        item_id = cur.lastrowid
        conn.close()
        return jsonify(id=item_id, name=name, created_at=now, slot=DEPLOYMENT_SLOT), 201
    rows = conn.execute("SELECT id, name, created_at FROM items ORDER BY id").fetchall()
    conn.close()
    return jsonify(
        count=len(rows),
        slot=DEPLOYMENT_SLOT,
        items=[dict(r) for r in rows],
    ), 200


@app.route("/secret-check")
def secret_check():
    if not API_SECRET_KEY:
        return jsonify(configured=False, fingerprint="none"), 503
    fp = hashlib.sha256(API_SECRET_KEY.encode()).hexdigest()[:12]
    return jsonify(configured=True, fingerprint=fp, version=APP_VERSION), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
