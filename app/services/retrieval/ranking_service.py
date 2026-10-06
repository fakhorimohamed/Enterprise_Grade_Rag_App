import time
import logfire
import requests
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

from app.configs.config import settings


class RerankService:
    """Service for semantically reranking documents using the Jina Reranker API."""

    def __init__(self):
        self.session = requests.Session()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
        before_sleep=before_sleep_log(logfire, "warning"),
    )
    def _rank_with_retry(self, query: str, documents: list[str], top_n: int) -> list[str]:
        """Core Jina API ranking logic configured with retry on transient failures."""
        response = self.session.post(
            settings.JINA_RERANK_URL,
            headers={
                "Authorization": f"Bearer {settings.JINA_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.JINA_RERANK_MODEL,
                "query": query,
                "documents": documents,
                "top_n": top_n,
                "return_documents": True,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()

        results = payload.get("results", [])
        reranked_docs = []
        
        for res in results[:top_n]:
            doc_text = res.get("document")
            if doc_text is None:
                # Fallback to original index if document text is missing
                index = res.get("index")
                if index is not None and 0 <= index < len(documents):
                    doc_text = documents[index]
            
            if doc_text is not None:
                reranked_docs.append(doc_text)

        return reranked_docs

    def rank(self, query: str, documents: list[str], top_n: int = 5) -> list[str]:
        """
        Public interface for reranking. 
        Refines retrieval results by re-scoring documents against the query semantically.
        Retries transient failures (via _rank_with_retry) and falls back to the original 
        order if reranking ultimately fails, ensuring the user still receives an answer.
        """
        if not documents:
            return []

        if not getattr(settings, "JINA_API_KEY", None):
            logfire.warning("⚠️ JINA_API_KEY not set — skipping reranking.")
            return documents[:top_n]

        start_time = time.time()
        logfire.info(f"📡 [Reranker] Sending {len(documents)} docs to Jina Reranker API...")

        try:
            reranked_docs = self._rank_with_retry(query, documents, top_n)
            duration = time.time() - start_time
            logfire.info(f"✅ [Reranker] Done in {duration:.2f}s.")
            return reranked_docs
        except Exception as e:
            logfire.error(f"❌ [Reranker] Semantic Reranking Failed after retries: {e}")
            # Fallback to the original order to ensure the user still gets an answer
            return documents[:top_n]

rerank_service = RerankService()