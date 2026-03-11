import shutil
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.app.services.db_service import (
    insert_raw_log,
    insert_metrics,
    insert_cv_features,
    insert_nlp_features,
    insert_forecast
)
from backend.app.services.cv_service import run_cv_pipeline
from backend.app.services.nlp_service import run_nlp_pipeline
from backend.app.services.forecast_service import run_forecast_pipeline

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/submit/full-entry")
async def submit_full_entry(
    user_id: int = Form(...),
    workout_date: str = Form(...),
    workout_text: str = Form(...),
    weight: float = Form(None),
    steps: int = Form(None),
    calories_burned: float = Form(None),
    sleep_hours: float = Form(None),
    water_intake: float = Form(None),
    heart_rate: float = Form(None),
    image: UploadFile = File(None)
):
    try:
        image_path = None

        if image is not None and image.filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = image.filename.replace(" ", "_")
            filename = f"user_{user_id}_{timestamp}_{safe_name}"
            file_path = UPLOAD_DIR / filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            image_path = str(file_path)

        log_id = insert_raw_log(
            user_id=user_id,
            workout_date=workout_date,
            workout_text=workout_text,
            image_path=image_path
        )

        insert_metrics(
            user_id=user_id,
            log_id=log_id,
            workout_date=workout_date,
            weight=weight,
            steps=steps,
            calories_burned=calories_burned,
            sleep_hours=sleep_hours,
            water_intake=water_intake,
            heart_rate=heart_rate
        )

        
        
        cv_result = run_cv_pipeline(image_path)
        print("CV RESULT =", cv_result)
        insert_cv_features(
            user_id=user_id,
            log_id=log_id,
            pose_score=cv_result["pose_score"],
            posture_label=cv_result["posture_label"],
            movement_quality=cv_result["movement_quality"],
            extracted_keypoints=cv_result["extracted_keypoints"],
            predicted_exercise=cv_result.get("predicted_exercise"),
            prediction_confidence=cv_result.get("prediction_confidence")
        )



        nlp_result = run_nlp_pipeline(workout_text)
        insert_nlp_features(
            user_id=user_id,
            log_id=log_id,
            sentiment_score=nlp_result["sentiment_score"],
            fatigue_level=nlp_result["fatigue_level"],
            workout_type=nlp_result["workout_type"],
            workout_duration_minutes=nlp_result["workout_duration_minutes"],
            extracted_entities=nlp_result["extracted_entities"]
        )

        forecast_result = run_forecast_pipeline(
            user_id=user_id,
            weight=weight,
            steps=steps,
            calories_burned=calories_burned
        )

        insert_forecast(
            user_id=user_id,
            forecast_date=workout_date,
            predicted_weight=forecast_result["predicted_weight"],
            predicted_steps=forecast_result["predicted_steps"],
            predicted_calories=forecast_result["predicted_calories"],
            confidence_score=forecast_result["confidence_score"]
        )

        return {
            "status": "success",
            "log_id": log_id,
            "image_path": image_path,
            "cv_result": cv_result,
            "nlp_result": nlp_result,
            "forecast_result": forecast_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))