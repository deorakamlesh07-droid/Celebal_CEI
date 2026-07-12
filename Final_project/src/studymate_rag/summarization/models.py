from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class SummaryScope(str, Enum):
    ENTIRE_DOCUMENT = "entire_document"
    SPECIFIC_DOCUMENT = "specific_document"
    PAGE_RANGE = "page_range"
    TOPIC = "topic"
    RETRIEVED_CONTEXT = "retrieved_context"
    SELECTED_TEXT = "selected_text"

class SummaryLevel(str, Enum):
    QUICK = "quick"
    ONE_MINUTE = "one_minute"
    FIVE_MINUTE = "five_minute"
    DETAILED = "detailed"
    ACADEMIC = "academic"
    EXECUTIVE = "executive"
    BULLET = "bullet"
    ELI10 = "eli10"
    TECHNICAL = "technical"
    EXAM_REVISION = "exam_revision"

class SummaryRequest(BaseModel):
    text: str = ""
    scope: SummaryScope = SummaryScope.ENTIRE_DOCUMENT
    level: SummaryLevel = SummaryLevel.DETAILED
    document_name: Optional[str] = None
    page_range: Optional[tuple[int, int]] = None
    topic: Optional[str] = None

class SummaryResult(BaseModel):
    title: str = Field(default="", description="Title of the summary")
    key_topics: list[str] = Field(default_factory=list, description="Key topics extracted")
    summary: str = Field(default="", description="The main summary text")
    concepts: list[str] = Field(default_factory=list, description="Important concepts")
    definitions: dict[str, str] = Field(default_factory=dict, description="Important definitions")
    examples: list[str] = Field(default_factory=list, description="Examples mentioned")
    formulas: list[str] = Field(default_factory=list, description="Important formulas or equations")
    common_mistakes: list[str] = Field(default_factory=list, description="Common mistakes or misconceptions")
    exam_tips: list[str] = Field(default_factory=list, description="Tips for exams")
    revision_checklist: list[str] = Field(default_factory=list, description="Checklist for revision")
    follow_up_questions: list[str] = Field(default_factory=list, description="Suggested follow up questions")
    
    # Computed metadata
    confidence_score: float = Field(default=0.0, description="Confidence score of the summary")
    reading_time_minutes: int = Field(default=0, description="Estimated reading time in minutes")
    word_count: int = Field(default=0, description="Word count of the summary")
    difficulty_level: str = Field(default="Intermediate", description="Estimated difficulty level")
    keywords: list[str] = Field(default_factory=list, description="Keywords extracted from text")
