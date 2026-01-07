import streamlit as st

from app.file_parser import extract_text
from app.prompts import build_resume_prompt
from app.analyzer import analyze_resume


def run_app():
    st.set_page_config(
        page_title="Resume Critiquer",
        page_icon="🗓️",
        layout="centered",
    )

    st.title("Resume Critiquer")
    st.markdown(
        "Upload your resume and get AI-powered feedback tailored to your industry and role."
    )

    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or TXT)",
        type=["pdf", "txt"],
    )

    job_role = st.text_input(
        "Enter the job role you are targeting for (optional)"
    )

    analyze_clicked = st.button("Analyze Resume")

    if analyze_clicked and uploaded_file:
        try:
            resume_text = extract_text(uploaded_file)

            if not resume_text.strip():
                st.error("File has no readable content.")
                return

            prompt = build_resume_prompt(
                resume_text=resume_text,
                job_role=job_role or None,
            )

            with st.spinner("Analyzing resume..."):
                analysis = analyze_resume(prompt)

            st.markdown("### Analysis Results")
            st.write(analysis)

        except Exception as e:
            st.error(f"An error occurred: {e}")
