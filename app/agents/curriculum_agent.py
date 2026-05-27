"""
Curriculum Agent — Decides what the learner should work on next.

It can consume data from SkillTool (weak skills) and HistoryTool to produce
structured recommendations that the CurriculumTool can then turn into real blocks.
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI

from app.core.llm import get_llm_client, get_model_name
from app.agents.schemas import CurriculumRecommendation, BlockSuggestion


SYSTEM_PROMPT = """You are a curriculum planning agent for a language learner.

You will receive:
- Recent performance data (mastery scores on specific skills)
- Recent session history summary
- The user's current CEFR level

Your job is to recommend 1-3 focused next blocks.
- If the user is struggling (many low mastery scores), recommend remedial blocks.
- If the user is doing well, recommend the logical next progression.

Respond ONLY with valid JSON matching this structure:

{
  "suggestions": [
    {
      "title": "string",
      "description": "string",
      "cefr_level": "A1" | "A2" | ...,
      "reason": "why this block is recommended",
      "priority": 1-5
    }
  ],
  "rationale": "overall reasoning in one paragraph"
}
"""


class CurriculumAgent:
    """Produces structured curriculum recommendations."""

    def __init__(self, client: Optional[OpenAI] = None):
        self.client = client or get_llm_client()

    def suggest(
        self,
        *,
        user_id: str,
        current_cefr: str = "A1",
        weak_skills: List[Dict[str, Any]] = None,
        recent_sessions: List[Dict[str, Any]] = None,
    ) -> CurriculumRecommendation:
        """Generate curriculum recommendations for a user."""
        weak_skills = weak_skills or []
        recent_sessions = recent_sessions or []

        prompt = f"""User ID: {user_id}
Current CEFR: {current_cefr}

Weak Skills (low mastery):
{weak_skills}

Recent Sessions:
{recent_sessions}
"""

        response = self.client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.6,
        )

        content = response.choices[0].message.content or "{}"

        try:
            return CurriculumRecommendation.model_validate_json(content)
        except Exception:
            return CurriculumRecommendation(
                suggestions=[],
                rationale="Unable to generate recommendations at this time."
            )


# Legacy function for backwards compatibility
def suggest_curriculum(
    client: Optional[OpenAI] = None,
    completed_tasks: List[Dict[str, Any]] = None,
    performance: Dict[str, Any] = None,
    observer_feedback: Optional[str] = None,
    possible_blocks: List[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """Legacy wrapper. Prefer CurriculumAgent class for new code."""
    agent = CurriculumAgent(client=client)
    rec = agent.suggest(
        user_id="unknown",
        current_cefr="A1",
        weak_skills=performance.get("weak_skills", []) if performance else [],
    )
    return [s.model_dump() for s in rec.suggestions]
