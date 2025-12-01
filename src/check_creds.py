import os
from dotenv import load_dotenv

load_dotenv()

def check_creds():
    # Notion
    n_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
    if n_key:
        print(f"Notion Token found. Length: {len(n_key)}")
        if n_key.startswith("secret_") or n_key.startswith("ntn_"):
            print("Notion Token format: CORRECT (starts with 'secret_' or 'ntn_')")
        else:
            print(f"Notion Token format: INVALID (starts with '{n_key[:4]}...', expected 'secret_' or 'ntn_')")
    else:
        print("Notion Token: MISSING")

    # Google
    g_project = os.getenv("GOOGLE_CLOUD_PROJECT")
    g_api_key = os.getenv("GOOGLE_API_KEY")
    
    if g_project:
        print(f"Google Cloud Project: {g_project}")
    else:
        print("Google Cloud Project: MISSING")
        
    if g_api_key:
        print("Google API Key: FOUND")
    else:
        print("Google API Key: MISSING")

if __name__ == "__main__":
    check_creds()
