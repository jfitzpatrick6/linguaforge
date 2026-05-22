from sqlalchemy.orm import Session
from app.models import Skill, SkillProgress
from app.exceptions import ToolError
from typing import List


class SkillTool:
    """Manage skills and mastery levels."""

    def __init__(self, db: Session):
        self.db = db

    def get_weak_skills(self, user_id: int, threshold: float = 0.5) -> List[Skill]:
        """Get skills with mastery below threshold."""
        skills = self.db.query(Skill).all()
        weak_skills = []
        for skill in skills:
            progress = self.db.query(SkillProgress).filter(
                SkillProgress.user_id == user_id,
                SkillProgress.skill_id == skill.id
            ).first()
            if not progress or progress.mastery < threshold:
                weak_skills.append(skill)
        return weak_skills

    def update_mastery(self, user_id: int, skill_id: int, mastery: float) -> SkillProgress:
        """Update mastery level for a skill."""
        progress = self.db.query(SkillProgress).filter(
            SkillProgress.user_id == user_id,
            SkillProgress.skill_id == skill_id
        ).first()

        if not progress:
            progress = SkillProgress(user_id=user_id, skill_id=skill_id, mastery=mastery)
            self.db.add(progress)
        else:
            progress.mastery = mastery

        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_skill_tree(self, skill_id: int) -> List[Skill]:
        """Get all skills in the tree (e.g., prerequisites and related)."""
        # Placeholder: implement based on model relationships
        return self.db.query(Skill).all()  # Replace with actual tree logic