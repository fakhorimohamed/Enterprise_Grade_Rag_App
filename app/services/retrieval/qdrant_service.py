import logfire
from qdrant_client import QdrantClient
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

from app.configs.config import settings
from app.core.embedding.embedding import embed_query


class   RetrieveService :
    """
    Service class for performing high-precision searches 
    in the enterprise knowledge base using Qdrant.
    """

    def __init__(self):
        """Initialize the Qdrant Client."""
        self.client = QdrantClient(
            url=settings.QDRANT_CLUSTER_ENDPOINT, 
            api_key=settings.QDRANT_API_KEY
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
        before_sleep=before_sleep_log(logfire, "warning"),
    )
    def _search_enterprise_knowledge(self, query: str, limit: int = 8) -> list[dict]:
        """Internal search method ."""
        query_vector = embed_query(query)

        response = self.client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_vector,
            limit=limit,
            with_payload=True,  
        )

        results = []
        for res in response.points:
            results.append(
                {
                    "content": res.payload.get("text", ""), 
                    "source": res.payload.get("source", "Unknown"), 
                    "score": res.score
                }
            )

        return results

    def search_enterprise_knowledge(self, query: str, limit: int = 8) -> list[dict]:
        """
        Public interface for searching the enterprise knowledge base.
        Retries transient failures and gracefully degrades to an empty 
        result set on persistent failure.
        """
        try:
            return self._search_enterprise_knowledge(query, limit=limit)
        except Exception as e:
            logfire.error(f"❌ Qdrant Search Failed after retries: {e}")
            return []


retrieve_service = RetrieveService()