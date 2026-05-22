from typing import Dict, Any
from openai import OpenAI

SYSTEM_PROMPT = """
You are a lesson generator agent that creates personalized learning content based on user skill level and grounding RAG.

You will receive:
- A user's skill level (e.g., beginner, intermediate, advanced)
- A task or topic to teach
- Retrieved relevant context from a RAG system (e.g., documentation, examples, code snippets)

Your task is to:
1. Generate a concise, structured lesson that matches the user's skill level
2. Use the RAG context to ensure accuracy and relevance
3. Include:
   - A brief explanation
   - Code examples (if applicable)
   - Common pitfalls and how to avoid them
   - Suggested next steps

Ensure the tone is supportive and pedagogical. Avoid jargon unless defined.
"""

def generate_lesson(client: OpenAI, skill_level: str, topic: str, rag_context: str) -> str:
    """Generate a personalized lesson based on skill level and RAG context."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Skill Level: {skill_level}\nTopic: {topic}\nRAG Context: {rag_context}"}
        ]
    )
    return response.choices[0].message.content
