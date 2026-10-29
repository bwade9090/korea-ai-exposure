"""Shared pytest configuration."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip tests marked ``data`` when any file named by any of their ``data`` markers (paths
    relative to the repository root) is absent, so that the suite runs offline on a clean clone."""
    for item in items:
        markers = list(item.iter_markers("data"))
        if not markers:
            continue
        if any(not marker.args for marker in markers):
            raise pytest.UsageError(f"{item.nodeid}: @pytest.mark.data needs at least one path")
        missing = [path for marker in markers for path in marker.args if not (ROOT / path).exists()]
        if missing:
            item.add_marker(pytest.mark.skip(reason=f"data not downloaded: {', '.join(missing)}"))
