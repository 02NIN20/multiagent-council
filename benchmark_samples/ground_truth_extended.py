"""
ground_truth.py — Combined ground truth findings for ALL benchmark samples.

Contains expected findings for each test file so precision/recall can be calculated.

Used by backend/benchmark/metrics.py to evaluate single-agent vs multi-agent.
"""

# sqli_app.py (4 known vulnerabilities)
ground_truth_sqli = [
    {
        "title": "SQL injection in user endpoint",
        "detail": "sqli_app.py: f-string interpolation in get_user() — user_id directly concatenated",
        "impact": "Critical",
        "proposal": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
    },
    {
        "title": "SQL injection in login",
        "detail": "sqli_app.py: f-string interpolation in login() — username/password concatenated",
        "impact": "Critical",
        "proposal": "Use parameterized queries for authentication"
    },
    {
        "title": "Missing authentication — users endpoint",
        "detail": "sqli_app.py: /users endpoint exposes all user data without auth check",
        "impact": "High",
        "proposal": "Add authentication middleware before listing users"
    },
    {
        "title": "Debug mode enabled",
        "detail": "sqli_app.py: app.run(debug=True) exposes stack traces",
        "impact": "Medium",
        "proposal": "Set debug=False in production"
    },
]

# xss_app.py (5 known vulnerabilities)
ground_truth_xss = [
    {
        "title": "Reflected XSS in search endpoint",
        "detail": "xss_app.py: search() returns user input directly in HTML without escaping",
        "impact": "Critical",
        "proposal": "Use Flask's render_template with autoescaping instead of f-strings"
    },
    {
        "title": "Stored XSS in profile endpoint",
        "detail": "xss_app.py: profile() inserts username directly into HTML and JavaScript",
        "impact": "Critical",
        "proposal": "Escape output with html.escape() and use Content-Security-Policy header"
    },
    {
        "title": "Stored XSS in comment endpoint",
        "detail": "xss_app.py: add_comment() renders user comment without sanitization",
        "impact": "Critical",
        "proposal": "Sanitize HTML with bleach.clean() or use template autoescaping"
    },
    {
        "title": "Insecure cookie — no HttpOnly or Secure flags",
        "detail": "xss_app.py: set-cookie endpoint sets session_id without HttpOnly or Secure",
        "impact": "High",
        "proposal": "Set httponly=True and secure=True on all cookies"
    },
    {
        "title": "Debug mode enabled",
        "detail": "xss_app.py: app.run(debug=True) exposes stack traces",
        "impact": "Medium",
        "proposal": "Set debug=False in production"
    },
]

# cmd_injection.py (5 known vulnerabilities)
ground_truth_cmd = [
    {
        "title": "OS command injection in ping endpoint",
        "detail": "cmd_injection.py: os.system() with user-controlled host parameter",
        "impact": "Critical",
        "proposal": "Use subprocess.run() with shell=False and validate input against allowlist"
    },
    {
        "title": "Shell injection via subprocess with shell=True",
        "detail": "cmd_injection.py: run_script() uses shell=True with user-controlled script parameter",
        "impact": "Critical",
        "proposal": "Use shell=False and pass arguments as a list"
    },
    {
        "title": "eval() on user input in template processing",
        "detail": "cmd_injection.py: process_template() uses eval() on user template input",
        "impact": "Critical",
        "proposal": "Remove eval(); use a secure template engine like Jinja2"
    },
    {
        "title": "Blind command injection via subprocess.Popen",
        "detail": "cmd_injection.py: execute() uses shell=True with user-controlled command",
        "impact": "Critical",
        "proposal": "Use shell=False and pass command as argument list"
    },
    {
        "title": "Debug mode enabled",
        "detail": "cmd_injection.py: app.run(debug=True) exposes stack traces",
        "impact": "Medium",
        "proposal": "Set debug=False in production"
    },
]

# hardcoded_secrets.py (7 known vulnerabilities)
ground_truth_secrets = [
    {
        "title": "Hardcoded database password",
        "detail": "hardcoded_secrets.py: DB_PASSWORD exposed in source code",
        "impact": "Critical",
        "proposal": "Use environment variables: os.environ.get('DB_PASSWORD')"
    },
    {
        "title": "Hardcoded API key",
        "detail": "hardcoded_secrets.py: API_KEY exposed in source code",
        "impact": "Critical",
        "proposal": "Use a secrets manager or environment variable"
    },
    {
        "title": "Hardcoded JWT secret",
        "detail": "hardcoded_secrets.py: JWT_SECRET exposed in source code",
        "impact": "Critical",
        "proposal": "Use a strong, randomly generated secret from environment"
    },
    {
        "title": "Hardcoded AWS credentials",
        "detail": "hardcoded_secrets.py: AWS_ACCESS_KEY and AWS_SECRET_KEY exposed",
        "impact": "Critical",
        "proposal": "Use AWS IAM roles or environment variables"
    },
    {
        "title": "Hardcoded SMTP credentials",
        "detail": "hardcoded_secrets.py: SMTP username and password hardcoded in send_email()",
        "impact": "High",
        "proposal": "Move SMTP credentials to environment variables"
    },
    {
        "title": "Sensitive config exposed via API",
        "detail": "hardcoded_secrets.py: /config endpoint exposes DB_PASSWORD, API_KEY, JWT_SECRET",
        "impact": "Critical",
        "proposal": "Remove sensitive fields from the /config endpoint"
    },
    {
        "title": "Debug mode enabled",
        "detail": "hardcoded_secrets.py: app.run(debug=True) exposes stack traces",
        "impact": "Medium",
        "proposal": "Set debug=False in production"
    },
]

# insecure_deserialize.py (5 known vulnerabilities)
ground_truth_deserialize = [
    {
        "title": "Insecure pickle deserialization",
        "detail": "insecure_deserialize.py: pickle.loads() on base64-decoded user input",
        "impact": "Critical",
        "proposal": "Use JSON for serialization; never unpickle untrusted data"
    },
    {
        "title": "Insecure YAML load",
        "detail": "insecure_deserialize.py: yaml.load() with default loader is unsafe",
        "impact": "Critical",
        "proposal": "Use yaml.safe_load() instead of yaml.load()"
    },
    {
        "title": "eval() on user input",
        "detail": "insecure_deserialize.py: evaluate_expression() uses eval() on user input",
        "impact": "Critical",
        "proposal": "Replace eval() with ast.literal_eval() or a safe expression parser"
    },
    {
        "title": "OS command injection via os.system",
        "detail": "insecure_deserialize.py: run_command() uses os.system() with user input",
        "impact": "Critical",
        "proposal": "Use subprocess.run() with shell=False"
    },
    {
        "title": "Debug mode enabled",
        "detail": "insecure_deserialize.py: app.run(debug=True) exposes stack traces",
        "impact": "Medium",
        "proposal": "Set debug=False in production"
    },
]

# path_traversal.py (5 known vulnerabilities)
ground_truth_path = [
    {
        "title": "Path traversal in read-file endpoint",
        "detail": "path_traversal.py: os.path.join() with user input without validation — allows ../",
        "impact": "Critical",
        "proposal": "Use os.path.realpath() and validate resolved path is within BASE_DIR"
    },
    {
        "title": "Path traversal in download endpoint",
        "detail": "path_traversal.py: send_file() with user-controlled filename without validation",
        "impact": "Critical",
        "proposal": "Validate resolved path is within the allowed directory before sending"
    },
    {
        "title": "Zip slip — path traversal in archive extraction",
        "detail": "path_traversal.py: zipfile.extractall() without checking for ../ in filenames",
        "impact": "Critical",
        "proposal": "Validate each entry's filename before extraction: os.path.realpath() check"
    },
    {
        "title": "Symlink following — arbitrary file read",
        "detail": "path_traversal.py: read_symlink() doesn't check if file is a symlink",
        "impact": "High",
        "proposal": "Use os.path.islink() check and deny symlink reads"
    },
    {
        "title": "Debug mode enabled",
        "detail": "path_traversal.py: app.run(debug=True) exposes stack traces",
        "impact": "Medium",
        "proposal": "Set debug=False in production"
    },
]

# csrf_missing.py (5 known vulnerabilities)
ground_truth_csrf = [
    {
        "title": "Missing CSRF protection on money transfer",
        "detail": "csrf_missing.py: /transfer endpoint has no CSRF token validation",
        "impact": "Critical",
        "proposal": "Use Flask-WTF CSRFProtect or validate CSRF tokens on state-changing requests"
    },
    {
        "title": "GET-based state change (idempotency violation)",
        "detail": "csrf_missing.py: /change-email uses GET to change state — CSRF via <img> tag",
        "impact": "High",
        "proposal": "Use POST for state-changing operations and include CSRF token"
    },
    {
        "title": "Missing CSRF on account deletion",
        "detail": "csrf_missing.py: /delete-account has no CSRF token validation",
        "impact": "Critical",
        "proposal": "Add CSRF token validation before deleting accounts"
    },
    {
        "title": "Insecure cookie settings — no SameSite/HttpOnly/Secure",
        "detail": "csrf_missing.py: login() sets session cookie without SameSite, HttpOnly, or Secure flags",
        "impact": "High",
        "proposal": "Set samesite='Strict', httponly=True, secure=True on session cookies"
    },
    {
        "title": "Debug mode enabled",
        "detail": "csrf_missing.py: app.run(debug=True) exposes stack traces",
        "impact": "Medium",
        "proposal": "Set debug=False in production"
    },
]

# Mapping of filename -> ground_truth list
FILE_GROUND_TRUTH = {
    "vulnerable_app.py": "ground_truth_vulnerable_app",
    "flask_app.py": "ground_truth_flask_app",
    "api_service.py": "ground_truth_flask_app",
    "sqli_app.py": ground_truth_sqli,
    "xss_app.py": ground_truth_xss,
    "cmd_injection.py": ground_truth_cmd,
    "hardcoded_secrets.py": ground_truth_secrets,
    "insecure_deserialize.py": ground_truth_deserialize,
    "path_traversal.py": ground_truth_path,
    "csrf_missing.py": ground_truth_csrf,
}

ALL_GROUND_TRUTHS = {
    "sqli_app.py": {"findings": ground_truth_sqli, "total": len(ground_truth_sqli)},
    "xss_app.py": {"findings": ground_truth_xss, "total": len(ground_truth_xss)},
    "cmd_injection.py": {"findings": ground_truth_cmd, "total": len(ground_truth_cmd)},
    "hardcoded_secrets.py": {"findings": ground_truth_secrets, "total": len(ground_truth_secrets)},
    "insecure_deserialize.py": {"findings": ground_truth_deserialize, "total": len(ground_truth_deserialize)},
    "path_traversal.py": {"findings": ground_truth_path, "total": len(ground_truth_path)},
    "csrf_missing.py": {"findings": ground_truth_csrf, "total": len(ground_truth_csrf)},
}
