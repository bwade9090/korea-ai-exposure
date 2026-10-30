"""``outputs/facts.json``: the numbers the brief quotes, each with unit, period, sources and the
producing function (PLAN §9), and the result tables in ``outputs/tables``. Phase 3 adds the
national profile (RQ1) and table T1."""

import json
import numbers
import re

import pandas as pd

from korea_ai_exposure import aui, national, paths

FACTS = paths.OUTPUTS / "facts.json"
TABLES = paths.OUTPUTS / "tables"
TRAIT_UNITS = {
    "ai_autonomy_mean": "1-5 scale",
    "human_education_years_mean": "years",
    "ai_education_years_mean": "years",
    "human_only_time_mean": "hours",
    "human_with_ai_time_mean": "minutes",
}
PEER_COLUMNS = ("P1a", "P1b", "P2", "P3", "P4")
_PRODUCER = "korea_ai_exposure.national."


def national_facts(frames: dict[str, pd.DataFrame], population: pd.Series) -> list[dict]:
    """RQ1 facts: the share and AUI series (F1), Korea against peers in May 2026 (F2, F3, T1),
    Korea's gap to the global sample in every snapshot, and the SOC, request and artifact gaps
    (F4)."""
    facts = []
    series = national.series(frames, population)
    for snapshot in national.SNAPSHOTS:
        row = series.loc[snapshot.label]
        period, slug = snapshot.label, snapshot.period_start[:7]
        with_population = [snapshot.source, national.POPULATION_SOURCE]
        share_rank = national.rank_text(row.share_rank_min, row.share_rank_max, row.share_n)
        rank = national.rank_text(row.rank_min, row.rank_max, row.n)
        add = _adder(facts, period, f"{_PRODUCER}series")
        add(
            f"rq1.share.{slug}",
            row.share_pct,
            f"{row.share_pct:.2f}%",
            "percent of global conversations",
            [snapshot.source],
        )
        add(f"rq1.share_rank.{slug}", row.share_rank_min, share_rank, "rank", with_population)
        add(f"rq1.aui.{slug}", row.aui, f"{row.aui:.2f}", "index, headline basis", with_population)
        add(f"rq1.aui_rank.{slug}", row.rank_min, rank, "rank, headline basis", with_population)
        if snapshot.published_basis:
            basis = f"{snapshot.published_basis} basis, as published"
            published_rank = national.rank_text(
                row.published_rank_min, row.published_rank_max, row.published_n
            )
            add(
                f"rq1.aui_published.{slug}",
                row.published_aui,
                f"{row.published_aui:.2f}",
                f"index, {basis}",
                with_population,
            )
            add(
                f"rq1.aui_published_rank.{slug}",
                row.published_rank_min,
                published_rank,
                f"rank, {basis}",
                with_population,
            )

    headline = national.HEADLINE
    frame = frames[headline.label]
    slug, sources = headline.period_start[:7], [headline.source]
    peers = national.peer_sets(frame, population)
    add = _adder(facts, headline.label, f"{_PRODUCER}peer_sets")
    for name, members in peers.items():
        add(f"rq1.peers.{name}.{slug}", len(members), str(len(members)), "countries", sources)
    add = _adder(facts, headline.label, f"{_PRODUCER}against_peers")
    for metric, row in national.against_peers(national.profile(frame), peers).iterrows():
        unit = _unit(metric, headline)
        for column in ("korea", "global", *(f"{name}_median" for name in PEER_COLUMNS)):
            add(
                f"rq1.{metric}.{column}.{slug}",
                row[column],
                _display(row[column], unit),
                unit,
                sources,
            )
        rank, n = int(row.korea_rank), int(row.rank_n)  # iterrows turns integers into floats
        add(
            f"rq1.{metric}.korea_rank.{slug}",
            rank,
            f"{rank} of {n}",
            "rank among P3 and Korea",
            sources,
        )

    for (label, metric), row in national.m9_by_snapshot(frames, population).iterrows():
        snapshot = next(s for s in national.SNAPSHOTS if s.label == label)
        unit = _unit(metric, snapshot, gap=True)
        gap = row.korea - row["global"]
        add = _adder(facts, label, f"{_PRODUCER}m9_by_snapshot")
        add(
            f"rq1.{metric}.gap_global.{snapshot.period_start[:7]}",
            gap,
            _display(gap, unit),
            unit,
            [snapshot.source],
        )

    for snapshot in national.SNAPSHOTS:
        if snapshot.label in ("Nov 2025", "Feb 2026"):  # no SOC mix published (ADR 0006 item 7)
            continue
        soc = national.soc_mix(frames[snapshot.label]).dropna(subset=["gap_pp"])
        _gap_facts(facts, "soc_gap", soc, snapshot, "soc_mix")
    requests = national.request_mix(frame).dropna(subset=["gap_pp"])
    _gap_facts(
        facts,
        "request_gap",
        pd.concat([requests.head(5), requests.tail(5)]),
        headline,
        "request_mix",
    )
    artifacts = national.artifact_mix(frame).dropna(subset=["gap_pp"])
    _gap_facts(
        facts,
        "artifact_gap",
        pd.concat([artifacts.head(3), artifacts.tail(3)]),
        headline,
        "artifact_mix",
    )
    return facts


def t1(frames: dict[str, pd.DataFrame], population: pd.Series) -> pd.DataFrame:
    """T1: national metrics against peers in the headline month (May 2026)."""
    frame = frames[national.HEADLINE.label]
    table = national.against_peers(national.profile(frame), national.peer_sets(frame, population))
    return table.dropna(subset=["korea"])


def t1_markdown(table: pd.DataFrame) -> str:
    """T1 as a Markdown table: medians with their N, and Korea's rank among P3 and Korea."""
    header = [
        "Metric",
        "Korea",
        "Global",
        *(f"{name} median (N)" for name in PEER_COLUMNS),
        "Korea's rank",
    ]
    lines = ["| " + " | ".join(header) + " |", "|" + " --- |" * len(header)]
    for metric, row in table.iterrows():
        decimals = 2 if metric in TRAIT_UNITS else 1
        cells = [
            national.LABELS[metric],
            f"{row.korea:.{decimals}f}",
            f"{row['global']:.{decimals}f}",
        ]
        cells += [
            f"{row[f'{name}_median']:.{decimals}f} ({int(row[f'{name}_n'])})"
            for name in PEER_COLUMNS
        ]
        cells.append(f"{int(row.korea_rank)} of {int(row.rank_n)}")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def write(facts: list[dict], frames: dict[str, pd.DataFrame], population: pd.Series) -> None:
    ids = [fact["id"] for fact in facts]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate fact ids")
    FACTS.parent.mkdir(parents=True, exist_ok=True)
    FACTS.write_text(
        json.dumps(facts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    TABLES.mkdir(parents=True, exist_ok=True)
    table = t1(frames, population)
    table.to_csv(TABLES / "T1.csv", float_format="%.4f", lineterminator="\n")
    (TABLES / "T1.md").write_text(t1_markdown(table), encoding="utf-8", newline="\n")
    national.m9_by_snapshot(frames, population).to_csv(
        TABLES / "T1_snapshots.csv", float_format="%.4f", lineterminator="\n"
    )
    national.series(frames, population).to_csv(
        TABLES / "rq1_series.csv", float_format="%.4f", lineterminator="\n"
    )


def _adder(facts: list[dict], period: str, producer: str):
    """A function that appends one fact for ``period`` and ``producer`` to ``facts``; values
    are integers, floats rounded to six decimals, or null where not published."""

    def add(id_: str, value, display: str, unit: str, sources: list[str]) -> None:
        if pd.isna(value):
            value = None
        elif isinstance(value, numbers.Integral):
            value = int(value)
        else:
            value = round(float(value), 6)
        facts.append(
            {
                "id": id_,
                "value": value,
                "display": display,
                "unit": unit,
                "period": period,
                "sources": sources,
                "producer": producer,
            }
        )

    return add


def _gap_facts(facts: list[dict], kind: str, table: pd.DataFrame, snapshot, producer: str) -> None:
    add = _adder(facts, snapshot.label, f"{_PRODUCER}{producer}")
    for row in table.itertuples():
        slug = re.sub(r"[^a-z0-9]+", "_", row.name.lower()).strip("_")
        add(
            f"rq1.{kind}.{slug}.{snapshot.period_start[:7]}",
            row.gap_pp,
            f"{row.name}: {row.gap_pp:+.2f} pp",
            "percentage points, Korea minus global",
            [snapshot.source],
        )


def _unit(metric: str, snapshot, gap: bool = False) -> str:
    if metric not in TRAIT_UNITS:
        return "percentage points, Korea minus global" if gap else "percent"
    unit = TRAIT_UNITS[metric] if snapshot.release == "2026-06-26" else "release scale"
    return f"{unit}, Korea minus global" if gap else unit


def _display(value: float, unit: str) -> str:
    if pd.isna(value):
        return "not published"
    if unit.startswith("percentage points"):
        return f"{value:+.1f} pp"
    if unit == "percent":
        return f"{value:.1f}%"
    return f"{value:+.2f}" if "minus" in unit else f"{value:.2f}"


def main() -> int:
    frames = national.snapshots()
    population = aui.working_age_population()
    facts = national_facts(frames, population)
    write(facts, frames, population)
    print(
        f"wrote {FACTS.relative_to(paths.ROOT).as_posix()}: {len(facts)} facts; T1 in "
        f"{TABLES.relative_to(paths.ROOT).as_posix()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
