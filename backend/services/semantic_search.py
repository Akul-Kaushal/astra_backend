import os
import re
import json
import base64
import pickle
import asyncio
from datetime import datetime
from typing import List, Tuple
from dotenv import load_dotenv
import numpy as np
from notion_client import AsyncClient
from .gemini_embedding import get_gemini_embedding

load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
_EMBEDDING_PATH = os.path.join(os.path.dirname(__file__), "embedding_index.pkl")

if not NOTION_API_TOKEN:
    NOTION_API_TOKEN = None

notion = AsyncClient(auth=NOTION_API_TOKEN) if NOTION_API_TOKEN else None

_MAX_CHARS_PER_RICH_TEXT = 2000
_embedding_index = None


def cos_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(a_norm, b_norm.T)


def _load_local_index():
    if not os.path.exists(_EMBEDDING_PATH):
        return []
    try:
        with open(_EMBEDDING_PATH, "rb") as f:
            return pickle.load(f)
    except Exception:
        return []


async def _search_page_by_title(title: str):
    try:
        resp = await notion.search(query=title, filter={"property": "object", "value": "page"}, page_size=10)
        results = resp.get("results", [])
        for page in results:
            page_title = ""
            props = page.get("properties", {})
            for key, val in props.items():
                if isinstance(val, dict) and val.get("type") == "title":
                    title_list = val.get("title", [])
                    if title_list:
                        page_title = title_list[0].get("plain_text", "")
                    break
            if title.lower() in page_title.lower():
                return page
        if results:
            return results[0]
        return None
    except Exception:
        return None


async def _fetch_children_blocks(page_id: str) -> List[dict]:
    blocks = []
    start_cursor = None
    while True:
        if start_cursor:
            resp = await notion.blocks.children.list(block_id=page_id, start_cursor=start_cursor)
        else:
            resp = await notion.blocks.children.list(block_id=page_id)
        results = resp.get("results", [])
        blocks.extend(results)
        start_cursor = resp.get("next_cursor")
        if not start_cursor:
            break
    return blocks


def _is_base64(s: str) -> bool:
    s = s.strip()
    if len(s) < 80:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9+/=\s]+", s))


async def _fetch_embeddings_from_notion_async() -> List[dict]:
    if not notion:
        return []
    page = await _search_page_by_title("Embeddings")
    if not page:
        return []
    page_id = page.get("id")
    if not page_id:
        return []
    blocks = await _fetch_children_blocks(page_id)
    docs = []
    last_text_snippet = None
    for b in blocks:
        btype = b.get("type")
        if btype == "paragraph":
            rich = b.get("paragraph", {}).get("rich_text", [])
            text = "".join([r.get("plain_text", "") for r in rich]).strip()
            if not text:
                continue
            if "Original text snippet:" in text:
                snippet = text.split("Original text snippet:", 1)[1].strip()
                last_text_snippet = snippet
                continue
            if "Embedding (base64-encoded JSON)" in text:
                # next paragraph likely contains the base64
                continue
            if _is_base64(text):
                try:
                    b64 = "".join(text.split())
                    decoded = base64.b64decode(b64).decode("utf-8")
                    payload = json.loads(decoded)
                    embedding = payload.get("embedding") or payload.get("vector") or []
                    if embedding and isinstance(embedding, list):
                        docs.append({
                            "text": last_text_snippet or "",
                            "embedding": embedding,
                            "source": f"notion-{page_id}"
                        })
                        last_text_snippet = None
                except Exception:
                    continue
            else:
                # plain paragraph not base64 -> might be a snippet
                last_text_snippet = text if len(text) <= 2000 else text[:2000]
        elif btype in ("heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"):
            rich = b.get(btype, {}).get("rich_text", [])
            text = "".join([r.get("plain_text", "") for r in rich]).strip()
            if text:
                last_text_snippet = text
        else:
            continue
    return docs


def _fetch_embeddings_from_notion() -> List[dict]:
    try:
        return asyncio.run(_fetch_embeddings_from_notion_async())
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                task = asyncio.ensure_future(_fetch_embeddings_from_notion_async())
                # can't block; return empty and let user refresh later
                return []
            else:
                return loop.run_until_complete(_fetch_embeddings_from_notion_async())
        except Exception:
            return []


def _build_index():
    global _embedding_index
    if _embedding_index is not None:
        return _embedding_index
    idx = []
    if notion:
        idx = _fetch_embeddings_from_notion()
    if not idx:
        idx = _load_local_index()
    if not isinstance(idx, list):
        idx = []
    _embedding_index = idx
    return _embedding_index


def simple_tokenize(text: str):
    return set(re.findall(r"\b\w+\b", text.lower()))


def find_similar_documents(query: str, top_k: int = 3, min_score: float = 0.6) -> List[Tuple[float, dict]]:
    index = _build_index()
    if not index:
        return []
    q_vec = get_gemini_embedding(query)
    if not q_vec:
        return []
    q_vec = np.array(q_vec).reshape(1, -1)
    if q_vec.shape[1] == 0:
        return []
    q_tokens = simple_tokenize(query)
    matches = []
    for doc in index:
        emb = doc.get("embedding") or doc.get("vector") or []
        if not emb:
            continue
        try:
            d_vec = np.array(emb).reshape(1, -1)
        except Exception:
            continue
        if d_vec.shape[1] != q_vec.shape[1]:
            continue
        score = float(cos_sim(q_vec, d_vec).item())
        doc_tokens = simple_tokenize(doc.get("text", ""))
        shared_words = q_tokens.intersection(doc_tokens)
        if score >= min_score and len(shared_words) >= 2:
            matches.append((score, doc))
    matches.sort(key=lambda x: x[0], reverse=True)
    return matches[:top_k]
