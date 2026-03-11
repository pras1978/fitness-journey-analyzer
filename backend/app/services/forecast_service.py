def run_forecast_pipeline(user_id, weight=None, steps=None, calories_burned=None):
    predicted_weight = weight - 0.1 if weight is not None else None
    predicted_steps = int(steps * 1.05) if steps is not None else None
    predicted_calories = calories_burned + 50 if calories_burned is not None else None

    return {
        "predicted_weight": predicted_weight,
        "predicted_steps": predicted_steps,
        "predicted_calories": predicted_calories,
        "confidence_score": 0.78
    }