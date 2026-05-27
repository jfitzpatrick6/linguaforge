"""
Reviewer Agent — Analyzes tool usage and errors.

Primarily useful for robust agent loops and giving users helpful
feedback when something goes wrong with tools.
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI

from app.core.llm import get_llm_client, get_model_name
from app.agents.schemas import ToolReview


SYSTEM_PROMPT = """You are a precise debugging assistant for tool-using systems.

Given tool calls and an optional error, produce a short analysis and concrete fixes.

Respond with JSON:
{
  "analysis": "what happened",
  "suggested_fixes": ["action 1", "action 2"],
  "confidence": "low" | "medium" | "high"
}
"""


class ReviewerAgent:
    """Reviews tool calls and suggests fixes."""

    def __init__(self, client: Optional[OpenAI] = None):
        self.client = client or get_llm_client()

    def review(
        self,
        *,
        tool_calls: List[Dict[str, Any]] = None,
        error: Optional[str] = None,
        context: str = "",
    ) -> ToolReview:
        tool_calls = tool_calls or []

        prompt = f"Context: {context}\n\nTool Calls: {tool_calls}"
        if error:
            prompt += f"\n\nError: {error}"

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
            return ToolReview.model_validate_json(content)
        except Exception:
            return ToolReview(
                analysis="Unable to analyze the tool call.",
                suggested_fixes=["Retry the operation."],
                confidence="low",
            )


# Legacy function
def review_tool_usage(
    client: Optional[OpenAI] = None,
    tool_calls: List[Dict[str, Any]] = None,
    error: Optional[str] = None,
    context: str = "",
) -> str:
    agent = ReviewerAgent(client=client)
    review = agent.review(tool_calls=tool_calls, error=error, context=context)
    return review.model_dump_json()