import os
import time
import json
import base64
import asyncio
from typing import List, Optional
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("[gemini_embedding] ERROR: GEMINI_API_KEY not set in environment.")
    client = None
else:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[gemini_embedding] ERROR creating Gemini client: {e}")
        client = None

_EMBED_MODEL = "models/embedding-001"

def _safe_sleep_backoff(attempt: int):
    time.sleep(min(2 ** attempt, 10))

def get_gemini_embedding(text: str, max_retries: int = 3, truncate_to: int = 3500) -> Optional[List[float]]:
    """
    Returns a list of floats (embedding) on success, or None on failure.
    """
    if not text or not text.strip():
        print("[gemini_embedding] WARN: empty input text for embedding.")
        return None

    if client is None:
        print("[gemini_embedding] WARN: Gemini client not initialized.")
        return None

    truncated = text[:truncate_to]
    attempt = 0
    while attempt < max_retries:
        try:
            resp = client.models.embed_content(model=_EMBED_MODEL, contents=truncated)
            # The SDK response shape may differ by version — inspect resp in debug mode if needed
            embeddings = getattr(resp, "embeddings", None)
            if embeddings and len(embeddings) > 0:
                values = getattr(embeddings[0], "values", None)
                if values and len(values) > 0:
                    return list(values)
                else:
                    print("[gemini_embedding] DEBUG: embeddings[0].values empty.")
            else:
                # try alternative shapes (dict-like)
                try:
                    # if resp is dict-like
                    rdict = resp if isinstance(resp, dict) else getattr(resp, "__dict__", None)
                    if rdict:
                        # try common keys
                        embs = rdict.get("embeddings") if isinstance(rdict, dict) else None
                        if embs and len(embs) > 0:
                            vals = embs[0].get("values") if isinstance(embs[0], dict) else None
                            if vals:
                                return list(vals)
                except Exception:
                    pass

            # nothing valid found in response
            print(f"[gemini_embedding] WARN: empty embed response (attempt {attempt+1}). Response repr: {repr(resp)[:400]}")
        except Exception as e:
            print(f"[gemini_embedding] Exception calling embed API (attempt {attempt+1}): {e}")

        attempt += 1
        _safe_sleep_backoff(attempt)

    print("[gemini_embedding] ERROR: failed to obtain embedding after retries.")
    return None



from notion_client import AsyncClient
from datetime import datetime

NOTION_API_TOKEN = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if NOTION_API_TOKEN:
    notion = AsyncClient(auth=NOTION_API_TOKEN)
else:
    notion = None

_MAX_CHARS_PER_RICH_TEXT = 2000
_MAX_BLOCKS_PER_APPEND = 100

def _chunk_text(text: str, max_size: int):
    start = 0
    n = len(text)
    while start < n:
        end = min(start + max_size, n)
        if end < n:
            split_at = text.rfind("\n", start, end)
            if split_at <= start:
                split_at = text.rfind(" ", start, end)
            if split_at > start:
                end = split_at
        yield text[start:end].strip()
        start = end
        while start < n and text[start].isspace():
            start += 1

async def _append_blocks(page_id: str, blocks: list):
    idx = 0
    n = len(blocks)
    while idx < n:
        batch = blocks[idx: idx + _MAX_BLOCKS_PER_APPEND]
        await notion.blocks.children.append(block_id=page_id, children=batch)
        idx += len(batch)

async def _get_or_create_embeddings_page():
    try:
        resp = await notion.search(query="Embeddings", filter={"property":"object","value":"page"}, page_size=10)
        results = resp.get("results", [])
        for page in results:
            props = page.get("properties", {})
            for k,v in props.items():
                if isinstance(v, dict) and v.get("type") == "title":
                    title_list = v.get("title", [])
                    if title_list and "Embeddings".lower() in title_list[0].get("plain_text","").lower():
                        return page.get("id")

        if DATABASE_ID:
            props = {"Name": {"title": [{"type":"text","text":{"content":"Embeddings"}}]}}
            newp = await notion.pages.create(parent={"database_id":DATABASE_ID}, properties=props)
            return newp.get("id")
        else:
            newp = await notion.pages.create(parent={"type":"page_id","page_id":None}, properties={})
            await notion.blocks.children.append(block_id=newp["id"], children=[{
                "object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":"Embeddings"}}]}}])
            return newp.get("id")
    except Exception as e:
        print(f"[gemini_embedding] Notion page create/search failed: {e}")
        return None

async def _store_embedding_async(text: str):
    embedding = get_gemini_embedding(text)
    if not embedding:
        return False
    page_id = await _get_or_create_embeddings_page()
    if not page_id:
        return False
    ts = datetime.utcnow().isoformat() + "Z"
    snippet = text if len(text)<=500 else text[:500] + "..."
    emb_json = json.dumps({"embedding": embedding}, separators=(",",":"))
    emb_b64 = base64.b64encode(emb_json.encode("utf-8")).decode("utf-8")
    header = f"Embedding — {ts}"
    parts = [f"Original text snippet:\n{snippet}", f"Embedding (base64-encoded JSON):\n{emb_b64}"]
    full_content = "\n\n".join(parts)
    blocks = [{"object":"block","type":"heading_3","heading_3":{"rich_text":[{"type":"text","text":{"content":header}}]}}]
    paragraphs = [p.strip() for p in full_content.split("\n\n") if p.strip()]
    for p in paragraphs:
        for chunk in _chunk_text(p, _MAX_CHARS_PER_RICH_TEXT):
            blocks.append({"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":chunk}}]}})
    blocks.append({"object":"block","type":"divider","divider":{}})
    await _append_blocks(page_id, blocks)
    return True

def store_embedding_to_notion(text: str) -> bool:
    try:
        return asyncio.run(_store_embedding_async(text))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_store_embedding_async(text))
            return True
        else:
            return loop.run_until_complete(_store_embedding_async(text))
