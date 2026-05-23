from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic, Optional
from dataclasses import dataclass

T = TypeVar("T")

@dataclass
class ToolError(Exception):
    """Custom error for tool operations"""
    code: str
    message: str
    details: Optional[dict] = None

    def __str__(self):
        return f"{self.code}: {self.message}"

class BaseTool:
    """Base class for all tools with common patterns"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def safe_commit(self) -> None:
        """Safely commit changes with rollback on error"""
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise ToolError(
                code="DB_COMMIT_ERROR",
                message=str(e),
                details={"original_error": type(e).__name__}
            ) from e

    async def safe_rollback(self) -> None:
        """Rollback current transaction"""
        await self.db.rollback()
