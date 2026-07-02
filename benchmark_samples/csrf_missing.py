"""CSRF missing protection — benchmark sample."""
from flask import Flask, request, render_template_string, jsonify, make_response
import os

app = Flask(__name__)

# VULN: No CSRF protection on any endpoint
# VULN: No SameSite cookie attribute


@app.route("/transfer", methods=["POST"])
def transfer_money():
    """VULN: No CSRF token — any site can POST to this endpoint."""
    data = request.get_json()
    amount = data.get("amount", 0)
    to_account = data.get("to_account", "")
    # Process transfer
    return jsonify({
        "status": "transferred",
        "amount": amount,
        "to": to_account,
    })


# VULN: GET-based state change (idempotency violation)
@app.route("/change-email", methods=["GET"])
def change_email():
    """VULN: GET request changes state — CSRF via <img> tag."""
    new_email = request.args.get("email", "")
    # Changes email without any token
    return jsonify({"status": "email_updated", "new_email": new_email})


# VULN: No CSRF on delete action
@app.route("/delete-account", methods=["POST"])
def delete_account():
    """VULN: Account deletion without CSRF token."""
    user_id = request.form.get("user_id", "")
    # Deletes account
    return jsonify({"status": "account_deleted", "user_id": user_id})


# VULN: Insecure cookie settings
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    if username == "admin" and password == "admin":
        resp = make_response(jsonify({"status": "ok"}))
        # VULN: No SameSite, no HttpOnly, no Secure
        resp.set_cookie(
            "session",
            "admin-token-123",
            httponly=False,
            secure=False,
            samesite=None,
        )
        return resp
    return jsonify({"error": "Invalid credentials"}), 401


if __name__ == "__main__":
    app.run(debug=True)
