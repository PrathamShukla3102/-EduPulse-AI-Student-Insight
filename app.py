import streamlit as st
from datetime import datetime
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt


genai.configure(api_key="AIzaSyD0FF3SkwjVh1diVJ-xEJyw2aIECrzpoMY")  # Replace with your Gemini API key

# Initialize Gemini model
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

st.set_page_config(page_title="EduPulse – AI Student Insight", layout="centered")


if "history" not in st.session_state:
    st.session_state.history = []


def generate_ai_text(prompt: str) -> str:
    try:
        response = model.generate_content([{"role": "user", "parts": [prompt]}])
        return response.text
    except Exception as e:
        return f"⚠️ Error generating AI content: {e}"

st.title("🎓 EduPulse – AI Student Insight")
st.markdown("Empower feedback with AI-driven analysis. Select a KPI or view:")


option = st.sidebar.selectbox(
    "📌 Select KPI or View:",
    ["Feedback Lag Index (FLI)", "Personal Relevance Score (PRS)", "All Students"]
)

# FLI Section
if option == "Feedback Lag Index (FLI)":
    st.header("🕒 Feedback Lag Index")
    with st.form("fli_form"):
        student_id = st.text_input("Student ID")
        student_name = st.text_input("Student Name")
        submission_time_str = st.text_input("Submission Time (YYYY-MM-DD HH:MM)")
        feedback_time_str = st.text_input("Feedback Time (YYYY-MM-DD HH:MM)")
        submitted = st.form_submit_button("✨ Generate Insight")

    if submitted:
        try:
            submission_time = datetime.strptime(submission_time_str, "%Y-%m-%d %H:%M")
            feedback_time = datetime.strptime(feedback_time_str, "%Y-%m-%d %H:%M")
            time_diff_hours = (feedback_time - submission_time).total_seconds() / 3600

            st.success(f"⏳ Feedback Lag: **{time_diff_hours:.2f} hours**")

            prompt = f"""
Student ID: {student_id}
Student Name: {student_name}
Submission Time: {submission_time_str}
Feedback Time: {feedback_time_str}
Time difference: {time_diff_hours:.2f} hours

As an AI learning advisor, analyze this feedback lag timing and provide a concise insight with possible causes and recommendations.
Limit the response to under 100 words.
"""
            insight = generate_ai_text(prompt)
            st.markdown("#### 🤖 AI Insight:")
            st.info(insight)

            st.session_state.history.append({
                "KPI": "FLI",
                "Student ID": student_id,
                "Student Name": student_name,
                "Lag (hrs)": round(time_diff_hours, 2),
                "Date": submission_time.date(),
                "Insight": insight
            })

        except Exception as e:
            st.error(f"⚠️ Error: {e}. Please use format YYYY-MM-DD HH:MM.")

# PRS Section
elif option == "Personal Relevance Score (PRS)":
    st.header("🎯 Personal Relevance Score")
    subjects = [
        "Data Science Foundations", "Machine Learning",
        "Deep Learning", "Data Visualization", "NLP"
    ]
    with st.form("prs_form"):
        student_id = st.text_input("Student ID")
        student_name = st.text_input("Student Name")
        subject = st.selectbox("Select Subject", subjects)
        prs_score = st.slider("Personal Relevance Score (1 = low, 5 = high)", 1, 5)
        submitted = st.form_submit_button("✨ Generate Insight")

    if submitted:
        prompt = f"""
Student ID: {student_id}
Student Name: {student_name}
Subject: {subject}
PRS Score: {prs_score}/5

As an AI learning analyst, provide a brief summary and suggestions to improve engagement and learning outcomes.
Keep it actionable and under 100 words.
"""
        insight = generate_ai_text(prompt)
        st.markdown("#### 🤖 AI Insight:")
        st.info(insight)

        st.session_state.history.append({
            "KPI": "PRS",
            "Student ID": student_id,
            "Student Name": student_name,
            "Subject": subject,
            "Score": prs_score,
            "Date": datetime.today().date(),
            "Insight": insight
        })




if st.session_state.history:
    st.subheader("📊 Student KPI History")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)

    if option != "All Students":
        # Single student selection and plots
        selected_student = st.selectbox("📌 Select a student to plot insights:", df["Student Name"].unique())
        student_df = df[df["Student Name"] == selected_student]

        if not student_df.empty:
            if "Lag (hrs)" in student_df.columns:
                lag_data = student_df.dropna(subset=["Lag (hrs)"])
                if not lag_data.empty:
                    st.markdown("#### 🧭 Feedback Lag Over Time")
                    plt.figure(figsize=(6, 3))
                    plt.plot(lag_data["Date"], lag_data["Lag (hrs)"], marker='o', linestyle='-')
                    plt.xlabel("Date")
                    plt.ylabel("Lag (hrs)")
                    plt.title(f"Feedback Lag for {selected_student}")
                    plt.grid(True)
                    st.pyplot(plt.gcf())

            if "Score" in student_df.columns:
                prs_data = student_df.dropna(subset=["Score"])
                if not prs_data.empty:
                    st.markdown("#### 📈 PRS Scores Over Time")
                    plt.figure(figsize=(6, 3))
                    plt.plot(prs_data["Date"], prs_data["Score"], marker='s', linestyle='--', color='green')
                    plt.xlabel("Date")
                    plt.ylabel("Score")
                    plt.title(f"PRS Scores for {selected_student}")
                    plt.grid(True)
                    st.pyplot(plt.gcf())

    else:
    
        df['Date'] = pd.to_datetime(df['Date'])

        if "Lag (hrs)" in df.columns:
            st.markdown("### 🧭 Average Feedback Lag Over Time (All Students)")
            lag_df = df.dropna(subset=["Lag (hrs)"])
            if not lag_df.empty:
                lag_avg = lag_df.groupby('Date')['Lag (hrs)'].mean().reset_index()
                plt.figure(figsize=(8, 4))
                plt.plot(lag_avg['Date'], lag_avg['Lag (hrs)'], marker='o')
                plt.xlabel("Date")
                plt.ylabel("Average Lag (hrs)")
                plt.title("Average Feedback Lag Over Time (All Students)")
                plt.grid(True)
                st.pyplot(plt.gcf())

        if "Score" in df.columns:
            st.markdown("### 📈 Average PRS Scores Over Time (All Students)")
            prs_df = df.dropna(subset=["Score"])
            if not prs_df.empty:
                prs_avg = prs_df.groupby('Date')['Score'].mean().reset_index()
                plt.figure(figsize=(8, 4))
                plt.plot(prs_avg['Date'], prs_avg['Score'], marker='s', linestyle='--', color='green')
                plt.xlabel("Date")
                plt.ylabel("Average PRS Score")
                plt.title("Average PRS Score Over Time (All Students)")
                plt.grid(True)
                st.pyplot(plt.gcf())
