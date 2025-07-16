import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/get-emails": {"origins": ["https://research-helper.vercel.app"]}})

# --- keep‑alive route ---
@app.route("/", methods=["GET"])
def health():
    return "OK", 200

# --- load CSVs (same as before) ---
BASE = Path(__file__).parent
data = {
    "georgia tech": pd.read_csv(BASE / "faculty" / "gt_faculty.csv"),
    "stanford":     pd.read_csv(BASE / "faculty" / "stanford_faculty.csv"),
    "uiuc":         pd.read_csv(BASE / "faculty" / "uiuc_faculty.csv"),
    "purdue":       pd.read_csv(BASE / "faculty" / "purdue_faculty.csv"),
}
for key in data:
    data[key].columns = [c.lower() for c in data[key].columns]

# --- email route, now with OPTIONS ---
@app.route("/get-emails", methods=["POST", "OPTIONS"])
def get_emails():
    if request.method == "OPTIONS":
        return "", 204          # reply to pre‑flight
    payload = request.get_json(silent=True) or {}
    school = payload.get("school", "").lower()
    ...
    return jsonify({"emails": emails})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
