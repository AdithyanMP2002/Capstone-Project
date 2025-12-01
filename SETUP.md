# THE ROUNDTABLE - Setup Guide

## Prerequisites
- Python 3.10+
- Google Cloud Platform Account
- Notion Account (for MCP)
- Google Calendar Account (for MCP)

## 1. Environment Setup

### Google Cloud
1.  Create a Google Cloud Project.
2.  Enable the **Vertex AI API**.
3.  Install the `gcloud` CLI and authenticate:
    ```bash
    gcloud auth application-default login
    ```

### MCP Servers
This project uses the Model Context Protocol (MCP) to connect to Notion and Google Calendar. You need to run these servers locally or have them accessible.

#### Notion MCP
1.  Get your Notion Integration Token.
2.  Run the Notion MCP server (example using `uv` or `npx`):
    ```bash
    npx -y @modelcontextprotocol/server-notion
    ```
    *Note: You'll need to set `NOTION_API_KEY` environment variable for the server.*

#### Google Calendar MCP
1.  Run the Google Calendar MCP server:
    ```bash
    npx -y @modelcontextprotocol/server-google-calendar
    ```
    *Note: Follow the authentication flow provided by the server.*

## 2. Project Configuration
1.  Copy `.env.template` to `.env`:
    ```bash
    cp .env.template .env
    ```
2.  Edit `.env` and fill in your details:
    - `GOOGLE_CLOUD_PROJECT`: Your GCP Project ID.
    - `GOOGLE_CLOUD_LOCATION`: e.g., `us-central1`.
    - MCP Server configurations if they are running on specific ports/URLs (default assumes stdio or specific setup).

## 3. Installation
```bash
pip install -r requirements.txt
```

## 4. Running the Application
```bash
streamlit run src/app.py
```
