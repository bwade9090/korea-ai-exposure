"""The ``data`` marker hook in conftest.py, run in a separate pytest process."""

from pathlib import Path

import pytest

pytest_plugins = ["pytester"]

ROOT = Path(__file__).resolve().parents[1]

TESTS = """
import pytest

pytestmark = pytest.mark.data("present.txt")


def test_present():
    pass


@pytest.mark.data("absent.txt")
def test_absent():
    pass


@pytest.mark.data("present.txt")
@pytest.mark.data("absent.txt")
def test_stacked_with_one_absent():
    pass
"""


@pytest.fixture
def project(pytester):
    pytester.makeini("[pytest]\nmarkers =\n    data(*paths): needs downloaded files\n")
    (pytester.path / "tests").mkdir()
    conftest = (ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
    (pytester.path / "tests" / "conftest.py").write_text(conftest, encoding="utf-8")
    (pytester.path / "present.txt").write_text("x", encoding="utf-8")
    return pytester


def test_missing_files_skip_and_present_files_run(project):
    (project.path / "tests" / "test_marked.py").write_text(TESTS, encoding="utf-8")
    result = project.runpytest_subprocess("tests", "-p", "no:cacheprovider")
    result.assert_outcomes(passed=1, skipped=2)


def test_a_marker_without_paths_is_a_usage_error(project):
    (project.path / "tests" / "test_bare.py").write_text(
        "import pytest\n\n\n@pytest.mark.data\ndef test_bare():\n    pass\n", encoding="utf-8"
    )
    result = project.runpytest_subprocess("tests", "-p", "no:cacheprovider")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
