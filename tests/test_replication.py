"""Replication of PLAN §3 and Phase 2.4 from the pinned files. Needs `make fetch`; skipped
otherwise (CI runs offline)."""

import pytest

from korea_ai_exposure import aei, aui, paths, replication

PINNED = [r.file for r in aei.RELEASES] + [aei.ISO_CODES, aui.WORKING_AGE_POP]
pytestmark = pytest.mark.data(
    *(p.relative_to(paths.ROOT).as_posix() for p in [*PINNED, replication.JOB_EXPOSURE])
)

ROWS = {
    "2025-09-15": 136_705,  # 136,845 published rows less 140 zero-filled usage rows
    "2026-01-15": 458_778,
    "2026-03-24": 477_717,
    "2026-06-26": 1_636_573,
}


@pytest.mark.parametrize(("release", "rows"), ROWS.items())
def test_every_release_loads_with_its_expected_row_count(release, rows):
    assert len(aei.load(release)) == rows


@pytest.mark.parametrize("release", ["2025-09-15", "2026-01-15", "2026-03-24"])
def test_no_whole_geography_usage_count_is_zero(release):
    frame = aei.load(release)
    for level in ("country", "subregion"):
        assert (aei.geo_values(frame, level, "usage_count") > 0).all()


def test_august_2025_has_the_countries_of_the_raw_file():
    counts = aei.geo_values(aei.load("2025-09-15"), "country", "usage_count")
    assert len(counts) == 173  # 172 countries and not_classified, as in the raw file
    assert counts.min() >= 15


def test_every_replication_check_passes():
    checks = replication.run()
    failed = [check for check in checks if not check.passed]
    assert not failed, replication.to_markdown(failed)
