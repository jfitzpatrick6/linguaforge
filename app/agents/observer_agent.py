from typing import List, Dict, Any
from openai import OpenAI

from app.core.llm import get_llm_client, get_model_name

SYSTEM_PROMPT = """
You are an observer agent responsible for analyzing session data and generating reflective insights.

After a user session, you will receive:
- A list of user actions (e.g., code edits, tool calls)
- A summary of the task being worked on
- The final outcome or state of the system

Your task is to generate a concise, insightful post-session observation that includes:
1. What was achieved
2. What might be missing or could be improved
3. Suggested next steps or learning opportunities

Be reflective, constructive, and human-like in tone. Avoid repetition or generic feedback.
"""


def observe_session(
    client: OpenAI | None = None,
    actions: List[Dict[str, Any]] = None,
    task_summary: str = "",
    final_state: str = "",
) -> str:
    """Generate a reflective post-session observation.

    If client is not provided, a properly configured local client is obtained
    automatically via the central LLM factory.
    """
    if client is None:
        client = get_llm_client()
    actions = actions or []

    response = client.chat.completions.create(
        model=get_model_name(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Task: {task_summary}\n\nActions: {actions}\n\nFinal State: {final_state}"}
        ]
    )
    return response.choices[0].message.content or ""
