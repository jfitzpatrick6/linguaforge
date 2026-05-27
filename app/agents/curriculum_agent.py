from typing import List, Dict, Any
from openai import OpenAI

from app.core.llm import get_llm_client, get_model_name

SYSTEM_PROMPT = """
You are a curriculum agent responsible for dynamically adjusting the learning path.

You will receive:
- A list of completed tasks
- User performance (e.g., success rate, time to complete)
- Feedback from the observer agent (if available)
- A list of possible new or remedial learning blocks

Your task is to:
1. Determine if the user needs remedial content (e.g., due to errors or slow progress)
2. Suggest new blocks if the user has succeeded and is ready for advancement
3. Return a list of recommended blocks (either remedial or new)

Only add blocks when necessary. Prioritize relevance and progression. Do not recommend redundant or unnecessary content.
"""

def suggest_curriculum(
    client: OpenAI | None = None,
    completed_tasks: List[Dict[str, Any]] = None,
    performance: Dict[str, Any] = None,
    observer_feedback: str = None,
    possible_blocks: List[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """Suggest remedial or new curriculum blocks based on performance and feedback.

    If client is not provided, a properly configured local client is obtained
    automatically via the central LLM factory.
    """
    if client is None:
        client = get_llm_client()

    completed_tasks = completed_tasks or []
    performance = performance or {}

    prompt = f"Completed Tasks: {completed_tasks}\nPerformance: {performance}"
    if observer_feedback:
        prompt += f"\nObserver Feedback: {observer_feedback}"
    if possible_blocks:
        prompt += f"\nPossible Blocks: {possible_blocks}"

    response = client.chat.completions.create(
        model=get_model_name(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    # Assuming the response is a JSON list of blocks
    try:
        import json
        return json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, TypeError, AttributeError):
        # Fallback: return empty list if parsing fails
        return []
