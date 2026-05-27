from typing import List, Dict, Any
from openai import OpenAI

from app.core.llm import get_llm_client, get_model_name

SYSTEM_PROMPT = """
You are a reviewer agent responsible for analyzing tool usage and identifying errors.

You will receive:
- A list of tool calls made by the user
- The error message (if any) returned by the tool
- The context of the task

Your task is to:
1. Analyze the error and determine the root cause
2. Suggest a corrected tool call or a sequence of actions to fix the issue
3. If no error, confirm success and suggest possible improvements

Provide clear, actionable advice. Use minimal, precise language. Avoid over-explaining.
"""

def review_tool_usage(
    client: OpenAI | None = None,
    tool_calls: List[Dict[str, Any]] = None,
    error: str = None,
    context: str = "",
) -> str:
    """Analyze tool usage and suggest remediation.

    If client is not provided, a properly configured local client is obtained
    automatically via the central LLM factory.
    """
    if client is None:
        client = get_llm_client()
    tool_calls = tool_calls or []

    prompt = f"Context: {context}\n\nTool Calls: {tool_calls}"
    if error:
        prompt += f"\n\nError: {error}"

    response = client.chat.completions.create(
        model=get_model_name(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content or ""
