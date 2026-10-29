"""Shared pytest configuration."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip tests marked ``data`` whose files (paths relative to the repository root) are absent,
    so that the suite runs offline on a clean clone."""
    for item in items:
        marker = item.get_closest_marker("data")
        if marker is None:
            continue
        if not marker.args:
            raise pytest.UsageError(f"{item.nodeid}: @pytest.mark.data needs at least one path")
        missing = [path for path in marker.args if not (ROOT / path).exists()]
        if missing:
            item.add_marker(pytest.mark.skip(reason=f"data not downloaded: {', '.join(missing)}"))
