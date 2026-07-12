from datetime import datetime, timedelta
import logging

from studymate_rag.learning.models import StudentProfile, Recommendation, DailyGoal

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self):
        # Spaced repetition intervals in days
        self.intervals = [1, 3, 7, 14, 30]

    def generate_recommendations(self, profile: StudentProfile) -> list[Recommendation]:
        recs = []
        
        # 1. High priority: Weak concepts
        for topic in profile.weak_concepts:
            recs.append(Recommendation(
                type="revise",
                topic=topic,
                reason="You scored low on this topic recently.",
                priority=1,
                difficulty="beginner" if profile.knowledge_level == "beginner" else "intermediate"
            ))
            
        # 2. Medium priority: Spaced repetition
        last_studied = {}
        for record in profile.learning_history:
            try:
                dt = datetime.fromisoformat(record.timestamp)
                if record.topic not in last_studied or dt > last_studied[record.topic]:
                    last_studied[record.topic] = dt
            except ValueError:
                continue
                
        now = datetime.now()
        for topic, last_date in last_studied.items():
            if topic in profile.mastered_concepts:
                continue
                
            days_since = (now - last_date).days
            for interval in self.intervals:
                if days_since >= interval:
                    recs.append(Recommendation(
                        type="review",
                        topic=topic,
                        reason=f"It's been {days_since} days since you reviewed this.",
                        priority=2 if interval < 7 else 3,
                        difficulty=profile.preferred_difficulty
                    ))
                    break # Only add one review rec per topic
                    
        # 3. Low priority: Mastered concepts (Quiz challenge)
        for topic in profile.mastered_concepts:
            # Check if they haven't quized it in a while
            if topic in last_studied and (now - last_studied[topic]).days > 14:
                recs.append(Recommendation(
                    type="quiz",
                    topic=topic,
                    reason="Keep your mastery sharp with a quick quiz.",
                    priority=4,
                    difficulty="advanced"
                ))

        # 4. Fallback if no recs
        if not recs:
            recs.append(Recommendation(
                type="study",
                topic="New Material",
                reason="Upload a new document to start learning.",
                priority=5,
                difficulty=profile.preferred_difficulty
            ))
            
        # Sort by priority and return top 5
        return sorted(recs, key=lambda x: x.priority)[:5]

    def get_study_plan(self, profile: StudentProfile) -> DailyGoal:
        # Simple daily goal calculation
        target_mins = 30
        if profile.knowledge_level == "advanced":
            target_mins = 60
        elif profile.study_streak > 7:
            target_mins = 45
            
        target_topics = min(3, max(1, len(profile.weak_concepts) + 1))
        
        # Calculate completed today
        today = datetime.now().date()
        completed_mins = 0.0
        completed_topics = set()
        
        for record in profile.learning_history:
            try:
                dt = datetime.fromisoformat(record.timestamp)
                if dt.date() == today:
                    completed_mins += record.duration_minutes
                    completed_topics.add(record.topic)
            except ValueError:
                continue
                
        return DailyGoal(
            target_minutes=target_mins,
            target_topics=target_topics,
            completed_minutes=completed_mins,
            completed_topics=list(completed_topics)
        )

    def get_difficulty_adjustment(self, profile: StudentProfile, topic: str) -> str:
        # Analyze recent quizzes for this topic
        topic_scores = [q for q in profile.quiz_scores if q.topic == topic]
        if not topic_scores:
            return profile.preferred_difficulty
            
        recent = topic_scores[-3:] # Look at last 3
        avg = sum(q.score / max(1, q.total) for q in recent) / len(recent)
        
        if avg < 0.5:
            return "beginner"
        elif avg > 0.85:
            return "advanced"
        return "intermediate"
