import json
from backend.app.db import get_connection


def insert_raw_log(user_id, workout_date, workout_text, image_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO raw_logs (user_id, workout_date, workout_text, image_path)
        VALUES (?, ?, ?, ?)
    """, (user_id, workout_date, workout_text, image_path))
    conn.commit()
    log_id = cur.lastrowid
    conn.close()
    return log_id


def insert_metrics(
    user_id,
    log_id,
    workout_date,
    weight,
    steps,
    calories_burned,
    sleep_hours,
    water_intake,
    heart_rate
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO metrics (
            user_id, log_id, weight, steps, calories_burned,
            sleep_hours, water_intake, heart_rate, metric_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, log_id, weight, steps, calories_burned,
        sleep_hours, water_intake, heart_rate, workout_date
    ))
    conn.commit()
    metric_id = cur.lastrowid
    conn.close()
    return metric_id


def insert_cv_features(
    user_id,
    log_id,
    pose_score,
    posture_label,
    movement_quality,
    extracted_keypoints,
    predicted_exercise,
    prediction_confidence
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO cv_features (
            user_id,
            log_id,
            pose_score,
            posture_label,
            movement_quality,
            extracted_keypoints,
            predicted_exercise,
            prediction_confidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        log_id,
        pose_score,
        posture_label,
        movement_quality,
        json.dumps(extracted_keypoints),
        predicted_exercise,
        prediction_confidence
    ))
    conn.commit()
    conn.close()


def insert_nlp_features(
    user_id,
    log_id,
    sentiment_score,
    fatigue_level,
    workout_type,
    workout_duration_minutes,
    extracted_entities
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO nlp_features (
            user_id, log_id, sentiment_score, fatigue_level,
            workout_type, workout_duration_minutes, extracted_entities
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, log_id, sentiment_score, fatigue_level,
        workout_type, workout_duration_minutes, json.dumps(extracted_entities)
    ))
    conn.commit()
    conn.close()


def insert_forecast(
    user_id,
    forecast_date,
    predicted_weight,
    predicted_steps,
    predicted_calories,
    confidence_score,
    model_version="v1"
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO forecasts (
            user_id, forecast_date, predicted_weight,
            predicted_steps, predicted_calories,
            confidence_score, model_version
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, forecast_date, predicted_weight,
        predicted_steps, predicted_calories,
        confidence_score, model_version
    ))
    conn.commit()
    conn.close()