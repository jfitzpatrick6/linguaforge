from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic, Optional
from dataclasses import dataclass

T = TypeVar("T")

@dataclass
class ToolError(Exception):
    """
    Custom error for tool operations.
    
    Attributes:
        code: Unique error code identifying the type of failure
        message: Human-readable description of the error
        details: Optional dictionary with additional context about the error
    """
    code: str
    message: str
    details: Optional[dict] = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class BaseTool:
    """
    Base class for all tools with common patterns.
    
    This class provides a foundation for database operations with safe commit/rollback
    semantics and error handling. All tool classes should inherit from this base.
    
    Attributes:
        db: Async database session used for all database operations
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the tool with a database session.
        
        Args:
            db: Async database session to be used for all operations
        """
        self.db = db

    async def safe_commit(self) -> None:
        """
        Safely commit changes to the database with automatic rollback on failure.
        
        If an exception occurs during commit, the transaction is rolled back and
        a ToolError is raised with details about the original error.
        
        Raises:
            ToolError: If commit fails, with code 'DB_COMMIT_ERROR' and details
                      about the original exception type.
        """
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
        """
        Rollback the current transaction.
        
        This method should be used when an operation fails and you need to
        explicitly rollback the transaction.
        """
        await self.db.rollback()
