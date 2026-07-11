from pathlib import Path
from studymate_rag.core.config import Settings
from studymate_rag.learning.learning_service import LearningService
from studymate_rag.learning.models import StudentProfile

def test_learning_service_records_activity(tmp_path: Path):
    settings = Settings(LEARNING_DATA_DIR=tmp_path)
    service = LearningService(settings)
    
    student_id = "test_student"
    service.record_study_activity(student_id, "Python", 30.0)
    
    profile = service.get_profile(student_id)
    assert len(profile.learning_history) == 1
    assert profile.learning_history[0].topic == "Python"
    assert profile.learning_history[0].duration_minutes == 30.0
    assert profile.total_study_minutes == 30.0

def test_learning_service_quiz_updates_mastery(tmp_path: Path):
    settings = Settings(LEARNING_DATA_DIR=tmp_path)
    service = LearningService(settings)
    student_id = "test_student"
    
    # Score 90%
    service.record_quiz_result(student_id, "Math", 9, 10)
    profile = service.get_profile(student_id)
    
    assert "Math" in profile.mastered_concepts
    assert "Math" not in profile.weak_concepts
    
    # Score 40%
    service.record_quiz_result(student_id, "History", 4, 10)
    profile = service.get_profile(student_id)
    
    assert "History" in profile.weak_concepts
    assert "History" not in profile.mastered_concepts

def test_recommendation_priorities(tmp_path: Path):
    settings = Settings(LEARNING_DATA_DIR=tmp_path)
    service = LearningService(settings)
    student_id = "test_student"
    
    # Create a weak concept
    service.record_quiz_result(student_id, "Physics", 2, 10)
    
    recs = service.get_recommendations(student_id)
    assert len(recs) > 0
    # Weak topics should be highest priority (1)
    assert recs[0].topic == "Physics"
    assert recs[0].priority == 1


def test_quiz_score_is_clamped_to_valid_range(tmp_path: Path):
    settings = Settings(LEARNING_DATA_DIR=tmp_path)
    service = LearningService(settings)

    service.record_quiz_result("student", "Security", 150, 100)
    profile = service.get_profile("student")

    assert profile.quiz_scores[0].score == 100
    assert profile.quiz_scores[0].total == 100
