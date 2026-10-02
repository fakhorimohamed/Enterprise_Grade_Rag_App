# app/ingestion/metadata_store.py
import os
import json
import shutil 
import logfire

class LocalMetadataStore:
    """
    Handles saving parsed/processed metadata as JSON files on disk.
    """
    
    def __init__(self, base_dir: str = "processed_data", wipe: bool = False):
        self.base_dir = base_dir
        
        #Check if base_dir exists and remove it if wipe=True
        if wipe and os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
            logfire.info(f" Wiped existing metadata directory: {self.base_dir}")
    
    def save_processed_locally(self, filename: str, source_type: str, data: dict) -> str:
        """
        Save processed metadata as JSON in processed_data/<source_type>/.
                """
        with logfire.span("Saving Metadata Locally", filename=filename, source_type=source_type):
            
            folder = os.path.join(self.base_dir, source_type)
            os.makedirs(folder, exist_ok=True)
            
            dest = os.path.join(folder, f"{filename}.json")
            with open(dest, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logfire.info(f"Saved processed data → {dest}")
            return dest