import os
import datetime
from typing import Any, Dict, List, Optional
from langchain_core.tools import tool
from notion_client import Client as NotionClient

# --- Notion Tools (Python Native) ---

def _get_notion_client():
    api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
    if not api_key:
        raise ValueError("NOTION_API_KEY or NOTION_TOKEN not found in environment variables.")
    return NotionClient(auth=api_key)

@tool
async def notion_search(query: str):
    """Search for pages in Notion matching the query."""
    try:
        notion = _get_notion_client()
        response = notion.search(query=query, page_size=5)
        
        results = []
        for result in response.get("results", []):
            title = "Untitled"
            if "properties" in result:
                # Try to find a title property (it varies by database/page type)
                for prop in result["properties"].values():
                    if prop["type"] == "title":
                        title = prop["title"][0]["plain_text"] if prop["title"] else "Untitled"
                        break
            
            results.append(f"ID: {result['id']}, Title: {title}, URL: {result.get('url')}")
            
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Error searching Notion: {str(e)}"

@tool
async def notion_read_page(page_id: str):
    """Read the content of a Notion page by its ID."""
    try:
        notion = _get_notion_client()
        # Fetch page blocks
        blocks = notion.blocks.children.list(block_id=page_id)
        
        content = []
        for block in blocks.get("results", []):
            btype = block["type"]
            if btype in block and "rich_text" in block[btype]:
                text_parts = [t["plain_text"] for t in block[btype]["rich_text"]]
                content.append("".join(text_parts))
        
        return "\n".join(content) if content else "Empty page or unsupported block types."
    except Exception as e:
        return f"Error reading page: {str(e)}"

# --- Notion Calendar Tools ---

@tool
async def calendar_list_events(start_time: str, end_time: str):
    """
    List events from the Notion 'Calendar' or 'Events' database.
    It searches for a database with a likely name and returns items.
    """
    try:
        notion = _get_notion_client()
        
        # 1. Find the database
        # We search for "Calendar" or "Events" or "Task"
        db_name = os.getenv("NOTION_CALENDAR_DATABASE_NAME", "Calendar")
        # Search without filter first, then filter in Python to be safe
        search_res = notion.search(query=db_name)
        
        # Filter for databases only
        databases = [r for r in search_res["results"] if r["object"] == "database"]
        
        if not databases:
            # Fallback 1: Search for "Task" or "To-do"
            search_res = notion.search(query="To-do")
            databases = [r for r in search_res["results"] if r["object"] == "database"]
            
        if not databases:
            # Fallback 2: Specific known DB "Weekly To-do List"
            search_res = notion.search(query="Weekly To-do List")
            databases = [r for r in search_res["results"] if r["object"] == "database"]
            
        if not databases:
            return "No 'Calendar', 'To-do', or 'Weekly To-do List' database found in Notion."
            
        db_id = databases[0]["id"]
        db_title = databases[0]["title"][0]["plain_text"]
        
        # 2. Query the database
        # We just get the last 10 items for now as a "schedule"
        # Filtering by date in Notion API requires knowing the property name (e.g. "Date")
        # We will try to fetch and then parse.
        query_res = notion.databases.query(database_id=db_id, page_size=10)
        
        events = []
        for page in query_res["results"]:
            props = page["properties"]
            title = "Untitled"
            date_str = "No Date"
            
            # Find title
            for key, val in props.items():
                if val["type"] == "title" and val["title"]:
                    title = val["title"][0]["plain_text"]
                elif val["type"] == "date" and val["date"]:
                    date_str = val["date"]["start"]
            
            events.append(f"- {title} ({date_str})")
            
        return f"Events from Notion DB '{db_title}':\n" + "\n".join(events)

    except Exception as e:
        return f"Error fetching Notion calendar: {str(e)}"

@tool
async def calendar_create_event(summary: str, start_time: str, end_time: str, description: str = ""):
    """
    Create a new event in the Notion Calendar database.
    """
    try:
        notion = _get_notion_client()
        
        # 1. Find DB (same logic as above, ideally cached)
        db_name = os.getenv("NOTION_CALENDAR_DATABASE_NAME", "Calendar")
        search_res = notion.search(query=db_name)
        databases = [r for r in search_res["results"] if r["object"] == "database"]
        
        if not databases:
             return "No 'Calendar' database found to create event."
        
        db_id = databases[0]["id"]
        
        # 2. Create Page
        # We assume the title property is named "Name" or "Title" (standard)
        # We assume there is a Date property named "Date"
        new_page = {
            "parent": {"database_id": db_id},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": summary}}]
                },
                "Date": {
                    "date": {"start": start_time}
                }
            }
        }
        
        # Note: This might fail if property names don't match exactly. 
        # A robust implementation would inspect the schema first.
        # For this demo, we try standard names.
        try:
            notion.pages.create(**new_page)
            return f"Created Notion page '{summary}' in database '{db_name}'."
        except Exception as create_err:
            return f"Failed to create page. Ensure DB has properties 'Name' (title) and 'Date' (date). Error: {create_err}"

    except Exception as e:
        return f"Error creating Notion event: {str(e)}"
