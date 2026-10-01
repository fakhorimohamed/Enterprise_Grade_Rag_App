from  app.ingestion.processor import IngestionPipeline 
from app.core.qdrant_service import VectorStoreAdapter 
from app.ingestion.metadata_stor import LocalMetadataStore
from app.configs.config import settings 
import argparse
import logfire 
import os
import sys 

_logfire_base_url = settings.LOGFIRE_BASE_URL
if not _logfire_base_url and settings.LOGFIRE_TOKEN:
    if settings.LOGFIRE_TOKEN.startswith("pylf_v2_eu_"):
        _logfire_base_url = "https://logfire-eu.pydantic.dev"

if settings.LOGFIRE_TOKEN:
    logfire.configure(
        token=settings.LOGFIRE_TOKEN,
        service_name="enterprise-ingestion-service",
        advanced=logfire.AdvancedOptions(base_url=_logfire_base_url) if _logfire_base_url else None,
    )
    
def main () :
    parser = argparse.ArgumentParser(
        prog="python -m app.ingestion.processor",
        description="Universal data ingestion processor."
        
    )
    
    parser.add_argument("target_dir" , nargs="?" , default="DATA" , help="Target directory to process (default: DATA)" )
    parser.add_argument("explicit_type" ,  nargs="?" , default=None ,help="Force a specific source type (e.g., 'true')" )
    parser.add_argument("--wipe" , action="store_true" ,help="Wipe existing data before ingestion")
    
    #parse the arguments 
    args = parser.parse_args()
    
    # ─ 4. Validate Input ────────────────────────────────────────
    if not os.path.exists(args.target_dir):
        print(f"Error: path '{args.target_dir}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(args.target_dir):
        print(f"Error: path '{args.target_dir}' is not a directory.")
        sys.exit(1)
    
    with logfire.span(" Universal Data Ingestion",target_dir =args.target_dir ,explicit_type=args.explicit_type ,wipe=args.wipe ) :
        vector_store = VectorStoreAdapter(settings.QDRANT_URL , settings.QDRANT_API_KEY , settings.QDRANT_COLLECTION)
        local_store = LocalMetadataStore(base_dir=args.target_dir)
        
        #Create IngestionPipeline instance 
        pipeline = IngestionPipeline(vector_store , local_store)

        pipeline.run(
            base_dir=args.target_dir,
            explicit_source_type=args.explicit_type,
            wipe=args.wipe
        )
        
        logfire.info("✅ Ingestion job completed successfully.")

        
if __name__ == "__main__":
    main() 