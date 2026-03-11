from pathlib import Path
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image


BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BASE_DIR / "models" / "exercise_model.h5"

model = load_model(str(MODEL_PATH))

CLASS_NAMES = [
    "barbell biceps curl",
    "bench press",
    "chest fly machine",
    "deadlift",
    "decline bench press",
    "hammer curl",
    "hip thrust",
    "incline bench press",
    "lat pulldown",
    "lateral raises",
    "leg extension",
    "leg raises",
    "plank",
    "pull up",
    "push up",
    "romanian deadlift",
    "russian twist",
    "shoulder press",
    "squat",
    "t bar row",
    "tricep dips",
    "tricep pushdown"
]


def run_cv_pipeline(image_path):
    if not image_path:
        return {
            "pose_score": None,
            "posture_label": "No image uploaded",
            "movement_quality": None,
            "extracted_keypoints": {},
            "predicted_exercise": None,
            "prediction_confidence": None
        }

    try:
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array, verbose=0)[0]
        pred_index = int(np.argmax(prediction))
        pred_label = CLASS_NAMES[pred_index]
        confidence = float(prediction[pred_index])

        if confidence >= 0.85:
            posture_label = "Exercise recognized clearly"
            movement_quality = "High confidence"
            pose_score = round(confidence, 2)
        elif confidence >= 0.60:
            posture_label = "Exercise recognized"
            movement_quality = "Moderate confidence"
            pose_score = round(confidence, 2)
        else:
            posture_label = "Uncertain recognition"
            movement_quality = "Low confidence"
            pose_score = round(confidence, 2)

        return {
            "pose_score": pose_score,
            "posture_label": posture_label,
            "movement_quality": movement_quality,
            "extracted_keypoints": {},
            "predicted_exercise": pred_label,
            "prediction_confidence": round(confidence, 4)
        }

    except Exception as e:
        return {
            "pose_score": None,
            "posture_label": f"CV error: {str(e)}",
            "movement_quality": None,
            "extracted_keypoints": {},
            "predicted_exercise": None,
            "prediction_confidence": None
        }