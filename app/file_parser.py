import io
import PyPDF2
import streamlit as st

MAX_UPLOAD_SIZE_MB = 5
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

from app.logger import get_logger

log = get_logger()


class FileTooLargeError(ValueError):
    pass

def validate_pdf_size(pdf_bytes: bytes) -> None:
    size = len(pdf_bytes)

    if size > MAX_UPLOAD_SIZE_BYTES:
        log.warning(
            "upload_size_limit_exceeded",
            extra={
                "size_bytes": size,
                "limit_bytes": MAX_UPLOAD_SIZE_BYTES,
                "limit_mb": MAX_UPLOAD_SIZE_MB,
            },
        )
        raise FileTooLargeError(
            f"File too large: {size} bytes (limit {MAX_UPLOAD_SIZE_BYTES} bytes)"
        )

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text

    except Exception:
        log.exception("Failed to extract text from PDF")
        return ""


@st.cache_data(show_spinner=False)
def cached_extract_text(file_bytes: bytes, file_type: str) -> str:
    log.info("cached_extract_text called | type=%s | size_bytes=%d", file_type, len(file_bytes))

    if file_type == "application/pdf":
        validate_pdf_size(file_bytes)
        text = extract_text_from_pdf(file_bytes)
        log.info("PDF text extraction finished | chars=%d", len(text))
        return text


    text = file_bytes.decode("utf-8", errors="ignore")
    log.info("TXT decode finished | chars=%d", len(text))
    return text
