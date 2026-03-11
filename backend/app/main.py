from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
import pandas as pd
import os
import numpy as np
from backend.app.routes.process import router as process_router


app = FastAPI(title="Intelligent Fitness Journey Analyzer")
app.include_router(process_router)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE_PATH = os.path.join(PROJECT_ROOT, "data", "processed")


def load_csv_safe(file_path: str):
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    try:
        df = pd.read_csv(file_path)
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.astype(object).where(pd.notnull(df), None)
        return jsonable_encoder(df.to_dict(orient="records"))
    except Exception as e:
        return {"error": str(e), "file_path": file_path}


@app.get("/")
def home():
    return {"message": "Fitness Journey Analyzer API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/forecast")
def forecast():
    return load_csv_safe(os.path.join(BASE_PATH, "fitness_forecast.csv"))


@app.get("/dashboard/summary")
def dashboard_summary():
    return load_csv_safe(os.path.join(BASE_PATH, "final_dashboard_summary.csv"))


@app.get("/insights")
def insights():
    return load_csv_safe(os.path.join(BASE_PATH, "final_insights.csv"))


@app.get("/timeline")
def timeline():
    return load_csv_safe(os.path.join(BASE_PATH, "combined_timeline.csv"))
