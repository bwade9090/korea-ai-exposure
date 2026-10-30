"""``outputs/facts.json``: the numbers the brief quotes, each with unit, period, sources and the
producing function (PLAN §9), and the result tables in ``outputs/tables``. Phase 3 adds the
national profile (RQ1) and table T1, Phase 4 the regional distribution (RQ2) and table T2,
Phase 5 composition against adoption (RQ3-RQ4) and table T3."""

import json
import numbers
import re

import pandas as pd

from korea_ai_exposure import aui, crosswalk, decomposition, national, paths, regional, regions

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
T2_COLUMNS = {
    "share": "Usage share (%)",
    "population_share": "Residents 15-64 (%)",
    "workers_share": "Workers by workplace (%)",
    "employed_share": "Employed by residence (%)",
    "index_population": "Index: residents",
    "index_workers": "Index: workers",
    "index_employed": "Index: employed",
    "work_usage": "Work-usage share (%)",
    "commuting_ratio": "Commuting ratio",
}
DENOMINATOR_UNITS = {
    "population": "index over the share of residents aged 15-64 (1 = parity)",
    "workers": "index over the share of workers by workplace region (1 = parity)",
    "employed": "index over the share of employed persons by residence (1 = parity)",
}
_PRODUCER = "korea_ai_exposure.national."
_REGIONAL = "korea_ai_exposure.regional."
_DECOMPOSITION = "korea_ai_exposure.decomposition."
_CROSSWALK_PRODUCER = "korea_ai_exposure.crosswalk."
_CHAIN = ["XW-SOC1018", "XW-ISCO-SOC", "XW-KSCO-ISCO"]  # SOC 2018 -> 2010 -> ISCO -> KSCO


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


def regional_facts(frames: dict[str, pd.DataFrame]) -> list[dict]:
    """RQ2 facts: each region's usage share and population-based index in every regional
    snapshot (F5); its other indices, work-usage share and commuting ratio in May 2026 (T2); the
    capital region's shares (F6); stability; ranks outside the capital region; the GRDP
    association (F7); and the range of the regional facets in May 2026."""
    facts = []
    tables = regional.regional_tables(frames)
    headline = regional.HEADLINE
    for snapshot in regional.SNAPSHOTS:
        slug, latest = snapshot.period_start[:7], snapshot == headline
        add = _adder(facts, snapshot.label, f"{_REGIONAL}regional_tables")
        for code, row in tables[snapshot.label].iterrows():
            name = _slug(regions.by_iso(code).name)
            add(
                f"rq2.share.{name}.{slug}",
                row.share,
                f"{row.share:.2f}%",
                "percent of Korean conversations",
                [snapshot.source],
            )
            for denominator in regional.DENOMINATORS if latest else ("population",):
                value = row[f"index_{denominator}"]
                add(
                    f"rq2.index_{denominator}.{name}.{slug}",
                    value,
                    f"{value:.2f}",
                    DENOMINATOR_UNITS[denominator],
                    [snapshot.source, regional.SOURCES[denominator]],
                )
            if latest:
                add(
                    f"rq2.work_usage.{name}.{slug}",
                    row.work_usage,
                    f"{row.work_usage:.2f}%",
                    "percent of Korean work-related conversations",
                    [snapshot.source],
                )
                if pd.notna(row.commuting_ratio):
                    add(
                        f"rq2.commuting_ratio.{name}.{slug}",
                        row.commuting_ratio,
                        f"{row.commuting_ratio:.2f}",
                        "workplace over residence employment, first half of 2026",
                        [regional.SOURCES["commuting"]],
                    )

    for label, row in regional.capital_shares(tables).iterrows():
        snapshot = next(s for s in regional.SNAPSHOTS if s.label == label)
        slug = snapshot.period_start[:7]
        add = _adder(facts, label, f"{_REGIONAL}capital_shares")
        add(
            f"rq2.capital.usage.{slug}",
            row.usage_share,
            f"{row.usage_share:.1f}%",
            "percent of Korean conversations, Seoul, Gyeonggi and Incheon",
            [snapshot.source],
        )
        if snapshot == headline:
            for denominator in regional.DENOMINATORS:
                value = row[f"{denominator}_share"]
                add(
                    f"rq2.capital.{denominator}.{slug}",
                    value,
                    f"{value:.1f}%",
                    "percent of Korea, Seoul, Gyeonggi and Incheon",
                    [regional.SOURCES[denominator]],
                )

    usage_sources = list(dict.fromkeys(s.source for s in regional.SNAPSHOTS))
    rho, moves = regional.stability(tables)
    add = _adder(facts, "Nov 2025 to May 2026", f"{_REGIONAL}stability")
    for _, row in rho.iterrows():
        add(
            f"rq2.rho.{_slug(row['first'])}.{_slug(row['second'])}",
            row.rho,
            f"{row.rho:.2f} (N = {int(row.n)})",
            "Spearman's rho of the population-based index between two snapshots",
            [*usage_sources, regional.SOURCES["population"]],
        )
    for _, row in moves.iterrows():
        name = _slug(regions.by_iso(row.region).name)
        add(
            f"rq2.share_change.{name}.{_slug(row['from'])}.{_slug(row['to'])}",
            row.change * 100,
            f"{row.share_before:.2f}% to {row.share_after:.2f}%",
            "percent change in the usage share",
            usage_sources,
        )

    slug = headline.period_start[:7]
    latest_table = tables[headline.label]
    ranks = regional.non_capital_ranks(latest_table)
    add = _adder(facts, headline.label, f"{_REGIONAL}non_capital_ranks")
    for code, rank in ranks.items():
        add(
            f"rq2.noncapital_rank.{_slug(regions.by_iso(code).name)}.{slug}",
            int(rank),
            f"{rank} of {len(ranks)}",
            "rank of the population-based index outside the capital region",
            [headline.source, regional.SOURCES["population"]],
        )
    association = regional.grdp_association(latest_table)
    add = _adder(facts, headline.label, f"{_REGIONAL}grdp_association")
    add(
        f"rq2.grdp_rho.{slug}",
        association["rho"],
        f"{association['rho']:.2f} (N = {association['n']})",
        "Spearman's rho, population-based index and GRDP per capita (2024)",
        [headline.source, regional.SOURCES["population"], regional.SOURCES["grdp"]],
    )

    facets = regional.facets(frames[headline.label]).loc[list(regional.REGION_CODES)]
    add = _adder(facts, headline.label, f"{_REGIONAL}facets")
    for metric in facets.columns:
        unit, values = _unit(metric, headline), facets[metric]
        for kind, code in (("min", values.idxmin()), ("max", values.idxmax()), ("seoul", "KR-11")):
            name = regions.by_iso(code).name
            add(
                f"rq2.facet.{metric}.{kind}.{slug}",
                values[code],
                f"{name}: {_display(values[code], unit)}",
                unit,
                [headline.source],
            )
    return facts


def t2(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """T2: regional shares, denominators, indices and intervals in every regional snapshot."""
    return pd.concat(regional.regional_tables(frames), names=["snapshot", "region"])


def t2_markdown(table: pd.DataFrame) -> str:
    """T2 for one snapshot as a Markdown table; the commuting ratio has no value for Sejong."""
    header = ["Region", *T2_COLUMNS.values()]
    lines = ["| " + " | ".join(header) + " |", "|" + " --- |" * len(header)]
    for code, row in table.iterrows():
        cells = [regions.by_iso(code).name]
        cells += ["n/a" if pd.isna(row[c]) else f"{row[c]:.2f}" for c in T2_COLUMNS]
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
    regional_table = t2(frames)
    regional_table.to_csv(TABLES / "T2.csv", float_format="%.4f", lineterminator="\n")
    latest = regional_table.loc[regional.HEADLINE.label]
    (TABLES / "T2.md").write_text(t2_markdown(latest), encoding="utf-8", newline="\n")
    rho, moves = regional.stability(regional.regional_tables(frames))
    rho.to_csv(TABLES / "rq2_stability.csv", index=False, float_format="%.4f", lineterminator="\n")
    moves.to_csv(TABLES / "rq2_moves.csv", index=False, float_format="%.4f", lineterminator="\n")
    facets = {s.label: regional.facets(frames[s.label]) for s in regional.SNAPSHOTS}
    pd.concat(facets, names=["snapshot", "region"]).to_csv(
        TABLES / "T2_facets.csv", float_format="%.4f", lineterminator="\n"
    )
    csv = {"float_format": "%.4f", "lineterminator": "\n"}
    robustness = decomposition.robustness(frames)
    robustness.to_csv(TABLES / "T3.csv", index=False, **csv)
    (TABLES / "T3.md").write_text(t3_markdown(robustness), encoding="utf-8", newline="\n")
    korea = decomposition.korea(frames)
    korea.to_csv(TABLES / "rq3_korea.csv", **csv)
    decomposition.us_states(frames).to_csv(TABLES / "rq3_us_states.csv", **csv)
    decomposition.bok_comparison(korea).to_csv(TABLES / "rq4_bok.csv", index=False, **csv)
    crosswalk.coverage(frames).to_csv(TABLES / "rq3_coverage.csv", **csv)
    audit = crosswalk.audit(frames)
    rows = [(kind, code) for kind, codes in audit.items() for code in codes]
    pd.DataFrame(rows, columns=["kind", "code"]).to_csv(
        TABLES / "rq3_audit.csv", index=False, lineterminator="\n"
    )


def composition_facts(frames: dict[str, pd.DataFrame]) -> list[dict]:
    """RQ3 and RQ4 facts: each region's predicted work usage, residual and exposure (F9), the
    Korean and US fits (F8, F9), crosswalk coverage, the Bank of Korea rank comparison, and the
    robustness checks of T3."""
    facts = []
    headline, slug = national.HEADLINE, national.HEADLINE.period_start[:7]
    korea = decomposition.korea(frames)
    usage_sources = [headline.source, "KR-OCC", "KR-OCC-NAT", "US-OEWS-NAT", *_CHAIN]
    exposure_sources = {
        "ilo": ["KR-OCC", "KR-OCC-NAT", "XW-KSCO-ISCO", "ILO-WP140"],
        "observed": ["KR-OCC", "KR-OCC-NAT", "AEI-LMI", "US-OEWS-NAT", *_CHAIN],
    }
    add = _adder(facts, headline.label, f"{_DECOMPOSITION}korea")
    for code, row in korea.iterrows():
        name = _slug(regions.by_iso(code).name)
        add(
            f"rq3.predicted_work.{name}.{slug}",
            row.predicted_work,
            f"{row.predicted_work:.2f}%",
            "percent of predicted Korean work usage",
            usage_sources,
        )
        add(
            f"rq3.residual.{name}.{slug}",
            row.residual,
            f"{row.residual:.2f}",
            "observed over predicted work usage",
            usage_sources,
        )
    add = _adder(facts, "first half of 2026", f"{_DECOMPOSITION}korea")
    for code, row in korea.iterrows():
        name = _slug(regions.by_iso(code).name)
        for measure, sources in exposure_sources.items():
            add(
                f"rq4.exposure_{measure}.{name}.2026-h1",
                row[measure],
                f"{row[measure]:.3f}",
                f"employment-weighted {measure} exposure score (0-1)",
                sources,
            )

    us = decomposition.us_states(frames)
    add = _adder(facts, headline.label, f"{_DECOMPOSITION}fit")
    for area, table, sources in (
        ("korea", korea, usage_sources),
        ("us", us, [headline.source, "US-OEWS-NAT", "US-OEWS-ST"]),
    ):
        result = decomposition.fit(table["observed_work"], table["predicted_work"])
        n = result["n"]
        add(
            f"rq3.r2.{area}.{slug}",
            result["r2"],
            f"{result['r2']:.2f} (N = {n})",
            "share of variance in log observed work usage accounted for by log predicted",
            sources,
        )
        add(
            f"rq3.rho.{area}.{slug}",
            result["rho"],
            f"{result['rho']:.2f} (N = {n})",
            "Spearman's rho, observed and predicted work usage",
            sources,
        )
    for kind, value in (("min", us["coverage"].min()), ("max", us["coverage"].max())):
        add(
            f"rq3.us_coverage.{kind}.{slug}",
            value * 100,
            f"{value * 100:.1f}%",
            "percent of state employment in published cells with an intensity",
            ["US-OEWS-ST"],
        )

    add = _adder(facts, headline.label, f"{_CROSSWALK_PRODUCER}coverage")
    for measure, row in crosswalk.coverage(frames).iterrows():
        for column, value in row.items():
            if pd.notna(value):
                add(
                    f"rq3.coverage.{measure}.{column}",
                    value * 100,
                    f"{value * 100:.1f}%",
                    "percent of employment",
                    ["US-OEWS-NAT", "KR-OCC-NAT", *_CHAIN],
                )

    add = _adder(facts, headline.label, f"{_DECOMPOSITION}bok_comparison")
    for row in decomposition.bok_comparison(korea).itertuples():
        add(
            f"rq4.bok.{row.bok}.{row.project}",
            row.rho,
            f"{row.rho:.2f} (N = {row.n})",
            "Spearman's rho with the Bank of Korea's published rank order",
            ["BOK-2026-09", headline.source, "KR-OCC", "ILO-WP140"],
        )

    add = _adder(facts, headline.label, f"{_DECOMPOSITION}robustness")
    for row in decomposition.robustness(frames).itertuples():
        add(
            f"rq3.robustness.{_slug(row.ranking)}.{_slug(row.variant)}",
            row.rho,
            f"{row.rho:.2f}",
            "Spearman's rho with the headline regional ranking",
            usage_sources,
        )
    return facts


def t3_markdown(table: pd.DataFrame) -> str:
    """T3: Spearman's rho of each headline regional ranking with its variants (N = 17)."""
    lines = [
        "| Ranking | Variant | Spearman's rho | Robust (rho >= 0.9) |",
        "| --- | --- | --- | --- |",
    ]
    for row in table.itertuples():
        lines.append(
            f"| {row.ranking} | {row.variant} | {row.rho:.3f} | {'yes' if row.robust else 'no'} |"
        )
    return "\n".join(lines) + "\n"


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


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _gap_facts(facts: list[dict], kind: str, table: pd.DataFrame, snapshot, producer: str) -> None:
    add = _adder(facts, snapshot.label, f"{_PRODUCER}{producer}")
    for row in table.itertuples():
        add(
            f"rq1.{kind}.{_slug(row.name)}.{snapshot.period_start[:7]}",
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
    facts = national_facts(frames, population) + regional_facts(frames) + composition_facts(frames)
    write(facts, frames, population)
    print(
        f"wrote {FACTS.relative_to(paths.ROOT).as_posix()}: {len(facts)} facts; T1-T3 in "
        f"{TABLES.relative_to(paths.ROOT).as_posix()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
