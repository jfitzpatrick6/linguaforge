import pytest
from app.tools.base_tool import BaseTool, ToolError

def test_tool_error_creation():
    error = ToolError(code="TEST_ERROR", message="Test message")
    assert error.code == "TEST_ERROR"
    assert str(error) == "TEST_ERROR: Test message"
