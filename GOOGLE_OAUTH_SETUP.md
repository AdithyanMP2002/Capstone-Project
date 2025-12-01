# How to Get Google OAuth Credentials for Calendar

## Quick Setup (5-10 minutes)

### Step 1: Create Google Cloud Project (FREE)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: `THE-ROUNDTABLE`
4. Click **"Create"**

### Step 2: Enable Google Calendar API

1. In Google Cloud Console, make sure your new project is selected
2. Go to **"APIs & Services"** → **"Library"** (left sidebar)
3. Search for: `Google Calendar API`
4. Click on it, then click **"Enable"**

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Choose **"External"** (unless you have a Google Workspace)
3. Click **"Create"**
4. Fill in:
   - App name: `THE ROUNDTABLE`
   - User support email: Your email
   - Developer contact: Your email
5. Click **"Save and Continue"**
6. **Scopes**: Click **"Add or Remove Scopes"**
   - Search for `calendar`
   - Check: `https://www.googleapis.com/auth/calendar.readonly`
   - Click **"Update"** → **"Save and Continue"**
7. **Test users**: Click **"Add Users"**
   - Enter your Gmail address
   - Click **"Add"** → **"Save and Continue"**
8. Click **"Back to Dashboard"**

### Step 4: Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**
4. Application type: **"Desktop app"**
5. Name: `THE ROUNDTABLE Desktop`
6. Click **"Create"**
7. A popup appears with your credentials
8. Click **"Download JSON"**
9. Save the file as `google-oauth.json` in a safe location

### Step 5: Update .env File

```env
GOOGLE_OAUTH_CREDENTIALS=/full/path/to/google-oauth.json
```

### Step 6: Authenticate

Run this BEFORE starting the Python script:

```bash
export GOOGLE_OAUTH_CREDENTIALS=/full/path/to/google-oauth.json
npx -y @cocal/google-calendar-mcp auth
```

A browser will open - sign in and grant calendar access.

---

**Cost**: ✅ **100% FREE** - Google Calendar API is free for personal use

**Time**: ~5-10 minutes for first-time setup

**Note**: If you see "App not verified" warning during sign-in, click "Advanced" → "Go to THE ROUNDTABLE (unsafe)" - this is normal for personal projects.
