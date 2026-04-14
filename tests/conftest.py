from pathlib import Path

import pytest


@pytest.fixture
def fake_istool() -> Path:
    """Absolute path to the argv-echoing fake istool binary."""
    return (Path(__file__).parent / "fixtures" / "fake_istool.sh").resolve()
