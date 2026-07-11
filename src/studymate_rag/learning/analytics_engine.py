from datetime import datetime, timedelta
import logging

from studymate_rag.learning.models import StudentProfile, LearningAnalytics

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    def compute_analytics(self, profile: StudentProfile) -> LearningAnalytics:
        analytics = LearningAnalytics()
        analytics.study_streak = profile.study_streak
        
        # Topic Mastery & Accuracy
        topic_scores = {}
        for q in profile.quiz_scores:
            if q.topic not in topic_scores:
                topic_scores[q.topic] = []
            topic_scores[q.topic].append(q.score / max(1, q.total))
            
        for topic, scores in topic_scores.items():
            # Recent scores weighted more
            avg = sum(scores) / len(scores)
            analytics.accuracy_by_topic[topic] = avg * 100
            analytics.topic_mastery[topic] = min(100.0, avg * 100 + (len(scores) * 2)) # slight bump for reps
            
        analytics.weak_topics = profile.weak_concepts
        analytics.strong_topics = profile.mastered_concepts
        
        # Daily minutes
        now = datetime.now()
        for i in range(7):
            d = (now - timedelta(days=i)).date()
            analytics.daily_minutes[d.isoformat()] = 0.0
            
        for r in profile.learning_history:
            try:
                dt = datetime.fromisoformat(r.timestamp).date()
                iso = dt.isoformat()
                if iso in analytics.daily_minutes:
                    analytics.daily_minutes[iso] += r.duration_minutes
            except ValueError:
                continue
                
        # Scores
        total_topics = len(set(r.topic for r in profile.learning_history))
        mastered = len(profile.mastered_concepts)
        
        analytics.completion_score = min(100.0, total_topics * 10.0)
        analytics.learning_score = min(100.0, sum(analytics.accuracy_by_topic.values()) / max(1, len(analytics.accuracy_by_topic)))
        
        # Progress score = mix of streak, learning score, and completion
        analytics.progress_score = (analytics.learning_score * 0.5) + (min(profile.study_streak * 10, 100) * 0.2) + (analytics.completion_score * 0.3)
        
        return analytics
