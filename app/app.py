import asyncio
import json
import os
import sqlite3
import subprocess
import threading
import time

import logging

import websockets
from websockets.asyncio.server import broadcast
from flask import Flask, render_template

DB_PATH = "/srv/db/chat.db"
SHARE_DIR = "/srv/static/share"
app = Flask(__name__)


# Setup DB on launch
def init_db():
    with app.app_context():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                time INTEGER NOT NULL,
                message TEXT NOT NULL,
                user TEXT,
                PRIMARY KEY (time, message, user)
            )
        """
        )
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS chat_historical AS
            SELECT * FROM chat_history
            ORDER BY time DESC
        """
        )
        conn.commit()
        conn.close()


@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT time, message, user FROM chat_historical LIMIT 100")
    rows = cursor.fetchall()
    conn.close()

    messages = [
        {"time": row[0], "message": row[1], "user": row[2]} for row in reversed(rows)
    ]

    # get files in the share directory and list them
    if not os.path.exists(SHARE_DIR):
        os.makedirs(SHARE_DIR)
    files = os.listdir(SHARE_DIR)

    return render_template("index.html", messages=messages, files=files)



# WebSocket server setup

clients = set()

async def internet_status_broadcaster():
    while True:
        print("Checking internet status...")
        # Ping 8.8.8.8 with a 1-second timeout
        try:
            result = subprocess.run(
                "ping -c 1 -W 1 8.8.8.8".split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            online = result.returncode == 0
        except Exception:
            online = False

        status_message = json.dumps({
            "type": "status",
            "online": online
        })

        broadcast(clients, status_message)
        await asyncio.sleep(10)


async def handler(websocket):
    clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            username = data.get("username", "Anonymous")
            content = data.get("content", "")

            print(f"Received message from {username}: {content}")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            timestamp = int(time.time())
            cursor.execute(
                "INSERT INTO chat_history (time, message, user) VALUES (?, ?, ?)",
                (timestamp, content, username),
            )
            conn.commit()
            conn.close()

            # Broadcast to all clients
            message_broadcast = json.dumps({"username": username, "content": content})
            broadcast(clients, message_broadcast)

            print(f"Broadcasted message: {message_broadcast}")
    finally:
        clients.remove(websocket)


async def start_ws_server():
    print("WebSocket server starting on ws://0.0.0.0:6789")
    async with websockets.serve(
        handler, "0.0.0.0", 6789, ping_interval=20, ping_timeout=10
    ):
        await asyncio.gather(
            internet_status_broadcaster(),
            asyncio.Future() # Run forever
        )


def run_websocket():
    asyncio.run(start_ws_server())


if __name__ == "__main__":
    init_db()

    # Start WebSocket server in a separate thread
    threading.Thread(target=run_websocket, daemon=True).start()

    # run Flask app
    app.run(host="0.0.0.0", port=8765)

