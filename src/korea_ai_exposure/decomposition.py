"""Composition against adoption: PLAN Phase 5.3-5.6 (RQ3-RQ4), measures M6-M8.

M6, regional exposure: X_r = sum_k s_rk x_k, the employment-weighted mean exposure of each
region's workers over the 56 KSCO-8 sub-major groups (지역별고용조사, first half of 2026, paired
with May 2026). ILO WP140 is the primary measure (ADR 0009), observed exposure the secondary.
M7, predicted work usage: w^_r = sum_k E_rk v_k / sum_s sum_k E_sk v_k, with v_k the US usage per
worker (M5a); the residual R_r = w_r / w^_r compares it with observed work usage (M4). M5a
assumes that workers generate conversations about their own occupation's tasks; AEI classifies
conversation content and does not observe users' occupations. M8 is M7 for the 50 states and
DC, on OEWS state employment by occupation with no crosswalk.

Both shares scale with an area's employment, so areas are compared per worker (ADR 0010): each
share over the area's share of the employment behind the prediction. Predicted usage per worker
is then occupational composition alone, and the residual is unchanged.

Every cross-regional statistic carries N, and all are associations, not effects.
"""

import numpy as np
import pandas as pd

from korea_ai_exposure import aei, crosswalk, national, paths, regional, regions

KR_OCC_FILE = paths.RAW / "kosis/KR-OCC/DT_1ES3B06J_202502_202601.json"
EXPOSURE_MEASURES = ("ilo", "observed")
HEADLINE_EXPOSURE = "ilo"  # ADR 0009
# Bank of Korea, Issue Note 2026-25 (15 September 2026), Figure 7 (p. 9): published regional rank
# orders of occupational exposure, descending. Only the rank orders are used (ADR 0007).
BOK_RANKS = {
    "generative": (
        "Seoul",
        "Sejong",
        "Gyeonggi",
        "Incheon",
        "Busan",
        "Daejeon",
        "Daegu",
        "Gwangju",
        "Jeju",
        "Chungbuk",
        "Ulsan",
        "Gyeongnam",
        "Jeonbuk",
        "Chungnam",
        "Gangwon",
        "Gyeongbuk",
        "Jeonnam",
    ),
    "agentic": (
        "Seoul",
        "Sejong",
        "Gyeonggi",
        "Daejeon",
        "Busan",
        "Daegu",
        "Incheon",
        "Gwangju",
        "Jeju",
        "Jeonbuk",
        "Gyeongnam",
        "Chungbuk",
        "Ulsan",
        "Gangwon",
        "Chungnam",
        "Jeonnam",
        "Gyeongbuk",
    ),
    "physical": (
        "Gyeongbuk",
        "Jeonnam",
        "Chungbuk",
        "Ulsan",
        "Chungnam",
        "Gyeongnam",
        "Gangwon",
        "Jeonbuk",
        "Jeju",
        "Daegu",
        "Gwangju",
        "Incheon",
        "Busan",
        "Daejeon",
        "Gyeonggi",
        "Seoul",
        "Sejong",
    ),
}


def korean_employment(period: str = crosswalk.KOREAN_PERIOD) -> pd.DataFrame:
    """Employed persons (thousands) by region (rows) and KSCO-8 sub-major group (columns) in
    ``period``; cells KOSIS does not publish are missing."""
    rows = regional.kosis_table(KR_OCC_FILE, "survey4", item="T1")
    rows = rows[(rows["PRD_DE"] == period) & rows["C2"].str.fullmatch(r"\d{2}")]
    return rows.pivot(index="region", columns="C2", values="value").loc[list(regional.REGION_CODES)]


def regional_exposure(employment: pd.DataFrame, values: pd.DataFrame) -> pd.DataFrame:
    """M6 for each exposure measure: the employment-weighted mean over the sub-major groups that
    have a value and a published cell (weights renormalized over them, D3)."""
    result = {}
    for measure in EXPOSURE_MEASURES:
        x = values[measure].dropna()
        cells = employment[employment.columns.intersection(x.index)]
        weights = cells.where(cells.notna())
        result[measure] = (weights * x[cells.columns]).sum(axis=1) / weights.sum(axis=1)
    return pd.DataFrame(result)


def predicted_shares(employment: pd.DataFrame, intensity: pd.Series) -> pd.Series:
    """M7 (or M8): each area's share of predicted usage, sum_k E_rk v_k over all areas, in percent,
    over the occupations with an intensity (D3)."""
    v = intensity.dropna()
    cells = employment[employment.columns.intersection(v.index)]
    raw = (cells * v[cells.columns]).sum(axis=1)
    return raw / raw.sum() * 100


def covered_employment(employment: pd.DataFrame, intensity: pd.Series) -> pd.Series:
    """Each area's employment in the published cells with an intensity: the workers behind its
    predicted usage (D3)."""
    return employment[employment.columns.intersection(intensity.dropna().index)].sum(axis=1)


def per_worker(shares: pd.Series, employment: pd.Series) -> pd.Series:
    """A share of usage per worker: the share over the area's share of ``employment`` (1 = the
    average of all areas). For predicted usage over covered employment this is the
    employment-weighted mean intensity of the area's workers over that of all areas."""
    return shares / (employment / employment.sum() * 100)


def fit(observed: pd.Series, predicted: pd.Series) -> dict[str, float]:
    """M7's fit across areas, on usage per worker (ADR 0010). With y the log of observed and p the
    log of predicted usage: R^2 and slope of the regression of y on p, and the share of var(y)
    that p accounts for, cov(y, p) / var(y), in percent; the log residual y - p accounts for the
    rest, and R^2 = slope x share. Spearman's rho and N too."""
    pair = pd.concat([observed, predicted], axis=1).dropna()
    y, p = np.log(pair.iloc[:, 0]), np.log(pair.iloc[:, 1])
    covariance = y.cov(p)
    return {
        "r2": float(y.corr(p) ** 2),
        "slope": float(covariance / p.var()),
        "composition_share": float(covariance / y.var() * 100),
        "rho": regional.spearman(pair.iloc[:, 0], pair.iloc[:, 1]),
        "n": len(pair),
    }


def fits(korea_table: pd.DataFrame, us_table: pd.DataFrame) -> dict[str, dict[str, float]]:
    """The fit for Korea's 17 regions, for the 14 outside the capital region (which a
    Seoul-centred location bias distorts less), and for the 50 states and DC."""
    areas = {
        "korea": korea_table,
        "korea_outside_capital": korea_table.drop(index=list(regional.CAPITAL)),
        "us": us_table,
    }
    return {
        area: fit(table["observed_per_worker"], table["predicted_per_worker"])
        for area, table in areas.items()
    }


def korea(frames: dict[str, pd.DataFrame], values: pd.DataFrame | None = None) -> pd.DataFrame:
    """Phase 5.4 for the 17 regions: M6 under both exposure measures, observed work usage (M4,
    May 2026), predicted work usage (M7), the residual R_r, and both usages per worker."""
    values = crosswalk.occupation_values(frames) if values is None else values
    employment = korean_employment()
    table = regional_exposure(employment, values)
    tables = regional.regional_tables(frames)
    table["observed_work"] = tables[national.HEADLINE.label]["work_usage"]
    table["predicted_work"] = predicted_shares(employment, values["usage"])
    table["residual"] = table["observed_work"] / table["predicted_work"]
    covered = covered_employment(employment, values["usage"])
    table["observed_per_worker"] = per_worker(table["observed_work"], covered)
    table["predicted_per_worker"] = per_worker(table["predicted_work"], covered)
    table["index_population"] = tables[national.HEADLINE.label]["index_population"]
    return table.rename_axis("region")


def us_states(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """M8 (Phase 5.3): for the 50 states and DC, observed work usage (each state's share of US
    usage times its work share, normalized; May 2026), predicted work usage from OEWS state
    employment and the national usage per worker, the residual, both usages per worker, the
    published state AUI, and the share of state employment in published cells with an
    intensity (D4)."""
    soc = crosswalk.soc_values(frames)
    employment = crosswalk.oews_states()
    frame = frames[national.HEADLINE.label]
    shares = _states(aei.geo_values(frame, "subregion", "usage_pct"))
    work = _states(aei.geo_values(frame, "subregion", "use_case_work_pct"))
    weighted = shares * work
    table = pd.DataFrame({"observed_work": weighted / weighted.sum() * 100})
    table["predicted_work"] = predicted_shares(employment, soc["usage"])
    table["residual"] = table["observed_work"] / table["predicted_work"]
    covered = covered_employment(employment, soc["usage"])
    table["observed_per_worker"] = per_worker(table["observed_work"], covered)
    table["predicted_per_worker"] = per_worker(table["predicted_work"], covered)
    table["aui"] = _states(aei.geo_values(frame, "subregion", "usage_per_capita_index"))
    table["coverage"] = covered / _state_totals()
    return table.rename_axis("state")


def bok_comparison(table: pd.DataFrame) -> pd.DataFrame:
    """Phase 5.5: Spearman's rho (N = 17) between each Bank of Korea rank order and the project's
    exposure (M6, both measures), usage index (M3) and observed work usage per worker (M4)
    rankings."""
    rows = []
    for name, order in BOK_RANKS.items():
        bok = pd.Series(
            {regions.from_name(region).iso: len(order) - rank for rank, region in enumerate(order)}
        )
        for column in ("ilo", "observed", "index_population", "observed_per_worker"):
            rows.append(
                {
                    "bok": name,
                    "project": column,
                    "rho": regional.spearman(bok, table[column]),
                    "n": len(bok),
                }
            )
    return pd.DataFrame(rows)


def robustness(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Phase 5.6 (T3): Spearman's rho between each headline regional ranking and its variants:
    the intensity (v, x, ILO), the KSCO weighting rule (minimum, maximum, first link), global
    usage shares for v, the denominator of the index, and the snapshot. Usage rankings are per
    worker (ADR 0010). PLAN §7: rho below 0.9 is reported as not robust."""
    headline_values = crosswalk.occupation_values(frames)
    base = korea(frames, headline_values)
    employment = korean_employment()
    rows = []

    def add(ranking: str, variant: str, other: pd.Series, reference: pd.Series) -> None:
        rho = regional.spearman(reference, other)
        rows.append({"ranking": ranking, "variant": variant, "rho": rho, "robust": rho >= 0.9})

    def predicted(intensity: pd.Series) -> pd.Series:
        shares = predicted_shares(employment, intensity)
        return per_worker(shares, covered_employment(employment, intensity))

    reference = base["predicted_per_worker"]
    for measure in ("observed", "ilo"):
        other = predicted(headline_values[measure])
        add("predicted work usage per worker (v)", f"intensity: {measure}", other, reference)
    add("exposure (ILO)", "exposure: observed", base["observed"], base["ilo"])
    for rule in crosswalk.RULES[1:]:
        values = crosswalk.occupation_values(frames, rule=rule)
        other = predicted(values["usage"])
        add("predicted work usage per worker (v)", f"weighting: {rule}", other, reference)
        add(
            "exposure (ILO)",
            f"weighting: {rule}",
            regional_exposure(employment, values)["ilo"],
            base["ilo"],
        )
    global_values = crosswalk.occupation_values(frames, geography="GLOBAL")
    other = predicted(global_values["usage"])
    add("predicted work usage per worker (v)", "v from global shares", other, reference)
    tables = regional.regional_tables(frames)
    latest = tables[national.HEADLINE.label]
    for denominator in ("workers", "employed"):
        add(
            "usage index (residents 15-64)",
            f"denominator: {denominator}",
            latest[f"index_{denominator}"],
            latest["index_population"],
        )
    for label, table in tables.items():
        if label != national.HEADLINE.label:
            add(
                "usage index (residents 15-64)",
                f"snapshot: {label}",
                table["index_population"],
                latest["index_population"],
            )
            paired = korean_employment(regional.SURVEY_PERIODS[label])
            add(
                "observed work usage per worker",
                f"snapshot: {label}",
                per_worker(
                    table["work_usage"], covered_employment(paired, headline_values["usage"])
                ),
                base["observed_per_worker"],
            )
    return pd.DataFrame(rows)


def _states(values: pd.Series) -> pd.Series:
    """Values of the 50 states and DC, indexed by two-letter code."""
    values = values[values.index.str.startswith("US-")]
    values.index = values.index.str.removeprefix("US-")
    values = values.reindex(crosswalk.STATES)
    if values.isna().any():
        raise ValueError("a state or DC is not published")
    return values


def _state_totals() -> pd.Series:
    """Total employment of each state and DC (the OEWS all-occupations row)."""
    table = crosswalk._oews_table(crosswalk.OEWS_STATE_FILE)
    table = table[(table["O_GROUP"] == "total") & table["PRIM_STATE"].isin(crosswalk.STATES)]
    return pd.to_numeric(table.set_index("PRIM_STATE")["TOT_EMP"], errors="coerce")
