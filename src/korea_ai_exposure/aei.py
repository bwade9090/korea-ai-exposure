"""Anthropic Economic Index (AEI): the releases this project uses, and adapters that turn each
release's schema into one canonical long table (PLAN 2.2).

Canonical columns (``COLUMNS``):

- ``release``: the release date, for example ``2026-01-15``;
- ``period_start``, ``period_end``: ISO dates, ``period_end`` exclusive. The weekly releases
  sample one week, so their ``date_end`` is read as exclusive and must be seven days after
  ``date_start``;
- ``geo_level``: ``global``, ``country`` or ``subregion``;
- ``geo_id``: ``GLOBAL``; ISO 3166-1 alpha-3 for countries (two-letter codes are mapped with the
  release's own ISO table); ISO 3166-2 for subregions (bare US state codes in release
  2025-09-15 become ``US-CA``). Pseudo-geographies keep their source IDs: ``not_classified``,
  ``NONE``, ``US-not_classified``;
- ``facet``, ``hierarchy_level``, ``node_id``, ``node_name``, ``metric``, ``value``.

Facet and metric names stay as published: they differ between releases because the methods do
(ADR 0006). The weekly releases have no node IDs, so ``node_id`` repeats the cluster name. Rows
about a whole geography have an empty ``node_id`` in every release.

A missing row means "not published", never zero (CLAUDE.md). The enriched file of release
2025-09-15 adds every country with a population but no published usage, with zero usage values
(28 countries); their usage rows are dropped, and their population and GDP rows kept. The raw
files publish no count below 15, so a zero count can only come from that fill.
"""

from dataclasses import dataclass
from functools import cache
from pathlib import Path

import pandas as pd

from korea_ai_exposure import paths

HF_COMMIT = "4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6"
COLUMNS = (
    "release",
    "period_start",
    "period_end",
    "geo_level",
    "geo_id",
    "facet",
    "hierarchy_level",
    "node_id",
    "node_name",
    "metric",
    "value",
)
GEO_LEVELS = frozenset({"global", "country", "subregion"})
PSEUDO_GEO_IDS = frozenset({"not_classified", "NONE"})
LONG_TABLE = paths.INTERIM / "aei_long.parquet"
ISO_CODES = paths.RAW / "aei/release_2025_09_15/iso_country_codes.csv"

_WEEKLY_COLUMNS = (
    "geo_id",
    "geography",
    "date_start",
    "date_end",
    "platform_and_product",
    "facet",
    "level",
    "variable",
    "cluster_name",
    "value",
)
_MONTHLY_COLUMNS = (
    "date_start",
    "date_end",
    "geo_id",
    "geo_level",
    "category_name",
    "hierarchy_level",
    "metric_id",
    "value",
    "node_name",
    "node_external_id",
)
_WEEKLY_GEOGRAPHY = {
    "global": "global",
    "country": "country",
    "country-state": "subregion",
    "state_us": "subregion",
}
CANONICAL_KEY = [
    "release",
    "period_start",
    "geo_level",
    "geo_id",
    "facet",
    "hierarchy_level",
    "metric",
    "node_id",
]
# Usage metrics that the 2025-09-15 enrichment fills with zeros for countries without usage.
_ZERO_FILLED_METRICS = frozenset(
    {"usage_count", "usage_pct", "usage_per_capita", "usage_per_capita_index", "usage_tier"}
)


@dataclass(frozen=True)
class Release:
    release: str
    source: str  # ID in docs/DATA_SOURCES.md
    path: str  # under data/raw/, as pinned in data/manifest.json
    schema: str  # "weekly" (releases 2025-09-15 to 2026-03-24) or "monthly" (2026-06-26)
    product: str  # product scope as documented by the release

    @property
    def file(self) -> Path:
        return paths.RAW / self.path


RELEASES = (
    Release(
        "2025-09-15",
        "AEI-2025-09",
        "aei/release_2025_09_15/aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv",
        "weekly",
        "Claude.ai Free and Pro",
    ),
    Release(
        "2026-01-15",
        "AEI-2026-01",
        "aei/release_2026_01_15/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv",
        "weekly",
        "Claude.ai Free and Pro (the online appendix says Free, Pro and Max)",
    ),
    Release(
        "2026-03-24",
        "AEI-2026-03",
        "aei/release_2026_03_24/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv",
        "weekly",
        "Claude.ai Free, Pro and Max",
    ),
    Release(
        "2026-06-26",
        "AEI-2026-06",
        "aei/release_2026_06_26/aei_claude_ai_2026-06-26.csv",
        "monthly",
        "Claude chat and Cowork, Free, Pro and Max",
    ),
)


def get_release(name: str) -> Release:
    for release in RELEASES:
        if release.release == name:
            return release
    raise KeyError(f"unknown AEI release {name!r}")


def iso2_to_iso3(path: Path | None = None) -> dict[str, str]:
    """ISO 3166-1 alpha-2 to alpha-3, from the table shipped with release 2025-09-15. Read with
    ``keep_default_na=False``: Namibia's code is ``NA``."""
    path = path or ISO_CODES
    table = pd.read_csv(path, keep_default_na=False, dtype=str)
    mapping = dict(zip(table["iso_alpha_2"], table["iso_alpha_3"], strict=True))
    if len(mapping) != len(table):
        raise ValueError(f"{path}: duplicate ISO alpha-2 codes")
    return mapping


def read_weekly(path: Path, release: str, iso_map: dict[str, str]) -> pd.DataFrame:
    """Adapt a raw or enriched weekly file (releases 2025-09-15 to 2026-03-24)."""
    raw = pd.read_csv(path, keep_default_na=False, dtype=str, usecols=list(_WEEKLY_COLUMNS))
    _require_one(raw, "platform_and_product", path)
    geo_level = raw["geography"].map(_WEEKLY_GEOGRAPHY)
    if geo_level.isna().any():
        unknown = sorted(set(raw.loc[geo_level.isna(), "geography"]))
        raise ValueError(f"{path}: unknown geography values {unknown}")
    geo_id = raw["geo_id"].copy()
    two_letter = (raw["geography"] == "country") & raw["geo_id"].str.fullmatch(r"[A-Z]{2}")
    unmapped = sorted(set(raw.loc[two_letter, "geo_id"]) - set(iso_map))
    if unmapped:
        raise ValueError(f"{path}: country codes without an ISO alpha-3 mapping: {unmapped}")
    geo_id[two_letter] = raw.loc[two_letter, "geo_id"].map(iso_map)
    states = raw["geography"] == "state_us"
    geo_id[states] = "US-" + raw.loc[states, "geo_id"]
    start = pd.to_datetime(raw["date_start"], format="%Y-%m-%d")
    end = pd.to_datetime(raw["date_end"], format="%Y-%m-%d")
    if not ((end - start) == pd.Timedelta(days=7)).all():
        raise ValueError(f"{path}: expected one-week windows (date_end = date_start + 7 days)")
    frame = pd.DataFrame(
        {
            "release": release,
            "period_start": raw["date_start"],
            "period_end": raw["date_end"],
            "geo_level": geo_level,
            "geo_id": geo_id,
            "facet": raw["facet"],
            "hierarchy_level": raw["level"].astype("int64"),
            "node_id": raw["cluster_name"],
            "node_name": raw["cluster_name"],
            "metric": raw["variable"],
            "value": pd.to_numeric(raw["value"], errors="raise"),
        }
    )
    return _drop_zero_fill(frame)


def _drop_zero_fill(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop the usage rows of geographies whose whole-geography usage count is zero: unpublished,
    not zero (see the module docstring)."""
    zero = (frame["node_id"] == "") & (frame["metric"] == "usage_count") & (frame["value"] == 0)
    filled = frame.loc[zero, "geo_id"].unique()
    if len(filled) == 0:
        return frame
    drop = frame["geo_id"].isin(filled) & frame["metric"].isin(_ZERO_FILLED_METRICS)
    return frame[~drop].reset_index(drop=True)


def read_monthly(path: Path, release: str) -> pd.DataFrame:
    """Adapt the monthly file of release 2026-06-26. ``node_external_id`` ``-`` marks rows about
    a whole geography and becomes an empty ``node_id``."""
    raw = pd.read_csv(path, keep_default_na=False, dtype=str, usecols=list(_MONTHLY_COLUMNS))
    unknown = sorted(set(raw["geo_level"]) - GEO_LEVELS)
    if unknown:
        raise ValueError(f"{path}: unknown geo_level values {unknown}")
    return pd.DataFrame(
        {
            "release": release,
            "period_start": raw["date_start"],
            "period_end": raw["date_end"],
            "geo_level": raw["geo_level"],
            "geo_id": raw["geo_id"],
            "facet": raw["category_name"],
            "hierarchy_level": raw["hierarchy_level"].astype("int64"),
            "node_id": raw["node_external_id"].replace("-", ""),
            "node_name": raw["node_name"],
            "metric": raw["metric_id"],
            "value": pd.to_numeric(raw["value"], errors="raise"),
        }
    )


def load(name: str) -> pd.DataFrame:
    """One release in canonical form. The parsed release is cached; each call returns a shallow
    copy, which (under pandas copy-on-write) shares the data but keeps caller edits local."""
    return _load(name).copy(deep=False)


@cache
def _load(name: str) -> pd.DataFrame:
    release = get_release(name)
    if release.schema == "weekly":
        frame = read_weekly(release.file, release.release, iso2_to_iso3())
    else:
        frame = read_monthly(release.file, release.release)
    check_long(frame)
    return frame


def load_all() -> pd.DataFrame:
    return pd.concat([load(r.release) for r in RELEASES], ignore_index=True)


def geo_values(
    frame: pd.DataFrame, geo_level: str, metric: str, period_start: str | None = None
) -> pd.Series:
    """Whole-geography values (empty ``node_id``) of ``metric``, for example ``usage_count``,
    ``usage_pct``, ``usage_per_capita_index`` or ``ai_autonomy_mean``, in one release's canonical
    frame, indexed by ``geo_id``. A release with several periods (2026-06-26) needs
    ``period_start``. Raises ``ValueError`` when nothing matches. Categorical metrics of the
    weekly releases (``human_only_ability_pct``, ``multitasking_pct``) have one row per category
    and no whole-geography row; select their category node instead."""
    rows = frame[
        (frame["geo_level"] == geo_level) & (frame["metric"] == metric) & (frame["node_id"] == "")
    ]
    if period_start is not None:
        rows = rows[rows["period_start"] == period_start]
    if rows.empty:
        when = f" in {period_start}" if period_start else ""
        raise ValueError(f"no whole-geography {metric} rows at {geo_level} level{when}")
    if rows["period_start"].nunique() > 1:
        raise ValueError(f"{metric}: several periods; pass period_start")
    if rows["geo_id"].duplicated().any():
        raise ValueError(f"{metric}: several values per geo_id at {geo_level} level")
    return rows.set_index("geo_id")["value"].rename(metric)


def check_long(frame: pd.DataFrame) -> None:
    """Invariants of the canonical table; raises ``ValueError`` on the first violation."""
    if tuple(frame.columns) != COLUMNS:
        raise ValueError(f"columns {tuple(frame.columns)} differ from {COLUMNS}")
    if frame.isna().any().any():
        raise ValueError("missing values in the canonical table")
    if not set(frame["geo_level"]) <= GEO_LEVELS:
        raise ValueError(f"unknown geo_level values {sorted(set(frame['geo_level']) - GEO_LEVELS)}")
    countries = frame.loc[frame["geo_level"] == "country", "geo_id"]
    bad = sorted(set(countries[~countries.str.fullmatch(r"[A-Z]{3}")]) - PSEUDO_GEO_IDS)
    if bad:
        raise ValueError(f"country IDs that are neither ISO alpha-3 nor pseudo: {bad}")
    subregions = frame.loc[frame["geo_level"] == "subregion", "geo_id"]
    bad = sorted(set(subregions[~subregions.str.match(r"[A-Z]{2}-")]))
    if bad:
        raise ValueError(f"subregion IDs without a country prefix: {bad}")
    if not set(frame.loc[frame["geo_level"] == "global", "geo_id"]) <= {"GLOBAL"}:
        raise ValueError("global rows must have geo_id GLOBAL")
    if not (frame["period_end"] > frame["period_start"]).all():
        raise ValueError("period_end must be after period_start")


def build(path: Path = LONG_TABLE) -> pd.DataFrame:
    """Write every release in canonical form to ``path`` (Parquet), sorted deterministically."""
    frame = load_all()
    check_long(frame)
    if frame.duplicated(CANONICAL_KEY).any():
        raise ValueError(f"the canonical key {CANONICAL_KEY} is not unique")
    frame = frame.sort_values(CANONICAL_KEY, kind="stable", ignore_index=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return frame


def _require_one(frame: pd.DataFrame, column: str, path: Path) -> None:
    values = sorted(set(frame[column]))
    if len(values) != 1:
        raise ValueError(f"{path}: expected one {column}, found {values}")
