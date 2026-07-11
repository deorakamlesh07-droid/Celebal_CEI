from studymate_rag.ingestion.chunker import SemanticChunker
from studymate_rag.ingestion.loader import LoadedPage


def test_chunker_keeps_metadata():
    page = LoadedPage("doc", "notes.pdf", 3, " ".join(f"word{i}" for i in range(12)))
    chunks = SemanticChunker(chunk_size=5, overlap=1).split_pages([page])

    assert len(chunks) == 3
    assert chunks[0].metadata["source"] == "notes.pdf"
    assert chunks[0].metadata["page"] == 3
    assert chunks[1].text.startswith("word4")


def test_chunker_rejects_bad_overlap():
    try:
        SemanticChunker(chunk_size=5, overlap=5)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

