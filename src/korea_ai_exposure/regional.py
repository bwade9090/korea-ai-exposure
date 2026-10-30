"""Korean regional usage: PLAN Phase 4 (RQ2), measures M2-M4 with the denominators of ADR 0005.

Denominators come from pinned KOSIS tables: residents aged 15-64 at month end (resident
registration, which excludes foreign residents), workers by workplace region (establishment
survey: employees of industries B-S only), and employed persons by residence (지역별고용조사,
half-yearly, paired with snapshots as in ADR 0004). Rows are joined through
``regions.from_kosis``, which checks every row's label; national totals and the merged
Gwangju-Jeonnam aggregate are dropped.

Usage is located by IP address, so commuting, mobile and corporate gateways and VPNs can shift
it toward Seoul (CLAUDE.md). Read every result with the commuting check and the stability
measures, and report N = 17 with every cross-regional statistic.
"""

import itertools
import json
from pathlib import Path

import pandas as pd

from korea_ai_exposure import aei, national, paths, regions

SNAPSHOTS = national.SNAPSHOTS[1:]  # regional usage starts in November 2025 (ADR 0006 item 6)
HEADLINE = national.HEADLINE
KOSIS = paths.RAW / "kosis"
POPULATION_FILE = KOSIS / "KR-POP/DT_1B04005N_age15-64_202511_202605.json"
WORKERS_FILE = KOSIS / "KR-WORK-EST/DT_118N_MOND66_workers_202511_202605.json"
EMPLOYED_FILE = KOSIS / "KR-WORK/DT_1ES3B01J_employed_202502_202601.json"
WORKPLACE_FILE = KOSIS / "KR-WORK/DT_1ES3C01S_employed_202502_202601.json"
RESIDENCE_FILE = KOSIS / "KR-WORK/DT_1ES3A01S_employed_202502_202601.json"
GRDP_FILE = KOSIS / "KR-GRDP/DT_1C96_per_capita_2024.json"
SOURCES = {
    "population": "KR-POP",
    "workers": "KR-WORK-EST",
    "employed": "KR-WORK",
    "commuting": "KR-WORK",
    "grdp": "KR-GRDP",
}
AGES_15_64 = tuple(str(age) for age in range(20, 70, 5))  # age classes 15-19 ... 60-64
SURVEY_PERIODS = {  # half-years paired with snapshots (ADR 0004 item 2)
    "Nov 2025": "202502",
    "Feb 2026": "202502",
    "Apr 2026": "202601",
    "May 2026": "202601",
}
DENOMINATORS = ("population", "workers", "employed")
CAPITAL = ("KR-11", "KR-41", "KR-28")  # Seoul, Gyeonggi, Incheon
REGION_CODES = tuple(region.iso for region in regions.REGIONS)
FACET_METRICS = tuple(metric for metric in national.METRICS if metric != "top_100_tasks")
Z95 = 1.959964
DENOMINATORS_CSV = paths.PROCESSED / "denominators.csv"
_NATIONAL = {"admin": "00", "survey": "00", "survey4": "0000", "moel": "000000"}


def kosis_table(path: Path, system: str, item: str | None = None) -> pd.DataFrame:
    """A pinned KOSIS table (JSON rows), optionally only item ``item``, with a numeric ``value``
    (a cell KOSIS marks as not published, "-", is missing) and the ``region`` (ISO code) of each
    row, its code read in ``system``; national totals and the merged-region aggregate are
    dropped, and any other code that is not one of the 17 regions is an error."""
    rows = pd.DataFrame(json.loads(path.read_text(encoding="utf-8")))
    if item is not None:
        rows = rows[rows["ITM_ID"] == item]
    totals = {_NATIONAL[system], regions.MERGED_CODES.get(system)}
    rows = rows[~rows["C1"].str.removeprefix(regions.MOEL_PREFIX).isin(totals)].copy()
    rows["region"] = [
        regions.from_kosis(system, code, label).iso
        for code, label in zip(rows["C1"], rows["C1_NM"], strict=True)
    ]
    if not rows["DT"].str.fullmatch(r"-?[\d.]+|-").all():
        raise ValueError(f"{path.name}: unexpected cell values")
    rows["value"] = pd.to_numeric(rows["DT"], errors="coerce")
    return rows


def denominators() -> pd.DataFrame:
    """ADR 0005 denominators of every regional snapshot, in persons, indexed by snapshot and
    region: residents aged 15-64 at month end (``population``), workers by workplace region
    (``workers``) and employed persons by residence (``employed``, from the paired half-year)."""
    population = kosis_table(POPULATION_FILE, "admin")
    population = population[population["C2"].isin(AGES_15_64)]
    workers = kosis_table(WORKERS_FILE, "moel")
    employed = kosis_table(EMPLOYED_FILE, "survey4")
    tables = []
    for snapshot in SNAPSHOTS:
        month = snapshot.period_start[:4] + snapshot.period_start[5:7]
        half = employed[employed["PRD_DE"] == SURVEY_PERIODS[snapshot.label]]
        table = pd.DataFrame(
            {
                "population": population[population["PRD_DE"] == month]
                .groupby("region")["value"]
                .sum(),
                "workers": workers[workers["PRD_DE"] == month].set_index("region")["value"],
                "employed": half.set_index("region")["value"] * 1000,  # thousand persons
            }
        )
        if sorted(table.index) != sorted(REGION_CODES) or table.isna().any(axis=None):
            raise ValueError(f"{snapshot.label}: the denominators do not cover the 17 regions")
        tables.append(table.assign(snapshot=snapshot.label))
    frame = pd.concat(tables).rename_axis("region").reset_index()
    return frame.set_index(["snapshot", "region"])


def denominators_csv() -> str:
    """The denominators as committed in ``data/processed/denominators.csv``: whole persons."""
    return denominators().to_csv(float_format="%.0f", lineterminator="\n")


def write_denominators(path: Path = DENOMINATORS_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(denominators_csv(), encoding="utf-8", newline="\n")


def commuting_ratio() -> pd.DataFrame:
    """Workplace- over residence-based employment by half-year and region, each summed over the
    시군구 of the 지역별고용조사 (16 regions, no Sejong; not benchmarked to 시도 totals): the
    commuting check of ADR 0005 item 4, not a denominator."""
    sums = {}
    for name, path in (("workplace", WORKPLACE_FILE), ("residence", RESIDENCE_FILE)):
        rows = pd.DataFrame(json.loads(path.read_text(encoding="utf-8")))
        rows["region"] = [regions.by_code("survey", code[:2]).iso for code in rows["C1"]]
        rows["value"] = rows["DT"].astype(float)
        sums[name] = rows.groupby(["PRD_DE", "region"])["value"].sum()
    table = pd.DataFrame(sums)
    table["ratio"] = table["workplace"] / table["residence"]
    return table.rename_axis(["period", "region"])


def grdp_per_capita() -> pd.Series:
    """GRDP per capita by region, 2024 (preliminary), thousand won at current prices."""
    return kosis_table(GRDP_FILE, "survey").set_index("region")["value"].rename("grdp_per_capita")


def wilson(successes: pd.Series, trials: float, z: float = Z95) -> tuple[pd.Series, pd.Series]:
    """Wilson score interval of a binomial share, in percent."""
    p = successes / trials
    centre = (p + z**2 / (2 * trials)) / (1 + z**2 / trials)
    half = z * (p * (1 - p) / trials + z**2 / (4 * trials**2)) ** 0.5 / (1 + z**2 / trials)
    return (centre - half) * 100, (centre + half) * 100


def usage(frame: pd.DataFrame) -> pd.DataFrame:
    """M2 in one snapshot: each region's published share of Korean usage (percent), and in the
    weekly releases its conversation count with a Wilson 95% interval for the share. The
    intervals are understated, because conversations cluster by user (PLAN §6)."""
    table = pd.DataFrame({"share": _korean(aei.geo_values(frame, "subregion", "usage_pct"))})
    if (frame["metric"] == "usage_count").any():
        counts = _korean(aei.geo_values(frame, "subregion", "usage_count"))
        total = aei.geo_values(frame, "country", "usage_count")[national.KOREA]
        low, high = wilson(counts, total)
        table = table.assign(count=counts, share_low=low, share_high=high)
    return table


def indices(usage_table: pd.DataFrame, denominators: pd.DataFrame) -> pd.DataFrame:
    """M3: each region's usage share over its share of each denominator (1.0 = parity), with the
    usage interval carried over where there is one (the denominator taken as exact)."""
    columns = {}
    for name in DENOMINATORS:
        share = denominators[name] / denominators[name].sum() * 100
        columns[f"{name}_share"] = share
        columns[f"index_{name}"] = usage_table["share"] / share
        if "share_low" in usage_table:
            columns[f"index_{name}_low"] = usage_table["share_low"] / share
            columns[f"index_{name}_high"] = usage_table["share_high"] / share
    return pd.DataFrame(columns)


def work_usage(frame: pd.DataFrame, shares: pd.Series) -> pd.DataFrame:
    """M4: each region's share of Korea's work-related usage, u_r * work_r / sum of u_s * work_s
    (percent), with work_r the work share of classified use cases (ADR 0006 item 9). Where the
    release leaves a use case unpublished for a region (coursework in Ulsan and Jeju, February
    2026), every region of that snapshot uses its work share of all conversations instead."""
    classified = national.profile(frame, ("subregion",))["use_case_work"].reindex(shares.index)
    if classified.notna().all():
        work, basis = classified, "classified use cases"
    else:
        work, basis = _work_of_all(frame).reindex(shares.index), "all conversations"
    weighted = shares * work
    table = pd.DataFrame({"work_share": work, "work_usage": weighted / weighted.sum() * 100})
    return table.assign(work_basis=basis)


def regional_tables(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Per regional snapshot: M2 with intervals, the three denominators with their shares, M3
    under each denominator, M4, and the commuting ratio of the paired half-year."""
    denominator = denominators()
    commuting = commuting_ratio()["ratio"]
    tables = {}
    for snapshot in SNAPSHOTS:
        frame = frames[snapshot.label]
        own = denominator.loc[snapshot.label]
        table = usage(frame)
        table = table.join(own).join(indices(table, own)).join(work_usage(frame, table["share"]))
        ratio = commuting.loc[SURVEY_PERIODS[snapshot.label]]
        tables[snapshot.label] = table.join(ratio.rename("commuting_ratio")).loc[list(REGION_CODES)]
    return tables


def spearman(first: pd.Series, second: pd.Series) -> float:
    """Spearman's rank correlation, average ranks for ties (without SciPy)."""
    ranks = pd.concat([first, second], axis=1).dropna().rank()
    return float(ranks.iloc[:, 0].corr(ranks.iloc[:, 1]))


def stability(tables: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """PLAN 4.3: Spearman's rho of the population-based index between every pair of snapshots
    (N = 17), and the regions whose usage share moves by more than a third from one snapshot to
    the next."""
    labels = list(tables)
    rho = [
        {
            "first": a,
            "second": b,
            "rho": spearman(tables[a]["index_population"], tables[b]["index_population"]),
            "n": len(tables[a]),
        }
        for i, a in enumerate(labels)
        for b in labels[i + 1 :]
    ]
    moves = []
    for before, after in itertools.pairwise(labels):
        change = tables[after]["share"] / tables[before]["share"] - 1
        for region in change.index[change.abs() > 1 / 3]:
            moves.append(
                {
                    "region": region,
                    "from": before,
                    "to": after,
                    "share_before": tables[before].loc[region, "share"],
                    "share_after": tables[after].loc[region, "share"],
                    "change": change[region],
                }
            )
    return pd.DataFrame(rho), pd.DataFrame(moves, columns=list(_MOVE_COLUMNS))


_MOVE_COLUMNS = ("region", "from", "to", "share_before", "share_after", "change")


def capital_shares(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """PLAN 4.4: the capital region's (Seoul, Gyeonggi, Incheon) share of usage and of each
    denominator, per snapshot, in percent."""
    columns = ["share", *(f"{name}_share" for name in DENOMINATORS)]
    return pd.DataFrame(
        {label: table.loc[list(CAPITAL), columns].sum() for label, table in tables.items()}
    ).T.rename(columns={"share": "usage_share"})


def non_capital_ranks(table: pd.DataFrame) -> pd.Series:
    """PLAN 4.4: ranks (1 = highest) of the population-based index among the 14 regions outside
    the capital region, which a Seoul-centred gateway bias distorts less."""
    rest = table["index_population"].drop(index=list(CAPITAL))
    return rest.rank(ascending=False, method="min").astype(int).sort_values()


def facets(frame: pd.DataFrame) -> pd.DataFrame:
    """PLAN 4.5: the M9 metrics of the 17 regions and Korea in one snapshot, keeping only the
    metrics published for every region (task concentration is left out: regional task
    breakdowns are sparse, ADR 0006 item 9)."""
    table = national.profile(frame, ("subregion", "country"))
    table = table.reindex([*REGION_CODES, national.KOREA])[list(FACET_METRICS)]
    complete = table.loc[list(REGION_CODES)].notna().all()
    return table.loc[:, complete]


def grdp_association(table: pd.DataFrame) -> dict[str, float]:
    """PLAN 4.6: Spearman's rho between the population-based index and GRDP per capita, N = 17."""
    grdp = grdp_per_capita()
    return {"rho": spearman(table["index_population"], grdp), "n": len(table)}


def _korean(values: pd.Series) -> pd.Series:
    values = values[values.index.str.startswith("KR-")]
    if sorted(values.index) != sorted(REGION_CODES):
        raise ValueError("the snapshot does not publish all 17 Korean regions")
    return values


def _work_of_all(frame: pd.DataFrame) -> pd.Series:
    """Each region's published work share of all its conversations (both release schemas)."""
    rows = frame[
        (frame["geo_level"] == "subregion")
        & (
            ((frame["metric"] == "use_case_work_pct") & (frame["node_id"] == ""))
            | ((frame["metric"] == "use_case_pct") & (frame["node_id"] == "work"))
        )
    ]
    return rows.set_index("geo_id")["value"]
