import logfire
from typing import Type

from app.ingestion.loaders.base import BaseLoader
from app.ingestion.loaders.pdf import PdfLoader
from app.ingestion.loaders.html import HtmlLoader
from app.ingestion.loaders.text import TextLoader
from app.ingestion.loaders.office import OfficeLoader


class LoaderFactory:
    """
    Maps file extensions to the correct loader class.
    
    The pipeline asks: "Give me the right loader for this file."
    The factory answers with the correct class.
    """

    _LOADERS: dict[str, Type[BaseLoader]] = {
        "pdf": PdfLoader,
        "html": HtmlLoader,
        "txt": TextLoader,
        "docx": OfficeLoader,
        "pptx": OfficeLoader,
    }

    @classmethod
    def get_loader(cls, filename: str) -> Type[BaseLoader] | None:
        """
        Return the loader class for the given filename.
        """
        ext = filename.lower().rsplit(".", 1)[-1]
        loader_class = cls._LOADERS.get(ext)

        if loader_class is None:
            logfire.warning(f"No loader registered for extension: .{ext} ({filename})")
        
        return loader_class

    @classmethod
    def supported_extensions(cls) -> list[str]:
        """Return all used  file extensions."""
        return list(cls._LOADERS.keys())