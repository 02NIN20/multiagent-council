"""XSS vulnerable app — benchmark sample."""
from flask import Flask, request, make_response
import os

app = Flask(__name__)


@app.route("/search")
def search():
    query = request.args.get("q", "")
    # VULN: Reflected XSS — user input directly in response
    return f"""
    <html>
    <head><title>Search Results</title></head>
    <body>
        <h1>Search results for: {query}</h1>
        <p>No results found.</p>
    </body>
    </html>
    """


@app.route("/profile/<username>")
def profile(username):
    # VULN: Stored XSS via URL parameter
    return f"""
    <html>
    <head><title>Profile</title></head>
    <body>
        <h1>Welcome, {username}!</h1>
        <script>document.cookie = "last_user={username}"</script>
    </body>
    </html>
    """


@app.route("/comment", methods=["POST"])
def add_comment():
    data = request.get_json()
    comment = data.get("text", "")
    # VULN: Stored XSS — comment rendered without sanitization
    # (simulating storage and retrieval)
    html = f"""
    <html>
    <head><title>Comment added</title></head>
    <body>
        <div class="comment">{comment}</div>
        <a href="/">Back</a>
    </body>
    </html>
    """
    return make_response(html, 201)


@app.route("/set-cookie")
def set_cookie():
    resp = make_response("Cookie set")
    # VULN: Cookie without HttpOnly or Secure flags
    resp.set_cookie("session_id", "abc123", httponly=False, secure=False)
    return resp


if __name__ == "__main__":
    app.run(debug=True)
