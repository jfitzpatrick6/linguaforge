"""
Lesson Generator Agent — The heart of the learning experience.

This agent produces personalized, grounded lessons by combining:
- User context (CEFR level, weak skills)
- Relevant retrieved content from language grounding PDFs via PDFGrounding
- The local LLM (via the central client factory)

It returns a structured `Lesson` Pydantic model.
"""
from typing import Optional, List
from openai import OpenAI

from app.core.llm import get_llm_client, get_model_name
from app.agents.schemas import Lesson
from app.services.pdf_grounding import get_pdf_grounding_service, PDFGrounding


SYSTEM_PROMPT = """You are an expert language teacher creating a short, focused lesson.

You will be given:
- Target CEFR level (A1–B2)
- The specific topic or skill to teach
- Relevant excerpts retrieved from trusted language learning materials (RAG)

Your job:
1. Write a clear, encouraging explanation suitable for the given CEFR level.
2. Provide 2–4 natural, useful examples.
3. Suggest 2–3 practice items the learner can do immediately.
4. Call out 1–2 common pitfalls with simple advice.
5. Give 1–2 concrete next steps.

Respond ONLY with valid JSON matching this exact structure (no extra text):

{
  "title": "string",
  "explanation": "string",
  "examples": ["string", ...],
  "practice_items": ["string", ...],
  "common_pitfalls": ["string", ...],
  "next_steps": ["string", ...],
  "cefr_level": "A1" | "A2" | ...
}
"""


class LessonGeneratorAgent:
    """
    Generates structured lessons using RAG from grounding PDFs + the local LLM.
    """

    def __init__(
        self,
        grounding_service: Optional[PDFGrounding] = None,
        client: Optional[OpenAI] = None,
    ):
        self.grounding = grounding_service or get_pdf_grounding_service()
        self.client = client or get_llm_client()

    def generate(
        self,
        *,
        language: str,
        topic: str,
        skill_level: str = "A1",
        user_id: Optional[str] = None,
        k: int = 5,
    ) -> Lesson:
        """
        Generate a lesson for the given topic in the target language.

        The agent automatically retrieves relevant context from the language's
        grounding collection before calling the LLM.
        """
        # 1. Retrieve relevant grounding context
        hits = self.grounding.query_grounding(language, topic, k=k)
        rag_context = "\n\n---\n\n".join(h["text"] for h in hits) if hits else "No specific reference material found."

        # 2. Build the user prompt
        user_prompt = f"""Target Language: {language}
CEFR Level: {skill_level}
Topic: {topic}

Relevant Reference Material (RAG):
{rag_context}
"""

        # 3. Call the model with JSON mode
        response = self.client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content or "{}"

        # 4. Parse into our Pydantic model (with fallback)
        try:
            lesson = Lesson.model_validate_json(content)
            if not lesson.cefr_level:
                lesson.cefr_level = skill_level
            return lesson
        except Exception:
            # Fallback: return a minimal lesson so the system doesn't explode
            return Lesson(
                title=f"Lesson: {topic}",
                explanation=f"This is a lesson about {topic} at {skill_level} level.",
                examples=[],
                practice_items=[f"Practice using {topic} in a sentence."],
                common_pitfalls=[],
                next_steps=["Review the examples and try the practice items."],
                cefr_level=skill_level,
            )


# Backwards-compatible function (for any code still calling the old API)
def generate_lesson(
    client: Optional[OpenAI] = None,
    skill_level: str = "A1",
    topic: str = "",
    rag_context: str = "",
    language: str = "es",
) -> str:
    """
    Legacy function wrapper.

    New code should prefer:
        agent = LessonGeneratorAgent()
        lesson = agent.generate(language=..., topic=..., skill_level=...)
    """
    agent = LessonGeneratorAgent(client=client)
    lesson = agent.generate(language=language, topic=topic, skill_level=skill_level)
    # Return JSON string for backwards compatibility with old callers
    return lesson.model_dump_json()
