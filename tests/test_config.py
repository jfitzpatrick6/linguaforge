import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.core.config import settings

def test_settings_loaded():
    assert settings.AI_BASE_URL is not None
    assert settings.AI_MODEL is not None
    print("✅ Settings loaded correctly")