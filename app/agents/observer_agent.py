"""
Observer Agent — Produces reflective post-session insights.

Useful after lessons, practice, or conversations to help the learner
(and the system) understand what happened and what to do next.
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI

from app.core.llm import get_llm_client, get_model_name
from app.agents.schemas import SessionObservation


SYSTEM_PROMPT = """You are a thoughtful language learning coach.

After a session you receive:
- What the learner was working on
- Key actions they took
- The outcome

Write a short, encouraging observation that includes:
- What went well
- What could be improved
- 1-2 concrete next steps

Respond with valid JSON:
{
  "summary": "one paragraph reflection",
  "strengths": ["string", ...],
  "areas_for_improvement": ["string", ...],
  "suggested_next_steps": ["string", ...]
}
"""


class ObserverAgent:
    """Generates reflective observations after learning sessions."""

    def __init__(self, client: Optional[OpenAI] = None):
        self.client = client or get_llm_client()

    def observe(
        self,
        *,
        task_summary: str,
        actions: List[Dict[str, Any]] = None,
        final_state: str = "",
    ) -> SessionObservation:
        actions = actions or []

        prompt = f"""Task: {task_summary}

Actions taken:
{actions}

Final outcome:
{final_state}
"""

        response = self.client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        try:
            return SessionObservation.model_validate_json(content)
        except Exception:
            return SessionObservation(
                summary="Session completed.",
                suggested_next_steps=["Continue practicing regularly."],
            )


# Legacy function
def observe_session(
    client: Optional[OpenAI] = None,
    actions: List[Dict[str, Any]] = None,
    task_summary: str = "",
    final_state: str = "",
) -> str:
    agent = ObserverAgent(client=client)
    obs = agent.observe(task_summary=task_summary, actions=actions, final_state=final_state)
    return obs.model_dump_json()
