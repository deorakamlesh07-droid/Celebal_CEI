import json
import logging
from typing import Any
from pydantic import ValidationError

from studymate_rag.core.config import Settings
from studymate_rag.core.exceptions import SummarizationError
from studymate_rag.services.rag_service import RagService
from studymate_rag.services.document_service import DocumentService
from studymate_rag.llm.providers import build_llm
from studymate_rag.summarization.models import SummaryRequest, SummaryResult, SummaryScope
from studymate_rag.summarization.prompts import get_prompt
from studymate_rag.summarization.cache import SummaryCache, generate_cache_key

logger = logging.getLogger(__name__)

class SummaryService:
    def __init__(self, settings: Settings, rag_service: RagService, document_service: DocumentService):
        self.settings = settings
        self.rag = rag_service
        self.documents = document_service
        self.llm = build_llm(settings)
        self.cache = SummaryCache(settings.summary_cache_dir)
        # Using a slightly larger chunk size for summarization to preserve context
        self.chunk_size = settings.chunk_size * 2

    def summarize(self, request: SummaryRequest) -> SummaryResult:
        try:
            text = self._extract_text(request)
            if not text.strip():
                raise SummarizationError("No text provided or extracted for summarization.")

            cache_key = generate_cache_key(text, request.level, request.scope)
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Summary cache hit for key {cache_key}")
                try:
                    return SummaryResult.model_validate(cached_data)
                except ValidationError:
                    logger.warning("Cached data invalid, regenerating.")

            logger.info(f"Generating summary for scope: {request.scope}, level: {request.level}")
            
            # Simple fallback for short text
            if len(text.split()) < self.chunk_size:
                result_dict = self._generate_json(text, request.level)
            else:
                result_dict = self._chunk_and_summarize(text, request.level)
            
            result = SummaryResult.model_validate(result_dict)
            self._compute_metadata(text, result)
            
            self.cache.set(cache_key, result.model_dump())
            return result
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            if isinstance(e, SummarizationError):
                raise
            raise SummarizationError(f"Failed to generate summary: {str(e)}") from e

    def _extract_text(self, request: SummaryRequest) -> str:
        if request.scope == SummaryScope.SELECTED_TEXT or request.scope == SummaryScope.ENTIRE_DOCUMENT:
            return request.text
            
        if request.scope == SummaryScope.SPECIFIC_DOCUMENT:
            if not request.document_name:
                raise SummarizationError("Document name required for SPECIFIC_DOCUMENT scope")
            for doc_path in self.documents.list_documents():
                if doc_path.name == request.document_name:
                    pages = self.documents.loader.load(doc_path)
                    return "\n\n".join(p.text for p in pages)
            raise SummarizationError(f"Document {request.document_name} not found")
            
        if request.scope == SummaryScope.PAGE_RANGE:
            if not request.document_name or not request.page_range:
                raise SummarizationError("Document name and page range required for PAGE_RANGE scope")
            start, end = request.page_range
            for doc_path in self.documents.list_documents():
                if doc_path.name == request.document_name:
                    pages = self.documents.loader.load(doc_path)
                    return "\n\n".join(p.text for p in pages if start <= p.page_number <= end)
            raise SummarizationError(f"Document {request.document_name} not found")
            
        if request.scope == SummaryScope.TOPIC:
            if not request.topic:
                raise SummarizationError("Topic required for TOPIC scope")
            # Retrieve top chunks related to topic
            try:
                query_engine = self.rag.index.as_query_engine(self.rag.embed_model, self.llm, top_k=10)
                response = query_engine.query(request.topic)
                text = "\n\n".join([node.node.get_content() for node in getattr(response, "source_nodes", [])])
                return text or request.text
            except Exception as e:
                logger.warning(f"Topic retrieval failed: {e}")
                return request.text
                
        if request.scope == SummaryScope.RETRIEVED_CONTEXT:
            return request.text

        return request.text

    def _chunk_and_summarize(self, text: str, level: str) -> dict[str, Any]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size):
            chunks.append(" ".join(words[i:i + self.chunk_size]))
            
        logger.info(f"Split text into {len(chunks)} chunks for summarization.")
        
        chunk_summaries = []
        for chunk in chunks:
            chunk_summary = self._generate_json(chunk, level)
            chunk_summaries.append(chunk_summary)
            
        return self._merge_summaries(chunk_summaries, level)

    def _merge_summaries(self, summaries: list[dict[str, Any]], level: str) -> dict[str, Any]:
        if not summaries:
            return {}
        if len(summaries) == 1:
            return summaries[0]
            
        # Combine all summaries into a massive JSON representation string to pass to LLM
        combined_text = json.dumps(summaries, ensure_ascii=False)
        prompt_override = f"Merge the following JSON summaries into a single cohesive JSON summary, resolving duplicates and combining lists. Do NOT hallucinate.\n\n{combined_text}"
        
        return self._generate_json(prompt_override, level, is_merge=True)

    def _generate_json(self, text: str, level: str, is_merge: bool = False) -> dict[str, Any]:
        prompt = get_prompt(level)
        if is_merge:
            full_prompt = f"{prompt}\n\nTask: Merge these summaries.\nText:\n{text}"
        else:
            full_prompt = f"{prompt}\n\nText to summarize:\n{text}"
            
        response = self.llm.complete(full_prompt)
        response_str = str(response).strip()
        
        return self._parse_json(response_str)

    def _parse_json(self, response_str: str) -> dict[str, Any]:
        # Try to extract JSON from markdown blocks
        if "```json" in response_str:
            start = response_str.find("```json") + 7
            end = response_str.rfind("```")
            response_str = response_str[start:end].strip()
        elif "```" in response_str:
            start = response_str.find("```") + 3
            end = response_str.rfind("```")
            response_str = response_str[start:end].strip()
            
        try:
            return json.loads(response_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON output: {e}\nOutput: {response_str}")
            # Fallback for completely mangled JSON
            return {
                "title": "Generated Summary (Partial)",
                "summary": response_str[:1000] + "... (JSON Parse Error)"
            }

    def _compute_metadata(self, original_text: str, result: SummaryResult):
        words = original_text.split()
        result.word_count = len(result.summary.split())
        result.reading_time_minutes = max(1, result.word_count // 200) # Average reading speed 200 wpm
        
        # Simple heuristic for difficulty
        avg_word_len = sum(len(w) for w in result.summary.split()) / max(1, result.word_count)
        if avg_word_len > 6.0:
            result.difficulty_level = "Advanced"
        elif avg_word_len > 5.0:
            result.difficulty_level = "Intermediate"
        else:
            result.difficulty_level = "Beginner"
            
        # Confidence score based on populated fields and useful source coverage.
        fields_populated = sum(1 for v in [result.title, result.summary, result.key_topics, result.concepts] if v)
        field_score = fields_populated / 4.0
        source_words = len(original_text.split())
        coverage_score = min(1.0, source_words / 120.0)
        result.confidence_score = min(1.0, (field_score * 0.75) + (coverage_score * 0.25))
        if "JSON Parse Error" in result.summary:
            result.confidence_score = min(result.confidence_score, 0.35)
