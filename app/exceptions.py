"""
Central exception definitions for LinguaForge.

Re-exports ToolError from the tool layer for convenience so that
`from app.exceptions import ToolError` works everywhere (including
in legacy code and the curriculum tool).
"""
from app.tools.base_tool import ToolError

__all__ = ["ToolError"]