from fastapi import APIRouter

router = APIRouter(tags=["dashboard"])

@router.get("/dashboard/summary")
def dashboard_summary():
    return {"user_id": "demo", "latest_metrics": {}, "insights": [], "forecast": {}}
