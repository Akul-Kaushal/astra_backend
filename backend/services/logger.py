import os
import asyncio
import threading
from datetime import datetime
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not NOTION_API_TOKEN:
    raise RuntimeError("NOTION_API_KEY is missing in environment")

notion = AsyncClient(auth=NOTION_API_TOKEN)

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
    except:
        return None


async def _create_logs_page(title: str = "Logs"):
    try:
        if DATABASE_ID:
            properties = {
                "Name": {"title": [{"type": "text", "text": {"content": title}}]}
            }
            page = await notion.pages.create(parent={"database_id": DATABASE_ID}, properties=properties)
            return page
        else:
            page = await notion.pages.create(parent={"type": "page_id", "page_id": None}, properties={})
            await notion.blocks.children.append(
                block_id=page["id"],
                children=[
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {"rich_text": [{"type": "text", "text": {"content": title}}]}
                    }
                ]
            )
            return page
    except:
        return None


async def _get_or_create_logs_page():
    page = await _search_page_by_title("Logs")
    if page:
        return page.get("id")
    page = await _create_logs_page("Logs")
    if page:
        return page.get("id")
    return None


async def _append_blocks(page_id: str, blocks: list):
    idx = 0
    n = len(blocks)
    while idx < n:
        batch = blocks[idx: idx + _MAX_BLOCKS_PER_APPEND]
        await notion.blocks.children.append(block_id=page_id, children=batch)
        idx += len(batch)


async def _log_to_notion_async(prompt: str, context: str, output: str, matched_files: list):
    page_id = await _get_or_create_logs_page()
    if not page_id:
        return

    ts = datetime.utcnow().isoformat() + "Z"
    matched_str = ", ".join(matched_files) if matched_files else "None"

    header = f"Log entry — {ts}"
    parts = [
        f"Prompt:\n{prompt}",
        f"Matched files:\n{matched_str}",
        f"Context excerpts:\n{context if context.strip() else 'None'}",
        f"Model output:\n{output if output else 'None'}",
    ]
    full_content = "\n\n".join(parts)

    blocks = []
    blocks.append({
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": header}}]}
    })

    paragraphs = [p.strip() for p in full_content.split("\n\n") if p.strip()]
    for p in paragraphs:
        for chunk in _chunk_text(p, _MAX_CHARS_PER_RICH_TEXT):
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}]
                }
            })

    blocks.append({"object": "block", "type": "divider", "divider": {}})

    await _append_blocks(page_id, blocks)


def _run_async_in_thread(coro):
    try:
        asyncio.run(coro)
    except:
        pass


def log_interaction(prompt: str, context: str, output: str, matched_files: list):
    try:
        asyncio.run(_log_to_notion_async(prompt, context, output, matched_files))
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(_log_to_notion_async(prompt, context, output, matched_files))
            else:
                t = threading.Thread(target=_run_async_in_thread, args=(_log_to_notion_async(prompt, context, output, matched_files),), daemon=True)
                t.start()
        except:
            pass
