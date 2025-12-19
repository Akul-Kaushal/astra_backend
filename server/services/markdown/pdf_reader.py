import fitz
from io import BytesIO

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page in document:
        text = page.get_text()
        if text.strip():
            pages.append(text)
    return "\n".join(pages)    