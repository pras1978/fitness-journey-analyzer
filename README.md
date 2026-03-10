# Intelligent Fitness Journey Analyzer

An AI-powered system that helps users analyze workouts, evaluate exercise posture, understand workout sentiment, and forecast fitness progress.

This project combines Computer Vision, Natural Language Processing, and Time-Series Forecasting to provide actionable insights for improving fitness performance.

---

# Project Overview

Users can upload:

- Workout images
- Daily workout logs
- Fitness metrics (steps, calories, sleep, etc.)

The system analyzes these inputs using multiple AI models and produces insights such as:

- Exercise recognition
- Posture quality score
- Sentiment and fatigue analysis
- Forecasted weight progress

---

# System Architecture

User Input
│
├── Workout Image
├── Workout Log
├── Fitness Metrics
│
▼

AI Models

- Exercise Recognition (MobileNetV2)
- Pose Detection (MoveNet)
- NLP Log Analysis (Transformer)
- Progress Forecasting (Prophet)

▼

Integration Layer

▼

SQLite Database

▼

FastAPI Backend

▼

Streamlit Dashboard

---

# Machine Learning Modules

| Module | Model Used |
|------|------|
Exercise Recognition | MobileNetV2 |
Pose Detection | MoveNet |
Workout Log Analysis | Transformer (HuggingFace) |
Progress Forecasting | Prophet |

---

# Project Structure


---

# Database Schema

SQLite database contains the following tables:

- users
- raw_logs
- metrics
- cv_features
- nlp_features
- forecasts

These tables store AI outputs and user fitness data.

---

Install dependencies:


---

# Running the System

Start backend API:

Run the dashboard:


---

# Example AI Insights

Example system output:

Exercise detected: Squat  
Posture score: 0.84  
Sentiment: Positive  
Fatigue: Low  

Predicted weight after 30 days: 75.8 kg

---

# Technologies Used

- Python
- TensorFlow
- TensorFlow Hub
- HuggingFace Transformers
- Prophet
- FastAPI
- Streamlit
- SQLite
- Pandas
- NumPy

---

# Future Improvements

- Real-time posture correction
- Wearable sensor integration
- Personalized workout recommendations
- Mobile app deployment

---

# Authors

PR  
John  
Sai  

Master's Capstone Project
