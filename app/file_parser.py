import io
import PyPDF2
import streamlit as st


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


@st.cache_data(show_spinner=False)
def cached_extract_text(file_bytes: bytes, file_type: str) -> str:
    if file_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)

    return file_bytes.decode("utf-8", errors="ignore")
