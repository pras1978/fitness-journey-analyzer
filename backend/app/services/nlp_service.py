import re


def run_nlp_pipeline(workout_text: str):
    text = workout_text.lower()

    workout_type = "general"
    if "run" in text or "cardio" in text:
        workout_type = "cardio"
    elif "bench" in text or "squat" in text or "deadlift" in text:
        workout_type = "strength"

    fatigue_level = "medium"
    if any(word in text for word in ["tired", "exhausted", "fatigue"]):
        fatigue_level = "high"
    elif any(word in text for word in ["energetic", "strong", "good"]):
        fatigue_level = "low"

    duration_match = re.search(r"(\d+)\s*min", text)
    duration = float(duration_match.group(1)) if duration_match else None

    sentiment_score = 0.75 if fatigue_level == "low" else 0.45 if fatigue_level == "medium" else 0.20

    return {
        "sentiment_score": sentiment_score,
        "fatigue_level": fatigue_level,
        "workout_type": workout_type,
        "workout_duration_minutes": duration,
        "extracted_entities": {
            "keywords": re.findall(r"\b\w+\b", workout_text)[:10]
        }
    }