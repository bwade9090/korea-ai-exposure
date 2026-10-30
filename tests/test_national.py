"""National profile measures (RQ1): peer sets, shares and collaboration buckets, task
concentration and mix gaps on synthetic snapshots; the data-marked tests check the AUI series
and the buckets against Anthropic's published values."""

import pandas as pd
import pytest

from korea_ai_exposure import aui, national

COLUMNS = [
    "release",
    "period_start",
    "period_end",
    "geo_level",
    "geo_id",
    "facet",
    "hierarchy_level",
    "node_id",
    "node_name",
    "metric",
    "value",
]
DATA = pytest.mark.data(
    "data/interim/aei_long.parquet",
    "data/raw/aei/release_2025_09_15/working_age_pop_2024_country.csv",
)


def snapshot(*records) -> pd.DataFrame:
    """Canonical rows from (geo_id, facet, metric, value[, node_id[, hierarchy_level]])."""
    rows = []
    for geo_id, facet, metric, value, *node in records:
        node_id = node[0] if node else ""
        level = node[1] if len(node) > 1 else 0
        geo_level = "global" if geo_id == "GLOBAL" else "country"
        rows.append(
            ("r", "2026-05-01", "2026-06-01", geo_level, geo_id, facet, level, node_id, node_id,
             metric, float(value))
        )  # fmt: skip
    return pd.DataFrame(rows, columns=COLUMNS)


def test_weekly_profile_shares_buckets_traits_and_task_concentration():
    patterns = {"directive": 30, "feedback loop": 10, "task iteration": 35, "learning": 20,
                "validation": 5, "none": 4}  # fmt: skip
    use_cases = {"work": 50, "personal": 30, "coursework": 19.9, "not_classified": 0.1}
    records = [("KOR", "collaboration", "collaboration_pct", v, n) for n, v in patterns.items()]
    records += [
        ("JPN", "collaboration", "collaboration_pct", v, n)
        for n, v in patterns.items()
        if n != "validation"  # not published for Japan
    ]
    records += [("KOR", "use_case", "use_case_pct", v, n) for n, v in use_cases.items()]
    records += [
        ("KOR", "ai_autonomy", "ai_autonomy_mean", 3.3),
        ("KOR", "human_only_ability", "human_only_ability_pct", 85, "yes"),
        ("KOR", "human_only_ability", "human_only_ability_pct", 15, "no"),
        ("KOR", "onet_task", "onet_task_pct", 10, "none"),
        ("KOR", "onet_task", "onet_task_pct", 15, "not_classified"),
    ]
    records += [("KOR", "onet_task", "onet_task_pct", 0.5, f"task {i}") for i in range(150)]
    result = national.profile(snapshot(*records))
    korea = result.loc["KOR"]
    assert korea["automation"] == pytest.approx(40.0)  # (30 + 10) of the five patterns, not "none"
    assert korea["augmentation"] == pytest.approx(60.0)
    assert korea["task_iteration"] == pytest.approx(35.0)
    assert korea["use_case_work"] == pytest.approx(100 * 50 / 99.9)  # of the classified use cases
    assert korea["ai_autonomy_mean"] == 3.3
    assert korea["human_only_ability_pct"] == 85
    assert pd.isna(korea["multitasking_pct"])
    assert korea["top_100_tasks"] == pytest.approx(50.0)  # "none" and "not_classified" are no tasks
    assert result.loc["JPN", ["automation", "augmentation", "directive"]].isna().all()


def test_monthly_profile_reads_the_overall_metrics_and_leaf_tasks():
    overall = {
        "collaboration_directive_pct": 29.63,
        "collaboration_feedback_loop_pct": 13.16,
        "collaboration_task_iteration_pct": 33.69,
        "collaboration_learning_pct": 17.49,
        "collaboration_validation_pct": 3.83,
        "collaboration_none_pct": 2.2,
        "use_case_work_pct": 47.24,
        "use_case_personal_pct": 37.86,
        "use_case_coursework_pct": 14.9,
        "ai_autonomy_mean": 2.64,
    }
    records = [("KOR", "overall", metric, value) for metric, value in overall.items()]
    records += [("KOR", "onet", "pct", 1.0, str(i), 0) for i in range(120)]
    records += [("KOR", "onet", "pct", 30.0, "4.A.1", 3)]  # a work activity, not a task
    korea = national.profile(snapshot(*records)).loc["KOR"]
    assert korea["automation"] == pytest.approx(100 * (29.63 + 13.16) / 97.8)
    assert korea["use_case_work"] == pytest.approx(47.24)
    assert korea["ai_autonomy_mean"] == 2.64
    assert korea["top_100_tasks"] == pytest.approx(100.0)


def test_peer_sets_follow_adr_0003():
    counts = {
        "KOR": 3000, "GBR": 3250, "JPN": 2750, "DEU": 2400, "FRA": 2200, "BRA": 3900,
        "CAN": 2000, "AUS": 1500, "IND": 5000, "SGP": 900, "MEX": 700, "NZL": 400,
        "USA": 20000, "TWN": 150, "not_classified": 6000, "SYC": 900, "REU": 500,
    }  # fmt: skip
    records = [(geo, "country", "usage_count", n) for geo, n in counts.items()]
    records += [(geo, "country", "usage_pct", n / 1000) for geo, n in counts.items()]
    population = pd.Series(
        1.0, index=[geo for geo in counts if geo not in ("not_classified", "REU")]
    )
    peers = national.peer_sets(snapshot(*records), population)
    assert peers["P1a"] == ("JPN", "SGP", "AUS", "NZL")  # Taiwan is below the 200 floor
    assert peers["P1b"] == ("AUS", "IND", "JPN", "NZL", "SGP")
    # unlocated, Seychelles, Reunion (no population), Taiwan and Korea itself are not peers
    assert peers["P3"] == ("AUS", "BRA", "CAN", "DEU", "FRA", "GBR", "IND", "JPN", "MEX", "NZL",
                           "SGP", "USA")  # fmt: skip
    # equal populations: AUI above 1 means more than the mean count of the 13 ranked countries
    assert peers["P2"] == ("BRA", "IND", "USA")
    # nearest in share; Britain and Japan tie at 0.25 points and are ordered by code
    assert peers["P4"] == ("GBR", "JPN", "DEU", "FRA", "BRA", "CAN", "AUS", "IND", "SGP", "MEX")


def test_mix_gaps_renormalize_over_classified_nodes_and_keep_unpublished_missing():
    table = pd.DataFrame(
        {
            "a": {"KOR": 30.0, "GLOBAL": 20.0},
            "b": {"KOR": 30.0, "GLOBAL": 40.0},
            "c": {"KOR": None, "GLOBAL": 20.0},
            "not_classified": {"KOR": 40.0, "GLOBAL": 20.0},
        }
    )
    gaps = national.mix_gaps(table, {"a": "Alpha"})
    assert list(gaps.index) == ["a", "b", "c"]  # largest gap first, unpublished last
    assert gaps.loc["a", ["korea", "global", "gap_pp"]].tolist() == pytest.approx([50, 25, 25])
    assert gaps.loc["b", "gap_pp"] == pytest.approx(0)
    assert pd.isna(gaps.loc["c", "korea"]) and pd.isna(gaps.loc["c", "gap_pp"])
    assert gaps.loc["a", "name"] == "Alpha" and gaps.loc["b", "name"] == "b"


def test_against_peers_gives_medians_counts_and_koreas_rank():
    values = pd.DataFrame(
        {"m": {"KOR": 5.0, "GLOBAL": 4.0, "A": 1.0, "B": 7.0, "C": None, "D": 6.0}}
    )
    row = national.against_peers(values, {"P1a": ("A", "C"), "P3": ("A", "B", "C", "D")}).loc["m"]
    assert (row["korea"], row["global"]) == (5.0, 4.0)
    assert (row["P1a_median"], row["P1a_n"]) == (1.0, 1)
    assert (row["P3_median"], row["P3_n"]) == (6.0, 3)
    assert (row["korea_rank"], row["rank_n"]) == (3, 4)  # B and D are higher


@pytest.mark.parametrize(
    ("rank_min", "rank_max", "text"), [(14, 14, "14 of 121"), (9, 10, "9\N{EN DASH}10 of 121")]
)
def test_rank_text_shows_ties_as_ranges(rank_min, rank_max, text):
    assert national.rank_text(rank_min, rank_max, 121) == text


@DATA
def test_series_keeps_the_headline_and_published_values():
    series = national.series(national.snapshots(), aui.working_age_population())
    headline = [(round(r.aui, 3), r.rank_min, r.rank_max, r.n) for r in series.itertuples()]
    assert headline == [
        (4.420, 5, 5, 115),
        (3.819, 7, 7, 116),
        (3.692, 12, 12, 116),
        (3.920, 9, 10, 114),
        (3.780, 14, 14, 121),
    ]
    published = series.dropna(subset=["published_aui"])
    assert list(published.index) == ["Aug 2025", "Nov 2025", "Apr 2026", "May 2026"]
    assert published["published_aui"].round(3).tolist() == [3.725, 3.123, 3.92, 3.78]
    assert published["published_rank_min"].tolist() == [5, 7, 9, 14]


@DATA
def test_collaboration_buckets_reproduce_anthropics():
    frames = national.snapshots()
    for label, facet, metric, tolerance in (
        ("Aug 2025", "collaboration_automation_augmentation", "automation_pct", 1e-9),
        ("May 2026", "overall", "collaboration_bucket_automation_pct", 0.02),  # rounded inputs
    ):
        frame = frames[label]
        rows = frame[
            frame["geo_level"].isin(["country", "global"])
            & (frame["facet"] == facet)
            & (frame["metric"] == metric)
        ]
        published = rows.set_index("geo_id")["value"]
        ours = national.profile(frame)["automation"].dropna()
        assert len(ours) > 90
        assert (ours - published[ours.index]).abs().max() < tolerance
