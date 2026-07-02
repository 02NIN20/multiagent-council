"""Path Traversal vulnerable app — benchmark sample."""
import os
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)
BASE_DIR = "/app/data"


# VULN: Path traversal — no sanitization
@app.route("/read-file")
def read_file():
    filename = request.args.get("file", "")
    # VULN: Direct path join without validation
    filepath = os.path.join(BASE_DIR, filename)
    try:
        with open(filepath, "r") as f:
            content = f.read()
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# VULN: send_file with user input
@app.route("/download")
def download():
    filename = request.args.get("file", "")
    try:
        # VULN: send_file without path validation
        return send_file(os.path.join(BASE_DIR, filename))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# VULN: Zip slip — extracting archives without path validation
import zipfile
import tempfile


@app.route("/upload-zip", methods=["POST"])
def upload_zip():
    file = request.files.get("zipfile")
    if not file:
        return jsonify({"error": "No file"}), 400
    # VULN: No path traversal check during extraction
    with zipfile.ZipFile(file) as zf:
        zf.extractall("/app/uploads")
    return jsonify({"status": "extracted"})


# VULN: Symlink following
@app.route("/read-symlink")
def read_symlink():
    filename = request.args.get("file", "")
    filepath = os.path.join(BASE_DIR, filename)
    # VULN: No check if file is a symlink
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            content = f.read()
        return jsonify({"content": content})
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
