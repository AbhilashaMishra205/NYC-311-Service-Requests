import glob
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUTS_DIR = BASE_DIR / "outputs"
VISUALS_DIR = BASE_DIR / "visuals"

app = Flask(__name__)


def latest_part_csv(dataset_name: str) -> Path | None:
    pattern = str(OUTPUTS_DIR / dataset_name / "part-*.csv")
    matches = glob.glob(pattern)
    if not matches:
        return None
    return Path(max(matches, key=lambda p: Path(p).stat().st_mtime))


def load_dataset(dataset_name: str) -> dict:
    csv_path = latest_part_csv(dataset_name)
    if not csv_path:
        return {"exists": False, "columns": [], "rows": [], "file": None}

    df = pd.read_csv(csv_path)
    rows = df.to_dict(orient="records")
    return {
        "exists": True,
        "columns": list(df.columns),
        "rows": rows,
        "file": str(csv_path),
    }


def collect_results() -> dict:
    datasets = {
        "borough_counts": load_dataset("borough_counts"),
        "high_volume_boroughs": load_dataset("high_volume_boroughs"),
        "hourly_trend": load_dataset("hourly_trend"),
        "monthly_trend": load_dataset("monthly_trend"),
        "top_complaints": load_dataset("top_complaints"),
    }

    total_requests = 0
    if datasets["borough_counts"]["exists"]:
        total_requests = int(sum(r.get("count", 0) for r in datasets["borough_counts"]["rows"]))

    top_label = "N/A"
    top_count = None
    top_complaints_list = []
    if datasets["top_complaints"]["exists"] and datasets["top_complaints"]["rows"]:
        top_rows = sorted(
            datasets["top_complaints"]["rows"],
            key=lambda r: r.get("count", 0),
            reverse=True,
        )
        top_row = top_rows[0]
        top_label = str(top_row.get("complaint_type", "N/A"))
        top_count = int(top_row.get("count", 0))
        for row in top_rows[:5]:
            top_complaints_list.append(
                {
                    "complaint_type": str(row.get("complaint_type", "N/A")),
                    "count": int(row.get("count", 0)),
                }
            )

    summary = {
        "total_requests": total_requests,
        "boroughs": len(datasets["borough_counts"]["rows"]) if datasets["borough_counts"]["exists"] else 0,
        "top_complaint_type": top_label,
        "top_complaint_count": top_count,
        "top_complaints": top_complaints_list,
    }

    visuals = []
    if VISUALS_DIR.exists():
        for path in sorted(VISUALS_DIR.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True):
            visuals.append({"name": path.name, "url": f"/visuals/{path.name}"})

    return {"summary": summary, "datasets": datasets, "visuals": visuals}


def validate_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def run_pipeline(start_date: str, end_date: str) -> list[dict]:
    commands = [
        [sys.executable, str(SCRIPTS_DIR / "download_api.py"), "--start-date", start_date, "--end-date", end_date],
        [sys.executable, str(SCRIPTS_DIR / "clean_data.py")],
        [sys.executable, str(SCRIPTS_DIR / "spark_analysis.py")],
        [sys.executable, str(SCRIPTS_DIR / "visualizations.py")],
    ]

    logs: list[dict] = []
    for cmd in commands:
        proc = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        logs.append(
            {
                "command": " ".join(cmd),
                "returncode": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            }
        )
        if proc.returncode != 0:
            break

    return logs


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/results")
def api_results():
    return jsonify({"ok": True, **collect_results()})


@app.get("/visuals/<path:filename>")
def get_visual(filename: str):
    return send_from_directory(VISUALS_DIR, filename)


@app.post("/api/run")
def api_run():
    payload = request.get_json(silent=True) or {}
    start_date = str(payload.get("start_date", "")).strip()
    end_date = str(payload.get("end_date", "")).strip()

    if not start_date or not validate_date(start_date):
        return jsonify({"ok": False, "error": "Invalid start date."}), 400
    if not end_date or not validate_date(end_date):
        return jsonify({"ok": False, "error": "Invalid end date."}), 400
    if start_date > end_date:
        return jsonify({"ok": False, "error": "Start date must be on or before end date."}), 400

    logs = run_pipeline(start_date, end_date)
    failed = next((entry for entry in logs if entry["returncode"] != 0), None)

    if failed:
        return jsonify(
            {
                "ok": False,
                "error": "Pipeline failed. Check logs.",
                "logs": logs,
            }
        ), 500

    return jsonify({"ok": True, "logs": logs, **collect_results()})


if __name__ == "__main__":
    app.run(debug=True)
