from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.configs.config import settings
from typing import Optional,List , Dict , Any
import logfire 
import uuid


class VectorStoreAdapter : 
    
    def __init__(self , qdrant_url: str ,  qdrant_api_key : str , default_collection:str = settings.QDRANT_COLLECTION)  : 
        self.qdrant_client = QdrantClient(url=qdrant_url , 
                                          api_key=qdrant_api_key,
                                          ) 
        self.default_collection = default_collection 
        logfire.info(f"VectorStoreAdapter initialized → {qdrant_url} (default: {default_collection})")

    
    def _get_collection (self , collection_name : Optional[str] = None) ->str :
        """use the provided collection name, or fall back to the default."""
        if not collection_name:
            return self.default_collection 
        return collection_name
    
    def collection_exist (self , collection_name :str) ->bool :
        """Check if the collection already exists in Qdrant."""
        target = self._get_collection(collection_name)
        
        return self.qdrant_client.collection_exists(target)  
    
    def wipe_collection (self ,  collection_name : Optional[str] =None) ->None: 
        target = self._get_collection(collection_name) 
        with logfire.span("Wiping Qdrant Collection", collection=target):
            if self.collection_exist(target) :
                self.qdrant_client.delete_collection(target)
                logfire.info(f"Collection '{target}' deleted.")
            else : 
                logfire.info(f"Collection '{target}' did not exist — nothing to wipe.")
    
    def ensure_collection_exists(self, dim: int, collection_name: Optional[str] = None) -> None:
        target = self._get_collection(collection_name)
        with logfire.span("Ensuring Qdrant Collection Exists", collection=target, dim=dim):
            if not self.collection_exist(target):
                self.qdrant_client.create_collection(
                    collection_name=target,
                    vectors_config=models.VectorParams(
                        size=dim,
                        distance=models.Distance.COSINE,
                    ),
                )
                logfire.info(f"Created collection '{target}' ({dim}-dim, Cosine).")
            else:
                logfire.info(f"Collection '{target}' already exists.")
    
    
    def upsert_chunks(self, chunks: List[Dict[str, Any]],embeddings :list[list[float]] , source:str , source_type:str ,  collection_name: Optional[str] = None) -> None:
        """
        Upsert a list of chunk dictionaries into Qdrant.
        
        Expected chunk format:
        {
            "id": "unique_chunk_id",
            "embedding": [0.1, 0.2, ...],  # List of floats
            "text": "The chunk text content",
            "souce": {"source": "file.pdf"} , 
            "source_type":"PDF" , "TXT" .....
        }
        """
        target = self._get_collection(collection_name)
        
        with logfire.span("Upserting chunks to Qdrant", collection=target, chunk_count=len(chunks)):
            if not chunks:
                logfire.warn("No chunks to upsert.")
                return

            # Transform chunks into Qdrant PointStruct format
            points = [
                models.PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{source}_{chunk[:100]}")), # Fallback ID if missing
                    vector=vector,
                    payload={
                        "text": chunk,
                        "source": source,
                        "source_type": source_type,
                    },
                )
                for chunk , vector in zip(chunks , embeddings)
            ]
            
            # Perform the upsert
            self.qdrant_client.upsert(
                collection_name=target,
                points=points,
                wait=True # Ensure it's written before moving on
            )
            
            logfire.info(f"✅ Successfully upserted {len(points)} chunks to '{target}'")
                
    
    
        
         
    
                
                
                
                
        