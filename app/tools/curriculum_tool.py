"""
CurriculumTool (temporary skeleton during Phase 0).

The real implementation (full async + BaseTool inheritance + proper methods)
is being written in Phase 0-5. This stub exists only so that package imports
succeed while the rest of stabilization finishes.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import CurriculumBlock
from app.tools.base_tool import BaseTool, ToolError


class CurriculumTool(BaseTool):
    """Manage curriculum blocks and learning progression (hybrid seed + agent model)."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_active_block(self, user_id: str) -> Optional[CurriculumBlock]:
        """Retrieve the user's currently active curriculum block."""
        result = await self.db.execute(
            select(CurriculumBlock).where(
                CurriculumBlock.user_id == user_id,
                CurriculumBlock.status == "active"
            ).order_by(CurriculumBlock.order_index.asc())
        )
        return result.scalars().first()

    async def create_block(
        self,
        user_id: str,
        title: str,
        cefr_level: str = "A1",
        description: str = "",
        source: str = "seed",
        targeted_skill_ids: str | None = None,
    ) -> CurriculumBlock:
        """Create a new curriculum block for the user."""
        block = CurriculumBlock(
            user_id=user_id,
            title=title,
            description=description,
            cefr_level=cefr_level,
            status="active",
            source=source,
            targeted_skill_ids=targeted_skill_ids,
        )
        self.db.add(block)
        await self.safe_commit()
        await self.db.refresh(block)
        return block

    # Additional methods (recommend_remedial, advance, etc.) will be implemented
    # in the full Phase 0-5 rewrite after the schema settles.
