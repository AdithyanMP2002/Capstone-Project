# Deployment Guide - Streamlit Community Cloud

This guide explains how to deploy "THE ROUNDTABLE" for free using Streamlit Community Cloud.

## Prerequisites
1.  A [GitHub](https://github.com/) account.
2.  A [Streamlit Community Cloud](https://streamlit.io/cloud) account (connected to GitHub).

## Step 1: Prepare Repository
1.  Create a new repository on GitHub (e.g., `the-roundtable`).
2.  Push your code to this repository.
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/the-roundtable.git
    git push -u origin main
    ```

## Step 2: Deploy to Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **New app**.
3.  Select your repository (`the-roundtable`), branch (`main`), and main file path (`src/app.py`).
4.  Click **Deploy!**

## Step 3: Configure Secrets
Your app will fail initially because it doesn't have your API keys. You need to add them to Streamlit's "Secrets".

1.  On your app's dashboard in Streamlit Cloud, click **Manage app** (bottom right) -> **...** (three dots) -> **Settings**.
2.  Go to the **Secrets** tab.
3.  Paste the content of your `.env` file, but formatted like TOML (Streamlit uses TOML for secrets).

    **Example:**
    ```toml
    GOOGLE_API_KEY = "AIza..."
    NOTION_TOKEN = "ntn_..."
    # If you have a specific calendar database name
    NOTION_CALENDAR_DATABASE_NAME = "Calendar" 
    ```
4.  Click **Save**.

## Step 4: Reboot
1.  Go back to your app.
2.  If it's still showing an error, click **Manage app** -> **Reboot app**.

## Troubleshooting
- **ModuleNotFoundError**: Ensure `requirements.txt` is in the root directory.
- **Auth Errors**: Double-check your API keys in the Secrets tab.
