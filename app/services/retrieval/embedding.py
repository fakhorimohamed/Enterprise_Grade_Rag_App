
from app.services.retrieval.jina_embed import JinaEmbeddingProvider 
from app.services.retrieval.fallback_embed import LocalFallbackProvider 
from app.services.retrieval.configloader import EmbeddingConfig
from app.services.retrieval.embed_provider import EmbeddingProvider 
from app.config import settings 
from pathlib import Path 
import logfire 
from typing import List 

class EmbeddingService:
    def __init__(self, config_path: str | Path):
        self.config = EmbeddingConfig.from_yaml(config_path)
        
        self._jina_provider = JinaEmbeddingProvider(
            config=self.config, 
            api_key=getattr(settings, "JINA_API_KEY", None)
        )
        self._fallback_provider = LocalFallbackProvider(config=self.config)
        self._current_provider: EmbeddingProvider = self._determine_initial_provider()

    def _determine_initial_provider(self) -> EmbeddingProvider:
        if self._jina_provider.is_available():
            return self._jina_provider
        logfire.warning("Jina API unavailable. Using local fallback.")
        return self._fallback_provider

    def _ensure_fallback(self):
        if self._current_provider.name != "local-fallback":
            logfire.error("Switching to local fallback embeddings due to previous failure.")
            self._current_provider = self._fallback_provider

    @property
    def dimension(self) -> int:
        return self._current_provider.dimension

    def embed_texts(self, texts: List[str], task: str = "retrieval.passage") -> List[List[float]]:
        try:
            return self._current_provider.embed_batch(texts, task)
        except Exception as e:
            logfire.error(f"Embedding failed with {self._current_provider.name}: {e}. Triggering fallback.")
            self._ensure_fallback()
            return self._current_provider.embed_batch(texts, task)

    def embed_query(self, query: str) -> List[float]:
        result = self.embed_texts([query], task="retrieval.query")
        return result[0]


# ==============================================================================
# 6. MODULE EXPORTS (Singleton-like usage)
# ==============================================================================
# Initialize once with the path to your YAML file
_embedding_service = EmbeddingService(config_path="app/services/retrieval/config.yml")

def get_embedding_dim() -> int:
    return _embedding_service.dimension

def embed_query(query: str) -> List[float]:
    return _embedding_service.embed_query(query)
def embed_texts(texts: List[str]) -> List[List[float]]:
    return _embedding_service.embed_texts(texts)
