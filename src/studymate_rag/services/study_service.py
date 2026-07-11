from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Flashcard:
    front: str
    back: str


@dataclass(frozen=True)
class QuizQuestion:
    question: str
    answer: str
    source: str = ""


class StudyService:
    def summarize(self, text: str, max_sentences: int = 5) -> str:
        sentences = self._sentences(text)
        return " ".join(sentences[:max_sentences])

    def flashcards(self, text: str, limit: int = 8) -> list[Flashcard]:
        cards: list[Flashcard] = []
        for sentence in self._sentences(text):
            key = self._keyword(sentence)
            if key and len(sentence.split()) >= 6:
                cards.append(Flashcard(front=f"What is important about {key}?", back=sentence))
            if len(cards) >= limit:
                break
        return cards

    def quiz(self, text: str, limit: int = 5) -> list[QuizQuestion]:
        questions: list[QuizQuestion] = []
        used_answers: set[str] = set()
        for sentence in self._ranked_sentences(text):
            question = self._question_from_sentence(sentence)
            if not question or sentence in used_answers:
                continue
            questions.append(QuizQuestion(question=question, answer=sentence, source=sentence))
            used_answers.add(sentence)
            if len(questions) >= limit:
                break
        return questions

    def key_concepts(self, text: str, limit: int = 10) -> list[str]:
        words = [
            word.strip(".,:;()[]{}").lower()
            for word in text.split()
            if len(word.strip(".,:;()[]{}")) > 5
        ]
        counts: dict[str, int] = {}
        for word in words:
            counts[word] = counts.get(word, 0) + 1
        return [word for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]

    def revision_notes(self, text: str) -> list[str]:
        return [f"- {sentence}" for sentence in self._sentences(text)[:8]]

    def interview_prompts(self, text: str, limit: int = 5) -> list[str]:
        return [f"How would you explain {concept} with an example?" for concept in self.key_concepts(text, limit)]

    def suggestions(self, text: str) -> list[str]:
        concepts = self.key_concepts(text, 3)
        if not concepts:
            return ["Add more source material before generating a study plan."]
        return [
            f"Review {concepts[0]} first because it appears most often.",
            "Convert weak areas into flashcards and revisit them tomorrow.",
            "Use interview mode after reading the summary once.",
        ]

    def _sentences(self, text: str) -> list[str]:
        cleaned = " ".join(text.split())
        if not cleaned:
            return []
        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        return [part.strip() for part in parts if len(part.split()) >= 2]

    def _keyword(self, sentence: str) -> str:
        words = [word.strip(".,:;()[]{}") for word in sentence.split()]
        candidates = [word for word in words if len(word) > 5]
        return candidates[0] if candidates else ""

    def _ranked_sentences(self, text: str) -> list[str]:
        sentences = self._sentences(text)
        if not sentences:
            return []
        concept_counts = {concept: text.lower().count(concept) for concept in self.key_concepts(text, 20)}
        return sorted(sentences, key=lambda item: self._sentence_score(item, concept_counts), reverse=True)

    def _sentence_score(self, sentence: str, concept_counts: dict[str, int]) -> int:
        lowered = sentence.lower()
        score = sum(count for concept, count in concept_counts.items() if concept in lowered)
        if any(char.isdigit() for char in sentence):
            score += 3
        if any(marker in lowered for marker in ("because", "therefore", "means", "refers to", "defined as")):
            score += 2
        length = len(sentence.split())
        if 8 <= length <= 35:
            score += 2
        return score

    def _question_from_sentence(self, sentence: str) -> str:
        clean = sentence.strip()
        lowered = clean.lower()
        concept = self._best_concept(clean)
        if not concept:
            return ""
        if "because" in lowered:
            return f"Why is {concept} important in this context?"
        if any(marker in lowered for marker in ("means", "refers to", "defined as")):
            return f"What does {concept} mean according to the material?"
        if any(char.isdigit() for char in clean):
            return f"What key fact or value is stated about {concept}?"
        return f"What does the material say about {concept}?"

    def _best_concept(self, sentence: str) -> str:
        words = [
            word.strip(".,:;()[]{}").lower()
            for word in sentence.split()
            if len(word.strip(".,:;()[]{}")) > 5
        ]
        stopwords = {
            "according", "important", "material", "context", "students", "should",
            "through", "because", "therefore", "between", "example", "question",
        }
        candidates = [word for word in words if word not in stopwords]
        return candidates[0] if candidates else ""
