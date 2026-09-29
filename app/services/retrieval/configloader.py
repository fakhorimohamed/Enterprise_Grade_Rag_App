import logfire 
from dataclasses import dataclass
from pathlib import Path 
import yaml 


@dataclass
class JinaConfig:
    url: str
    model: str

@dataclass
class FallbackConfig:
    model: str

@dataclass
class EmbeddingConfig:
    batch_size: int
    embedding_dim: int
    jina: JinaConfig
    fallback: FallbackConfig

    @classmethod
    def from_yaml(cls, yaml_path: str | Path) -> "EmbeddingConfig":
        """Loads and validates the embedding configuration from a YAML file."""
        path = Path(yaml_path)
        if not path.exists():
            logfire.warning(f"Embedding config not found at {path}. Using defaults.")
            return cls._default()

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        emb_data = data.get("embedding", {})
        return cls(
            batch_size=emb_data.get("batch_size", 64),
            embedding_dim=emb_data.get("embedding_dim", 1024),
            jina=JinaConfig(
                url=emb_data.get("jina", {}).get("url", "https://api.jina.ai/v1/embeddings"),
                model=emb_data.get("jina", {}).get("model", "jina-embeddings-v3")
            ),
            fallback=FallbackConfig(
                model=emb_data.get("fallback", {}).get("model", "mixedbread-ai/mxbai-embed-large-v1")
            )
        )

    @classmethod
    def _default(cls) -> "EmbeddingConfig":
        """Fallback defaults if YAML is missing."""
        return cls(
            batch_size=64,
            embedding_dim=1024,
            jina=JinaConfig(url="https://api.jina.ai/v1/embeddings", model="jina-embeddings-v3"),
            fallback=FallbackConfig(model="mixedbread-ai/mxbai-embed-large-v1")
        )
 # __repr__  used for logs
    def __repr__(self) -> str:
        return f"EmbeddingConfig(batch_size={self.batch_size}, dim={self.embedding_dim}, jina={self.jina.model} , fallback={self.fallback.model})"