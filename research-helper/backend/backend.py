# backend.py
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)

# CORS: allow React dev server (change if your port/origin differs)
CORS(
    app,
    resources={r"/get-emails": {"origins": "*"}},
    supports_credentials=True,
    methods=["POST", "OPTIONS"],
)

# ---------- Load CSVs once at startup ----------
BASE = Path(__file__).resolve().parent  # folder where backend.py lives
data = {
    'georgia tech': pd.read_csv(BASE / "faculty" / "gt_faculty.csv"),
    'stanford':     pd.read_csv(BASE / "faculty" / "stanford_faculty.csv"),
    'uiuc':         pd.read_csv(BASE / "faculty" / "uiuc_faculty.csv"),
    'purdue':       pd.read_csv(BASE / "faculty" / "purdue_faculty.csv"),
}

# Normalize all column names to lowercase
for key in data:
    data[key].columns = [col.lower() for col in data[key].columns]
# ------------------------------------------------

@app.route("/get-emails", methods=["POST"])
def get_emails():
    """
    Accepts JSON  {"school": "<free‑text>"}  and returns
    {"emails": ["a@x", "b@x", "c@x"]}  (first three rows of 'email' column).
    """
    payload = request.get_json(silent=True) or {}
    user_input = payload.get("school", "").lower()

    # -------- Normalize school ----------
    if "georgia" in user_input or "tech" in user_input:
        df = data["georgia tech"]
    elif "stanford" in user_input:
        df = data["stanford"]
    elif "illinois" in user_input or "uiuc" in user_input:
        df = data["uiuc"]
    elif "purdue" in user_input:
        df = data["purdue"]
    else:
        return jsonify({"error": "School not found"}), 404
    # -------------------------------------

    if "email" not in df.columns:
        return jsonify({"error": "CSV missing 'email' column"}), 500

    emails = df["email"].head(3).dropna().tolist()
    return jsonify({"emails": emails})

if __name__ == "__main__":
    # Turn off threaded reloader to avoid duplicate log lines
    app.run(debug=True, host="0.0.0.0", port=5050, use_reloader=False)
