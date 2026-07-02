"""Insecure Deserialization vulnerable app — benchmark sample."""
import pickle
import base64
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# VULN: Pickle deserialization from user input
@app.route("/deserialize", methods=["POST"])
def deserialize_data():
    data = request.get_json()
    raw = data.get("data", "")
    try:
        decoded = base64.b64decode(raw)
        # VULN: Unpickling untrusted data
        obj = pickle.loads(decoded)
        return jsonify({"result": str(obj)[:100]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# VULN: Yaml load with unsafe loader
import yaml


@app.route("/parse-yaml", methods=["POST"])
def parse_yaml():
    data = request.get_json()
    yaml_text = data.get("yaml", "")
    try:
        # VULN: yaml.load() with default loader is unsafe
        obj = yaml.load(yaml_text)
        return jsonify({"result": str(obj)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# VULN: eval() from user input
@app.route("/evaluate", methods=["POST"])
def evaluate_expression():
    data = request.get_json()
    expr = data.get("expression", "")
    # VULN: eval() of user input
    result = eval(expr)
    return jsonify({"result": result})


# VULN: Command injection via os.system
@app.route("/run", methods=["POST"])
def run_command():
    data = request.get_json()
    cmd = data.get("cmd", "ls")
    # VULN: os.system with user input
    os.system(cmd)
    return jsonify({"status": "executed"})


if __name__ == "__main__":
    app.run(debug=True)
