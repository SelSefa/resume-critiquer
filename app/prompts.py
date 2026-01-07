def build_resume_prompt(resume_text: str, job_role: str | None) -> str:
    
    prompt = f"""Please analyze this resume and provide constructive feedback. 
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'}
        
        Resume content:
        {resume_text}

        Please provide your analysis in a clear, structured format with specific recommendations."""

    return prompt