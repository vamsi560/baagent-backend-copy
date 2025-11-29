# config.py
# Configuration settings for the BA Agent

import os
from dotenv import load_dotenv, find_dotenv
from docx import Document as DocxDocument

# Load environment variables (handle potential Windows BOM/UTF-16 encodings)
try:
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        try:
            # utf-8-sig gracefully handles UTF-8 with BOM on Windows
            load_dotenv(dotenv_path=dotenv_path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            # Fallback for files saved with UTF-16 BOM (common on Windows Notepad)
            load_dotenv(dotenv_path=dotenv_path, encoding="utf-16")
    else:
        load_dotenv()
except Exception as env_exc:
    print(f"WARNING: Failed to load .env file: {env_exc}")


# Database Configuration
DATABASE_URL = 'postgresql+psycopg2://bauser:Valuemomentum123@baagent.postgres.database.azure.com:5432/ba_agent'

# Qdrant Vector Database Configuration
QDRANT_ENABLED = True
QDRANT_HOST = 'localhost'
QDRANT_PORT = 6333

# Azure Configuration
ACS_CONNECTION_STRING = 'endpoint=https://baagentacs123.india.communication.azure.com/;accesskey=3NFm6rs3wKyuP2B5BljzjkjGlWUC7SXWIilVOiHlF0jlpJQ8PiQ6JQQJ99BIACULyCpAhliiAAAAAZCSEmoo'
ACS_SENDER_ADDRESS = 'DoNotReply@0a996688-51d4-48e5-a65c-ad35a83a9c77.azurecomm.net'
APPROVAL_RECIPIENT_EMAIL = 'Raghavendra.Lakkamaraju@valuemomentum.com'
BACKEND_BASE_URL = 'http://127.0.0.1:5000'
ADO_ORGANIZATION_URL = 'https://dev.azure.com/prayankagochipatula/'
ADO_PROJECT_NAME = 'Backstage'
# Azure DevOps Personal Access Token - Updated with new token
ADO_PAT = 'DHDzeRhCouK9QI5q2q0cgu7OJpwKU7bJzkwvq2HxZhOquS4qkdxUJQQJ99BIACAAAAAAhliiAAASAZDO39lF'

# Gemini API Key
GEMINI_API_KEY = 'AIzaSyA5_KnR58T2MTG4oOvBeAqbd8idJCdOlRA'
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Debug: Print the API key being used (first few characters)
print(f"DEBUG: Using Gemini API key: {GEMINI_API_KEY[:20]}...") 

# OneDrive Integration Configuration
ONEDRIVE_ENABLED = True
ONEDRIVE_CLIENT_ID = '545e5a9b-421b-493b-a4f2-5c6f7af44b86'
ONEDRIVE_CLIENT_SECRET = 'vY38Q~4TweP9tH5cPoBcEHuTY0thvwWKicYP5bLZ'
ONEDRIVE_TENANT_ID = 'common'
ONEDRIVE_REDIRECT_URI = 'http://localhost:3000/auth/callback'
ONEDRIVE_AUTHORITY = 'https://login.microsoftonline.com/common'
ONEDRIVE_SCOPE = 'https://graph.microsoft.com/.default'

# Lucid Integration
LUCID_ENABLED = False
LUCID_API_KEY = ''
LUCID_TEAM_ID = ''
LUCID_BASE_URL = 'https://api.lucid.co'