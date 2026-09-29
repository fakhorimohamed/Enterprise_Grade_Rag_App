
from app.services.retrieval.configloader import EmbeddingConfig 
from app.services.retrieval.embed_provider import EmbeddingProvider 
from sentence_transformers import SentenceTransformer
import logfire 
from typing import List 

class LocalFallbackProvider(EmbeddingProvider):
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self._model = None  # Lazy loading

    @property
    def name(self) -> str:
        return "local-fallback"

    @property
    def dimension(self) -> int:
        return self.config.embedding_dim

    def _load_model(self):
        if self._model is None:
            logfire.info(f"Loading fallback embedding model ({self.config.fallback.model}).")
            self._model = SentenceTransformer(self.config.fallback.model)

    def embed_batch(self, texts: List[str], task: str) -> List[List[float]]:
        self._load_model()
        all_embeddings = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i : i + self.config.batch_size]
            with logfire.span("Embed batch via fallback model", size=len(batch)):
                embeddings = self._model.encode(batch, show_progress_bar=False)
                all_embeddings.extend(embeddings.tolist())
        return all_embeddings