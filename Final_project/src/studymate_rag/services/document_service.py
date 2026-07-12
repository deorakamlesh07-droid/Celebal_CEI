from pathlib import Path
from studymate_rag.core.config import Settings
from studymate_rag.ingestion.chunker import SemanticChunker, TextChunk
from studymate_rag.ingestion.loader import DocumentLoader


class DocumentService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.loader = DocumentLoader()
        self.chunker = SemanticChunker(settings.chunk_size, settings.chunk_overlap)

    def save_upload(self, name: str, content: bytes) -> Path:
        safe_name = Path(name).name
        path = self.settings.upload_dir / safe_name
        path.write_bytes(content)
        return path

    def list_documents(self) -> list[Path]:
        return sorted(
            [path for path in self.settings.upload_dir.iterdir() if path.is_file()],
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )

    def load_and_chunk(self, path: Path) -> list[TextChunk]:
        pages = self.loader.load(path)
        return self.chunker.split_pages(pages)

