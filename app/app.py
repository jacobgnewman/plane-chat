from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_socketio import SocketIO, emit, send

import sqlite3
import logging
import time


db = f"db/chat.db"

app = Flask(__name__)
socketio = SocketIO(app)

logging.basicConfig(level=logging.DEBUG)



with app.app_context():
    conn = sqlite3.connect(db)
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

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    match request.method:
        case "POST":
            # Get the message from the form
            message = request.form.get("message")
            user = request.form.get("user")
            send(str({"message": message, "user": user}), broadcast=True, namespace="/")
            # timestamp message
            ts = time.time()

            cursor.execute("""
                INSERT INTO chat_history VALUES (?, ?, ?)
            """,(ts, message, user))
            conn.commit()
            conn.close()
                
            # Set a cookie to remember the user's name
            resp = make_response(redirect(url_for("index")))
            resp.set_cookie("username", user)
            return resp
        case "GET":
            cursor.execute("""
                SELECT * FROM chat_historical
            """)
            messages = [{"message": m[1],"user": m[2]} for m in cursor.fetchall()]
            app.logger.debug(f"{messages}")
            conn.close()
            user = request.cookies.get("username", "")
            return render_template("index.html", messages=messages, user=user)
        
        case _:
            response = make_response("Method Not Allowed", 405)
            response.headers["Allow"] = "GET, POST"
            return response

    

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8765, debug=True, allow_unsafe_werkzeug=True)

