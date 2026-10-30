"""Korea's national profile against peer economies: PLAN Phase 3 (RQ1), measures M1 and M9.

Peer sets follow ADR 0003; floors, pseudo-geographies and the AUI bases follow ADR 0006. Every
comparison is made within one snapshot. Only ``series`` spans snapshots, and it labels each
snapshot with its method, since a change between snapshots mixes real change with method change.

Shares are taken over what a release classifies and publishes: use cases over work, personal
and coursework; collaboration patterns over the five patterns without "none", which is how
Anthropic computes its automation and augmentation buckets; SOC major groups, request topics
and artifacts over their published, classified rows. A value that a release does not publish
stays missing and is never read as zero.
"""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from korea_ai_exposure import aei, aui

KOREA = "KOR"
GLOBAL = "GLOBAL"
P1A = ("JPN", "SGP", "TWN", "AUS", "NZL")  # advanced Asia-Pacific
P1B = (
    "AUS",
    "IND",
    "IDN",
    "JPN",
    "MYS",
    "NZL",
    "PHL",
    "SGP",
    "THA",
)  # BIS Asian Consultative Council
P4_SIZE = 10
TOP_TASKS = 100
NAMES = {
    "KOR": "Korea", "GLOBAL": "Global", "JPN": "Japan", "SGP": "Singapore", "TWN": "Taiwan",
    "AUS": "Australia", "NZL": "New Zealand", "IND": "India", "IDN": "Indonesia",
    "MYS": "Malaysia", "PHL": "Philippines", "THA": "Thailand",
}  # fmt: skip
POPULATION_SOURCE = "AEI-WAP2024"


@dataclass(frozen=True)
class Snapshot:
    label: str
    release: str
    period_start: str
    source: str  # ID in docs/DATA_SOURCES.md
    published_basis: str | None  # basis of the AUI Anthropic published for this snapshot
    method: str  # what a comparison with other snapshots has to allow for


SNAPSHOTS = (
    Snapshot("Aug 2025", "2025-09-15", "2025-08-04", "AEI-2025-09", "anthropic_2025",
             "one-week sample, 4-11 Aug 2025; O*NET 20.1 tasks"),
    Snapshot("Nov 2025", "2026-01-15", "2025-11-13", "AEI-2026-01", "anthropic_2025",
             "one-week sample, 13-20 Nov 2025; O*NET 20.1 tasks"),
    Snapshot("Feb 2026", "2026-03-24", "2026-02-05", "AEI-2026-03", None,
             "one-week sample, 5-12 Feb 2026; O*NET 20.1 tasks"),
    Snapshot("Apr 2026", "2026-06-26", "2026-04-01", "AEI-2026-06", "renormalized",
             "calendar month, chat sampling from 10 April; O*NET 30.2 tasks and SOC 2018; new "
             "sampling, request taxonomy, artifact classifier and trait scales; no counts"),
    Snapshot("May 2026", "2026-06-26", "2026-05-01", "AEI-2026-06", "renormalized",
             "calendar month; methods as in April 2026"),
)  # fmt: skip
HEADLINE = SNAPSHOTS[-1]  # ADR 0006 item 6

PATTERNS = ("directive", "feedback_loop", "task_iteration", "learning", "validation")
AUTOMATION = ("directive", "feedback_loop")
USE_CASES = ("work", "personal", "coursework")
TRAITS = (
    "ai_autonomy_mean",
    "human_education_years_mean",
    "ai_education_years_mean",
    "human_only_time_mean",
    "human_with_ai_time_mean",
    "human_only_ability_pct",
    "multitasking_pct",
)
METRICS = (
    *(f"use_case_{use_case}" for use_case in USE_CASES),
    "automation",
    "augmentation",
    *PATTERNS,
    *TRAITS,
    "top_100_tasks",
)
# Trait units are those of the 2026-06-26 documentation; the weekly releases use other scales.
LABELS = {
    "use_case_work": "Work, % of use cases",
    "use_case_personal": "Personal, % of use cases",
    "use_case_coursework": "Coursework, % of use cases",
    "automation": "Automation, % of collaboration patterns",
    "augmentation": "Augmentation, % of collaboration patterns",
    "directive": "Directive, % of patterns",
    "feedback_loop": "Feedback loop, % of patterns",
    "task_iteration": "Task iteration, % of patterns",
    "learning": "Learning, % of patterns",
    "validation": "Validation, % of patterns",
    "ai_autonomy_mean": "AI autonomy, mean (1-5 scale)",
    "human_education_years_mean": "Human education needed, mean years",
    "ai_education_years_mean": "AI education shown, mean years",
    "human_only_time_mean": "Time for a human alone, mean hours",
    "human_with_ai_time_mean": "Time for a human with AI, mean minutes",
    "human_only_ability_pct": "A human could do it alone, % yes",
    "multitasking_pct": "Several tasks in one conversation, % yes",
    "top_100_tasks": "Top 100 O*NET tasks, % of conversations",
}
EN_DASH = "\N{EN DASH}"
_GEO_LEVELS = ("country", "global")


def snapshots(path: Path = aei.LONG_TABLE) -> dict[str, pd.DataFrame]:
    """The canonical long table (``make build``) split into the five snapshots, by label."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found: run make build first")
    frame = pd.read_parquet(path)
    return {
        s.label: frame[(frame["release"] == s.release) & (frame["period_start"] == s.period_start)]
        for s in SNAPSHOTS
    }


def country_usage(frame: pd.DataFrame) -> tuple[pd.Series, float | None]:
    """What the AUI is computed from: conversation counts and the 200 floor in the weekly
    releases; in release 2026-06-26, which has no counts, the published shares of the countries
    with a published AUI, and no floor (ADR 0006 item 2)."""
    if (frame["metric"] == "usage_count").any():
        return aei.geo_values(frame, "country", "usage_count"), aui.FLOOR
    shares = aei.geo_values(frame, "country", "usage_pct")
    published = aei.geo_values(frame, "country", "usage_per_capita_index")
    return shares[shares.index.isin(published.index)], None


def headline_aui(frame: pd.DataFrame, population: pd.Series) -> pd.DataFrame:
    """AUI of the ranked countries on the headline basis (ADR 0006 item 4b), with ranks:
    recomputed from counts in the weekly releases; in release 2026-06-26 the published values,
    which are on this basis already. Recomputing them from shares rounded to two decimals would
    only add rounding error (it moves Korea from 14th to 13th in May 2026)."""
    usage, floor = country_usage(frame)
    if floor is None:
        values = aei.geo_values(frame, "country", "usage_per_capita_index")
        return aui.published(values, floor=None)
    return aui.compute(usage, population, basis="renormalized", floor=floor)


def published_aui(
    frame: pd.DataFrame, snapshot: Snapshot, population: pd.Series
) -> pd.DataFrame | None:
    """AUIs on the basis Anthropic published for ``snapshot``, with ranks: the release's own
    index where it has one (August 2025, April-May 2026); for November 2025, whose release has
    none, the anthropic_2025 rule, which reproduces the January 2026 appendix; none for
    February 2026, which was published only as a statement."""
    if snapshot.published_basis is None:
        return None
    usage, floor = country_usage(frame)
    if (frame["metric"] == "usage_per_capita_index").any():
        values = aei.geo_values(frame, "country", "usage_per_capita_index")
        return aui.published(values, usage if floor else None, floor)
    return aui.compute(usage, population, basis=snapshot.published_basis, floor=floor)


def series(frames: dict[str, pd.DataFrame], population: pd.Series) -> pd.DataFrame:
    """M1 for Korea in every snapshot: the published share of global usage and its rank, the
    headline AUI with rank and N, and the published AUI with its basis (ADR 0006 items 4-5)."""
    rows = []
    for snapshot in SNAPSHOTS:
        frame = frames[snapshot.label]
        usage, floor = country_usage(frame)
        headline = headline_aui(frame, population)
        shares = aui.share_ranks(
            aei.geo_values(frame, "country", "usage_pct"), usage, population, floor
        )
        row = {
            "snapshot": snapshot.label,
            "share_pct": shares.loc[KOREA, "share"],
            "share_rank_min": int(shares.loc[KOREA, "rank_min"]),
            "share_rank_max": int(shares.loc[KOREA, "rank_max"]),
            "share_n": len(shares),
            "aui": headline.loc[KOREA, "aui"],
            "rank_min": int(headline.loc[KOREA, "rank_min"]),
            "rank_max": int(headline.loc[KOREA, "rank_max"]),
            "n": len(headline),
            "published_basis": snapshot.published_basis or "",
            "published_aui": float("nan"),
            "published_rank_min": pd.NA,
            "published_rank_max": pd.NA,
            "published_n": pd.NA,
        }
        published = published_aui(frame, snapshot, population)
        if published is not None:
            row["published_aui"] = published.loc[KOREA, "aui"]
            row["published_rank_min"] = int(published.loc[KOREA, "rank_min"])
            row["published_rank_max"] = int(published.loc[KOREA, "rank_max"])
            row["published_n"] = len(published)
        rows.append(row)
    return pd.DataFrame(rows).set_index("snapshot")


def peer_sets(frame: pd.DataFrame, population: pd.Series) -> dict[str, tuple[str, ...]]:
    """ADR 0003 peer sets in one snapshot, Korea excluded: P1a and P1b as listed, where ranked;
    P2, the ranked countries with a headline AUI above 1; P3, every ranked country; P4, the ten
    ranked countries closest to Korea in share of global usage (ties by country code)."""
    others = headline_aui(frame, population).drop(index=KOREA)
    shares = aei.geo_values(frame, "country", "usage_pct")
    distance = (shares[others.index] - shares[KOREA]).abs()
    nearest = sorted(distance.index, key=lambda code: (distance[code], code))[:P4_SIZE]
    return {
        "P1a": tuple(code for code in P1A if code in others.index),
        "P1b": tuple(code for code in P1B if code in others.index),
        "P2": tuple(sorted(others.index[others["aui"] > 1])),
        "P3": tuple(sorted(others.index)),
        "P4": tuple(nearest),
    }


def profile(frame: pd.DataFrame, levels: tuple[str, ...] = _GEO_LEVELS) -> pd.DataFrame:
    """M9 scalar metrics (``METRICS``) of every geography at ``levels`` (countries and
    ``GLOBAL`` by default; ``("subregion",)`` for regions) in one snapshot: shares in percent,
    traits in the release's own units. A metric is missing for a geography whose release does
    not publish all of its inputs."""
    if _monthly(frame):
        patterns = pd.DataFrame(
            {p: _whole(frame, f"collaboration_{p}_pct", levels) for p in PATTERNS}
        )
        use_cases = pd.DataFrame({u: _whole(frame, f"use_case_{u}_pct", levels) for u in USE_CASES})
        traits = {trait: _whole(frame, trait, levels) for trait in TRAITS}
        tasks = _nodes(frame, "onet", "pct", level=0, levels=levels)
    else:
        patterns = _nodes(frame, "collaboration", "collaboration_pct", levels=levels)
        patterns = patterns.rename(columns=lambda node: node.replace(" ", "_"))
        use_cases = _nodes(frame, "use_case", "use_case_pct", levels=levels)
        traits = {
            trait: _whole(frame, trait, levels)
            if trait.endswith("_mean")
            else _yes_share(frame, trait, levels)
            for trait in TRAITS
        }
        tasks = _nodes(frame, "onet_task", "onet_task_pct", levels=levels).drop(
            columns=["none", "not_classified"], errors="ignore"
        )
    columns = {
        f"use_case_{use_case}": share
        for use_case, share in _shares(use_cases.reindex(columns=list(USE_CASES))).items()
    }
    five = _shares(patterns.reindex(columns=list(PATTERNS)))
    augmentation = [pattern for pattern in PATTERNS if pattern not in AUTOMATION]
    columns["automation"] = five[list(AUTOMATION)].sum(axis=1, min_count=len(AUTOMATION))
    columns["augmentation"] = five[augmentation].sum(axis=1, min_count=len(augmentation))
    columns.update(five.items())
    columns.update(traits)
    columns["top_100_tasks"] = _top_share(tasks)
    return pd.concat(columns, axis=1).reindex(columns=list(METRICS)).sort_index()


def against_peers(values: pd.DataFrame, peers: dict[str, tuple[str, ...]]) -> pd.DataFrame:
    """Per metric: Korea, global, each peer set's median and N (members with a value), and
    Korea's rank (1 = highest) among the P3 countries and Korea."""
    rows = []
    for metric in values.columns:
        column = values[metric]
        korea = column.get(KOREA, float("nan"))
        row = {"metric": metric, "korea": korea, "global": column.get(GLOBAL, float("nan"))}
        for name, members in peers.items():
            present = column.reindex(list(members)).dropna()
            row[f"{name}_median"] = present.median()
            row[f"{name}_n"] = len(present)
        pool = column.reindex([*peers["P3"], KOREA]).dropna()
        row["korea_rank"] = int((pool > korea).sum()) + 1 if pd.notna(korea) else pd.NA
        row["rank_n"] = len(pool)
        rows.append(row)
    return pd.DataFrame(rows).set_index("metric")


def m9_by_snapshot(frames: dict[str, pd.DataFrame], population: pd.Series) -> pd.DataFrame:
    """``against_peers`` in every snapshot, for the metrics each release publishes for Korea:
    the stability check of RQ1 (compare gaps, not levels, across releases)."""
    tables = []
    for snapshot in SNAPSHOTS:
        frame = frames[snapshot.label]
        table = against_peers(profile(frame), peer_sets(frame, population))
        tables.append(table.dropna(subset=["korea"]).assign(snapshot=snapshot.label))
    return pd.concat(tables).reset_index().set_index(["snapshot", "metric"])


def soc_mix(frame: pd.DataFrame) -> pd.DataFrame:
    """SOC major-group mix against global, published for August 2025 and April-May 2026
    (ADR 0006 item 7)."""
    if _monthly(frame):
        table = _nodes(frame, "soc_occupation", "pct", level=1)
    else:
        table = _nodes(frame, "soc_occupation", "soc_pct")
    return mix_gaps(table, _node_names(frame, "soc_occupation"))


def request_mix(frame: pd.DataFrame) -> pd.DataFrame:
    """Top-level request topics against global (the major topics of release 2026-06-26)."""
    level = int(frame.loc[frame["facet"] == "request", "hierarchy_level"].max())
    metric = "pct" if _monthly(frame) else "request_pct"
    return mix_gaps(_nodes(frame, "request", metric, level=level), _node_names(frame, "request"))


def artifact_mix(frame: pd.DataFrame) -> pd.DataFrame:
    """Artifact types against global (release 2026-06-26 only)."""
    metrics = sorted(m for m in frame["metric"].unique() if m.startswith("artifact_"))
    table = pd.DataFrame(
        {m.removeprefix("artifact_").removesuffix("_pct"): _whole(frame, m) for m in metrics}
    )
    return mix_gaps(table, {})


def mix_gaps(table: pd.DataFrame, names: dict[str, str]) -> pd.DataFrame:
    """Korea's and the global share of each node of ``table`` (geographies by nodes), over the
    published, classified nodes, and Korea's gap in percentage points, largest first. A node
    that Korea does not publish has no share and no gap."""
    pair = table.reindex(index=[KOREA, GLOBAL]).T.drop(index="not_classified", errors="ignore")
    shares = pair / pair.sum() * 100
    gaps = pd.DataFrame({"korea": shares[KOREA], "global": shares[GLOBAL]})
    gaps["gap_pp"] = gaps["korea"] - gaps["global"]
    gaps.insert(0, "name", [names.get(node, node) for node in gaps.index])
    return gaps.sort_values("gap_pp", ascending=False, kind="stable")


def rank_text(rank_min: int, rank_max: int, n: int) -> str:
    """A rank as published: ``14 of 121``, or a range joined by an en dash for a tie."""
    rank = f"{rank_min}" if rank_min == rank_max else f"{rank_min}{EN_DASH}{rank_max}"
    return f"{rank} of {n}"


def _monthly(frame: pd.DataFrame) -> bool:
    return bool((frame["facet"] == "overall").any())


def _whole(frame: pd.DataFrame, metric: str, levels: tuple[str, ...] = _GEO_LEVELS) -> pd.Series:
    """Whole-geography values of ``metric`` for the geographies at ``levels``; empty when the
    release does not publish the metric."""
    rows = frame[
        frame["geo_level"].isin(levels) & (frame["metric"] == metric) & (frame["node_id"] == "")
    ]
    if rows["geo_id"].duplicated().any():
        raise ValueError(f"{metric}: several values per geography")
    return rows.set_index("geo_id")["value"].rename(metric)


def _nodes(
    frame: pd.DataFrame,
    facet: str,
    metric: str,
    level: int | None = None,
    levels: tuple[str, ...] = _GEO_LEVELS,
) -> pd.DataFrame:
    """Values of ``metric`` in ``facet`` by geography (rows) and node (columns)."""
    rows = frame[
        frame["geo_level"].isin(levels)
        & (frame["facet"] == facet)
        & (frame["metric"] == metric)
        & (frame["node_id"] != "")
    ]
    if level is not None:
        rows = rows[rows["hierarchy_level"] == level]
    return rows.pivot(index="geo_id", columns="node_id", values="value")


def _node_names(frame: pd.DataFrame, facet: str) -> dict[str, str]:
    rows = frame.loc[frame["facet"] == facet, ["node_id", "node_name"]].drop_duplicates()
    return dict(zip(rows["node_id"], rows["node_name"], strict=True))


def _yes_share(
    frame: pd.DataFrame, metric: str, levels: tuple[str, ...] = _GEO_LEVELS
) -> pd.Series:
    """Share of conversations in the ``yes`` category of a yes/no facet of a weekly release."""
    table = _nodes(frame, metric.removesuffix("_pct"), metric, levels=levels)
    return table["yes"].rename(metric) if "yes" in table else pd.Series(dtype="float64")


def _shares(table: pd.DataFrame) -> pd.DataFrame:
    """Each row in percent of its total; a row with an unpublished column stays missing."""
    shares = table.div(table.sum(axis=1), axis=0) * 100
    return shares[table.notna().all(axis=1)].reindex(table.index)


def _top_share(tasks: pd.DataFrame) -> pd.Series:
    """Share of all conversations in the ``TOP_TASKS`` largest published O*NET tasks."""
    if tasks.empty:
        return pd.Series(dtype="float64")
    return tasks.apply(lambda row: row.nlargest(TOP_TASKS).sum(min_count=1), axis=1)
