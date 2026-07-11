from studymate_rag.summarization.models import SummaryLevel

SYSTEM_PROMPT = """You are an intelligent document summarization engine.
Your goal is to summarize the provided text based on the requested summary level.
You must return ONLY a JSON object that strictly matches the following structure:

{
  "title": "A descriptive title",
  "key_topics": ["Topic 1", "Topic 2"],
  "summary": "The main summary text based on the requested level",
  "concepts": ["Concept 1", "Concept 2"],
  "definitions": {"Term": "Definition"},
  "examples": ["Example 1"],
  "formulas": ["E=mc^2 (if any)"],
  "common_mistakes": ["Mistake 1"],
  "exam_tips": ["Tip 1"],
  "revision_checklist": ["Checklist item 1"],
  "follow_up_questions": ["Question 1"]
}

Rules:
1. Preserve facts, technical terms, equations, and definitions.
2. Avoid hallucination. Do not include external information not found in the text.
3. If a field (like formulas or exam tips) is not applicable or cannot be found in the text, return an empty list/dict for it.
4. Maintain logical flow and section hierarchy.
5. The JSON must be valid.
"""

LEVEL_INSTRUCTIONS = {
    SummaryLevel.QUICK: "Provide a very brief 3-sentence summary of the core message.",
    SummaryLevel.ONE_MINUTE: "Provide a summary that takes exactly one minute to read, hitting the main points.",
    SummaryLevel.FIVE_MINUTE: "Provide a comprehensive 5-minute reading summary covering all major sections.",
    SummaryLevel.DETAILED: "Provide a highly detailed summary capturing nuances, arguments, and supporting evidence.",
    SummaryLevel.ACADEMIC: "Summarize with an academic tone, focusing on methodology, findings, and conclusions.",
    SummaryLevel.EXECUTIVE: "Provide an executive summary, focusing on high-level takeaways and actionable items.",
    SummaryLevel.BULLET: "Provide the summary entirely as a well-structured list of bullet points.",
    SummaryLevel.ELI10: "Explain the main points simply, as if explaining to a 10-year-old child.",
    SummaryLevel.TECHNICAL: "Focus heavily on technical details, architecture, algorithms, or specifications.",
    SummaryLevel.EXAM_REVISION: "Focus on what is most likely to be tested: key facts, dates, definitions, and relationships."
}

def get_prompt(level: SummaryLevel) -> str:
    level_instruction = LEVEL_INSTRUCTIONS.get(level, LEVEL_INSTRUCTIONS[SummaryLevel.DETAILED])
    return f"{SYSTEM_PROMPT}\n\nTask for this level: {level_instruction}"
