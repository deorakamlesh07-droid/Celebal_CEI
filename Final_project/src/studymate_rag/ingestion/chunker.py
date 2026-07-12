from dataclasses import dataclass

from studymate_rag.ingestion.loader import LoadedPage


@dataclass(frozen=True)
class TextChunk:
    text: str
    metadata: dict[str, str | int]


class SemanticChunker:
    def __init__(self, chunk_size: int = 900, overlap: int = 140) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be non-negative and smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_pages(self, pages: list[LoadedPage]) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        for page in pages:
            for index, text in enumerate(self._split_text(page.text), start=1):
                chunks.append(
                    TextChunk(
                        text=text,
                        metadata={
                            "document_id": page.document_id,
                            "source": page.source_name,
                            "page": page.page_number,
                            "chunk": index,
                        },
                    )
                )
        return chunks

    def _split_text(self, text: str) -> list[str]:
        words = text.split()
        if not words:
            return []

        chunks: list[str] = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunks.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start = end - self.overlap
        return chunks

