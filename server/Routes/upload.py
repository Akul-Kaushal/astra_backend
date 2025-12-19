from fastapi import APIRouter, UploadFile, File
from server.services.markdown.pdf_reader import extract_text_from_pdf
from server.services.markdown.insurance_to_markdown import insurance_to_markdown
from server.services.markdown.extract_insurance_metadata import extract_insurance_metadata
from server.services.markdown.saving_markdown import save_markdown
from server.services.markdown.chunk_markdown import chunk_markdown
from server.services.markdown.utils import safe_filename
import uuid

router = APIRouter()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    text = extract_text_from_pdf(pdf_bytes)
    metadata= extract_insurance_metadata(text)

    markdown = insurance_to_markdown(
        text, 
        metadata.get("policy_name"),  
        metadata.get("provider"))
    
    filename = safe_filename(str(uuid.uuid4()))

    saved_path = save_markdown(markdown, filename=filename, doc_type=metadata.get("doc_type"))


    return {"extracted_length": len(text), "metadata": metadata, "markdown": markdown, "saved_path": saved_path }
