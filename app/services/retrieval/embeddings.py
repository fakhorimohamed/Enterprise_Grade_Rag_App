from urllib import response

import logfire
import requests 
from tenacity import before_sleep_log , retry , stop_after_attempt , wait_exponential


from app.config import settings 


BATCH_SIZE = 64
_EMBEDDING_DIM = 1024
_JINA_EMBEDDING_URL = "https://api.jina.ai/v1/embeddings"
_JINA_MODEL = "jina-embeddings-v3"
_FALLBACK_MODEL = "mixedbread-ai/mxbai-embed-large-v1"

_active_model = None 
_model_type : str |None = None 




def _load_fallback() : 
    """Load the local mxbai fallback model."""
    from sentence_transformers import SentenceTransformer 
    
    logfire.info(f"Loading fallback embedding model ({_FALLBACK_MODEL}, {_EMBEDDING_DIM}-dim).")
    return SentenceTransformer(_FALLBACK_MODEL) 


def _proba_jine_api()->bool:  
    """Verify the Jina Embeddings API is reachable with the configured key."""
    if not settings.JINA_API_KEY  :
        logfire.info("JINA_API_KEY not set — will use local fallback embeddings.")
        return False 
    
    try :
        response = requests.post(
            _JINA_EMBEDDING_URL , 
            headers= {
                "Authorization": f"Bearer {settings.JINA_API_KEY}",
                "Content-Type": "application/json", 
                              
            },
            json= {
                "model": _JINA_MODEL,
                "task": "retrieval.query",
                "normalized": True,
                "input": ["probe"],     
            },
            timeout=30 ,
        )
        
        response.raise_for_status() 
        payload = response.json() 
        if not payload.get("data") :
            raise RuntimeError("Jina API returned empty data")
        
        logfire.info("Jina Embeddings API ready (jina-embeddings-v3, 1024-dim).")
        return True             
    except Exception as e :
         logfire.warning(f"Jina Embeddings API probe failed: {e}. Will use local fallback embeddings.")
         return False 
    
def test_jina_api() :
    return _proba_jine_api() 