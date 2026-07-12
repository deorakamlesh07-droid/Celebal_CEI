import logging
from typing import Optional

from studymate_rag.core.config import Settings
from studymate_rag.learning.models import (
    StudentProfile, 
    ActivityRecord, 
    QuizScore, 
    Recommendation, 
    LearningAnalytics,
    DailyGoal
)
from studymate_rag.learning.profile_store import ProfileStore
from studymate_rag.learning.recommendation_engine import RecommendationEngine
from studymate_rag.learning.analytics_engine import AnalyticsEngine

logger = logging.getLogger(__name__)

class LearningService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.store = ProfileStore(settings.learning_data_dir)
        self.recommender = RecommendationEngine()
        self.analytics = AnalyticsEngine()

    def get_profile(self, student_id: str) -> StudentProfile:
        return self.store.load(student_id)

    def record_study_activity(self, student_id: str, topic: str, duration_minutes: float, activity_type: str = "study", score: Optional[float] = None) -> None:
        logger.info(f"Recording {activity_type} activity for {student_id} on {topic} ({duration_minutes}m)")
        activity = ActivityRecord(
            activity_type=activity_type,
            topic=topic,
            duration_minutes=duration_minutes,
            score=score
        )
        self.store.record_activity(student_id, activity)

    def record_quiz_result(self, student_id: str, topic: str, score: float, total: float) -> None:
        total = max(1.0, float(total))
        score = min(max(0.0, float(score)), total)
        logger.info(f"Recording quiz result for {student_id} on {topic}: {score}/{total}")
        quiz = QuizScore(
            topic=topic,
            score=score,
            total=total
        )
        self.store.record_quiz(student_id, quiz)
        # Also record it as an activity
        duration = total * 2.0 # Estimate 2 mins per question
        self.record_study_activity(student_id, topic, duration, "quiz", score/max(1, total))

    def get_recommendations(self, student_id: str) -> list[Recommendation]:
        profile = self.store.load(student_id)
        return self.recommender.generate_recommendations(profile)

    def get_analytics(self, student_id: str) -> LearningAnalytics:
        profile = self.store.load(student_id)
        return self.analytics.compute_analytics(profile)

    def get_daily_goal(self, student_id: str) -> DailyGoal:
        profile = self.store.load(student_id)
        return self.recommender.get_study_plan(profile)
        
    def get_difficulty_for_topic(self, student_id: str, topic: str) -> str:
        profile = self.store.load(student_id)
        return self.recommender.get_difficulty_adjustment(profile, topic)

    def get_dashboard_data(self, student_id: str) -> dict:
        profile = self.store.load(student_id)
        return {
            "profile": profile,
            "analytics": self.analytics.compute_analytics(profile),
            "recommendations": self.recommender.generate_recommendations(profile),
            "daily_goal": self.recommender.get_study_plan(profile)
        }
