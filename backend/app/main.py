from fastapi import FastAPI
from backend.app.api.v1.routes_dashboard import router as dashboard_router

app = FastAPI(title="Fitness Journey Analyzer", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(dashboard_router, prefix="/api/v1")
