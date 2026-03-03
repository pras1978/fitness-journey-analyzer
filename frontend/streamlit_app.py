import streamlit as st
import requests

st.title("Fitness Journey Analyzer")

if st.button("Check API Health"):
    r = requests.get("http://localhost:8000/health", timeout=10)
    st.json(r.json())

if st.button("Load Dashboard Summary"):
    r = requests.get("http://localhost:8000/api/v1/dashboard/summary", timeout=10)
    st.json(r.json())
