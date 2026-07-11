from studymate_rag.services.study_service import StudyService


def test_study_service_generates_flashcards_and_concepts():
    text = (
        "Retrieval augmented generation improves answers with document context. "
        "Citations help students verify important claims."
    )
    service = StudyService()

    cards = service.flashcards(text)
    concepts = service.key_concepts(text)

    assert cards
    assert any("retrieval" in concept for concept in concepts)


def test_summary_is_concise():
    text = "One important sentence. Two important sentence. Three important sentence."
    assert StudyService().summarize(text, max_sentences=2).count(".") == 2


def test_quiz_answers_are_grounded_in_source_text():
    text = (
        "The Universal Declaration of Human Rights was adopted in 1948 by the United Nations. "
        "Article 1 states that all human beings are born free and equal in dignity and rights. "
        "Students should verify claims using source citations."
    )

    quiz = StudyService().quiz(text, limit=2)

    assert quiz
    assert all(item.answer in text for item in quiz)
    assert all(item.source == item.answer for item in quiz)
