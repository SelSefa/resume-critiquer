import streamlit as st

from app.file_parser import cached_extract_text, FileTooLargeError, MAX_UPLOAD_SIZE_MB
from app.prompts import build_resume_prompt
from app.analyzer import analyze_resume

def run_app():
    st.set_page_config(
        page_title="Resume Critiquer",
        page_icon="🗓️",
        layout="centered",
    )

    st.session_state.setdefault("credits", 0)
    st.session_state.setdefault("purchase_clicks", 0)
    st.session_state.setdefault("ad_clicks", 0)

    st.session_state.setdefault("analysis_purchased", False)
    st.session_state.setdefault("rewrite_purchased", False)

    st.session_state.setdefault("analysis_result", None)
    st.session_state.setdefault("analysis_score", None)

    st.session_state.setdefault("rewrite_preview", None)
    st.session_state.setdefault("rewrite_full", None)

    st.sidebar.header("Credits")
    st.sidebar.write(f"Current credits: {st.session_state['credits']}")

    if st.sidebar.button("Buy +10 credits",key="buy_credits_sidebar"):
        st.session_state["credits"] += 10
        st.session_state["purchase_clicks"] += 1
        st.sidebar.success("Credits added: +10")

    if st.sidebar.button("Watch ad: +1 credit", key="watch_ad_sidebar"):
        st.session_state["credits"] += 1
        st.session_state["ad_clicks"] += 1
        st.sidebar.success("Credits added: +1")


    st.title("Resume Critiquer")
    st.markdown(
        "Upload your resume and get AI-powered feedback tailored to your industry and role."
    )
    
    st.subheader("Credits")
    st.write(f"Current credits: {st.session_state['credits']}")

    col_buy, col_ad = st.columns(2)

    with col_buy:
        if st.button("Buy +10 credits", key="buy_credits_main"):
            st.session_state["credits"] += 10
            st.session_state["purchase_clicks"] += 1
            st.success("Credits added: +10")

    with col_ad:
        if st.button("Watch ad: +1 credit", key="watch_ad_main"):
            st.session_state["credits"] += 1
            st.session_state["ad_clicks"] += 1
            st.success("Credits added: +1")

    uploaded_file = st.file_uploader(
    "Upload your resume (PDF or TXT)",
    type=["pdf", "txt"],
    )

    tab_analyze, tab_rewrite = st.tabs(["Analyze", "Rewrite"])

    with tab_analyze:
        st.subheader("Analyze")
        temperature_analyze = st.slider(
            "Analyze temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05,
            key="temperature_analyze",
        )

        analyze_clicked = st.button("Analyze Resume", key="analyze_btn")

        if analyze_clicked and uploaded_file:
            try:
                file_bytes = uploaded_file.getvalue()
                resume_text = cached_extract_text(file_bytes, uploaded_file.type)

                if not resume_text.strip():
                    st.error("File has no readable content.")
                    st.stop()

                prompt = build_resume_prompt(
                    resume_text=resume_text,
                    job_role=None,
                )

                with st.spinner("Analyzing resume..."):
                    analysis = analyze_resume(prompt, temperature=temperature_analyze)

                st.session_state["analysis_result"] = analysis

            except FileTooLargeError:
                st.error(
                    f"File too large. Please upload a file smaller than {MAX_UPLOAD_SIZE_MB}MB."
                )
                st.stop()

            except Exception as e:
                st.error(f"An error occurred: {e}")

        if st.session_state.get("analysis_result"):
            st.markdown("### Analysis Results")
            st.write(st.session_state["analysis_result"])

    with tab_rewrite:
        st.subheader("Rewrite")
        job_role = st.text_input("Target job role (optional)", key="job_role_rewrite")
        temperature_rewrite = st.slider(
            "Rewrite temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.05,
            key="temperature_rewrite",
        )

