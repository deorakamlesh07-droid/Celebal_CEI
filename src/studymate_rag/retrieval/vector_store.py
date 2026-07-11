from pathlib import Path
import shutil
import sqlite3
from datetime import datetime

import chromadb
from llama_index.core import Settings as LlamaSettings
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.vector_stores.chroma import ChromaVectorStore

from studymate_rag.ingestion.chunker import TextChunk


class ChromaIndex:
    def __init__(self, persist_path: Path, collection_name: str = "study_documents") -> None:
        self.persist_path = persist_path
        self.collection_name = collection_name
        self.client = self._client()
        self.collection = self.client.get_or_create_collection(collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)

    def _client(self):
        self.persist_path.mkdir(parents=True, exist_ok=True)
        if not self._store_has_valid_tenant():
            self._backup_corrupt_store()
            self.persist_path.mkdir(parents=True, exist_ok=True)
        try:
            return chromadb.PersistentClient(path=str(self.persist_path))
        except BaseException as exc:
            if not self._is_recoverable_chroma_error(exc):
                raise
            backup_path = self._backup_corrupt_store()
            self.persist_path.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(self.persist_path))
            marker = self.persist_path / "RECOVERED_FROM_CORRUPT_STORE.txt"
            marker.write_text(
                f"Recovered Chroma store at {datetime.now().isoformat()}.\n"
                f"Previous store moved to: {backup_path}\n",
                encoding="utf-8",
            )
            return client

    def _is_recoverable_chroma_error(self, exc: BaseException) -> bool:
        message = str(exc).lower()
        return (
            "default_tenant" in message
            or "tenant" in message
            or "range start index" in message
            or exc.__class__.__name__ == "PanicException"
        )

    def _backup_corrupt_store(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.persist_path.with_name(f"{self.persist_path.name}_backup_{timestamp}")
        if self.persist_path.exists():
            shutil.move(str(self.persist_path), str(backup_path))
        return backup_path

    def _store_has_valid_tenant(self) -> bool:
        db_path = self.persist_path / "chroma.sqlite3"
        if not db_path.exists():
            return True
        try:
            with sqlite3.connect(str(db_path)) as connection:
                rows = connection.execute("select * from tenants").fetchall()
            return any(row and row[0] == "default_tenant" for row in rows)
        except sqlite3.OperationalError as exc:
            if "locked" in str(exc).lower() or "access" in str(exc).lower():
                return True
            return False
        except sqlite3.Error:
            return False

    def build_or_load(self, embed_model) -> VectorStoreIndex:
        LlamaSettings.embed_model = embed_model
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        if self.collection.count() > 0:
            return VectorStoreIndex.from_vector_store(self.vector_store, storage_context=storage_context)
        return VectorStoreIndex([], storage_context=storage_context)

    def add_chunks(self, chunks: list[TextChunk], embed_model) -> int:
        if not chunks:
            return 0
        LlamaSettings.embed_model = embed_model
        nodes = [TextNode(text=chunk.text, metadata=chunk.metadata) for chunk in chunks]
        index = self.build_or_load(embed_model)
        index.insert_nodes(nodes)
        return len(nodes)

    def as_query_engine(self, embed_model, llm, top_k: int):
        LlamaSettings.embed_model = embed_model
        LlamaSettings.llm = llm
        index = self.build_or_load(embed_model)
        return index.as_query_engine(similarity_top_k=top_k, response_mode="compact")

    def count(self) -> int:
        return self.collection.count()
