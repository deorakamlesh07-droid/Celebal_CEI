from unittest.mock import Mock, patch
from pathlib import Path

from studymate_rag.core.config import Settings
from studymate_rag.summarization.models import SummaryRequest, SummaryScope, SummaryLevel, SummaryResult
from studymate_rag.summarization.summary_service import SummaryService

def test_summary_cache_hit(tmp_path: Path):
    settings = Settings(SUMMARY_CACHE_DIR=tmp_path)
    mock_rag = Mock()
    mock_doc = Mock()
    
    with patch("studymate_rag.summarization.summary_service.build_llm") as mock_build_llm:
        mock_llm = Mock()
        mock_build_llm.return_value = mock_llm
        
        service = SummaryService(settings, mock_rag, mock_doc)
        
        # Pre-populate cache
        req = SummaryRequest(text="Hello world", scope=SummaryScope.ENTIRE_DOCUMENT, level=SummaryLevel.QUICK)
        from studymate_rag.summarization.cache import generate_cache_key
        key = generate_cache_key("Hello world", req.level, req.scope)
        
        cached_result = SummaryResult(title="Cached Title", summary="Cached Summary")
        service.cache.set(key, cached_result.model_dump())
        
        # Should return cached result without calling LLM
        result = service.summarize(req)
        assert result.title == "Cached Title"
        assert result.summary == "Cached Summary"
        mock_llm.complete.assert_not_called()

def test_summary_generation_small_text(tmp_path: Path):
    settings = Settings(SUMMARY_CACHE_DIR=tmp_path)
    mock_rag = Mock()
    mock_doc = Mock()
    
    with patch("studymate_rag.summarization.summary_service.build_llm") as mock_build_llm:
        mock_llm = Mock()
        # Mock the LLM to return valid JSON string
        mock_llm.complete.return_value = '{"title": "Test Title", "summary": "Test Summary"}'
        mock_build_llm.return_value = mock_llm
        
        service = SummaryService(settings, mock_rag, mock_doc)
        
        req = SummaryRequest(text="Hello world", scope=SummaryScope.ENTIRE_DOCUMENT, level=SummaryLevel.QUICK)
        result = service.summarize(req)
        
        assert result.title == "Test Title"
        assert result.summary == "Test Summary"
        mock_llm.complete.assert_called_once()

def test_metadata_computation(tmp_path: Path):
    settings = Settings(SUMMARY_CACHE_DIR=tmp_path)
    mock_rag = Mock()
    mock_doc = Mock()
    
    with patch("studymate_rag.summarization.summary_service.build_llm"):
        service = SummaryService(settings, mock_rag, mock_doc)
        
        result = SummaryResult(title="T", summary="This is a simple short summary.")
        service._compute_metadata("Original text " * 10, result)
        
        assert result.word_count == 6
        assert result.reading_time_minutes == 1
        assert result.difficulty_level == "Beginner"


def test_summary_confidence_is_capped_for_parse_errors():
    service = SummaryService.__new__(SummaryService)
    result = SummaryResult(
        title="Partial",
        summary="Bad response... (JSON Parse Error)",
        key_topics=["topic"],
        concepts=["concept"],
    )

    service._compute_metadata("short source text", result)

    assert result.confidence_score <= 0.35
