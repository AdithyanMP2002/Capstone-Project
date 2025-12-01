# Quick Start Guide for THE ROUNDTABLE

## You Have: Gemini API Key + Notion Token ✅

You can start using THE ROUNDTABLE **right now** without Google Calendar OAuth! Here's how:

---

## Step 1: Get Your Credentials

### Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Get API Key"** or **"Create API Key"**
3. Copy the key (starts with `AIza...`)

### Notion Integration Token

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Find your integration or create a new one
3. Copy the **Internal Integration Token** (starts with `secret_...`)
4. **IMPORTANT**: Go to your Notion pages and click **Share** → **Invite** → Select your integration

---

## Step 2: Configure THE ROUNDTABLE

Run these commands:

```bash
cd /home/u1846/.gemini/antigravity/scratch/the-roundtable

# Create .env file from template
cp .env.example .env

# Edit the file
nano .env
```

Replace these two lines:

```env
GOOGLE_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE
NOTION_TOKEN=PASTE_YOUR_NOTION_TOKEN_HERE
```

With your actual keys. For example:

```env
GOOGLE_API_KEY=AIzaSyC_your_actual_key_here
NOTION_TOKEN=secret_your_actual_token_here
```

**Leave the Google Calendar line empty** (or delete it):
```env
GOOGLE_OAUTH_CREDENTIALS=
```

Save and exit (Ctrl+X, then Y, then Enter)

---

## Step 3: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

---

## Step 4: Run THE ROUNDTABLE!

```bash
python main.py
```

You should see:

```
🎭 THE ROUNDTABLE - Your Personal Board of Directors
✅ Notion MCP connected. Tools: ['notion_search', ...]
⚠️  WARNING: GOOGLE_OAUTH_CREDENTIALS not found. Calendar integration will be disabled.
✅ THE ROUNDTABLE is ready!

👤 You: 
```

**This is normal!** The system works perfectly with just Notion integration.

---

## Optional: Add Google Calendar Later

If you want Google Calendar integration later, see [GOOGLE_OAUTH_SETUP.md](file:///home/u1846/.gemini/antigravity/scratch/the-roundtable/GOOGLE_OAUTH_SETUP.md) for instructions.

It takes about 10 minutes to set up (all free) and requires:
1. Creating a Google Cloud Project
2. Enabling Calendar API  
3. Downloading OAuth credentials JSON

---

## What Works Right Now

With just Gemini + Notion:

- ✅ All 4 agents (Chief of Staff, Aria, Marcus, The Chair)
- ✅ Notion data access (search pages, read content)
- ✅ Debate workflow with consensus
- ✅ Persistent conversations (SQLite)
- ✅ Rate limit handling

What you don't have yet:
- ❌ Google Calendar event access

**But**: If you use Notion Calendar (databases with date properties), the Chief of Staff can still access that through the Notion API!

---

## Next Steps

1. **Set up your .env file** with Gemini + Notion credentials
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run**: `python main.py`
4. **Try it**: Ask "Should I schedule a meeting tomorrow?" or any decision-making question

The system will use your Notion workspace as ground-truth data for debates!
