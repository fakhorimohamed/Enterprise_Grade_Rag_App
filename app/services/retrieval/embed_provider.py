from abc import ABC , abstractmethod
from typing import List 


class EmbeddingProvider(ABC):
    """Abstract interface for any embedding provider."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str], task: str) -> List[List[float]]:
        pass