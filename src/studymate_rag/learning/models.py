from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ActivityRecord(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    activity_type: str = Field(description="study, revise, quiz, chat")
    topic: str
    duration_minutes: float = 0.0
    score: Optional[float] = None

class QuizScore(BaseModel):
    topic: str
    score: float
    total: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class StudentProfile(BaseModel):
    student_id: str
    knowledge_level: str = "beginner"
    preferred_difficulty: str = "intermediate"
    preferred_style: str = "detailed"
    weak_concepts: list[str] = Field(default_factory=list)
    mastered_concepts: list[str] = Field(default_factory=list)
    learning_history: list[ActivityRecord] = Field(default_factory=list)
    quiz_scores: list[QuizScore] = Field(default_factory=list)
    study_streak: int = 0
    total_study_minutes: float = 0.0
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Recommendation(BaseModel):
    type: str = Field(description="study, revise, quiz, review")
    topic: str
    reason: str
    priority: int = Field(description="1 (Highest) to 5 (Lowest)")
    difficulty: str

class DailyGoal(BaseModel):
    target_minutes: int = 30
    target_topics: int = 2
    completed_minutes: float = 0.0
    completed_topics: list[str] = Field(default_factory=list)

class LearningAnalytics(BaseModel):
    progress_score: float = 0.0
    learning_score: float = 0.0
    completion_score: float = 0.0
    revision_score: float = 0.0
    study_streak: int = 0
    topic_mastery: dict[str, float] = Field(default_factory=dict)
    weak_topics: list[str] = Field(default_factory=list)
    strong_topics: list[str] = Field(default_factory=list)
    accuracy_by_topic: dict[str, float] = Field(default_factory=dict)
    daily_minutes: dict[str, float] = Field(default_factory=dict)
    weekly_goal_progress: float = 0.0
