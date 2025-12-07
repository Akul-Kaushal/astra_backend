import os
import sys
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient

# Add project root to sys.path so we can import 'backend'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock environment variables BEFORE importing app/routes
with patch.dict(os.environ, {
    "GEMINI_API_KEY": "fake_key",
    "NOTION_API_KEY": "fake_notion_key",
    "NOTION_DATABASE_ID": "fake_db_id"
}):
    # Mock services that require external connections or credentials
    sys.modules["backend.services.gemini_api"] = MagicMock()
    sys.modules["backend.services.gemini_embedding"] = MagicMock()
    
    # Notion service functions are async, so we need AsyncMock or similar
    notion_mock = MagicMock()
    notion_mock.find_page_by_title = AsyncMock()
    notion_mock.append_markdown_to_page = AsyncMock()
    sys.modules["backend.services.notion_service"] = notion_mock
    
    # We also need to mock fitz (PyMuPDF) if it's not installed or we want to avoid file parsing
    sys.modules["fitz"] = MagicMock() 
    
    # Import app after mocking
    from main import app
    from backend.services.gemini_api import query_gemini, ask_gemini_about_image
    from backend.services.gemini_embedding import get_gemini_embedding, store_embedding_to_notion
    # Access the methods through the module mock or strictly imported names won't work if we re-assign them on the module 
    # BUT `files.py` imports the module `notion_service`. So modifying attributes on the module mock works.
    from backend.services.notion_service import find_page_by_title, append_markdown_to_page

client = TestClient(app)

def test_root():
    """Test the root endpoint to ensure app is up."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_chat_flow_success():
    """Test POST /chat/{uid} with valid prompt."""
    query_gemini.return_value = '```json\n{"reply": "Hello from Gemini"}\n```'
    
    response = client.post("/chat/test_uid", json={"prompt": "Hello"})
    
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["reply"] == "Hello from Gemini"

def test_image_chat_flow_success():
    """Test POST /chat/image/{uid} with mock image."""
    # Wrap in markdown JSON so parsing logic extracts it correctly
    ask_gemini_about_image.return_value = '```json\n{"reply": "Nice image"}\n```'
    
    # Create dummy image content
    files = {'file': ('test.jpg', b'fake image content', 'image/jpeg')}
    
    # Fix: 'prompt' is a query parameter
    with patch("imghdr.what", return_value="jpeg"):
        response = client.post("/chat/image/test_uid", params={"prompt": "Describe this"}, files=files)
    
    if response.status_code != 200:
        print(f"DEBUG: Image chat failed: {response.json()}")
        
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Nice image"

def test_embedding_flow_success():
    """Test POST /chat/embed/{uid}."""
    # Setup mock (sync because run in to_thread)
    get_gemini_embedding.return_value = [0.1, 0.2, 0.3]
    store_embedding_to_notion.return_value = True
    
    response = client.post("/chat/embed/test_uid", json={"text": "Embed this", "store": True})
    
    assert response.status_code == 200
    data = response.json()
    assert data["embedding"] == [0.1, 0.2, 0.3]
    assert data["stored"] is True

def test_upload_pdf_flow_success():
    """Test POST /upload/ with mocked PDF processing and Notion update."""
    # Configure AsyncMock return values
    find_page_by_title.return_value = {"id": "fake_page_id"}
    append_markdown_to_page.return_value = None
    
    with patch("backend.services.pdf_service.extract_markdown_from_pdf", return_value="# Mock PDF Content"):
        files = {'file': ('doc.pdf', b'%PDF-1.4...', 'application/pdf')}
        response = client.post("/upload/", files=files)
        
        if response.status_code != 200:
            print(f"DEBUG: Upload failed: {response.json()}")
        
        assert response.status_code == 200
        assert "Successfully processed" in response.json()["message"]

def test_upload_pdf_notion_page_not_found():
    """Test POST /upload/ when Notion page is missing."""
    # Configure AsyncMock to return None
    find_page_by_title.return_value = None
    
    with patch("backend.services.pdf_service.extract_markdown_from_pdf", return_value="# Mock PDF Content"):
        files = {'file': ('doc.pdf', b'%PDF-1.4...', 'application/pdf')}
        response = client.post("/upload/", files=files)
        
        if response.status_code != 404:
            print(f"DEBUG: Upload error response: {response.json()}")

        assert response.status_code == 404
        assert "Notion page" in response.json()["detail"]
