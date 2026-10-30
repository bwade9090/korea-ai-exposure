"""Figures of the brief (PLAN §9), one function per figure, in the project's shared style:
matplotlib, the Okabe-Ito colour-blind-safe palette, English labels. ``main`` saves each figure
as PNG and SVG in ``outputs/figures`` and writes the captions (period and source) to
``outputs/figures/captions.md``. Phase 3 adds F1-F4 (RQ1), Phase 4 F5-F7 (RQ2)."""

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from korea_ai_exposure import aui, decomposition, national, paths, regional, regions

FIGURES = paths.OUTPUTS / "figures"
COLORS = {  # Okabe and Ito (2008), colour-blind safe
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "green": "#009E73",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "grey": "#999999",
    "black": "#000000",
}
KOREA_COLOR = COLORS["vermillion"]
STYLE = {
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.titlesize": 8.5,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "svg.hashsalt": "korea-ai-exposure",
}
USE_CASE_COLORS = {
    "work": COLORS["blue"],
    "personal": COLORS["sky"],
    "coursework": COLORS["purple"],
}
BUCKET_COLORS = {"automation": COLORS["orange"], "augmentation": COLORS["green"]}
WAP = national.POPULATION_SOURCE


def f1_series(series: pd.DataFrame) -> tuple[Figure, str]:
    """F1: Korea's share of global usage and AUI across the five snapshots, with rank."""
    fig = Figure(figsize=(7.2, 3.0), layout="constrained")
    share_ax, aui_ax = fig.subplots(1, 2)
    x = list(range(len(series)))
    share_ax.bar(x, series["share_pct"], width=0.6, color=KOREA_COLOR)
    for xi, value in zip(x, series["share_pct"], strict=True):
        share_ax.annotate(f"{value:.2f}%", (xi, value), xytext=(0, 2), **_ANNOTATION)
    share_ax.set_ylim(0, series["share_pct"].max() * 1.25)
    share_ax.set_title("Share of global Claude.ai conversations (%)")
    aui_ax.plot(x, series["aui"], color=KOREA_COLOR, marker="o", label="Headline basis")
    aui_ax.plot(
        x,
        series["published_aui"],
        linestyle="none",
        marker="o",
        markersize=8,
        markerfacecolor="none",
        markeredgecolor=COLORS["black"],
        label="As published",
    )
    for xi, row in zip(x, series.itertuples(), strict=True):
        rank = national.rank_text(row.rank_min, row.rank_max, row.n)
        aui_ax.annotate(f"{row.aui:.2f}\nrank {rank}", (xi, row.aui), xytext=(0, 6), **_ANNOTATION)
    aui_ax.set_ylim(0, series["aui"].max() * 1.3)
    aui_ax.set_title("AI Usage Index (AUI)")
    aui_ax.legend(loc="lower left")
    for ax in (share_ax, aui_ax):
        ax.set_xticks(x, list(series.index))
        ax.axvline(2.5, color=COLORS["grey"], linestyle="--", linewidth=0.8)
    aui_ax.text(2.55, aui_ax.get_ylim()[1], "release 2026-06-26", va="top", fontsize=6.5)
    sources = ", ".join(dict.fromkeys(s.source for s in national.SNAPSHOTS))
    caption = (
        "Korea's share of global Claude.ai conversations and AI Usage Index (AUI), five "
        "snapshots: 4-11 August 2025, 13-20 November 2025, 5-12 February 2026, April 2026 and "
        "May 2026. Share: Anthropic's published usage_pct, the share of all sampled "
        "conversations. AUI: share of usage over share of working-age (15-64) population. "
        "Filled markers: the project's headline basis, both shares taken over the ranked "
        "countries (at least 200 conversations, or published, in release 2026-06-26; "
        "pseudo-geographies excluded); labels give the value and Korea's rank. Open markers: "
        "the AUI as published, on each release's basis (August and November 2025: every row "
        "above the floor in the usage total, unlocated conversations included; no value was "
        "published for February 2026). The dashed line marks release 2026-06-26, whose "
        "windows, sampling and classifiers differ, so changes across it mix method change with "
        f"real change. Sources: {sources}; population: {WAP}."
    )
    return fig, caption


def f2_mix(profile: pd.DataFrame, peers: dict[str, tuple[str, ...]]) -> tuple[Figure, str]:
    """F2: use-case mix and collaboration mode, Korea against the P1a and P1b economies."""
    use_cases = [f"use_case_{use_case}" for use_case in national.USE_CASES]
    buckets = list(BUCKET_COLORS)
    order = _economies(profile, peers, [*use_cases, *buckets])
    fig = Figure(figsize=(7.2, 3.8), layout="constrained")
    use_ax, collab_ax = fig.subplots(1, 2, sharey=True)
    y = list(range(len(order)))[::-1]
    _stacked(use_ax, profile.loc[order, use_cases], y, USE_CASE_COLORS)
    _stacked(collab_ax, profile.loc[order, buckets], y, BUCKET_COLORS)
    use_ax.set_yticks(y, [national.NAMES[code] for code in order])
    for label in use_ax.get_yticklabels():
        if label.get_text() == national.NAMES[national.KOREA]:
            label.set_fontweight("bold")
    use_ax.set_title("Use case (% of classified conversations)")
    collab_ax.set_title("Collaboration (% of the five patterns)")
    for ax, n in ((use_ax, 3), (collab_ax, 2)):
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=n)
    caption = (
        "Use-case mix (conversations classified as work, personal or coursework) and "
        "collaboration mode (automation: directive and feedback-loop patterns; augmentation: "
        "task iteration, learning and validation; shares of the five patterns, as in "
        "Anthropic's buckets), Korea, the global sample and the P1a and P1b peer economies, "
        f"May 2026. Source: {national.HEADLINE.source}."
    )
    return fig, caption


def f3_traits(profile: pd.DataFrame, peers: dict[str, tuple[str, ...]]) -> tuple[Figure, str]:
    """F3: task traits, Korea against the P1a and P1b economies (dot plot)."""
    shown = _economies(profile, peers, list(national.TRAITS))
    others = [code for code in shown if code not in (national.KOREA, national.GLOBAL)]
    fig = Figure(figsize=(6.4, 5.4), layout="constrained")
    axes = fig.subplots(len(national.TRAITS), 1)
    for ax, trait in zip(axes, national.TRAITS, strict=True):
        ax.scatter(profile.loc[others, trait], [0] * len(others), s=18, color=COLORS["grey"])
        ax.scatter(profile.loc[national.GLOBAL, trait], 0, s=26, marker="D", color="black")
        korea = profile.loc[national.KOREA, trait]
        ax.scatter(korea, 0, s=44, color=KOREA_COLOR, zorder=3)
        ax.annotate(f"{korea:.2f}", (korea, 0), xytext=(0, 5), **_ANNOTATION)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_title(national.LABELS[trait], fontweight="normal")
    handles = [
        Line2D([], [], linestyle="none", marker="o", color=KOREA_COLOR, label="Korea"),
        Line2D([], [], linestyle="none", marker="D", color="black", label="Global"),
        Line2D([], [], linestyle="none", marker="o", color=COLORS["grey"], label="P1a and P1b"),
    ]
    fig.legend(handles=handles, loc="outside lower center", ncol=3)
    caption = (
        "Task traits of Claude.ai conversations, May 2026: Korea, the global sample and the P1a "
        "and P1b peer economies (grey). Means and shares as published, in the units of the "
        "release documentation; trait levels are not comparable across releases. Source: "
        f"{national.HEADLINE.source}."
    )
    return fig, caption


def f4_gaps(soc: pd.DataFrame, requests: pd.DataFrame, top: int = 5) -> tuple[Figure, str]:
    """F4: SOC major-group mix against global (pp), and the most over- and under-represented
    request topics."""
    soc = soc.dropna(subset=["gap_pp"])
    requests = requests.dropna(subset=["gap_pp"])
    requests = pd.concat([requests.head(top), requests.tail(top)])
    fig = Figure(figsize=(9.0, 4.6), layout="constrained")
    soc_ax, request_ax = fig.subplots(1, 2, width_ratios=[1.15, 1])
    for ax, table in ((soc_ax, soc), (request_ax, requests)):
        y = list(range(len(table)))[::-1]
        colors = [KOREA_COLOR if gap > 0 else COLORS["blue"] for gap in table["gap_pp"]]
        ax.barh(y, table["gap_pp"], color=colors)
        ax.set_yticks(y, list(table["name"]))
        ax.axvline(0, color="black", linewidth=0.6)
        ax.set_xlabel("Korea minus global, percentage points")
    soc_ax.set_title("SOC major groups")
    request_ax.set_title(f"Request topics: the {top} largest gaps each way")
    caption = (
        "Korea's mix against the global sample, May 2026, in percentage points: SOC major "
        "groups (left), and the major request topics with the five largest gaps in each "
        "direction (right). Shares are taken over the published, classified groups. Source: "
        f"{national.HEADLINE.source}."
    )
    return fig, caption


def f5_index(tables: dict[str, pd.DataFrame]) -> tuple[Figure, str]:
    """F5: within-Korea usage index by region in the latest month, earlier snapshots as markers."""
    latest = tables[regional.HEADLINE.label]["index_population"].sort_values()
    fig = Figure(figsize=(6.4, 4.8), layout="constrained")
    ax = fig.subplots()
    y = list(range(len(latest)))
    ax.barh(y, latest, height=0.6, color=KOREA_COLOR, label=regional.HEADLINE.label)
    for (label, table), marker in zip(list(tables.items())[:-1], "osD", strict=True):
        earlier = table["index_population"].reindex(latest.index)
        ax.scatter(
            earlier,
            y,
            marker=marker,
            s=20,
            facecolors="none",
            edgecolors="black",
            label=label,
            zorder=3,
        )
    ax.axvline(1, color=COLORS["grey"], linestyle="--", linewidth=0.8)
    ax.set_yticks(y, [regions.by_iso(code).name for code in latest.index])
    ax.set_xlabel("Share of usage over share of residents aged 15-64 (1 = parity)")
    ax.legend(loc="lower right")
    sources = ", ".join(dict.fromkeys(s.source for s in regional.SNAPSHOTS))
    caption = (
        "Within-Korea usage index by region: the region's share of Korean Claude.ai "
        "conversations over its share of residents aged 15-64 at month end (resident "
        "registration, foreign residents excluded); 1 means parity. Bars: May 2026; markers: "
        "November 2025, February 2026 and April 2026. Usage is located by IP address, which can "
        "shift it toward Seoul through commuting, gateways and VPNs; the headline denominator "
        f"is chosen at Checkpoint B. N = 17. Sources: {sources}; {regional.SOURCES['population']}."
    )
    return fig, caption


def f6_capital(capital: pd.DataFrame) -> tuple[Figure, str]:
    """F6: the capital region against the rest: shares of usage, population and employment."""
    headline = capital.loc[regional.HEADLINE.label]
    bars = [(f"Usage, {label}", row.usage_share) for label, row in capital.iterrows()]
    bars += [
        ("Residents aged 15-64", headline.population_share),
        ("Workers by workplace", headline.workers_share),
        ("Employed by residence", headline.employed_share),
    ]
    fig = Figure(figsize=(6.4, 3.2), layout="constrained")
    ax = fig.subplots()
    y = list(range(len(bars)))[::-1]
    shares = [share for _, share in bars]
    ax.barh(y, shares, height=0.6, color=KOREA_COLOR, label="Seoul, Gyeonggi, Incheon")
    ax.barh(
        y,
        [100 - s for s in shares],
        left=shares,
        height=0.6,
        color=COLORS["grey"],
        label="Other 14 regions",
    )
    for yi, share in zip(y, shares, strict=True):
        ax.text(share / 2, yi, f"{share:.1f}", ha="center", va="center", color="white")
    ax.set_yticks(y, [name for name, _ in bars])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Percent of Korea")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
    caption = (
        "The capital region (Seoul, Gyeonggi, Incheon) against the other 14 regions: share of "
        "Korean Claude.ai conversations in each regional snapshot, and shares of residents aged "
        "15-64 (May 2026), workers by workplace region (establishment survey, employees of "
        "industries B-S, May 2026) and employed persons by residence (지역별고용조사, first half "
        f"of 2026). Sources: AEI-2026-01, AEI-2026-03, AEI-2026-06; "
        f"{', '.join(dict.fromkeys(regional.SOURCES[d] for d in regional.DENOMINATORS))}."
    )
    return fig, caption


def f7_grdp(table: pd.DataFrame, grdp: pd.Series, association: dict) -> tuple[Figure, str]:
    """F7: usage index against GRDP per capita, 17 regions."""
    x = grdp.reindex(table.index) / 1000
    fig = Figure(figsize=(6.0, 4.2), layout="constrained")
    ax = fig.subplots()
    ax.scatter(x, table["index_population"], s=28, color=KOREA_COLOR, zorder=3)
    for code, xi, yi in zip(table.index, x, table["index_population"], strict=True):
        ax.annotate(
            regions.by_iso(code).name,
            (xi, yi),
            xytext=_LABEL_OFFSETS.get(code, (4, 2)),
            textcoords="offset points",
            fontsize=6.5,
        )
    ax.set_yscale("log")
    ax.minorticks_off()
    ax.set_yticks([0.2, 0.5, 1, 2, 4], ["0.2", "0.5", "1", "2", "4"])
    ax.axhline(1, color=COLORS["grey"], linestyle="--", linewidth=0.8)
    ax.set_xlabel("GRDP per capita, 2024 (million won, current prices)")
    ax.set_ylabel("Usage index, May 2026 (log scale)")
    rho, n = association["rho"], association["n"]
    ax.set_title(f"Spearman's rho = {rho:.2f}, N = {n}")
    caption = (
        "Within-Korea usage index (May 2026; share of usage over share of residents aged 15-64) "
        "against GRDP per capita (2024, preliminary, current prices), 17 regions; log scale for "
        f"the index. Spearman's rho = {rho:.2f} (N = {n}): an association, not an effect. "
        f"Sources: {regional.HEADLINE.source}; {regional.SOURCES['population']}; "
        f"{regional.SOURCES['grdp']}."
    )
    return fig, caption


def f8_us(states: pd.DataFrame, fit: dict) -> tuple[Figure, str]:
    """F8: US states, observed against predicted work usage."""
    fig = Figure(figsize=(5.6, 4.8), layout="constrained")
    ax = fig.subplots()
    _observed_against_predicted(ax, states, fit, COLORS["blue"])
    labels = (np.log(states["residual"]).abs()).nlargest(6).index
    for code in labels:
        row = states.loc[code]
        ax.annotate(
            code,
            (row.predicted_work, row.observed_work),
            xytext=(4, 2),
            textcoords="offset points",
            fontsize=6.5,
        )
    ax.set_xlabel("Predicted share of US work usage (%, occupational composition)")
    ax.set_ylabel("Observed share of US work usage (%, May 2026)")
    caption = (
        "US states and DC: observed share of US work-related Claude.ai conversations (May 2026: "
        "each state's usage share times its work share, normalized) against the share predicted "
        "by occupational composition (OEWS May 2025 state employment by occupation times national "
        "usage per worker, M5a); log scales, dashed line: equality. R^2 is the share of variance "
        "in log observed usage accounted for by log predicted usage. M5a assumes that workers "
        "generate conversations about their own occupation's tasks; AEI classifies conversation "
        f"content, not users' occupations. N = {fit['n']}. Sources: {national.HEADLINE.source}; "
        "US-OEWS-NAT, US-OEWS-ST."
    )
    return fig, caption


def f9_korea(table: pd.DataFrame, fit: dict) -> tuple[Figure, str]:
    """F9: Korea, observed against predicted work usage, residuals, and exposure rank."""
    fig = Figure(figsize=(10.8, 4.0), layout="constrained")
    scatter_ax, residual_ax, rank_ax = fig.subplots(1, 3, width_ratios=[1.1, 1, 1])
    _observed_against_predicted(scatter_ax, table, fit, KOREA_COLOR)
    for code, row in table.iterrows():
        scatter_ax.annotate(
            regions.by_iso(code).name,
            (row.predicted_work, row.observed_work),
            xytext=(3, 2),
            textcoords="offset points",
            fontsize=6,
        )
    scatter_ax.set_xlabel("Predicted share of Korean work usage (%)")
    scatter_ax.set_ylabel("Observed share (%, May 2026)")
    residual = table["residual"].sort_values()
    y = list(range(len(residual)))
    colors = [KOREA_COLOR if r > 1 else COLORS["blue"] for r in residual]
    residual_ax.barh(y, np.log(residual), color=colors, height=0.6)
    residual_ax.set_yticks(y, [regions.by_iso(code).name for code in residual.index])
    ticks = [0.2, 0.5, 1, 2]
    residual_ax.set_xticks(np.log(ticks), [f"{t:g}" for t in ticks])
    residual_ax.axvline(0, color="black", linewidth=0.6)
    residual_ax.set_title("Observed over predicted (log scale)")
    exposure_rank = table["ilo"].rank(ascending=False)
    usage_rank = table["index_population"].rank(ascending=False)
    rank_ax.scatter(exposure_rank, usage_rank, s=22, color=KOREA_COLOR, zorder=3)
    for code in table.index:
        rank_ax.annotate(
            regions.by_iso(code).name,
            (exposure_rank[code], usage_rank[code]),
            xytext=(3, 2),
            textcoords="offset points",
            fontsize=6,
        )
    rank_ax.plot([1, 17], [1, 17], linestyle="--", color=COLORS["grey"], linewidth=0.8)
    rank_ax.set_xlabel("Exposure rank (ILO WP140; 1 = highest)")
    rank_ax.set_ylabel("Usage index rank (1 = highest)")
    rank_ax.set_xticks([1, 5, 9, 13, 17])
    rank_ax.set_yticks([1, 5, 9, 13, 17])
    rank_ax.invert_xaxis()
    rank_ax.invert_yaxis()
    caption = (
        "Korea's 17 regions, May 2026. Left: observed share of Korean work-related Claude.ai "
        "conversations (M4) against the share predicted by occupational composition "
        "(지역별고용조사 employment by KSCO-8 sub-major group, first half of 2026, times US usage "
        "per worker "
        "mapped SOC 2018 to SOC 2010 to ISCO-08 to KSCO-8, M5a); log scales, dashed line: "
        "equality. Centre: residual, observed over predicted, log scale. Right: rank of "
        "occupation-weighted exposure (ILO WP140, M6) against rank of the usage index (residents "
        f"aged 15-64). N = {fit['n']}; associations, not effects; IP-based location can shift "
        f"usage toward Seoul. Sources: {national.HEADLINE.source}; KR-OCC, KR-OCC-NAT, KR-POP; "
        "US-OEWS-NAT; XW-SOC1018, XW-ISCO-SOC, XW-KSCO-ISCO; ILO-WP140."
    )
    return fig, caption


def _observed_against_predicted(ax, table: pd.DataFrame, fit: dict, color: str) -> None:
    ax.scatter(table["predicted_work"], table["observed_work"], s=18, color=color, zorder=3)
    low = min(table["predicted_work"].min(), table["observed_work"].min()) * 0.7
    high = max(table["predicted_work"].max(), table["observed_work"].max()) * 1.4
    ax.plot([low, high], [low, high], linestyle="--", color=COLORS["grey"], linewidth=0.8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title(f"R^2 = {fit['r2']:.2f}, Spearman's rho = {fit['rho']:.2f}, N = {fit['n']}")


_ANNOTATION = {"textcoords": "offset points", "ha": "center", "va": "bottom", "fontsize": 6.5}
_LABEL_OFFSETS = {"KR-49": (4, -9)}  # F7: Jeju's label would cover Gwangju's


def _economies(
    profile: pd.DataFrame, peers: dict[str, tuple[str, ...]], columns: list[str]
) -> list[str]:
    """Korea, global, then the P1a and P1b economies that publish every column."""
    codes = dict.fromkeys([national.KOREA, national.GLOBAL, *peers["P1a"], *peers["P1b"]])
    return [code for code in codes if profile.loc[code, columns].notna().all()]


def _stacked(ax, table: pd.DataFrame, y: list[int], colors: dict[str, str]) -> None:
    """Horizontal stacked bars of ``table``'s columns, labelled and coloured by ``colors``."""
    left = pd.Series(0.0, index=table.index)
    for column, (label, color) in zip(table.columns, colors.items(), strict=True):
        ax.barh(y, table[column], left=left, color=color, height=0.7, label=label)
        for yi, start, width in zip(y, left, table[column], strict=True):
            if width >= 6:
                ax.text(
                    start + width / 2,
                    yi,
                    f"{width:.0f}",
                    ha="center",
                    va="center",
                    fontsize=6.5,
                    color="white",
                )
        left += table[column]
    ax.set_xlim(0, 100)


def main() -> int:
    frames = national.snapshots()
    population = aui.working_age_population()
    headline = frames[national.HEADLINE.label]
    profile = national.profile(headline)
    peers = national.peer_sets(headline, population)
    tables = regional.regional_tables(frames)
    korea, us = decomposition.korea(frames), decomposition.us_states(frames)
    drawings = {
        "F1": lambda: f1_series(national.series(frames, population)),
        "F2": lambda: f2_mix(profile, peers),
        "F3": lambda: f3_traits(profile, peers),
        "F4": lambda: f4_gaps(national.soc_mix(headline), national.request_mix(headline)),
        "F5": lambda: f5_index(tables),
        "F6": lambda: f6_capital(regional.capital_shares(tables)),
        "F7": lambda: f7_grdp(
            tables[regional.HEADLINE.label],
            regional.grdp_per_capita(),
            regional.grdp_association(tables[regional.HEADLINE.label]),
        ),
        "F8": lambda: f8_us(us, decomposition.fit(us["observed_work"], us["predicted_work"])),
        "F9": lambda: f9_korea(
            korea, decomposition.fit(korea["observed_work"], korea["predicted_work"])
        ),
    }
    FIGURES.mkdir(parents=True, exist_ok=True)
    captions = []
    with matplotlib.rc_context(STYLE):
        for name, draw in drawings.items():
            fig, caption = draw()
            fig.savefig(FIGURES / f"{name}.png")
            fig.savefig(FIGURES / f"{name}.svg", metadata={"Date": None})
            captions.append(f"**{name}.** {caption}\n")
            print(f"wrote {name}.png and {name}.svg")
    (FIGURES / "captions.md").write_text("\n".join(captions), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
