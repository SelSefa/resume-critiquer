import re

CV_KEYWORDS = [
                    "experience", "work experience", "professional experience",
                        "education", "skills", "projects", "certifications",
                                "summary", "profile", "objective",
                                        "linkedin", "github",
                                          "phone", "email",
                ]

NON_CV_HINTS = [
                        "abstract", "introduction", "methodology", "results",
                            "discussion", "references", "bibliography",
                                "table of contents", "figure", 
                                    "chapter","appendix",
                                        "contents",
                ]

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")

def is_probably_resume(text: str) -> tuple[bool, dict]:
    """
    Returns:
    (is_resume, signals)
    """
    t = (text or "").strip()
    if not t:
        return False, {"reason": "empty_text"}
    
    lower = t.lower()
    keyword_hits = sum(1 for k in CV_KEYWORDS if k in lower)
    non_cv_hits = sum(1 for k in NON_CV_HINTS if k in lower)
    has_email = bool(EMAIL_RE.search(t))
    has_phone = bool(PHONE_RE.search(t))
    char_len = len(t)
    
    if char_len < 400:
        return False, {"reason": "too_short", "char_len": char_len}
    
    score = keyword_hits
    if has_email:
        score += 1
    if has_phone:
        score += 1
    score -= non_cv_hits
    
    is_resume = score >= 2
    
    return is_resume, {
        "char_len": char_len,
        "keyword_hits": keyword_hits,
        "non_cv_hits": non_cv_hits,
        "has_email": has_email,
        "has_phone": has_phone,
        "score": score,
    }

            

