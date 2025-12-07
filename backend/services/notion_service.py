import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_KEY")

if not NOTION_API_TOKEN:
    raise RuntimeError("NOTION_API_KEY is missing in .env")

notion = AsyncClient(auth=NOTION_API_TOKEN)

async def find_page_by_title(title: str):
    """
    Finds a page by title using the Notion Search API.
    Returns the first matching page object or None.
    """
    try:
        response = await notion.search(
            query=title,
            filter={
                "property": "object",
                "value": "page"
            },
            page_size=5
        )
        results = response.get("results", [])

        for page in results:
            return page
        return None

    except Exception as e:
        print(f"Error searching for page: {e}")
        return None

async def append_markdown_to_page(page_id: str, markdown_text: str):
    """
    Appends the markdown text to the specified page as children blocks.
    Notion API limits block size (2000 chars). We handle basic splitting.
    """
    blocks = []
    
    paragraphs = markdown_text.split("\n\n")
    
    for p in paragraphs:
        if not p.strip():
            continue
            
        content = p[:2000] 
        
        block = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": content
                        }
                    }
                ]
            }
        }
        blocks.append(block)
        
        if len(blocks) >= 90:
             print(f"DEBUG: Appending batch of {len(blocks)} blocks...")
             await notion.blocks.children.append(block_id=page_id, children=blocks)
             blocks = []

    if blocks:
        print(f"DEBUG: Appending final batch of {len(blocks)} blocks...")
        import json
        print(json.dumps(blocks, indent=2))
        await notion.blocks.children.append(block_id=page_id, children=blocks)


