from flask import Flask, request, jsonify, send_from_directory, redirect, session
import subprocess
import os
import json
from functools import wraps
from Cleaning_agent.rules_read_toon import read_excel

app = Flask(__name__, static_folder="template", static_url_path="")
app.secret_key = "refineai-secret-key"

DATA_DIR = os.path.join("Cleaning_agent", "data")

# ---------------- AUTH GUARD ----------------

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/")   # always go to login
        return fn(*args, **kwargs)
    return wrapper


# ---------------- PUBLIC ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Demo auth (you can replace with DB later)
        if username and password:
            session["user"] = username
            return redirect("/dashboard")

    return send_from_directory("template", "login.html")


@app.route("/signup")
def signup():
    return send_from_directory("template", "signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- PROTECTED PAGES ----------------

@app.route("/dashboard")
@login_required
def dashboard():
    return send_from_directory("template", "dashboard.html")


@app.route("/projects")
@login_required
def projects():
    return send_from_directory("template", "projects.html")


@app.route("/upload")
@login_required
def upload():
    return send_from_directory("template", "upload.html")


@app.route("/rules")
@login_required
def rules():
    return send_from_directory("template", "rules.html")


@app.route("/logs")
@login_required
def logs():
    return send_from_directory("template", "logs.html")


@app.route("/history")
@login_required
def history():
    return send_from_directory("template", "history.html")


@app.route("/comparison")
@login_required
def comparison():
    return send_from_directory("template", "comparison.html")


# ---------------- PIPELINE ----------------

@app.route("/run", methods=["POST"])
@login_required
def run_cleaner():
    if "file" not in request.files or "rules" not in request.files:
        return jsonify({"error": "Missing CSV file or Rules file"}), 400

    file = request.files["file"]
    rules_file = request.files["rules"]

    os.makedirs(DATA_DIR, exist_ok=True)

    input_path = os.path.join(DATA_DIR, "input.csv")
    # Save rules as rules.xlsx so converter picks it up and makes rules.toon
    rules_excel_path = os.path.join(DATA_DIR, "rules.xlsx")

    file.save(input_path)
    rules_file.save(rules_excel_path)

    # Convert Excel rules to TOON format
    # This will generate 'rules.toon' in DATA_DIR
    try:
        read_excel(rules_excel_path, output_folder=DATA_DIR)
    except Exception as e:
        return jsonify({"error": f"Failed to process rules file: {str(e)}"}), 500

    # Run the pipeline
    # We must run inside Cleaning_agent dir so run.py can find 'data/'
    subprocess.run(["python", "run.py"], cwd="Cleaning_agent")

    return jsonify({"status": "completed"})


@app.route("/download", methods=["GET"])
@login_required
def download():
    return send_from_directory(DATA_DIR, "cleaned_output.csv", as_attachment=True)


@app.route("/api/results", methods=["GET"])
@login_required
def get_results():
    results_path = os.path.join(DATA_DIR, "results.json")
    if not os.path.exists(results_path):
        return jsonify({"error": "No results available. Please run the pipeline first."}), 404
    
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
