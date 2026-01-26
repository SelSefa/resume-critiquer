import streamlit as st
import re

from app.precheck import is_probably_resume
from app.prompts import build_analyze_prompt, build_rewrite_prompt
from app.file_parser import cached_extract_text, FileTooLargeError, MAX_UPLOAD_SIZE_MB
from app.analyzer import analyze_resume

def has_enough_credits(cost: int) -> bool:
    return st.session_state.get("credits", 0) >= cost

def spend_credits(cost: int) -> None:
    st.session_state["credits"] -= cost

PRIMARY_SCORE_RE = re.compile(r"PRIMARY_SCORE\s*:\s*(\d{1,3})", re.IGNORECASE)
STRUCTURE_SCORE_RE = re.compile(r"STRUCTURE_SCORE\s*:\s*(\d{1,3})", re.IGNORECASE)
STRUCTURE_NOTE_RE = re.compile(r"STRUCTURE_NOTE\s*:\s*(.*)", re.IGNORECASE)
PRIMARY_LABEL_RE = re.compile(r"PRIMARY_LABEL\s*:\s*(.*)", re.IGNORECASE)

def parse_analysis_output(text: str) -> dict:
    primary_score = None
    m = PRIMARY_SCORE_RE.search(text or "")
    if m:
        primary_score = int(m.group(1))

    structure_score = None
    m = STRUCTURE_SCORE_RE.search(text or "")
    if m:
        structure_score = int(m.group(1))

    structure_note = None
    m = STRUCTURE_NOTE_RE.search(text or "")
    if m:
        structure_note = m.group(1).strip()

    primary_label = None
    m = PRIMARY_LABEL_RE.search(text or "")
    if m:
        primary_label = m.group(1).strip()

    return {
        "primary_label": primary_label,
        "primary_score": primary_score,
        "structure_score": structure_score,
        "structure_note": structure_note,
    }


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
    
    st.session_state.setdefault("analysis_label", None)
    st.session_state.setdefault("analysis_structure_score", None)
    st.session_state.setdefault("analysis_structure_note", None)

    st.session_state.setdefault("rewrite_preview", None)
    st.session_state.setdefault("rewrite_full", None)

    st.sidebar.header("Credits")
    credits_sidebar_ph = st.sidebar.empty()  # placeholder

    st.title("Resume Critiquer")
    st.markdown("Upload your resume and get AI-powered feedback tailored to your industry and role.")

    st.subheader("Credits")
    credits_main_ph = st.empty() # placeholder

    def render_credits() -> None:
        credits = st.session_state.get("credits", 0)
        credits_sidebar_ph.write(f"Current credits: {credits}")
        credits_main_ph.write(f"Current credits: {credits}")

    render_credits()

    if st.sidebar.button("Buy +10 credits",key="buy_credits_sidebar"):
        st.session_state["credits"] += 10
        st.session_state["purchase_clicks"] += 1
        st.sidebar.success("Credits added: +10")
        render_credits()

    if st.sidebar.button("Watch ad: +1 credit", key="watch_ad_sidebar"):
        st.session_state["credits"] += 1
        st.session_state["ad_clicks"] += 1
        st.sidebar.success("Credits added: +1")
        render_credits()



    col_buy, col_ad = st.columns(2)

    with col_buy:
        if st.button("Buy +10 credits", key="buy_credits_main"):
            st.session_state["credits"] += 10
            st.session_state["purchase_clicks"] += 1
            st.success("Credits added: +10")
            render_credits()

    with col_ad:
        if st.button("Watch ad: +1 credit", key="watch_ad_main"):
            st.session_state["credits"] += 1
            st.session_state["ad_clicks"] += 1
            st.success("Credits added: +1")
            render_credits()

    uploaded_file = st.file_uploader(
    "Upload your resume (PDF or TXT)",
    type=["pdf", "txt"],
    )

    tab_analyze, tab_rewrite = st.tabs(["Analyze", "Rewrite"])

    with tab_analyze:
        st.subheader("Analyze")
        
        job_role_analyze = st.text_input("Target job role (optional)", key="job_role_analyze")
        job_role_clean = (job_role_analyze or "").strip()
        analyze_cost = 2 if job_role_clean else 0
        
        if analyze_cost:
            st.caption("Role based analysis costs 2 credits")

        
        temperature_analyze = st.slider(
            "Analyze temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05,
            key="temperature_analyze",
        )

        analyze_clicked = st.button("Analyze Resume", key="analyze_btn")

        if analyze_clicked:
            if not uploaded_file:
                st.warning("Please upload your resume (PDF or TXT) first.")

            elif analyze_cost and not has_enough_credits(analyze_cost):
                st.error("You don't have enough credits for role-based analysis.")

            else:
                try:
                    file_bytes = uploaded_file.getvalue()
                    resume_text = cached_extract_text(file_bytes, uploaded_file.type)

                    if not resume_text.strip():
                        st.error("File has no readable content.")
                        
                    else:    
                        is_resume, signals = is_probably_resume(resume_text)
                        if not is_resume:
                            st.error("This file doesn't look like a resume/CV. Please upload a resume.")
                        
                        else:

                            prompt = build_analyze_prompt(
                                resume_text=resume_text,
                                job_role=job_role_clean if job_role_clean else None,
                            )

                            if analyze_cost:
                                spend_credits(analyze_cost)
                                render_credits()
                            
                            with st.spinner("Analyzing resume..."):
                                analysis = analyze_resume(prompt, temperature=temperature_analyze)

                            parsed = parse_analysis_output(analysis)

                            st.session_state["analysis_result"] = analysis
                            st.session_state["analysis_score"] = parsed["primary_score"]
                            st.session_state["analysis_label"] = parsed["primary_label"]
                            st.session_state["analysis_structure_score"] = parsed["structure_score"]
                            st.session_state["analysis_structure_note"] = parsed["structure_note"]
                        
                except FileTooLargeError:
                    st.error(
                        f"File too large. Please upload a file smaller than {MAX_UPLOAD_SIZE_MB}MB.")

                except Exception as e:
                    st.error(f"An error occurred: {e}")

        if st.session_state.get("analysis_result"):
            label = st.session_state.get("analysis_label") or "Score"
            score = st.session_state.get("analysis_score")
            
            if score is not None:
                st.metric(f"Primary Score ({label})", f"{score}/100")

            structure_note = st.session_state.get("analysis_structure_note")
            structure_score = st.session_state.get("analysis_structure_score")

            if structure_note:
                if structure_score is not None:
                    st.metric("CV Structure Score", f"{structure_score}/100")
                st.write(structure_note)

            st.markdown("### Analysis Details")
            st.markdown(st.session_state.get("analysis_result", ""))

            st.markdown("### Next step")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Professional Rewrite (2 credits)", key="cta_prof_rewrite"):
                    st.session_state["job_role_rewrite"] = ""
                    st.info("Go to the Rewrite tab and click Rewrite Resume.")

            with col2:
                if st.button("Role-targeted Rewrite (5 credits)", key="cta_role_rewrite"):
                    st.session_state["job_role_rewrite"] = job_role_clean
                    if not job_role_clean:
                        st.warning("Enter a target job role to use Role-targeted Rewrite.")
                    else:
                        st.info("Go to the Rewrite tab and click Rewrite Resume.")



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

        rewrite_clicked = st.button("Rewrite Resume", key="rewrite_btn")

        if rewrite_clicked:
            if not uploaded_file:
                st.warning("Please upload your resume (PDF or TXT) first.")

            else:
                rewrite_cost = 5 if (job_role or "").strip() else 2

                if not has_enough_credits(rewrite_cost):
                    st.error("You don't have enough credits to rewrite a resume.")

                else:
                    try:
                        file_bytes = uploaded_file.getvalue()
                        resume_text = cached_extract_text(file_bytes, uploaded_file.type)

                        if not resume_text.strip():
                            st.error("File has no readable content.")

                        else:
                            is_resume, signals = is_probably_resume(resume_text)
                            if not is_resume:
                                st.error("This file doesn't look like a resume/CV. Please upload a resume.")

                            else:
                                prompt = build_rewrite_prompt(resume_text=resume_text, job_role=job_role)

                                spend_credits(rewrite_cost)
                                render_credits()

                                with st.spinner("Rewriting resume..."):
                                    rewritten = analyze_resume(prompt, temperature=temperature_rewrite)

                                st.session_state["rewrite_full"] = rewritten

                    except FileTooLargeError:
                        st.error(f"File too large. Please upload a file smaller than {MAX_UPLOAD_SIZE_MB}MB.")

                    except Exception as e:
                        st.error(f"An error occurred: {e}")

            
        if st.session_state.get("rewrite_full"):
            st.markdown("### Rewritten Resume")
            st.markdown(st.session_state["rewrite_full"])

    