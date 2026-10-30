"""Anthropic AI Usage Index (AUI): a country's share of usage over its share of working-age
population (PLAN M1), on the bases Anthropic's releases use (ADR 0006).

Bases (``BASES``):

- ``renormalized`` (the project's headline basis): usage and population shares both taken over
  the ranked countries. The published April and May 2026 values are on this basis.
- ``anthropic_2025``: the rule of the September 2025 enrichment code, which also reproduces the
  January 2026 appendix figures. The usage total sums every row with at least ``floor``
  conversations, pseudo-geographies included; the population total sums the countries among
  those rows that have a population.

Ranked countries: at least ``floor`` conversations (for releases without counts, every
published country), a working-age population, and not excluded (``EXCLUDED_FROM_RANKING``).
Within one snapshot the bases differ by a constant factor, so ranks agree; levels do not.
"""

from pathlib import Path

import pandas as pd

from korea_ai_exposure import paths

FLOOR = 200
BASES = ("renormalized", "anthropic_2025")
# Unlocated conversations, an undocumented pseudo-country (February 2026), and Seychelles,
# whose traffic Anthropic describes as VPN or abusive.
EXCLUDED_FROM_RANKING = frozenset({"not_classified", "NONE", "SYC"})
WORKING_AGE_POP = paths.RAW / "aei/release_2025_09_15/working_age_pop_2024_country.csv"


def working_age_population(path: Path = WORKING_AGE_POP) -> pd.Series:
    """Anthropic's 2024 working-age (15 to 64) population by ISO alpha-3 code (AEI-WAP2024)."""
    table = pd.read_csv(path, keep_default_na=False, dtype={"iso_alpha_3": str})
    if table["iso_alpha_3"].duplicated().any():
        raise ValueError(f"{path}: duplicate country codes")
    return table.set_index("iso_alpha_3")["working_age_pop"].astype("float64").rename(None)


def ranked(usage: pd.Series, population: pd.Series, floor: float | None = FLOOR) -> pd.Index:
    """Countries that enter the ranking: above the floor, with population, not excluded."""
    keep = usage.index.isin(population.index) & ~usage.index.isin(EXCLUDED_FROM_RANKING)
    if floor is not None:
        keep &= usage >= floor
    return usage.index[keep]


def compute(
    usage: pd.Series, population: pd.Series, *, basis: str, floor: float | None = FLOOR
) -> pd.DataFrame:
    """AUI of the ranked countries, with ranks. ``usage`` holds conversation counts (or, for a
    release without counts, published usage shares with ``floor=None``) by ISO alpha-3 code,
    including pseudo-geographies; ``population`` holds working-age population.

    Returns a frame indexed by country with columns ``usage``, ``population``, ``aui``,
    ``rank_min`` and ``rank_max`` (equal unless tied), sorted by AUI, descending.
    """
    if basis not in BASES:
        raise ValueError(f"unknown basis {basis!r}; use one of {BASES}")
    countries = ranked(usage, population, floor)
    if basis == "renormalized":
        usage_total = usage[countries].sum()
        population_total = population[countries].sum()
    else:
        if floor is None:
            raise ValueError("the anthropic_2025 basis needs conversation counts and a floor")
        rows = usage.index[usage >= floor]
        usage_total = usage[rows].sum()
        population_total = population[rows.intersection(population.index)].sum()
    frame = pd.DataFrame({"usage": usage[countries], "population": population[countries]})
    frame["aui"] = (frame["usage"] / usage_total) / (frame["population"] / population_total)
    return with_ranks(frame, "aui")


def published(
    values: pd.Series, usage: pd.Series | None = None, floor: float | None = FLOOR
) -> pd.DataFrame:
    """Published AUI values with ranks (ties as published), excluding pseudo-geographies and
    Seychelles. With ``usage`` (conversation counts), only countries at or above ``floor`` are
    kept; for a release without counts pass ``floor=None``: every published value counts."""
    keep = ~values.index.isin(EXCLUDED_FROM_RANKING)
    if floor is not None:
        if usage is None:
            raise ValueError("a floor needs conversation counts (usage)")
        keep &= values.index.isin(usage.index[usage >= floor])
    return with_ranks(pd.DataFrame({"aui": values[keep]}), "aui")


def with_ranks(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    """Add competition ranks (1 = highest): ``rank_min`` counts strictly higher values plus one,
    ``rank_max`` counts values at least as high, so a tie shows as a range."""
    values = frame[column]
    frame = frame.assign(
        rank_min=values.rank(method="min", ascending=False).astype("int64"),
        rank_max=values.rank(method="max", ascending=False).astype("int64"),
    )
    return frame.sort_values([column, "rank_min"], ascending=[False, True], kind="stable")


def share_ranks(shares: pd.Series) -> pd.DataFrame:
    """Countries ranked by share of global usage, pseudo-geographies and Seychelles excluded."""
    keep = shares[~shares.index.isin(EXCLUDED_FROM_RANKING)]
    return with_ranks(pd.DataFrame({"share": keep}), "share")
