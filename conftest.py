import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from app import app


@pytest.fixture
def dash_app():
    return app
