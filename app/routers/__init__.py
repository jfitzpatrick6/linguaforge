"""
Router package exports.

All routers are currently stub implementations. Real business logic
and dependency injection will be added in Phase 4.
"""
from app.routers.profile_router import profile_router
from app.routers.lesson_router import lesson_router
from app.routers.curriculum_router import curriculum_router
from app.routers.chat_router import chat_router

__all__ = [
    "profile_router",
    "lesson_router",
    "curriculum_router",
    "chat_router",
]