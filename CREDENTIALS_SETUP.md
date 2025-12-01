# Credentials Setup Guide

This guide explains how to get the necessary API keys and where to put them.

## 1. Where to Paste Credentials
You need to paste your credentials into a file named `.env` in the root of your project (`/home/u1846/.gemini/antigravity/scratch/the-roundtable/.env`).

1.  **Open the file**: Open `.env`. (If it doesn't exist, copy `.env.template` and rename it to `.env`).
2.  **Edit the variables**: You will see lines like `NOTION_API_KEY=...`. Replace the part after the `=` with your actual key.

---

## 2. Notion API Key (`NOTION_API_KEY`)

### Step A: Create the Integration
1.  Go to [Notion My Integrations](https://www.notion.so/my-integrations).
2.  Click **+ New integration**.
3.  **Name**: Enter "The Roundtable" (or any name).
4.  **Associated workspace**: Select the workspace you want to use.
5.  **Type**: Select "Internal" (unless you are building for public distribution).
6.  Click **Submit**.
7.  **Copy the Secret**: You will see an "Internal Integration Secret" (starts with `secret_...`).
    *   **Paste this** into your `.env` file as `NOTION_API_KEY=secret_...`

### Step B: Connect Pages
*Crucial Step*: The integration cannot see your pages by default. You must explicitly share them.
1.  Open Notion and go to the page (or database) you want the agents to access.
2.  Click the **...** (three dots) menu at the top right of the page.
3.  Scroll down to **Connections** (or "Add connections").
4.  Search for "The Roundtable" (the name you gave your integration).
5.  Select it and confirm.
    *   *Now the agent can read this page and its sub-pages.*

---

## 3. Google Cloud Project (`GOOGLE_CLOUD_PROJECT`)

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Click the project dropdown at the top left (next to the Google Cloud logo).
3.  Click **New Project**.
4.  **Project Name**: Enter "The Roundtable".
5.  Click **Create**.
6.  Wait for the notification that the project is created, then click **Select Project**.
7.  **Copy the Project ID**:
    *   On the Dashboard, look for the "Project info" card.
    *   Copy the **Project ID** (e.g., `the-roundtable-12345`).
    *   *Note: Do not use the Project Name if it differs from the ID.*
    *   **Paste this** into your `.env` file as `GOOGLE_CLOUD_PROJECT=the-roundtable-12345`.

### Enable Vertex AI
1.  In the search bar at the top, type "Vertex AI API".
2.  Select **Vertex AI API** from the Marketplace results.
3.  Click **Enable**.

---

## 4. Google Cloud Location (`GOOGLE_CLOUD_LOCATION`)

This is the region where your AI models will run.
*   **Default**: `us-central1` (Iowa) is a safe default.
*   **Paste this** into your `.env` file as `GOOGLE_CLOUD_LOCATION=us-central1`.
