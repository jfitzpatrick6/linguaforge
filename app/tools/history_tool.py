from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.history import SessionLog
from app.tools.base_tool import BaseTool, ToolError
from datetime import datetime, timezone
from typing import List, Dict


class HistoryTool(BaseTool):
    """Tool for logging user activity (lessons, quizzes, conversations)"""

    async def log_session(self, user_id: str, session_type: str,
                          data: dict, duration_minutes: int = 0) -> SessionLog:
        """Log a learning session"""
        log = SessionLog(
            user_id=user_id,
            session_type=session_type,  # "lesson", "quiz", "voice_chat", etc.
            data=data,                  # JSON-able dict with details
            duration_minutes=duration_minutes,
            timestamp=datetime.now(timezone.utc)
        )
        self.db.add(log)
        await self.safe_commit()
        await self.db.refresh(log)
        return log

    async def get_recent_sessions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent activity for a user"""
        result = await self.db.execute(
            select(SessionLog)
            .where(SessionLog.user_id == user_id)
            .order_by(SessionLog.timestamp.desc())
            .limit(limit)
        )
        logs = result.scalars().all()
        return [
            {
                "id": log.id,
                "session_type": log.session_type,
                "timestamp": log.timestamp,
                "duration_minutes": log.duration_minutes,
                "summary": log.data.get("summary", "") if isinstance(log.data, dict) else ""
            }
            for log in logs
        ]
