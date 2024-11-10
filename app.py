from flask import Flask, render_template, request, redirect, url_for, make_response

app = Flask(__name__)

# In-memory storage for messages
messages = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the message from the form
        message = request.form.get("message")
        user = request.form.get("user")
        if message:
            # Append the message to the messages list
            messages.append({"text" : message, "user": user})
            
            # Set a cookie to remember the user's name
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("username", user)
        return resp

    user = request.cookies.get("username", "")

    # Display the main page with all messages, passing the user value
    return render_template("index.html", messages=messages, user=user)

if __name__ == "__main__":
    app.run(host="10.42.0.1", port=80, debug=True)

