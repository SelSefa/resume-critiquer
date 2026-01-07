import io
import PyPDF2

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text

def extract_text(uploaded_file) -> str:
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file.read())

    return uploaded_file.read().decode("utf-8")
