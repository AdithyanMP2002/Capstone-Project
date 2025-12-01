import os
from dotenv import load_dotenv, find_dotenv

# Explicitly find .env
env_path = find_dotenv()
print(f"Found .env at: {env_path}")

# Load it
loaded = load_dotenv(env_path, override=True)
print(f"load_dotenv returned: {loaded}")

# Check key
key = os.getenv("NOTION_API_KEY")
if key:
    print(f"NOTION_API_KEY found: {key[:5]}...")
else:
    print("NOTION_API_KEY is None")

# Check file content (redacted)
if env_path:
    with open(env_path, "r") as f:
        content = f.read()
        print("\n--- .env content (redacted) ---")
        for line in content.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                print(f"{k}={'*' * len(v)}")
            else:
                print(line)
