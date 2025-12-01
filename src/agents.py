import os
from langchain_google_vertexai import ChatVertexAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.system_instructions import VISIONARY_INSTRUCTION, SKEPTIC_INSTRUCTION, CHAIRPERSON_INSTRUCTION
from src.tools import notion_search, notion_read_page, calendar_list_events, calendar_create_event

# Initialize Models
# Check if we have Vertex AI config or just API Key
# Initialize Models
# Check if we have Vertex AI config or just API Key
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    print("Using Google Gemini API Models (via API Key)")
    llm_pro = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, google_api_key=api_key)
    llm_flash = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, google_api_key=api_key)
elif project_id:
    print(f"Using Vertex AI Models (Project: {project_id}, Location: {location})")
    llm_pro = ChatVertexAI(
        model_name="gemini-1.5-pro-001", 
        temperature=0.7,
        project=project_id,
        location=location
    )
    llm_flash = ChatVertexAI(
        model_name="gemini-1.5-flash-001", 
        temperature=0.3,
        project=project_id,
        location=location
    )
else:
    raise ValueError("No Google Cloud Project or API Key found. Please configure .env.")

def get_visionary_agent():
    prompt = ChatPromptTemplate.from_messages([
        ("system", VISIONARY_INSTRUCTION),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return prompt | llm_pro

def get_skeptic_agent():
    prompt = ChatPromptTemplate.from_messages([
        ("system", SKEPTIC_INSTRUCTION),
        MessagesPlaceholder(variable_name="messages"),
    ])
    # Bind tools to Skeptic
    tools = [notion_search, notion_read_page, calendar_list_events, calendar_create_event]
    return prompt | llm_flash.bind_tools(tools)

def get_chair_agent():
    prompt = ChatPromptTemplate.from_messages([
        ("system", CHAIRPERSON_INSTRUCTION),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return prompt | llm_pro
