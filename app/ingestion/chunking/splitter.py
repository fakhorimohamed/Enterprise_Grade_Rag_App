from typing import List
import logfire

def chunk_text(text: str, chunk_size: int = 1500) -> List[str]:
    """
    Simple paragraph-based chunker with a fallback for oversized paragraphs.
    """
    with logfire.span("Text Chunking", text_length=len(text)):
        if not text.strip():
            return []

        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
                
            # Edge case: If the paragraph itself is larger than chunk_size
            if len(p) > chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # Fallback: split the oversized paragraph by sentences
                sentences = p.replace('. ', '.\n').split('\n')
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) < chunk_size:
                        current_chunk += sentence + " "
                    else:
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + " "
            else:
                # Normal case: paragraph fits
                if len(current_chunk) + len(p) < chunk_size:
                    current_chunk += p + "\n\n"
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = p + "\n\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        valid_chunks = [c for c in chunks if c.strip()]
        logfire.info(f" Generated {len(valid_chunks)} chunks")
        return valid_chunks