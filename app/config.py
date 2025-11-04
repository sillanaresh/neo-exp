import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    # API Keys
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    # Admin
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "neo-admin-2024")

    # Pinecone
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "neo-knowledge")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")

    # Models
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    LLM_MODEL = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet")

    # RAG Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 5

settings = Settings()
