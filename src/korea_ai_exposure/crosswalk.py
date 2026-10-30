"""Occupation crosswalks and occupation measures: PLAN §7 and Phase 5.1-5.2.

Chain (ADR 0004): SOC 2018 -> SOC 2010 (BLS) -> ISCO-08 (BLS) -> KSCO-8 unit group (KSSC,
November 2025 table) -> KSCO-8 sub-major group, the level of the regional employment data. US
occupations are the 830 detailed units of OEWS May 2025; 12 of them are OEWS aggregates (D5).

Weights (PLAN §7, D5): a SOC 2018 code divides its US employment equally over its SOC 2010 codes,
and each SOC 2010 code equally over its ISCO-08 codes; an ISCO group's value is the
employment-weighted mean of the SOC values allocated to it. A KSCO unit takes the equal-weight
mean of its ISCO links (sensitivities: their minimum, their maximum, and the first link listed,
a mechanical stand-in for the KSSC one-to-one rules, which need judgment). Units average
equally within minor groups, and minor groups are weighted by Korean national employment within
sub-major groups. A value missing at any step is left out and the weights renormalized (D3).

Measures (M5): ``usage``, US usage per worker (AEI USA shares of detailed occupations, May 2026,
over OEWS employment shares; D2); ``observed``, Anthropic's observed exposure; ``ilo``, the ILO
WP140 unit-group means (ADR 0009, the primary exposure measure).
"""

import io
import json
import zipfile
from collections import defaultdict
from functools import cache

import pandas as pd

from korea_ai_exposure import national, paths

RAW = paths.RAW
SOC1018_FILE = RAW / "bls/XW-SOC1018/soc_2010_to_2018_crosswalk.xlsx"
ISCO_SOC_FILE = RAW / "bls/XW-ISCO-SOC/ISCO_SOC_Crosswalk.xls"
SOC_STRUCTURE_FILE = RAW / "bls/US-SOC2018/soc_structure_2018.xlsx"
OEWS_NATIONAL_FILE = RAW / "bls/US-OEWS-NAT/oesm25nat.zip"
OEWS_STATE_FILE = RAW / "bls/US-OEWS-ST/oesm25st.zip"
ILO_FILE = RAW / "ilo/ILO-WP140/Final_Scores_ISCO08_Gmyrek_et_al_2025.xlsx"
KSSC_FILE = RAW / "kssc/XW-KSCO-ISCO/KSCO8_ISCO08_linkage_20260127.xlsx"
KR_OCC_NATIONAL_FILE = RAW / "kosis/KR-OCC-NAT/DT_1ES3B32J_202502_202601.json"
JOB_EXPOSURE_FILE = RAW / "aei/labor_market_impacts/job_exposure.csv"
MEASURES = ("usage", "observed", "ilo")
RULES = ("mean", "min", "max", "first")
KOREAN_PERIOD = "202601"  # 2026 first half, paired with April and May 2026 (ADR 0004 item 2)
# The OEWS-specific aggregates and their SOC 2018 components, from the OEWS occupation
# definitions (US-OEWS-OCCDEF); the other seven aggregates are SOC broad groups.
OEWS_AGGREGATES = {
    "21-1018": ("21-1011", "21-1014"),
    "25-2052": ("25-2055", "25-2056"),
    "25-9045": ("25-9042", "25-9043", "25-9049"),
    "51-2028": ("51-2022", "51-2023"),
    "53-1047": ("53-1042", "53-1043", "53-1044", "53-1049"),
}
STATES = (  # the 50 states and DC, as two-letter codes
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
)  # fmt: skip


@cache
def oews_national() -> pd.Series:
    """US employment, May 2025, of the 830 OEWS detailed units."""
    table = _oews_table(OEWS_NATIONAL_FILE)
    detail = table[table["O_GROUP"] == "detailed"].set_index("OCC_CODE")
    return pd.to_numeric(detail["TOT_EMP"], errors="coerce").rename("employment")


@cache
def oews_states() -> pd.DataFrame:
    """US employment, May 2025, by state (50 states and DC) and OEWS detailed unit; suppressed
    cells are missing (D4)."""
    table = _oews_table(OEWS_STATE_FILE)
    table = table[(table["O_GROUP"] == "detailed") & table["PRIM_STATE"].isin(STATES)]
    table = table.assign(employment=pd.to_numeric(table["TOT_EMP"], errors="coerce"))
    return table.pivot(index="PRIM_STATE", columns="OCC_CODE", values="employment")


@cache
def soc_structure() -> tuple[frozenset[str], dict[str, tuple[str, ...]]]:
    """The SOC 2018 detailed codes, and the detailed members of each broad group (the structure
    file lists members under their broad group; codes alone do not identify the parent)."""
    table = pd.read_excel(SOC_STRUCTURE_FILE, header=7, dtype=str)
    table.columns = ["major", "minor", "broad", "detailed", "title"]
    members: dict[str, list[str]] = defaultdict(list)
    broad = None
    for row in table.itertuples():
        if isinstance(row.broad, str):
            broad = row.broad
        if isinstance(row.detailed, str):
            members[broad].append(row.detailed)
    details = frozenset(code for codes in members.values() for code in codes)
    return details, {key: tuple(codes) for key, codes in members.items()}


def components(units: pd.Index) -> dict[str, tuple[str, ...]]:
    """The SOC 2018 detailed components of each OEWS unit: the unit itself, or for an aggregate
    its components (D5)."""
    details, members = soc_structure()
    result = {}
    for unit in units:
        if unit in details:
            result[unit] = (unit,)
        elif unit in OEWS_AGGREGATES:
            result[unit] = OEWS_AGGREGATES[unit]
        elif unit in members:
            result[unit] = members[unit]
        else:
            raise ValueError(f"OEWS unit {unit} is neither a SOC 2018 code nor a known aggregate")
    return result


def soc_isco_weights(unit_components: dict[str, tuple[str, ...]]) -> pd.DataFrame:
    """Allocation of each OEWS unit to ISCO-08 unit groups (``unit``, ``isco``, ``weight``): a SOC
    2018 code splits equally over its SOC 2010 codes and each of those equally over its ISCO
    codes; an aggregate averages its components' allocations. Each unit's weights sum to 1;
    units without any ISCO link are absent (``audit`` lists them)."""
    to2010 = _soc_2018_to_2010()
    to_isco = _soc_2010_to_isco()
    detail_weights: dict[str, dict[str, float]] = {}
    for code, codes2010 in to2010.items():
        weights: dict[str, float] = defaultdict(float)
        for code2010 in codes2010:
            linked = to_isco.get(code2010, ())
            for isco in linked:
                weights[isco] += 1 / len(codes2010) / len(linked)
        if weights:
            total = sum(weights.values())  # below 1 when some SOC 2010 codes have no ISCO link
            detail_weights[code] = {isco: w / total for isco, w in weights.items()}
    rows = []
    for unit, parts in unit_components.items():
        linked = [detail_weights[part] for part in parts if part in detail_weights]
        pooled: dict[str, float] = defaultdict(float)
        for weights in linked:
            for isco, w in weights.items():
                pooled[isco] += w / len(linked)
        rows += [(unit, isco, w) for isco, w in sorted(pooled.items())]
    return pd.DataFrame(rows, columns=["unit", "isco", "weight"])


@cache
def ksco_isco_links() -> pd.DataFrame:
    """KSCO-8 unit group -> ISCO-08 unit group links of the KSSC table (sheet 3-1), in table
    order, markers for multiple (*) and cross-major (#) links removed."""
    sheet = next(s for s in pd.ExcelFile(KSSC_FILE).sheet_names if s.startswith("3-1"))
    table = pd.read_excel(KSSC_FILE, sheet_name=sheet, header=None, dtype=str).iloc[6:, [6, 9]]
    table.columns = ["ksco", "isco"]
    table["ksco"] = table["ksco"].ffill()
    table["isco"] = table["isco"].str.replace(r"[*#\s]", "", regex=True)
    table = table.dropna(subset=["isco"])
    table = table[table["isco"].str.fullmatch(r"\d{4}") & table["ksco"].str.fullmatch(r"\d{4}")]
    return table.drop_duplicates().reset_index(drop=True)


@cache
def ilo_scores() -> pd.Series:
    """ILO WP140 generative-AI exposure (2025 mean score) by ISCO-08 unit group."""
    table = pd.read_excel(ILO_FILE, dtype={"ISCO_08": str})
    means = table.groupby("ISCO_08")["mean_score_2025"].agg(["min", "max"])
    if (means["max"] - means["min"]).abs().max() > 1e-9:
        raise ValueError("ILO WP140: unit-group means differ within a unit group")
    return means["min"].rename("ilo").rename_axis("isco")


def soc_values(frames: dict[str, pd.DataFrame], geography: str = "USA") -> pd.DataFrame:
    """M5 inputs by OEWS unit: US employment; usage share of ``geography`` (USA, or GLOBAL for
    the sensitivity) in May 2026, summed over an aggregate's published components; observed
    exposure, averaged over them; and usage per worker over the units with both shares."""
    employment = oews_national()
    parts = components(employment.index)
    usage = _soc_shares(frames[national.HEADLINE.label], geography)
    observed = pd.read_csv(JOB_EXPOSURE_FILE, dtype={"occ_code": str}).set_index("occ_code")
    observed = observed["observed_exposure"]
    table = pd.DataFrame({"employment": employment})
    table["usage_share"] = [usage.reindex(list(parts[u])).sum(min_count=1) for u in table.index]
    table["observed"] = [observed.reindex(list(parts[u])).mean() for u in table.index]
    both = table.dropna(subset=["usage_share", "employment"])
    table["usage"] = (both["usage_share"] / both["usage_share"].sum()) / (
        both["employment"] / both["employment"].sum()
    )
    return table


def isco_values(soc: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    """Values by ISCO-08 unit group: usage per worker from the usage and employment allocated to
    it, observed exposure as the employment-weighted mean of the allocated units (PLAN §7), and
    the ILO WP140 score."""
    allocated = weights.join(soc, on="unit")
    allocated["employment_w"] = allocated["weight"] * allocated["employment"]
    with_usage = allocated.dropna(subset=["usage_share"])
    usage_share = (
        (with_usage["weight"] * with_usage["usage_share"]).groupby(with_usage["isco"]).sum()
    )
    usage_emp = with_usage.groupby("isco")["employment_w"].sum()
    usage = (usage_share / usage_share.sum()) / (usage_emp / usage_emp.sum())
    with_observed = allocated.dropna(subset=["observed"])
    observed = (with_observed["employment_w"] * with_observed["observed"]).groupby(
        with_observed["isco"]
    ).sum() / with_observed.groupby("isco")["employment_w"].sum()
    table = pd.DataFrame({"usage": usage, "observed": observed})
    return table.join(ilo_scores(), how="outer").rename_axis("isco")


def ksco_unit_values(isco: pd.DataFrame, links: pd.DataFrame, rule: str = "mean") -> pd.DataFrame:
    """Values by KSCO-8 unit group from its ISCO links: their equal-weight mean, or for the
    sensitivities their minimum, maximum, or the first link listed (``RULES``)."""
    if rule not in RULES:
        raise ValueError(f"unknown rule {rule!r}; use one of {RULES}")
    linked = links.join(isco, on="isco")
    columns = list(MEASURES)
    if rule == "first":
        linked = linked.groupby("ksco", sort=False).head(1)
        return linked.set_index("ksco")[columns]
    return linked.groupby("ksco")[columns].agg(rule)


@cache
def korean_minor_employment(period: str = KOREAN_PERIOD) -> pd.Series:
    """Korean national employment (thousands) by KSCO-8 minor group in ``period``."""
    rows = pd.DataFrame(json.loads(KR_OCC_NATIONAL_FILE.read_text(encoding="utf-8")))
    rows = rows[(rows["ITM_ID"] == "T00") & (rows["PRD_DE"] == period)]
    rows = rows[rows["C1"].str.fullmatch(r"\d{3}")]
    return pd.to_numeric(rows.set_index("C1")["DT"], errors="coerce").rename("employment")


def ksco_values(unit_values: pd.DataFrame, minor_employment: pd.Series) -> pd.DataFrame:
    """Values by KSCO-8 sub-major group: units averaged equally within minor groups, minor groups
    weighted by Korean national employment within the sub-major group (PLAN §7)."""
    minors = unit_values.groupby(unit_values.index.str[:3]).mean()
    result = {}
    for measure in unit_values.columns:
        values = minors[measure].dropna()
        weights = minor_employment.reindex(values.index).dropna()
        values = values[weights.index]
        result[measure] = (values * weights).groupby(values.index.str[:2]).sum() / weights.groupby(
            weights.index.str[:2]
        ).sum()
    return pd.DataFrame(result).rename_axis("ksco")


def occupation_values(
    frames: dict[str, pd.DataFrame], rule: str = "mean", geography: str = "USA"
) -> pd.DataFrame:
    """The three M5 measures by KSCO-8 sub-major group, through the full chain."""
    soc = soc_values(frames, geography)
    weights = soc_isco_weights(components(soc.index))
    units = ksco_unit_values(isco_values(soc, weights), ksco_isco_links(), rule)
    return ksco_values(units, korean_minor_employment())


def coverage(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """PLAN §7 coverage: the share of US employment with a value at the SOC level and with an
    ISCO allocation, and the share of Korean employment in minor groups with a value."""
    soc = soc_values(frames)
    weights = soc_isco_weights(components(soc.index))
    mapped = soc.index.isin(weights["unit"])
    units = ksco_unit_values(isco_values(soc, weights), ksco_isco_links())
    minors = units.groupby(units.index.str[:3]).mean()
    korean = korean_minor_employment()
    rows = {}
    for measure in MEASURES:
        rows[measure] = {
            "us_with_value": soc.loc[soc[measure].notna(), "employment"].sum()
            / soc["employment"].sum()
            if measure != "ilo"
            else float("nan"),
            "us_mapped_to_isco": soc.loc[mapped, "employment"].sum() / soc["employment"].sum(),
            "korea_with_value": korean.reindex(minors.index[minors[measure].notna()]).sum()
            / korean.sum(),
        }
    return pd.DataFrame(rows).T


def audit(frames: dict[str, pd.DataFrame]) -> dict[str, list[str]]:
    """Codes that drop out of the chain (PLAN §7 audit table)."""
    soc = soc_values(frames)
    parts = components(soc.index)
    weights = soc_isco_weights(parts)
    links = ksco_isco_links()
    isco_used = set(weights["isco"])
    return {
        "oews_units_without_isco": sorted(set(soc.index) - set(weights["unit"])),
        "isco_without_ksco": sorted(isco_used - set(links["isco"])),
        "ksco_units_without_isco": sorted(_ksco_units() - set(links["ksco"])),
    }


@cache
def _oews_table(path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as archive:
        name = next(n for n in archive.namelist() if n.endswith(".xlsx"))
        return pd.read_excel(io.BytesIO(archive.read(name)), dtype=str)


@cache
def _soc_2018_to_2010() -> dict[str, tuple[str, ...]]:
    table = pd.read_excel(SOC1018_FILE, header=8, dtype=str).iloc[:, [0, 2]].dropna()
    table.columns = ["soc2010", "soc2018"]
    table = table.apply(lambda column: column.str.strip())
    return {code: tuple(group["soc2010"]) for code, group in table.groupby("soc2018")}


@cache
def _soc_2010_to_isco() -> dict[str, tuple[str, ...]]:
    """SOC 2010 -> ISCO-08 unit groups; codes in the BLS file can carry trailing spaces, and its
    two links to 3-digit ISCO groups are left out (no unit group to map)."""
    sheet = "2010 SOC to ISCO-08"
    table = pd.read_excel(ISCO_SOC_FILE, sheet_name=sheet, header=6, dtype=str).iloc[:, [0, 3]]
    table.columns = ["soc2010", "isco"]
    table = table.dropna().apply(lambda column: column.str.strip())
    table = table[table["isco"].str.fullmatch(r"\d{4}")]
    return {code: tuple(group["isco"]) for code, group in table.groupby("soc2010")}


def _soc_shares(frame: pd.DataFrame, geography: str) -> pd.Series:
    """Usage shares of detailed occupations (O*NET-SOC 2019 codes truncated to SOC 2018)."""
    rows = frame[
        (frame["geo_id"] == geography)
        & (frame["facet"] == "soc_occupation")
        & (frame["hierarchy_level"] == 0)
        & (frame["metric"] == "pct")
    ]
    return rows.groupby(rows["node_id"].str[:7])["value"].sum()


@cache
def _ksco_units() -> set[str]:
    sheet = next(s for s in pd.ExcelFile(KSSC_FILE).sheet_names if s.startswith("3-1"))
    table = pd.read_excel(KSSC_FILE, sheet_name=sheet, header=None, dtype=str).iloc[6:, 6]
    return set(table.dropna()[table.dropna().str.fullmatch(r"\d{4}")])
