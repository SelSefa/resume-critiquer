def build_analyze_prompt(resume_text: str, job_role: str | None) -> str:
    
    target = (job_role or "").strip()
    is_role_mode = bool(target)

    primary_label = "Role match" if is_role_mode else "Professionalism"
    target_line = target if is_role_mode else "N/A"

    prompt = f"""You are an expert resume reviewer.

                Task:
                - If Target role is provided, evaluate how well this resume matches that role.
                - If Target role is not provided, evaluate overall resume professionalism and clarity.

                Output format (no extra text, keep the labels exactly):
                PRIMARY_LABEL: {primary_label}
                PRIMARY_SCORE: <0-100>
                STRUCTURE_NOTE: <1-2 sentences about overall CV structure/clarity>
                STRUCTURE_SCORE: <0-100>   (include only when PRIMARY_LABEL is Role match)

                TOP_ISSUES:
                - <3 bullets>

                QUICK_WINS:
                - <3 bullets>

                REWRITE_RECOMMENDATION: <Professional|Role-targeted>
                REWRITE_REASON: <1 sentence>

                Target role: {target_line}

                Resume content:
                {resume_text}
            """
    return prompt


def build_rewrite_prompt(resume_text: str, job_role: str | None) -> str:
    
    target = (job_role or "").strip()
    target_line = target if target else "general job applications"

    prompt = f"""Rewrite the following resume to be stronger, clearer, and more achievement-focused.
                Target role: {target_line}

                Rules:
                - Keep it truthful: do not invent experience, companies, education, titles, dates, or metrics.
                - Do not add new numbers or achievements that are not explicitly present in the resume text.
                - Improve structure and wording; use concise bullet points.
                - Keep a standard resume structure when possible (Summary, Experience, Projects, Skills, Education).
                - Output in Markdown.

                Resume content:
                {resume_text}
            """
    return prompt
