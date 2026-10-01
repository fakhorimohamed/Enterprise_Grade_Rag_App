from typing import List
import logfire
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
from app.core.embedding.configloader import EmbeddingConfig
from app.core.embedding.embed_provider import EmbeddingProvider
class JinaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, config: EmbeddingConfig, api_key: str):
        self.config = config
        self.api_key = api_key
        self._is_available = self._probe_availability()

    @property
    def name(self) -> str:
        return "jina"

    @property
    def dimension(self) -> int:
        return self.config.embedding_dim

    def _probe_availability(self) -> bool:
        if not self.api_key:
            logfire.info("JINA_API_KEY not set — will use local fallback embeddings.")
            return False 
        
        try:
            response = requests.post(
                self.config.jina.url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.config.jina.model, "task": "retrieval.query", "normalized": True, "input": ["probe"]},
                timeout=10,
            )
            response.raise_for_status()
            if not response.json().get("data"):
                raise RuntimeError("Jina API returned empty data")
            logfire.info("Jina Embeddings API ready.")
            return True
        except Exception as e:
            logfire.warning(f"Jina Embeddings API probe failed: {e}. Will use local fallback.")
            return False

    def is_available(self) -> bool:
        return self._is_available

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
        before_sleep=before_sleep_log(logfire, "warning"),
    )
    def _call_api(self, texts: List[str], task: str) -> List[List[float]]:
        response = requests.post(
            self.config.jina.url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": self.config.jina.model, "task": task, "normalized": True, "input": texts},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("data", [])
        sorted_results = sorted(results, key=lambda x: x.get("index", 0))
        return [item["embedding"] for item in sorted_results]

    def embed_batch(self, texts: List[str], task: str) -> List[List[float]]:
        all_embeddings = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i : i + self.config.batch_size]
            with logfire.span("Embed batch via Jina API", size=len(batch)):
                all_embeddings.extend(self._call_api(batch, task))
        return all_embeddings