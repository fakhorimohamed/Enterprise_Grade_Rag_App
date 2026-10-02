from app.core.qdrant_service import VectorStoreAdapter
from app.ingestion.loaders.load_factory import LoaderFactory
from app.core.qdrant_service import VectorStoreAdapter
from app.ingestion.metadata_stor import LocalMetadataStore
from app.ingestion.loaders.load_factory import LoaderFactory
from app.ingestion.chunking.splitter import chunk_text
from app.core.embedding.embedding import embed_texts, get_embedding_dim
from app.configs.config import settings 
import os
import logfire

class IngestionPipeline:
    """
    Orchestrates the entire ingestion flow.
    
    Dependencies are injected via __init__ — no hardcoded connections.
    """

    def __init__(
        self,
        vector_store: VectorStoreAdapter,
        metadata_store: LocalMetadataStore,
    ):
        self.vector_store = vector_store
        self.metadata_store = metadata_store

    def run(self,base_dir: str,explicit_source_type: str | None = None,wipe: bool = False,) ->None:
        """
        Scan base_dir, map sub-folders to source types, and ingest all documents.
        """
        with logfire.span("Universal Ingestion Started", base_directory=base_dir):
            if wipe:
                self.vector_store.wipe_collection()
            
            dim = get_embedding_dim()
            self.vector_store.ensure_collection_exists(dim)
                
            subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

            if not subdirs:
                source_type = explicit_source_type or self._infer_source_type(base_dir)
                logfire.info(f"No sub-folders — processing '{base_dir}' as '{source_type}'.")
                self._process_directory(base_dir, source_type)
            else:
                for subdir in subdirs:
                    source_type = (
                        self._infer_source_type(subdir)
                        or explicit_source_type
                        or subdir
                    )
                    self._process_directory(os.path.join(base_dir, subdir), source_type)

    def _process_directory(self, dir_path: str, source_type: str):
        """Process every file in a directory."""
        with logfire.span("Scanning Directory", path=dir_path, source=source_type):
            files = [
                f for f in os.listdir(dir_path)
                if os.path.isfile(os.path.join(dir_path, f))
            ]
            logfire.info(f"Found {len(files)} files in {dir_path}.")

            for filename in files:
                self._process_file(
                    os.path.join(dir_path, filename),
                    filename,
                    source_type,
                )

    def _process_file(self, file_path: str, filename: str, source_type: str):
        """Parse → chunk → save metadata → embed → index."""
        with logfire.span("Processing File", file=filename, source=source_type):
            try:
                full_text = self._load_file(file_path, filename)
                if not full_text or not full_text.strip():
                    logfire.warning(f"No text extracted from {filename} — skipping.")
                    return

                chunks = chunk_text(full_text)
                if not chunks:
                    return

                self.metadata_store.save_processed_locally(
                    filename=filename,
                    source_type=source_type,
                    data={
                        "filename": filename,
                        "source_type": source_type,
                        "chunks": chunks,
                    },
                )

                embeddings = embed_texts(chunks)
                self.vector_store.upsert_chunks(
                    chunks=chunks,
                    embeddings=embeddings,
                    source=filename,
                    source_type=source_type,
                )

            except Exception as e:
                logfire.error(f"Failed to process {filename}: {e}")

    def _load_file(self, file_path: str, filename: str) -> str:
        """
        Use the LoaderFactory to find the right loader class,
        then call its .load() class method.
        """
        loader_class = LoaderFactory.get_loader(filename)

        if loader_class is None:
            logfire.warning(f"Skipping unsupported file: {filename}")
            return ""

        with logfire.span("Loading File", loader=loader_class.__name__, file=filename):
            return loader_class.load(file_path)

    @staticmethod
    def _infer_source_type(name: str) -> str:
        """Infer source type from folder/file name."""
        lower = name.lower()
        if "true" in lower:
            return "true"
        if "noisy" in lower:
            return "noisy"
        return "general"
    