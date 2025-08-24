import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from deep_translator import GoogleTranslator
import random
import google.generativeai as genai

# ---- CONFIG ----
st.set_page_config(page_title="NeuraVia Health Tracker", page_icon="🧠", layout="wide")

# ---- GEMINI API SETUP ----
genai.configure(api_key="AIzaSyAQHZUwqYjaVhBOkjW95VT-w_i5JT6QP1k")  
model = genai.GenerativeModel("gemini-1.5-flash")

# ---- LANGUAGE SELECTION ----
languages = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "Tamil": "ta",
    "Telugu": "te",
    "Bengali": "bn",
    "Japanese": "ja",
    "German": "de"
}
selected_lang = st.sidebar.selectbox("🌍 Select Language", list(languages.keys()))
lang_code = languages[selected_lang]


def t(text):
    """Translate text into selected language"""
    if lang_code == "en":
        return text
    return GoogleTranslator(source="en", target=lang_code).translate(text)

st.title("🧠 " + t("NeuraVia Health Tracker"))

# ---- DATA STORAGE ----
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Date", "Mood", "Sleep", "Stress", "Symptoms"])
if "last_date" not in st.session_state:
    st.session_state.last_date = None
    st.session_state.streak = 0

# ---- USER INPUT ----
st.subheader("📋 " + t("Log Today's Data"))

mood_choice = st.radio(t("How do you feel today?"),
                       ["😀 " + t("Happy"), "😐 " + t("Okay"), "😔 " + t("Low")])

sleep = st.number_input("😴 " + t("Hours of Sleep"), 0.0, 24.0, 7.0, step=0.5)
stress = st.slider("⚡ " + t("Stress Level"), 1, 10, 5)
symptoms = st.multiselect("💬 " + t("Symptoms"), ["Headache", "Fatigue", "Anxiety", "None"], default="None")

if st.button("✅ " + t("Save Entry")):
    new_row = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Mood": mood_choice,
        "Sleep": sleep,
        "Stress": stress,
        "Symptoms": ", ".join(symptoms)
    }
    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
    st.success(t("Entry saved!"))

    # Update streak
    today = datetime.now().date()
    if st.session_state.last_date != today:
        if st.session_state.last_date == today - pd.Timedelta(days=1):
            st.session_state.streak += 1
        else:
            st.session_state.streak = 1
        st.session_state.last_date = today

# ---- DASHBOARD ----
if not st.session_state.data.empty:
    st.subheader("📊 " + t("Your Health Data"))
    st.dataframe(st.session_state.data.tail(5))

    fig = px.line(st.session_state.data, x="Date", y="Stress", markers=True, title=t("Stress Trend"))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 " + t("Streak"), f"{st.session_state.streak} " + t("days"))
    col2.metric("😊 " + t("Avg Mood"), f"{st.session_state.data['Mood'].str.extract(r'(\w+)$').mode()[0]}")
    col3.metric("⚡ " + t("Avg Stress"), f"{st.session_state.data['Stress'].mean():.1f}/10")

# ---- QUICK WELLNESS TIP ----
tips = [
    "💧 Stay hydrated — drink a glass of water now!",
    "🌿 Try 5 minutes of meditation.",
    "🚶 Take a short walk to refresh your mind.",
    "📵 Reduce screen time before bed.",
    "🍎 Choose fruits over junk snacks today."
]

if st.button("✨ " + t("Get a Quick Wellness Tip")):
    st.info(t(random.choice(tips)))

# ---- AI DOCTOR (GEMINI) ----
st.subheader("🩺 " + t("Doctor's Recommendation (AI-Powered)"))

if st.button("🤖 " + t("Get Personalized AI Advice")):
    last_entry = st.session_state.data.iloc[-1].to_dict()
    prompt = f"""
    You are a friendly doctor. The patient reported:
    - Mood: {last_entry['Mood']}
    - Sleep: {last_entry['Sleep']} hours
    - Stress: {last_entry['Stress']} / 10
    - Symptoms: {last_entry['Symptoms']}

    Write a short, empathetic recommendation (doctor style), in {selected_lang}.
    """
    response = model.generate_content(prompt)
    st.info(response.text)

# ---- AI WELLNESS PLAN ----
st.subheader("📅 " + t("Generate a 3-Day Wellness Plan"))

if st.button("🧘 " + t("Create Plan")):
    avg_sleep = st.session_state.data["Sleep"].mean()
    avg_stress = st.session_state.data["Stress"].mean()

    prompt = f"""
    Create a 3-day personalized wellness plan for a person.
    Average sleep: {avg_sleep:.1f} hours
    Average stress: {avg_stress:.1f}/10
    Include morning, afternoon, evening recommendations.
    Language: {selected_lang}
    """
    plan = model.generate_content(prompt)
    st.success(plan.text)