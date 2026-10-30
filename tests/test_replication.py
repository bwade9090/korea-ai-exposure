"""Replication of PLAN §3 and Phase 2.4 from the pinned files. Needs `make fetch`; skipped
otherwise (CI runs offline)."""

import pytest

from korea_ai_exposure import aei, aui, paths, replication

PINNED = [r.file for r in aei.RELEASES] + [aei.ISO_CODES, aui.WORKING_AGE_POP]
pytestmark = pytest.mark.data(
    *(p.relative_to(paths.ROOT).as_posix() for p in [*PINNED, replication.JOB_EXPOSURE])
)

ROWS = {
    "2025-09-15": 136_845,
    "2026-01-15": 458_778,
    "2026-03-24": 477_717,
    "2026-06-26": 1_636_573,
}


@pytest.mark.parametrize(("release", "rows"), ROWS.items())
def test_every_release_loads_with_its_published_row_count(release, rows):
    assert len(aei.load(release)) == rows


def test_every_replication_check_passes():
    checks = replication.run()
    failed = [check for check in checks if not check.passed]
    assert not failed, replication.to_markdown(failed)
