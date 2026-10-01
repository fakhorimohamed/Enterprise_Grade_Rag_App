from app.ingestion.loaders.base import BaseLoader
import logfire

class TextLoader(BaseLoader) :
    
    @classmethod
    def load(cls, file_path: str):
        """
        Parses plain text files.
        """
        with logfire.span("📄 Text Parsing", filename=file_path):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    print (f"lengh of centent  {content}")
                    return content
            except Exception as e:
                print("failed to extract text ")
                logfire.error(f"❌ Text Parse Failed: {e}")
                raise 