import pytest
from app.tools.base_tool import BaseTool, ToolError
from unittest.mock import AsyncMock

def test_tool_error_creation():
    error = ToolError(code="TEST_ERROR", message="Something went wrong")
    assert error.code == "TEST_ERROR"
    assert "Something went wrong" in str(error)

@pytest.mark.asyncio
async def test_base_tool_safe_commit():
    mock_db = AsyncMock()
    tool = BaseTool(mock_db)
    await tool.safe_commit()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_base_tool_safe_commit_rollback():
    mock_db = AsyncMock()
    mock_db.commit.side_effect = Exception("Database error")
    tool = BaseTool(mock_db)
    with pytest.raises(ToolError) as exc_info:
        await tool.safe_commit()
    mock_db.rollback.assert_called_once()
    assert exc_info.value.code == "DB_COMMIT_ERROR"
    assert "Database error" in str(exc_info.value)
