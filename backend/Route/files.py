from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services import pdf_service, notion_service
router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        content = await file.read()
        

        markdown_text = pdf_service.extract_markdown_from_pdf(content)
        
        page_title = "Warehouse"
        page = await notion_service.find_page_by_title(page_title)
        
        if not page:
             raise HTTPException(status_code=404, detail=f"Notion page '{page_title}' not found.")
             
        await notion_service.append_markdown_to_page(page["id"], markdown_text)
        
        return {"message": f"Successfully processed '{file.filename}' and added to '{page_title}'."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
