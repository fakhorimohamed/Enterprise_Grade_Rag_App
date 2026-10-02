from re import S

from pydantic import Field , AliasChoices
from pydantic_settings import BaseSettings  , SettingsConfigDict

class Settings (BaseSettings) :
    
    """
    Load and validate environment variables from `.env`.

    - `extra="ignore"` lets `.env` keep legacy keys (`POSTGRES_URI`, `REDIS_URL`,
    old Groq keys, etc.) without failing startup.
    - Required fields raise a clear validation error at import time if missing.
    
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    #-------------------JINA API KEY (embeddings + reranker) -----------#
    JINA_API_KEY : str 
    #---------------QROQ API key ---------------####
    
    GROQ_API_KEY :str 
    GROQ_FALLBACK_API_KEY : str 
    
    #---------------Gemini API-Key ------------#
    GEMINI_API_KEY :str 
    
    # --- QDRANT VECTOR DB ---
    QDRANT_CLUSTER_ENDPOINT: str = Field(validation_alias=AliasChoices("QDRANT_URL", "QDRANT_CLUSTER_ENDPOINT"))
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "enterprise_rag"

    # --- OBSERVABILITY ---
    
    LOGFIRE_TOKEN: str | None = None
    LOGFIRE_BASE_URL: str | None = None

# Singleton used across the app.
settings = Settings()