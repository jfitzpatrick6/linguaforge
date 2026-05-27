from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from app.dependencies import (
    get_history_tool,
    get_observer_agent,
)
from app.tools import HistoryTool
from app.agents import ObserverAgent

chat_router = APIRouter()


class SessionLogRequest(BaseModel):
    user_id: str
    session_type: str = "lesson"  # lesson, quiz, chat, assessment, etc.
    data: Dict[str, Any] = Field(default_factory=dict)
    duration_minutes: int = 0
    summary: Optional[str] = None


class SessionLogResponse(BaseModel):
    id: int
    user_id: str
    session_type: str
    timestamp: str
    duration_minutes: int


class ObservationResponse(BaseModel):
    summary: str
    strengths: List[str]
    areas_for_improvement: List[str]
    suggested_next_steps: List[str]


@chat_router.post("/sessions/log", response_model=SessionLogResponse)
async def log_session(
    payload: SessionLogRequest,
    history_tool: HistoryTool = Depends(get_history_tool),
):
    """Log any learning session (lesson, practice, chat, etc.)."""
    log = await history_tool.log_session(
        user_id=payload.user_id,
        session_type=payload.session_type,
        data=payload.data,
        duration_minutes=payload.duration_minutes,
    )
    return log


@chat_router.post("/sessions/{user_id}/observe", response_model=ObservationResponse)
async def get_session_observation(
    user_id: str,
    recent_limit: int = 3,
    history_tool: HistoryTool = Depends(get_history_tool),
    observer: ObserverAgent = Depends(get_observer_agent),
):
    """
    Get an AI-generated reflection on the user's recent activity.
    Useful after a study session.
    """
    sessions = await history_tool.get_recent_sessions(user_id, limit=recent_limit)

    if not sessions:
        raise HTTPException(status_code=404, detail="No recent sessions found for observation")

    # Build a simple summary for the observer
    task_summary = f"Recent {len(sessions)} learning sessions for user {user_id}"
    actions = [{"type": s["session_type"], "time": str(s["timestamp"])} for s in sessions]

    observation = observer.observe(
        task_summary=task_summary,
        actions=actions,
        final_state="Completed recent learning activities.",
    )

    return observation


# Simple chat placeholder (can be expanded later into a full conversational agent)
@chat_router.post("/chat")
async def send_message(payload: dict):
    """
    Very thin chat endpoint for MVP.
    Future: wire in an agent loop that can call tools.
    """
    return {
        "reply": "Thanks for your message! Full conversational agent coming soon.",
        "echo": payload.get("message", ""),
    }
