from dataclasses import dataclass
from pathlib import Path
from studymate_rag.core.config import Settings
from studymate_rag.core.exceptions import RetrievalError
from studymate_rag.embeddings.factory import build_embedding_model
from studymate_rag.llm.providers import build_llm
from studymate_rag.retrieval.vector_store import ChromaIndex
from studymate_rag.services.document_service import DocumentService


@dataclass(frozen=True)
class Citation:
    source: str
    page: int | str
    chunk: int | str


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    citations: list[Citation]
    confidence: str


class RagService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.documents = DocumentService(settings)
        self.embed_model = build_embedding_model(settings)
        self.llm = build_llm(settings)
        self.index = ChromaIndex(settings.vector_db_path)

    def index_document(self, path: Path) -> int:
        chunks = self.documents.load_and_chunk(path)
        return self.index.add_chunks(chunks, self.embed_model)

    def ask(self, question: str, top_k: int | None = None) -> RagAnswer:
        if not question.strip():
            raise RetrievalError("Question cannot be empty")

        query_engine = self.index.as_query_engine(self.embed_model, self.llm, top_k or self.settings.top_k)
        response = query_engine.query(self._build_prompt(question))
        citations = self._extract_citations(response)
        return RagAnswer(
            answer=str(response).strip(),
            citations=citations,
            confidence=self._confidence_label(len(citations)),
        )

    def _build_prompt(self, question: str) -> str:
        return (
            "Answer using only the retrieved document context. "
            "If the answer is not supported, say what is missing. "
            "Keep the explanation clear for a student and include page-aware citations when possible.\n\n"
            f"Question: {question}"
        )

    def _extract_citations(self, response) -> list[Citation]:
        citations: list[Citation] = []
        for node in getattr(response, "source_nodes", []) or []:
            metadata = getattr(node.node, "metadata", {}) or {}
            citations.append(
                Citation(
                    source=str(metadata.get("source", "Unknown")),
                    page=metadata.get("page", "Unknown"),
                    chunk=metadata.get("chunk", "Unknown"),
                )
            )
        unique: dict[tuple[str, str, str], Citation] = {}
        for citation in citations:
            key = (citation.source, str(citation.page), str(citation.chunk))
            unique[key] = citation
        return list(unique.values())

    def _confidence_label(self, citation_count: int) -> str:
        if citation_count >= 3:
            return "High"
        if citation_count >= 1:
            return "Medium"
        return "Low"

