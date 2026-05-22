from sqlalchemy.orm import Session
from app.models import CurriculumBlock
from app.exceptions import ToolError


class CurriculumTool:
    """Manage curriculum blocks and learning progression."""

    def __init__(self, db: Session):
        self.db = db

    def get_active_block(self, user_id: int) -> CurriculumBlock | None:
        """Retrieve the currently active learning block."""
        return self.db.query(CurriculumBlock).filter(
            CurriculumBlock.user_id == user_id,
            CurriculumBlock.active == True
        ).first()

    def add_remedial_lessons(self, user_id: int, block_id: int, lesson_ids: List[int]) -> bool:
        """Add remedial lessons to a block."""
        block = self.db.query(CurriculumBlock).filter(
            CurriculumBlock.id == block_id,
            CurriculumBlock.user_id == user_id
        ).first()
        if not block:
            raise ToolError(f"Block {block_id} not found for user {user_id}")

        # Add logic to link lessons (e.g., via join table)
        # Placeholder: assuming a many-to-many relation
        block.remedial_lessons.extend(
            self.db.query(Lesson).filter(Lesson.id.in_(lesson_ids)).all()
        )
        self.db.commit()
        return True