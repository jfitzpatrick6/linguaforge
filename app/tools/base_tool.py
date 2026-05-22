from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic
from dataclasses import dataclass

T = TypeVar("T")

@dataclass
class ToolError(Exception):
    code: str
    message: str
    details: dict = None


class BaseTool:
    """Base class for all tools with common error handling"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def safe_commit(self):
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise ToolError("DB_COMMIT_ERROR", str(e)) from e
