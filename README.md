# NYC 311 Project

NYC 311 data pipeline with a Flask + HTML dashboard.

This project:
- Downloads 311 service request data from NYC Open Data (filtered by selected start date)
- Cleans and filters the dataset
- Runs analysis and writes results to `outputs/`
- Displays results in a browser UI

## Project Structure

- `scripts/download_api.py` - downloads raw data to `data/raw/` (supports `--start-date`)
- `scripts/clean_data.py` - cleans selected columns into `data/clean/`
- `scripts/spark_analysis.py` - analysis step that writes output folders/files under `outputs/`
- `app_web.py` - Flask backend API + web server
- `templates/index.html` - frontend dashboard (charts + tables)
- `outputs/` - result folders containing `part-*.csv` and `_SUCCESS`

## Prerequisites

- Python 3.10+
- Virtual environment (project uses `.venv`)
- Required Python packages:
  - `pandas`
  - `flask`

## Setup

Create and activate venv (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install pandas flask
```

## Run Flask Dashboard (Recommended)

```powershell
.\.venv\Scripts\python.exe app_web.py
```

Open:
- http://127.0.0.1:5000

## How The UI Works

- On page load/refresh, date and results start empty.
- Select a date in the date picker.
- Changing the date automatically runs the pipeline for that date.
- Pipeline executes, in order:
  1. `scripts/download_api.py --start-date <selected-date>`
  2. `scripts/clean_data.py`
  3. `scripts/spark_analysis.py`
- `Refresh Results` reruns the same pipeline for the selected date.
- After completion, the UI shows KPI cards, charts, and tables.
- The download step intentionally fetches a single ordered sample (`$limit=1000`, oldest rows after selected date), not full pagination.

## Run Manually (CLI)

```powershell
.\.venv\Scripts\python.exe scripts\download_api.py --start-date 2026-04-01
.\.venv\Scripts\python.exe scripts\clean_data.py
.\.venv\Scripts\python.exe scripts\spark_analysis.py
```

## Outputs

The pipeline writes these folders:
- `outputs/top_complaints`
- `outputs/borough_counts`
- `outputs/monthly_trend`
- `outputs/high_volume_boroughs`
- `outputs/hourly_trend`

Each folder contains:
- `part-*.csv` (latest dataset file)
- `_SUCCESS`

## Notes

- `high_volume_boroughs` and `borough_counts` can look very similar because both are borough-level counts.
- The dashboard always reads the latest `part-*.csv` in each output folder.

## Troubleshooting

### UI shows same results for different dates

Most common causes:
- More than one Flask/Python server is running, and browser is connected to a different instance.
- The browser has stale page assets.

Fix steps (PowerShell):

```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
cd C:\Users\komak\OneDrive\Documents\GitHub\NYC-311-Service-Requests
.\.venv\Scripts\python.exe app_web.py
```

Then:
- Open only `http://127.0.0.1:5000`
- Hard refresh with `Ctrl+F5`
## Note
My contributions: Data collection, cleaning pipeline, API integration.
