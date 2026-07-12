import json
import logging
import threading
from pathlib import Path
from datetime import datetime

from studymate_rag.core.exceptions import LearningEngineError
from studymate_rag.learning.models import StudentProfile, ActivityRecord, QuizScore

logger = logging.getLogger(__name__)

class ProfileStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def _get_path(self, student_id: str) -> Path:
        # Sanitize student_id for filename
        safe_id = "".join(c for c in student_id if c.isalnum() or c in ('-', '_')).strip()
        if not safe_id:
            safe_id = "default_student"
        return self.data_dir / f"{safe_id}.json"

    def load(self, student_id: str) -> StudentProfile:
        path = self._get_path(student_id)
        if not path.exists():
            return StudentProfile(student_id=student_id)
            
        with self.lock:
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    return StudentProfile.model_validate(data)
            except Exception as e:
                logger.error(f"Failed to load profile for {student_id}: {e}")
                # Fallback to a new profile if corrupted
                return StudentProfile(student_id=student_id)

    def save(self, profile: StudentProfile) -> None:
        path = self._get_path(profile.student_id)
        profile.updated_at = datetime.now().isoformat()
        
        with self.lock:
            try:
                with path.open("w", encoding="utf-8") as f:
                    f.write(profile.model_dump_json(indent=2))
            except Exception as e:
                logger.error(f"Failed to save profile for {profile.student_id}: {e}")
                raise LearningEngineError(f"Failed to save profile: {e}")

    def record_activity(self, student_id: str, activity: ActivityRecord) -> None:
        profile = self.load(student_id)
        profile.learning_history.append(activity)
        profile.total_study_minutes += activity.duration_minutes
        
        self._update_streak(profile)
        self.save(profile)

    def record_quiz(self, student_id: str, quiz: QuizScore) -> None:
        profile = self.load(student_id)
        profile.quiz_scores.append(quiz)
        
        # Update weak/mastered based on this quiz
        percentage = quiz.score / max(1, quiz.total)
        if percentage < 0.6:
            if quiz.topic not in profile.weak_concepts:
                profile.weak_concepts.append(quiz.topic)
            if quiz.topic in profile.mastered_concepts:
                profile.mastered_concepts.remove(quiz.topic)
        elif percentage >= 0.8:
            if quiz.topic not in profile.mastered_concepts:
                profile.mastered_concepts.append(quiz.topic)
            if quiz.topic in profile.weak_concepts:
                profile.weak_concepts.remove(quiz.topic)
                
        self.save(profile)

    def _update_streak(self, profile: StudentProfile) -> None:
        if not profile.learning_history:
            profile.study_streak = 0
            return
            
        # Get unique dates of study
        dates = set()
        for record in profile.learning_history:
            try:
                dt = datetime.fromisoformat(record.timestamp)
                dates.add(dt.date())
            except ValueError:
                continue
                
        sorted_dates = sorted(list(dates), reverse=True)
        if not sorted_dates:
            return
            
        today = datetime.now().date()
        if (today - sorted_dates[0]).days > 1:
            profile.study_streak = 0
            return
            
        streak = 0
        current_date = sorted_dates[0]
        
        for d in sorted_dates:
            if (current_date - d).days <= 1:
                streak += 1
                current_date = d
            else:
                break
                
        profile.study_streak = streak
