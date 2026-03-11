import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image


# =========================================================
# PATH SETUP
# =========================================================
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "fitness.db"
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
MODEL_DIR = BASE_DIR / "models"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# DATABASE
# =========================================================
def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        workout_date TEXT,
        workout_text TEXT,
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        log_id INTEGER,
        weight REAL,
        steps INTEGER,
        calories_burned REAL,
        sleep_hours REAL,
        water_intake REAL,
        heart_rate REAL,
        metric_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cv_features (
        cv_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        log_id INTEGER,
        pose_score REAL,
        posture_label TEXT,
        movement_quality TEXT,
        extracted_keypoints TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        predicted_exercise TEXT,
        prediction_confidence REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS nlp_features (
        nlp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        log_id INTEGER,
        sentiment_score REAL,
        fatigue_level TEXT,
        workout_type TEXT,
        workout_duration_minutes REAL,
        extracted_entities TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS forecasts (
        forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        forecast_date TEXT,
        predicted_weight REAL,
        predicted_steps INTEGER,
        predicted_calories REAL,
        confidence_score REAL,
        model_version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def ensure_nlp_columns():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE nlp_features ADD COLUMN sentiment_label TEXT")
    except:
        pass

    try:
        cur.execute("ALTER TABLE nlp_features ADD COLUMN sentiment_confidence REAL")
    except:
        pass

    try:
        cur.execute("ALTER TABLE nlp_features ADD COLUMN fatigue_confidence REAL")
    except:
        pass

    try:
        cur.execute("ALTER TABLE nlp_features ADD COLUMN workout_type_confidence REAL")
    except:
        pass

    conn.commit()
    conn.close()


# =========================================================
# MODEL LOADING
# =========================================================
@st.cache_resource
def load_exercise_model():
    model_path = MODEL_DIR / "exercise_model.h5"
    return load_model(str(model_path))


@st.cache_resource
def load_sentiment_model():
    return joblib.load(MODEL_DIR / "sentiment_model.pkl")


@st.cache_resource
def load_workout_type_model():
    return joblib.load(MODEL_DIR / "workout_type_model.pkl")


@st.cache_resource
def load_fatigue_model():
    return joblib.load(MODEL_DIR / "fatigue_model.pkl")


@st.cache_resource
def load_weight_forecast_model():
    return joblib.load(MODEL_DIR / "weight_forecast_model.pkl")


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


# =========================================================
# AI PIPELINES
# =========================================================
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
        model = load_exercise_model()

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


def run_nlp_pipeline(workout_text: str):
    sentiment_model = load_sentiment_model()
    workout_type_model = load_workout_type_model()
    fatigue_model = load_fatigue_model()

    text_input = [workout_text]

    sentiment_pred = sentiment_model.predict(text_input)[0]
    sentiment_probs = sentiment_model.predict_proba(text_input)[0]
    sentiment_conf = float(max(sentiment_probs))

    workout_type = workout_type_model.predict(text_input)[0]
    workout_type_probs = workout_type_model.predict_proba(text_input)[0]
    workout_type_conf = float(max(workout_type_probs))

    fatigue_level = fatigue_model.predict(text_input)[0]
    fatigue_probs = fatigue_model.predict_proba(text_input)[0]
    fatigue_conf = float(max(fatigue_probs))

    duration_match = re.search(r"(\d+)\s*min", workout_text.lower())
    duration = float(duration_match.group(1)) if duration_match else None

    sentiment_score = sentiment_conf if sentiment_pred == "positive" else 1 - sentiment_conf

    return {
        "sentiment_score": round(sentiment_score, 4),
        "sentiment_label": sentiment_pred,
        "sentiment_confidence": round(sentiment_conf, 4),
        "fatigue_level": fatigue_level,
        "fatigue_confidence": round(fatigue_conf, 4),
        "workout_type": workout_type,
        "workout_type_confidence": round(workout_type_conf, 4),
        "workout_duration_minutes": duration,
        "extracted_entities": {
            "keywords": workout_text.lower().split()[:10]
        }
    }


def run_forecast_pipeline(user_id, weight=None, steps=None, calories_burned=None):
    predicted_weight = None

    try:
        forecast_model = load_weight_forecast_model()

        conn = sqlite3.connect(str(DB_PATH))
        user_df = pd.read_sql("""
            SELECT metric_date, weight
            FROM metrics
            WHERE user_id = ? AND weight IS NOT NULL
            ORDER BY metric_date
        """, conn, params=(user_id,))
        conn.close()

        if len(user_df) > 0:
            next_day_index = len(user_df)
            predicted_weight = float(forecast_model.predict([[next_day_index]])[0])

    except Exception as e:
        print("Forecast error:", e)

    predicted_steps = int(steps * 1.05) if steps is not None else None
    predicted_calories = calories_burned + 50 if calories_burned is not None else None

    return {
        "predicted_weight": round(predicted_weight, 2) if predicted_weight is not None else None,
        "predicted_steps": predicted_steps,
        "predicted_calories": predicted_calories,
        "confidence_score": 0.78
    }


# =========================================================
# DB INSERTS
# =========================================================
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
    conn.close()


def insert_cv_features(user_id, log_id, cv_result):
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
        cv_result.get("pose_score"),
        cv_result.get("posture_label"),
        cv_result.get("movement_quality"),
        json.dumps(cv_result.get("extracted_keypoints", {})),
        cv_result.get("predicted_exercise"),
        cv_result.get("prediction_confidence")
    ))
    conn.commit()
    conn.close()


def insert_nlp_features(user_id, log_id, nlp_result):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO nlp_features (
            user_id,
            log_id,
            sentiment_score,
            sentiment_label,
            sentiment_confidence,
            fatigue_level,
            fatigue_confidence,
            workout_type,
            workout_type_confidence,
            workout_duration_minutes,
            extracted_entities
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        log_id,
        nlp_result.get("sentiment_score"),
        nlp_result.get("sentiment_label"),
        nlp_result.get("sentiment_confidence"),
        nlp_result.get("fatigue_level"),
        nlp_result.get("fatigue_confidence"),
        nlp_result.get("workout_type"),
        nlp_result.get("workout_type_confidence"),
        nlp_result.get("workout_duration_minutes"),
        json.dumps(nlp_result.get("extracted_entities", {}))
    ))
    conn.commit()
    conn.close()


def insert_forecast(user_id, workout_date, forecast_result):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO forecasts (
            user_id,
            forecast_date,
            predicted_weight,
            predicted_steps,
            predicted_calories,
            confidence_score,
            model_version
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        workout_date,
        forecast_result.get("predicted_weight"),
        forecast_result.get("predicted_steps"),
        forecast_result.get("predicted_calories"),
        forecast_result.get("confidence_score"),
        "v2"
    ))
    conn.commit()
    conn.close()


# =========================================================
# DB READS
# =========================================================
def read_table(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_dashboard_data():
    return read_table("""
        SELECT 
            r.log_id,
            r.user_id,
            r.workout_date,
            r.workout_text,
            m.weight,
            m.steps,
            m.calories_burned,
            m.sleep_hours,
            m.water_intake,
            m.heart_rate,
            c.predicted_exercise,
            c.prediction_confidence,
            c.pose_score,
            c.posture_label,
            c.movement_quality,
            n.sentiment_score,
            n.sentiment_label,
            n.sentiment_confidence,
            n.fatigue_level,
            n.fatigue_confidence,
            n.workout_type,
            n.workout_type_confidence,
            n.workout_duration_minutes,
            f.predicted_weight,
            f.predicted_steps,
            f.predicted_calories,
            f.confidence_score
        FROM raw_logs r
        LEFT JOIN metrics m ON r.log_id = m.log_id
        LEFT JOIN cv_features c ON r.log_id = c.log_id
        LEFT JOIN nlp_features n ON r.log_id = n.log_id
        LEFT JOIN forecasts f ON r.user_id = f.user_id AND r.workout_date = f.forecast_date
        ORDER BY r.workout_date DESC, r.log_id DESC
    """)


def generate_ai_insight(df):
    if df.empty:
        return "No workout data available yet."

    latest = df.iloc[0]

    top_exercise = None
    if "predicted_exercise" in df.columns and df["predicted_exercise"].notna().any():
        top_exercise = df["predicted_exercise"].mode().iloc[0]

    top_workout_type = None
    if "workout_type" in df.columns and df["workout_type"].notna().any():
        top_workout_type = df["workout_type"].mode().iloc[0]

    avg_steps = None
    if "steps" in df.columns and df["steps"].notna().any():
        avg_steps = int(df["steps"].dropna().mean())

    latest_fatigue = latest["fatigue_level"] if pd.notna(latest.get("fatigue_level")) else None
    latest_weight = latest["weight"] if pd.notna(latest.get("weight")) else None
    predicted_weight = latest["predicted_weight"] if pd.notna(latest.get("predicted_weight")) else None

    insight_parts = []

    if top_exercise:
        insight_parts.append(f"Most frequent exercise is **{top_exercise}**.")

    if top_workout_type:
        insight_parts.append(f"Most common workout type is **{top_workout_type}**.")

    if avg_steps is not None:
        insight_parts.append(f"Average daily steps are **{avg_steps}**.")

    if latest_fatigue:
        insight_parts.append(f"Latest fatigue level is **{latest_fatigue}**.")

    if latest_weight is not None and predicted_weight is not None:
        insight_parts.append(
            f"Latest weight is **{latest_weight:.1f} kg**, and forecasted next weight is **{predicted_weight:.1f} kg**."
        )

    if not insight_parts:
        return "Data is available, but not enough for deeper AI insights yet."

    return " ".join(insight_parts)


# =========================================================
# APP INIT
# =========================================================
init_db()
ensure_nlp_columns()

st.set_page_config(page_title="Fitness Journey Analyzer", layout="wide")
st.title("🏋️ Intelligent Fitness Journey Analyzer")
st.caption("AI-powered multimodal fitness analytics using Computer Vision, NLP, and Forecasting")

st.success("System ready: Streamlit + SQLite + CV model + NLP models + Forecast model")


# =========================================================
# SUBMIT NEW ENTRY
# =========================================================
st.subheader("Submit New Fitness Entry")

with st.form("fitness_entry_form"):
    user_id = st.number_input("User ID", min_value=1, step=1, value=1)
    workout_date = st.date_input("Workout Date")
    workout_text = st.text_area("Workout Log", placeholder="Example: 45 min cardio felt strong")
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
    steps = st.number_input("Steps", min_value=0, step=100)
    calories_burned = st.number_input("Calories Burned", min_value=0.0, step=1.0)
    sleep_hours = st.number_input("Sleep Hours", min_value=0.0, step=0.5)
    water_intake = st.number_input("Water Intake (L)", min_value=0.0, step=0.1)
    heart_rate = st.number_input("Heart Rate", min_value=0.0, step=1.0)
    uploaded_image = st.file_uploader("Upload Workout Image", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Submit Entry")

if submitted:
    try:
        image_path = None

        if uploaded_image is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = uploaded_image.name.replace(" ", "_")
            filename = f"user_{user_id}_{timestamp}_{safe_name}"
            file_path = UPLOAD_DIR / filename

            with open(file_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

            image_path = str(file_path)

        log_id = insert_raw_log(
            user_id=user_id,
            workout_date=str(workout_date),
            workout_text=workout_text,
            image_path=image_path
        )

        insert_metrics(
            user_id=user_id,
            log_id=log_id,
            workout_date=str(workout_date),
            weight=float(weight) if weight else None,
            steps=int(steps) if steps else None,
            calories_burned=float(calories_burned) if calories_burned else None,
            sleep_hours=float(sleep_hours) if sleep_hours else None,
            water_intake=float(water_intake) if water_intake else None,
            heart_rate=float(heart_rate) if heart_rate else None
        )

        cv_result = run_cv_pipeline(image_path)
        nlp_result = run_nlp_pipeline(workout_text)
        forecast_result = run_forecast_pipeline(
            user_id=user_id,
            weight=float(weight) if weight else None,
            steps=int(steps) if steps else None,
            calories_burned=float(calories_burned) if calories_burned else None
        )

        insert_cv_features(user_id, log_id, cv_result)
        insert_nlp_features(user_id, log_id, nlp_result)
        insert_forecast(user_id, str(workout_date), forecast_result)

        st.success("Entry submitted and processed successfully!")

        if uploaded_image is not None:
            st.write("### Uploaded Image")
            st.image(uploaded_image, width=300)

        c1, c2, c3 = st.columns(3)

        with c1:
            st.write("### CV Result")
            st.json(cv_result)

        with c2:
            st.write("### NLP Result")
            st.json(nlp_result)

        with c3:
            st.write("### Forecast Result")
            st.json(forecast_result)

        st.rerun()

    except Exception as e:
        st.error(f"Submission failed: {e}")


# =========================================================
# DASHBOARD
# =========================================================
st.markdown("---")
st.subheader("📊 Fitness Analytics Dashboard")

dashboard_df = load_dashboard_data()

if dashboard_df.empty:
    st.warning("No data available yet. Please submit a fitness entry first.")
else:
    dashboard_df["workout_date"] = pd.to_datetime(dashboard_df["workout_date"], errors="coerce")

    # KPI CARDS
    total_workouts = len(dashboard_df)

    latest_weight = None
    if dashboard_df["weight"].notna().any():
        latest_weight = dashboard_df["weight"].dropna().iloc[0]

    avg_steps = None
    if dashboard_df["steps"].notna().any():
        avg_steps = int(dashboard_df["steps"].dropna().mean())

    top_exercise = None
    if dashboard_df["predicted_exercise"].notna().any():
        top_exercise = dashboard_df["predicted_exercise"].mode().iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Workouts", total_workouts)
    k2.metric("Latest Weight (kg)", f"{latest_weight:.1f}" if latest_weight is not None else "N/A")
    k3.metric("Avg Steps", avg_steps if avg_steps is not None else "N/A")
    k4.metric("Top Exercise", top_exercise if top_exercise else "N/A")

    st.markdown("---")

    # WEIGHT TREND
    st.write("### Weight Trend")
    weight_df = dashboard_df[["workout_date", "weight"]].dropna().sort_values("workout_date")
    if not weight_df.empty:
        st.line_chart(weight_df.set_index("workout_date")["weight"])
    else:
        st.info("No weight data available.")

    # EXERCISE FREQUENCY
    st.write("### Exercise Frequency")
    exercise_df = dashboard_df["predicted_exercise"].dropna().value_counts().reset_index()
    exercise_df.columns = ["exercise", "count"]
    if not exercise_df.empty:
        st.bar_chart(exercise_df.set_index("exercise")["count"])
    else:
        st.info("No exercise prediction data available.")

    # WORKOUT TYPE DISTRIBUTION
    st.write("### Workout Type Distribution")
    workout_type_df = dashboard_df["workout_type"].dropna().value_counts().reset_index()
    workout_type_df.columns = ["workout_type", "count"]
    if not workout_type_df.empty:
        st.bar_chart(workout_type_df.set_index("workout_type")["count"])
    else:
        st.info("No workout type data available.")

    # FATIGUE DISTRIBUTION
    st.write("### Fatigue Distribution")
    fatigue_df = dashboard_df["fatigue_level"].dropna().value_counts().reset_index()
    fatigue_df.columns = ["fatigue_level", "count"]
    if not fatigue_df.empty:
        st.bar_chart(fatigue_df.set_index("fatigue_level")["count"])
    else:
        st.info("No fatigue data available.")

    st.markdown("---")

    # RAW AI MODEL PREDICTIONS
    st.write("### Raw AI Model Predictions")
    raw_cols = [
        "workout_date",
        "predicted_exercise",
        "prediction_confidence",
        "pose_score",
        "sentiment_label",
        "sentiment_confidence",
        "workout_type",
        "workout_type_confidence",
        "fatigue_level",
        "fatigue_confidence",
        "predicted_weight"
    ]
    raw_ai_df = dashboard_df[raw_cols].copy()
    st.dataframe(raw_ai_df.head(20), use_container_width=True)

    st.markdown("---")

    # RECENT ACTIVITY
    st.write("### Recent Activity")
    recent_cols = [
        "workout_date",
        "workout_text",
        "predicted_exercise",
        "workout_type",
        "fatigue_level",
        "weight",
        "steps",
        "calories_burned",
        "predicted_weight"
    ]
    recent_df = dashboard_df[recent_cols].copy()
    st.dataframe(recent_df.head(10), use_container_width=True)

    st.markdown("---")

    # AI INSIGHT SUMMARY
    st.write("### AI Insight Summary")
    insight_text = generate_ai_insight(dashboard_df)
    st.success(insight_text)