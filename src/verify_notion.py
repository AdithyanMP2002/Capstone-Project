import asyncio
import os
from dotenv import load_dotenv
from src.tools import notion_search

# Load environment variables from .env
load_dotenv()

async def verify():
    print(f"Checking Notion API Key presence: {'Yes' if os.getenv('NOTION_API_KEY') else 'No'}")
    
    print("Attempting to search for 'Reading List'...")
    try:
        # The tool expects a string query
        result = await notion_search.ainvoke({"query": "Reading List"})
        print("\n--- Search Result ---")
        print(result)
        print("\n--- End Result ---")
        
        if "Reading List" in str(result):
            print("\nSUCCESS: Found 'Reading List' in Notion.")
        else:
            print("\nWARNING: 'Reading List' not explicitly found in the top results. Check if the page is shared.")
            
    except Exception as e:
        print(f"\nERROR: Failed to connect or search. Details: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
