import os
import json
from dotenv import load_dotenv

# Smart search for credentials: look locally first, then check parent directory
# to load your corporate neo4j_instance_credentials.env file automatically!
dotenv_files = [
    ".env",
    "../.env",
    "../../.env",
    "neo4j_instance_credentials.env",
    "../neo4j_instance_credentials.env",
    "../../neo4j_instance_credentials.env"
]
for f in dotenv_files:
    if os.path.exists(f):
        load_dotenv(dotenv_path=f)

# --- Neo4j Database Configuration ---
# Map both NEO4J_URI (standard) and NEO4J_URL (used in your credentials file)
NEO4J_URI = os.getenv("NEO4J_URI") or os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
# Default to your active lineage schema 'governancemetadata'
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "governancemetadata")

# --- LLM: pick ONE named provider via LLM_PROVIDER ---
# For corporate deployment, we default LLM_PROVIDER to 'azure'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "azure").strip().lower()
LLM_MODEL = os.getenv("LLM_MODEL", "")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

# Azure OpenAI specific variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "").strip()

# Standard providers fallback keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_PROJECT = os.getenv("GOOGLE_PROJECT", "")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    '["*","http://127.0.0.1:5173","http://localhost:5173"]',
)

