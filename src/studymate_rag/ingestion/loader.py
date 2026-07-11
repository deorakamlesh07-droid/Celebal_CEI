from dataclasses import dataclass
from pathlib import Path

from studymate_rag.core.exceptions import DocumentIngestionError


@dataclass(frozen=True)
class LoadedPage:
    document_id: str
    source_name: str
    page_number: int
    text: str


class DocumentLoader:
    supported_suffixes = {".pdf", ".txt", ".md"}

    def load(self, path: Path) -> list[LoadedPage]:
        if path.suffix.lower() not in self.supported_suffixes:
            raise DocumentIngestionError(f"Unsupported file type: {path.suffix}")
        if path.suffix.lower() == ".pdf":
            return self._load_pdf(path)
        return self._load_text(path)

    def _load_pdf(self, path: Path) -> list[LoadedPage]:
        try:
            import fitz

            pages: list[LoadedPage] = []
            with fitz.open(path) as pdf:
                for index, page in enumerate(pdf, start=1):
                    text = page.get_text("text").strip()
                    if text:
                        pages.append(
                            LoadedPage(
                                document_id=path.stem,
                                source_name=path.name,
                                page_number=index,
                                text=text,
                            )
                        )
            return pages
        except Exception as exc:
            raise DocumentIngestionError(f"Failed to parse {path.name}") from exc

    def _load_text(self, path: Path) -> list[LoadedPage]:
        try:
            text = path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1").strip()
        return [LoadedPage(document_id=path.stem, source_name=path.name, page_number=1, text=text)] if text else []
