import os
import asyncio
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not NOTION_API_TOKEN:
    raise RuntimeError("NOTION_API_KEY is missing in .env")

if not DATABASE_ID:
    print("Warning: NOTION_DATABASE_ID is missing in .env")

notion = AsyncClient(auth=NOTION_API_TOKEN)

async def find_page(title: str):
    """
    Finds a page by title using the Notion Search API.
    Returns the first matching page or None.
    """
    print(f"Searching for page: '{title}'...")
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
        
        print(f"Found {len(results)} potential matches.")
        
        for page in results:
            page_id = page.get("id")
            page_title = "Untitled"
            
            try:
                props = page.get("properties", {})
                for key, val in props.items():
                    if val.get("type") == "title":
                        title_list = val.get("title", [])
                        if title_list:
                            page_title = title_list[0].get("plain_text", "")
                        break
            except Exception:
                pass
            
            print(f"Candidate: {page_id} | Title: {page_title}")
            
            if title.lower() in page_title.lower():
                return page
                
        return None

    except Exception as e:
        print(f"Error searching for page: {e}")
        return None

async def main():
    print("=== Notion Page Check Tool ===")
    
    try:
        me = await notion.search(page_size=1)
        print("Notion API connection: OK")
    except Exception as e:
        print(f"Notion API connection: FAILED ({e})")
        return

    test_title = "Warehouse"
    page = await find_page(test_title)
    
    if page:
        print(f"\nSUCCESS: Found page '{test_title}' (ID: {page['id']})")
    else:
        print(f"\nResult: Page '{test_title}' not found.")

if __name__ == "__main__":
    asyncio.run(main())
