from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.skill import Skill, UserSkill
from app.tools.base_tool import BaseTool, ToolError
from datetime import datetime, timezone
from typing import List, Dict


class SkillTool(BaseTool):
    """Tool for skill mastery tracking and CEFR management"""

    async def get_weak_skills(self, user_id: str, threshold: float = 0.6, limit: int = 10) -> List[Dict]:
        """Get skills where mastery is below threshold"""
        result = await self.db.execute(
            select(UserSkill)
            .where(UserSkill.user_id == user_id)
            .where(UserSkill.mastery < threshold)
            .order_by(UserSkill.mastery.asc())
            .limit(limit)
        )
        weak_skills = result.scalars().all()
        return [
            {
                "skill_id": ws.skill_id,
                "mastery": ws.mastery,
                "last_attempt": ws.last_attempt,
                "evidence_count": ws.evidence_count
            }
            for ws in weak_skills
        ]

    async def update_mastery(self, user_id: str, skill_id: int, score: float, evidence: str = "") -> UserSkill:
        """Update or create user skill mastery"""
        if not (0.0 <= score <= 1.0):
            raise ToolError("INVALID_MASTERY_SCORE", "Mastery must be between 0.0 and 1.0")

        # Find existing
        result = await self.db.execute(
            select(UserSkill).where(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == skill_id
            )
        )
        user_skill = result.scalar_one_or_none()

        if user_skill:
            # Update existing
            user_skill.mastery = (user_skill.mastery * user_skill.evidence_count + score) / (user_skill.evidence_count + 1)
            user_skill.evidence_count += 1
            user_skill.last_attempt = datetime.now(timezone.utc)
            if evidence:
                user_skill.notes = evidence
            await self.safe_commit()
        else:
            # Create new
            user_skill = UserSkill(
                user_id=user_id,
                skill_id=skill_id,
                mastery=score,
                evidence_count=1,
                last_attempt=datetime.now(timezone.utc),
                notes=evidence
            )
            self.db.add(user_skill)
            await self.safe_commit()
        await self.db.refresh(user_skill)
        return user_skill

    async def get_skill_tree(self, user_id: str) -> Dict:
        """Return overview of all skills for a user"""
        result = await self.db.execute(
            select(UserSkill).where(UserSkill.user_id == user_id)
        )
        skills = result.scalars().all()
        return {
            "total_skills": len(skills),
            "average_mastery": sum(s.mastery for s in skills) / len(skills) if skills else 0.0,
            "skills": [{"skill_id": s.skill_id, "mastery": s.mastery} for s in skills]
        }
