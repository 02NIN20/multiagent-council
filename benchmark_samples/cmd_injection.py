"""Command Injection vulnerable app — benchmark sample."""
import os
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)


# VULN: os.system with user input
@app.route("/ping", methods=["POST"])
def ping_host():
    data = request.get_json()
    host = data.get("host", "localhost")
    # VULN: Direct shell command with user input
    cmd = f"ping -c 4 {host}"
    result = os.system(cmd)
    return jsonify({"status": "executed", "code": result})


# VULN: subprocess with shell=True
@app.route("/run-script", methods=["POST"])
def run_script():
    data = request.get_json()
    script = data.get("script", "")
    # VULN: subprocess with shell=True and user input
    result = subprocess.run(
        script, shell=True, capture_output=True, text=True
    )
    return jsonify({"stdout": result.stdout, "stderr": result.stderr})


# VULN: Using eval with user-controlled filename
@app.route("/process-template", methods=["POST"])
def process_template():
    data = request.get_json()
    template = data.get("template", "")
    filename = data.get("filename", "output.txt")
    # VULN: eval on user input
    content = eval(f'f"""{template}"""')
    with open(filename, "w") as f:
        f.write(content)
    return jsonify({"status": "written"})


# VULN: Blind command injection via subprocess.Popen
@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json()
    command = data.get("command", "ls")
    # VULN: subprocess.Popen with shell=True
    proc = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    return jsonify({"stdout": stdout.decode(), "stderr": stderr.decode()})


if __name__ == "__main__":
    app.run(debug=True)
