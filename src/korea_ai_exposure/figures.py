"""Figures of the brief (PLAN §9), one function per figure, in the project's shared style:
matplotlib, the Okabe-Ito colour-blind-safe palette, English labels. ``main`` saves each figure
as PNG and SVG in ``outputs/figures`` and writes the captions (period and source) to
``outputs/figures/captions.md``. Phase 3 adds F1-F4 (RQ1)."""

import matplotlib
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from korea_ai_exposure import aui, national, paths

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


_ANNOTATION = {"textcoords": "offset points", "ha": "center", "va": "bottom", "fontsize": 6.5}


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
    drawings = {
        "F1": lambda: f1_series(national.series(frames, population)),
        "F2": lambda: f2_mix(profile, peers),
        "F3": lambda: f3_traits(profile, peers),
        "F4": lambda: f4_gaps(national.soc_mix(headline), national.request_mix(headline)),
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
