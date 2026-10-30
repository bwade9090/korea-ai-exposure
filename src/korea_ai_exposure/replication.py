"""Replication checks of Phase 2.4: the values in PLAN §3 and the published targets in PLAN 2.4,
recomputed from the pinned files, each on the basis of the published value (ADR 0006).

Tolerances (PLAN 2.4): ±0.05 for indices, ±0.1 percentage point for published shares, exact for
ranks and counts. Values in PLAN §3 were read from these same files, so they must match at the
precision they were recorded with. Values published to one decimal are checked on rank, and the
level is reported in the note. Every check has a status: pass, fail, or not run (optional
targets whose inputs are not pinned yet).

Run ``python -m korea_ai_exposure.replication`` for a Markdown table of the results.
"""

import math
import sys
from dataclasses import dataclass

import pandas as pd

from korea_ai_exposure import aei, aui, paths, regions

JOB_EXPOSURE = paths.RAW / "aei/labor_market_impacts/job_exposure.csv"
EN_DASH = "\N{EN DASH}"  # separates rank ranges (ties), as in the publications
CAPITAL_REGION = ("KR-11", "KR-41", "KR-28")  # Seoul, Gyeonggi, Incheon
WEEKLY = {"2026-01-15": "Nov 2025", "2026-03-24": "Feb 2026"}
MONTHLY = {"2026-04-01": "Apr 2026", "2026-05-01": "May 2026"}
STATUSES = ("pass", "fail", "not run")
AUSTRALIA_STATES = "Australia's state indices, Feb 2026 (optional; NSW 1.20, VIC 1.19, WA 0.68)"
OPTIONAL_TARGETS = frozenset({AUSTRALIA_STATES})


@dataclass(frozen=True)
class Check:
    target: str
    published: str
    observed: str
    status: str
    basis: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"status must be one of {STATUSES}, not {self.status!r}")

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def _status(condition: bool) -> str:
    return "pass" if condition else "fail"


def run() -> list[Check]:
    population = aui.working_age_population()
    return [
        *_plan_section_3(population),
        *_published_targets(population),
        _observed_exposure(),
    ]


def korean_regions(frame: pd.DataFrame, metric: str, period_start: str | None = None):
    values = aei.geo_values(frame, "subregion", metric, period_start)
    return values[values.index.str.startswith("KR-")]


def _plan_section_3(population: pd.Series) -> list[Check]:
    expected_share = {"Nov 2025": 3.06, "Feb 2026": 2.91, "Apr 2026": 3.19, "May 2026": 3.24}
    expected_count = {"Nov 2025": 30_618, "Feb 2026": 29_075}
    expected_min = {"Nov 2025": (175, "Ulsan"), "Feb 2026": (174, "Jeju")}
    expected_seoul = {"Nov 2025": 58.23, "Feb 2026": 56.09, "Apr 2026": 63.53, "May 2026": 63.65}
    expected_capital = {"Nov 2025": 79.09, "Feb 2026": 81.91, "Apr 2026": 83.34, "May 2026": 82.78}
    expected_incheon = {"Nov 2025": 4.82, "Feb 2026": 10.56, "Apr 2026": 6.94, "May 2026": 6.75}

    snapshots = []  # (label, country shares, Korean regional shares)
    checks = []
    for release, label in WEEKLY.items():
        frame = aei.load(release)
        counts = aei.geo_values(frame, "country", "usage_count")
        regional_counts = korean_regions(frame, "usage_count")
        snapshots.append(
            (
                label,
                aei.geo_values(frame, "country", "usage_pct"),
                korean_regions(frame, "usage_pct"),
            )
        )
        national = int(counts["KOR"])
        checks.append(_exact(f"Korean conversations, {label}", expected_count[label], national))
        total = int(regional_counts.sum())
        checks.append(
            Check(
                f"Korean regional counts sum to the national count, {label}",
                "exact",
                f"{total:,} of {national:,} ({len(regional_counts)} regions)",
                _status(total == national and len(regional_counts) == 17),
            )
        )
        smallest = regional_counts.idxmin()
        observed = (int(regional_counts[smallest]), regions.by_iso(smallest).name)
        count, name = expected_min[label]
        checks.append(
            Check(
                f"Smallest regional count, {label}",
                f"{count} ({name})",
                f"{observed[0]} ({observed[1]})",
                _status(observed == (count, name)),
            )
        )
    monthly = aei.load("2026-06-26")
    for period, label in MONTHLY.items():
        snapshots.append(
            (
                label,
                aei.geo_values(monthly, "country", "usage_pct", period),
                korean_regions(monthly, "usage_pct", period),
            )
        )
    for label, shares, regional in snapshots:
        checks.append(
            Check(
                f"Korean regions with published usage, {label}",
                "17",
                str(len(regional)),
                _status(sorted(regional.index) == sorted(r.iso for r in regions.REGIONS)),
            )
        )
        for target, expected, observed in (
            ("Korea's share of global conversations", expected_share, shares["KOR"]),
            ("Seoul's share of Korean usage", expected_seoul, regional["KR-11"]),
            ("Seoul + Gyeonggi + Incheon", expected_capital, regional[list(CAPITAL_REGION)].sum()),
            ("Incheon's share of Korean usage", expected_incheon, regional["KR-28"]),
        ):
            checks.append(_rounded(f"{target}, {label}", expected[label], observed, "%"))

    published_aui = (
        ("2026-04-01", "Apr 2026", 3.92, (9, 10, 114)),
        ("2026-05-01", "May 2026", 3.78, (14, 14, 121)),
    )
    for period, label, value, rank in published_aui:
        published = aui.published(
            aei.geo_values(monthly, "country", "usage_per_capita_index", period), floor=None
        )
        row = published.loc["KOR"]
        observed = (int(row["rank_min"]), int(row["rank_max"]), len(published))
        checks.append(
            Check(
                f"Korea's published AUI and rank, {label}",
                f"{value:.2f}, rank {_rank_text(*rank)}",
                f"{row['aui']:.2f}, rank {_rank_text(*observed)}",
                _status(_equal_at(row["aui"], value, 2) and observed == rank),
                "published",
            )
        )
        shares = aei.geo_values(monthly, "country", "usage_pct", period)
        recomputed = aui.compute(
            shares[shares.index.isin(published.index)], population, basis="renormalized", floor=None
        )
        checks.append(
            _within(
                f"Renormalized basis reproduces Korea's published AUI, {label}",
                value,
                recomputed.loc["KOR", "aui"],
                0.05,
                "renormalized",
            )
        )
    return checks


def _published_targets(population: pd.Series) -> list[Check]:
    checks = []
    august = aei.load("2025-09-15")
    counts = aei.geo_values(august, "country", "usage_count")
    published = aui.published(aei.geo_values(august, "country", "usage_per_capita_index"), counts)
    row = published.loc["KOR"]
    korea_rank = _rank_text(int(row["rank_min"]), int(row["rank_max"]), len(published))
    checks.append(
        Check(
            "Korea's AUI and rank, Aug 2025 (September 2025 report)",
            "3.73, rank 5",
            f"{row['aui']:.3f}, rank {korea_rank}",
            _status(abs(row["aui"] - 3.73) <= 0.05 and _rank(row) == (5, 5)),
            "published",
        )
    )
    rule = aui.compute(counts, population, basis="anthropic_2025")
    same_countries = rule.index.sort_values().equals(published.index.sort_values())
    gap = (rule["aui"] - published["aui"].reindex(rule.index)).abs().max(skipna=False)
    if same_countries:
        observed = f"largest absolute difference {gap:.1e} over {len(rule)} countries"
    else:
        observed = (
            f"country sets differ: {sorted(rule.index.symmetric_difference(published.index))}"
        )
    checks.append(
        Check(
            "Rule anthropic_2025 reproduces every published AUI, Aug 2025",
            f"{len(published)} values",
            observed,
            _status(same_countries and gap < 1e-6),
            "anthropic_2025",
        )
    )

    november = aei.load("2026-01-15")
    counts = aei.geo_values(november, "country", "usage_count")
    rule = aui.compute(counts, population, basis="anthropic_2025")
    row = rule.loc["KOR"]
    observed = (*_rank(row), len(rule))
    checks.append(
        Check(
            "Korea's AUI and rank, Nov 2025 (January 2026 appendix, Fig. 3)",
            "3.12, rank 7 of 116",
            f"{row['aui']:.3f}, rank {_rank_text(*observed)}",
            _status(abs(row["aui"] - 3.12) <= 0.05 and observed == (7, 7, 116)),
            "anthropic_2025",
        )
    )
    shares = aei.geo_values(november, "country", "usage_pct")
    ranked_shares = aui.share_ranks(shares, counts, population)
    row = ranked_shares.loc["IND"]
    checks.append(
        Check(
            "India's share of global usage and rank, Nov 2025 (India brief)",
            "5.8%, rank 2",
            f"{row['share']:.2f}%, rank {_rank_text(*_rank(row), len(ranked_shares))}",
            _status(abs(row["share"] - 5.8) <= 0.1 and _rank(row) == (2, 2)),
            "published usage_pct",
        )
    )

    february = aei.load("2026-03-24")
    counts = aei.geo_values(february, "country", "usage_count")
    shares = aei.geo_values(february, "country", "usage_pct")
    renormalized = aui.compute(counts, population, basis="renormalized")
    korea = renormalized.loc["KOR", "aui"]
    checks.append(
        Check(
            "Korea's AUI, Feb 2026 (Anthropic, 2026-05-26: 'more than 3.5 times')",
            "above 3.5",
            f"{korea:.3f}, rank {_rank_text(*_rank(renormalized.loc['KOR']), len(renormalized))}",
            _status(korea > 3.5),
            "renormalized",
        )
    )
    ranked_shares = aui.share_ranks(shares, counts, population)
    row = ranked_shares.loc["AUS"]
    checks.append(
        Check(
            "Australia's share of global usage and rank, Feb 2026 (Australia brief)",
            "1.6%, rank 11",
            f"{row['share']:.2f}%, rank {_rank_text(*_rank(row), len(ranked_shares))}",
            _status(abs(row["share"] - 1.6) <= 0.1 and _rank(row) == (11, 11)),
            "published usage_pct",
        )
    )
    row = renormalized.loc["AUS"]
    level = row["aui"]
    geolocated = _geolocated_aui("AUS", counts, shares, population)
    checks.append(
        Check(
            "Australia's AUI rank, Feb 2026 (Australia brief: 4.1, rank 7)",
            "rank 7",
            f"rank {_rank_text(*_rank(row), len(renormalized))}",
            _status(_rank(row) == (7, 7)),
            "renormalized",
            f"Published to one decimal; the basis is not pinned. Level {level:.3f} renormalized "
            f"(truncates to {math.floor(level * 10) / 10:.1f}, rounds to {round(level, 1):.1f}); "
            f"{geolocated:.3f} with usage over all geolocated conversations (rounds to "
            f"{round(geolocated, 1):.1f}).",
        )
    )
    checks.append(
        Check(
            AUSTRALIA_STATES,
            "NSW 1.20, VIC 1.19, WA 0.68",
            "not run",
            "not run",
            "",
            "Optional target: needs ABS state population (ABS-ERP), not pinned yet.",
        )
    )
    return checks


def _geolocated_aui(
    country: str, counts: pd.Series, shares: pd.Series, population: pd.Series
) -> float:
    """AUI with usage over all geolocated conversations of the published base (the sample total
    implied by usage_pct, less unlocated conversations) and population over the ranked
    countries: an alternative basis for statements published to one decimal."""
    sample = counts["KOR"] / shares["KOR"] * 100
    located = sample - counts["not_classified"]
    countries = aui.ranked(counts, population)
    return (counts[country] / located) / (population[country] / population[countries].sum())


def _observed_exposure() -> Check:
    table = pd.read_csv(JOB_EXPOSURE, keep_default_na=False)
    occupations = table["occ_code"].nunique()
    zeros = int((table["observed_exposure"] == 0).sum())
    maximum = table["observed_exposure"].max()
    return Check(
        "Anthropic observed_exposure: occupations, zeros, maximum",
        "756; 411; 0.745",
        f"{occupations}; {zeros}; {maximum:.4f}",
        _status(
            (occupations, zeros) == (756, 411)
            and _equal_at(maximum, 0.745, 3)
            and len(table) == occupations
        ),
    )


def _equal_at(observed: float, expected: float, decimals: int) -> bool:
    """True when ``observed`` shows as ``expected`` at ``decimals`` decimal places: within half a
    unit of the last place, with a small allowance for binary floating point."""
    return abs(observed - expected) <= 0.5 * 10**-decimals + 1e-9


def _exact(target: str, expected: int, observed: int) -> Check:
    return Check(target, f"{expected:,}", f"{observed:,}", _status(observed == expected))


def _rounded(target: str, expected: float, observed: float, unit: str = "") -> Check:
    return Check(
        target,
        f"{expected:.2f}{unit}",
        f"{observed:.4f}{unit}",
        _status(_equal_at(observed, expected, 2)),
    )


def _within(target: str, expected: float, observed: float, tolerance: float, basis: str) -> Check:
    return Check(
        target,
        f"{expected:.2f}",
        f"{observed:.3f}",
        _status(abs(observed - expected) <= tolerance),
        basis,
    )


def _rank(row: pd.Series) -> tuple[int, int]:
    return int(row["rank_min"]), int(row["rank_max"])


def _rank_text(rank_min: int, rank_max: int, n: int | None = None) -> str:
    text = str(rank_min) if rank_min == rank_max else f"{rank_min}{EN_DASH}{rank_max}"
    return text if n is None else f"{text} of {n}"


def summary(checks: list[Check]) -> str:
    counts = {status: sum(c.status == status for c in checks) for status in STATUSES}
    return ", ".join(f"{counts[status]} {status}" for status in STATUSES)


def to_markdown(checks: list[Check]) -> str:
    lines = [
        "| Target | Published | Reproduced | Basis | Result | Note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for c in checks:
        result = "**fail**" if c.status == "fail" else c.status
        cells = (c.target, c.published, c.observed, c.basis, result, c.note)
        lines.append("| " + " | ".join(cell.replace("|", "/") for cell in cells) + " |")
    return "\n".join(lines) + "\n"


def write_markdown(checks: list[Check], stream=None) -> None:
    """Write the table and a summary line as UTF-8 whatever the console encoding (cp949 on
    Korean Windows cannot encode the en dash of rank ranges)."""
    stream = stream or sys.stdout
    stream.reconfigure(encoding="utf-8")
    stream.write(to_markdown(checks) + f"\n{summary(checks)}.\n")
    stream.flush()


def main() -> int:
    checks = run()
    write_markdown(checks)
    return 1 if any(c.status == "fail" for c in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
