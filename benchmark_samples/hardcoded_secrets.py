"""Hardcoded secrets vulnerable app — benchmark sample."""
import os
import smtplib
from flask import Flask, request

app = Flask(__name__)

# VULN: Hardcoded database password
DB_PASSWORD = "SuperSecret123!"

# VULN: Hardcoded API key for external service
API_KEY = "sk-live-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"

# VULN: Hardcoded JWT secret
JWT_SECRET = "my-super-secret-jwt-key-12345"

# VULN: Hardcoded AWS access key
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json()
    # VULN: Hardcoded SMTP credentials
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "admin@example.com"
    smtp_pass = "password123"

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.sendmail(smtp_user, [data.get("to", "")], data.get("body", ""))
    server.quit()
    return {"status": "sent"}


@app.route("/config")
def get_config():
    # VULN: Exposes sensitive config
    return {
        "db_password": DB_PASSWORD,
        "api_key": API_KEY,
        "jwt_secret": JWT_SECRET,
    }


if __name__ == "__main__":
    app.run(debug=True)
