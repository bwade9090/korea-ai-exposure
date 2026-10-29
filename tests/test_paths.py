"""Repository paths resolve inside this checkout (the package is installed in editable mode)."""

from korea_ai_exposure import paths


def test_root_is_the_repository():
    assert (paths.ROOT / "pyproject.toml").is_file()
    assert (paths.ROOT / "CLAUDE.md").is_file()


def test_data_paths_sit_under_data():
    for path in (paths.RAW, paths.MANUAL, paths.INTERIM, paths.PROCESSED, paths.MANIFEST):
        assert path.parent == paths.DATA
    assert paths.DATA == paths.ROOT / "data"
