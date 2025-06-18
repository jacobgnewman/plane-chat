
import threading
import asyncio
import sqlite3
import json
import time

from flask import Flask, render_template, request, url_for
import websockets

DB_PATH = "/srv/db/chat.db"
app = Flask(__name__)

# Setup DB on launch
def init_db():
    with app.app_context():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                time INTEGER NOT NULL,
                message TEXT NOT NULL,
                user TEXT,
                PRIMARY KEY (time, message, user)
            )
        """)
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS chat_historical AS
            SELECT * FROM chat_history
            ORDER BY time DESC
        """)
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
        {'time': row[0], 'message': row[1], 'user': row[2]}
        for row in reversed(rows)
    ]
    return render_template("index.html", messages=messages)


# --- WebSocket server section ---
clients = set()

async def handler(websocket):
    clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            username = data.get("username", "Anonymous")
            content = data.get("content", "")

            print(f"Received message from {username}: {content}")

            # Save to SQLite
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            timestamp = int(time.time())
            cursor.execute(
                "INSERT INTO chat_history (time, message, user) VALUES (?, ?, ?)",
                (timestamp, content, username)
            )
            conn.commit()
            conn.close()

            # Broadcast to all clients
            broadcast = json.dumps({'username': username, 'content': content})
            await asyncio.gather(
                *[c.send(broadcast) for c in clients],
                return_exceptions=True
            )
            print(f"Broadcasted message: {broadcast}")
    finally:
        clients.remove(websocket)


async def start_ws_server():
    print("WebSocket server starting on ws://0.0.0.0:6789")
    async with websockets.serve(handler, "0.0.0.0", 6789):
        await asyncio.Future()  # run forever


def run_websocket():
    asyncio.run(start_ws_server())


# --- Main runner ---
if __name__ == "__main__":
    init_db()

    # Start WebSocket server in a separate thread
    threading.Thread(target=run_websocket, daemon=True).start()

    # Run Flask app (will block)
    app.run(host="0.0.0.0", port=8765)
