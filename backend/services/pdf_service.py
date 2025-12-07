import fitz  

def extract_markdown_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from a PDF file using PyMuPDF and formats it as basic Markdown.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        markdown_text = ""

        for page_num, page in enumerate(doc):
            markdown_text += f"## Page {page_num + 1}\n\n"
            text = page.get_text()
            markdown_text += text + "\n\n"
            
        doc.close()
        return markdown_text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        raise RuntimeError(f"Failed to extract text from PDF: {e}")
