import asyncio
import os
from dotenv import load_dotenv
from src.tools import calendar_list_events, calendar_create_event

load_dotenv()

async def verify_calendar():
    print("--- Verifying Notion Calendar ---")
    
    # 1. List Events
    print("\n1. Listing Events (searching for 'Calendar' or 'To-do')...")
    events = await calendar_list_events.ainvoke({"start_time": "", "end_time": ""})
    print(events)
    
    # 2. Create Event (Mock attempt if DB found)
    if "No 'Calendar'" not in str(events):
        print("\n2. Attempting to create a test event...")
        # We use a timestamp for uniqueness
        import time
        res = await calendar_create_event.ainvoke({
            "summary": f"Test Event {int(time.time())}",
            "start_time": "2025-12-01",
            "end_time": "2025-12-01"
        })
        print(res)
    else:
        print("\nSkipping creation test as no DB was found.")

if __name__ == "__main__":
    asyncio.run(verify_calendar())
