from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import tempfile
import imghdr
import asyncio

from backend.services.gemini_api import query_gemini, ask_gemini_about_image
from backend.services.gemini_embedding import get_gemini_embedding, store_embedding_to_notion

router = APIRouter()

ALLOWED_EXTENSIONS = {"png", "jpeg", "jpg"}
MAX_IMAGE_BYTES = 6 * 1024 * 1024  # 6 MB, change as needed


class TextRequest(BaseModel):
    prompt: str
    store_embedding: Optional[bool] = False


class EmbedRequest(BaseModel):
    text: str
    store: Optional[bool] = True


@router.post("/{uid}")
async def chat(uid: str, request: TextRequest) -> dict:
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="`prompt` must be a non-empty string")

    try:
        # run the sync query_gemini in a thread so the event loop is not blocked
        response = await asyncio.to_thread(query_gemini, request.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM query failed: {e}")

    cleaned = (response or "").strip()
    parsed = {}

    if cleaned.startswith("```json"):
        cleaned_body = cleaned.replace("```json", "").replace("```", "").strip()
        try:
            parsed = json.loads(cleaned_body)
        except Exception:
            parsed = {"reply": cleaned_body}
    else:
        parsed = {"reply": cleaned}

    reply_text = (parsed.get("summary") or "") + ("\n" + parsed.get("justification") if parsed.get("justification") else "")
    return {
        "reply": reply_text.strip() or parsed.get("reply", ""),
        "summary": parsed.get("summary"),
        "justification": parsed.get("justification"),
        "raw": parsed
    }


@router.post("/image/{uid}")
async def chat_image(uid: str, prompt: str, file: UploadFile = File(...)) -> dict:
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    ext = os.path.splitext(file.filename)[1].lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large (max {MAX_IMAGE_BYTES} bytes)")

    tmp_path = None
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
        tmp_path = tmp.name
        tmp.write(contents)
        tmp.close()

        detected = imghdr.what(tmp_path)
        if detected not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

        # run the sync vision call in a thread
        try:
            response = await asyncio.to_thread(ask_gemini_about_image, tmp_path, prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Vision API failed: {e}")

        cleaned = (response or "").strip()
        parsed = {}
        if cleaned.startswith("```json"):
            cleaned_body = cleaned.replace("```json", "").replace("```", "").strip()
            try:
                parsed = json.loads(cleaned_body)
            except Exception:
                parsed = {"reply": cleaned_body}
        else:
            parsed = {"reply": cleaned}

        # prefer explicit reply fields used by your vision schema
        reply_text = parsed.get("reply") or parsed.get("task_recommendation") or parsed.get("summary") or ""
        parsed["reply"] = reply_text
        return parsed

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


@router.post("/embed/{uid}")
async def chat_embedding(uid: str, request: EmbedRequest) -> dict:
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="`text` must be a non-empty string")

    try:
        embedding = await asyncio.to_thread(get_gemini_embedding, request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {e}")

    if not embedding:
        return {"embedding": [], "stored": False, "message": "Failed to generate embedding"}

    stored = False
    if request.store:
        try:
            stored = await asyncio.to_thread(store_embedding_to_notion, request.text)
        except Exception:
            stored = False

    return {
        "embedding": embedding,
        "stored": bool(stored),
        "message": "Embedding generated and stored in Notion" if stored else "Embedding generated"
    }
