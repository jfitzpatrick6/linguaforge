"""
CurriculumTool — Core tool for managing a user's personal learning curriculum.

Design principles (Phase 1):
- Hybrid model: seed blocks (core progression) + agent-created remedial/advancement blocks.
- No dedicated Lesson table for MVP. Lessons are generated on-demand by the
  LessonGeneratorAgent using RAG and recorded in SessionLog.
- All operations are user-scoped and safe (via BaseTool).
- Designed to be composed with SkillTool (for weak skill detection) and
  HistoryTool (for progress context) at the router/service layer.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import CurriculumBlock
from app.tools.base_tool import BaseTool, ToolError


# Status constants (keeps strings consistent)
STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"
STATUS_PAUSED = "paused"
STATUS_ARCHIVED = "archived"

SOURCE_SEED = "seed"
SOURCE_AGENT_REMEDIAL = "agent_remedial"
SOURCE_AGENT_ADVANCEMENT = "agent_advancement"


class CurriculumTool(BaseTool):
    """Manage curriculum blocks and learning progression (hybrid seed + agent model)."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    # ------------------------------------------------------------------ #
    # Query methods
    # ------------------------------------------------------------------ #

    async def get_active_block(self, user_id: str) -> Optional[CurriculumBlock]:
        """Return the user's single lowest-order active block (if any)."""
        result = await self.db.execute(
            select(CurriculumBlock)
            .where(
                CurriculumBlock.user_id == user_id,
                CurriculumBlock.status == STATUS_ACTIVE,
            )
            .order_by(CurriculumBlock.order_index.asc())
            .limit(1)
        )
        return result.scalars().first()

    async def list_blocks(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[CurriculumBlock]:
        """List blocks for a user, optionally filtered by status."""
        stmt = select(CurriculumBlock).where(CurriculumBlock.user_id == user_id)

        if status:
            stmt = stmt.where(CurriculumBlock.status == status)

        stmt = stmt.order_by(CurriculumBlock.order_index.asc()).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_block(self, block_id: int, user_id: str) -> Optional[CurriculumBlock]:
        """Fetch a specific block (ownership check)."""
        result = await self.db.execute(
            select(CurriculumBlock).where(
                CurriculumBlock.id == block_id,
                CurriculumBlock.user_id == user_id,
            )
        )
        return result.scalars().first()

    # ------------------------------------------------------------------ #
    # Mutation methods
    # ------------------------------------------------------------------ #

    async def create_block(
        self,
        user_id: str,
        title: str,
        cefr_level: str = "A1",
        language: str = "es",
        description: str = "",
        source: str = SOURCE_SEED,
        targeted_skill_ids: Optional[str] = None,
        order_index: Optional[int] = None,
    ) -> CurriculumBlock:
        """
        Create a new curriculum block.

        If order_index is not provided, it will be set to (max existing + 1).
        """
        if order_index is None:
            order_index = await self._next_order_index(user_id)

        block = CurriculumBlock(
            user_id=user_id,
            title=title,
            description=description or title,
            language=language,
            cefr_level=cefr_level,
            status=STATUS_ACTIVE,
            source=source,
            targeted_skill_ids=targeted_skill_ids,
            order_index=order_index,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(block)
        await self.safe_commit()
        await self.db.refresh(block)
        return block

    async def get_or_create_active_block(
        self,
        user_id: str,
        language: str = "es",
        default_cefr: str = "A1",
    ) -> CurriculumBlock:
        """
        Convenience for flows that always need "something active".

        If the user has no active block, creates a basic starter one.
        """
        active = await self.get_active_block(user_id)
        if active:
            return active

        return await self.create_block(
            user_id=user_id,
            title=f"Getting Started ({default_cefr})",
            cefr_level=default_cefr,
            language=language,
            description="Initial block created automatically.",
            source=SOURCE_SEED,
        )

    async def complete_block(self, block_id: int, user_id: str) -> CurriculumBlock:
        """Mark a block completed and set the completion timestamp."""
        block = await self.get_block(block_id, user_id)
        if not block:
            raise ToolError("BLOCK_NOT_FOUND", f"Block {block_id} not found for user {user_id}")

        if block.status == STATUS_COMPLETED:
            return block

        block.status = STATUS_COMPLETED
        block.completed_at = datetime.now(timezone.utc)
        await self.safe_commit()
        await self.db.refresh(block)
        return block

    async def create_remedial_block(
        self,
        user_id: str,
        title: str,
        cefr_level: str,
        language: str = "es",
        description: str = "",
        targeted_skill_ids: Optional[str] = None,
    ) -> CurriculumBlock:
        """
        Create a remedial block (typically called by CurriculumAgent or
        after detecting weak skills via SkillTool).
        """
        return await self.create_block(
            user_id=user_id,
            title=title,
            cefr_level=cefr_level,
            language=language,
            description=description,
            source=SOURCE_AGENT_REMEDIAL,
            targeted_skill_ids=targeted_skill_ids,
        )

    # ------------------------------------------------------------------ #
    # Higher-level / overview methods
    # ------------------------------------------------------------------ #

    async def get_curriculum_overview(self, user_id: str) -> Dict[str, Any]:
        """Return a convenient summary for UI / agent consumption."""
        blocks = await self.list_blocks(user_id)

        active = [b for b in blocks if b.status == STATUS_ACTIVE]
        completed = [b for b in blocks if b.status == STATUS_COMPLETED]

        next_block = active[0] if active else None

        return {
            "total_blocks": len(blocks),
            "active_count": len(active),
            "completed_count": len(completed),
            "next_block": {
                "id": next_block.id,
                "title": next_block.title,
                "cefr_level": next_block.cefr_level,
                "language": next_block.language,
                "order_index": next_block.order_index,
            } if next_block else None,
            "recent_completed": [
                {"id": b.id, "title": b.title, "completed_at": b.completed_at}
                for b in sorted(completed, key=lambda x: x.completed_at or x.created_at, reverse=True)[:3]
            ],
        }

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    async def _next_order_index(self, user_id: str) -> int:
        """Return the next safe order_index for a new block for this user."""
        result = await self.db.execute(
            select(func.max(CurriculumBlock.order_index)).where(
                CurriculumBlock.user_id == user_id
            )
        )
        max_idx = result.scalar_one_or_none()
        return (max_idx or 0) + 1

    # ------------------------------------------------------------------ #
    # Seeding
    # ------------------------------------------------------------------ #

    async def seed_initial_curriculum(
        self,
        user_id: str,
        language: str = "es",
        starting_cefr: str = "A1",
    ) -> List[CurriculumBlock]:
        """
        Seed a sensible starter curriculum for a new user.

        Idempotent: does nothing if the user already has blocks.
        """
        existing = await self.list_blocks(user_id, limit=1)
        if existing:
            return existing

        seeds = [
            {
                "title": "Greetings & Introductions",
                "cefr_level": starting_cefr,
                "description": "Basic hellos, goodbyes, name exchanges, and polite phrases.",
            },
            {
                "title": "Numbers, Time & Dates",
                "cefr_level": starting_cefr,
                "description": "Counting, telling time, days, months, and scheduling basics.",
            },
            {
                "title": "Food, Drink & Ordering",
                "cefr_level": starting_cefr,
                "description": "Menu vocabulary, ordering at cafes/restaurants, likes/dislikes.",
            },
            {
                "title": "Everyday Situations",
                "cefr_level": starting_cefr,
                "description": "Shopping, asking for directions, simple transactions.",
            },
            {
                "title": "Present Tense Foundations",
                "cefr_level": starting_cefr,
                "description": "Core present tense verbs and simple sentence construction.",
            },
        ]

        created: List[CurriculumBlock] = []
        for idx, seed in enumerate(seeds):
            block = await self.create_block(
                user_id=user_id,
                title=seed["title"],
                cefr_level=seed["cefr_level"],
                language=language,
                description=seed["description"],
                source=SOURCE_SEED,
                order_index=idx,
            )
            created.append(block)

        return created
