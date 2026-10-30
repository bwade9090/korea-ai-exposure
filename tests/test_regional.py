"""Regional measures (RQ2): KOSIS joins, intervals, indices, work-usage shares, stability and the
capital-region comparison on synthetic data; the data-marked tests check the pinned KOSIS
denominators against their national totals."""

import json

import pandas as pd
import pytest

from korea_ai_exposure import paths, regional

DATA = pytest.mark.data(
    "data/interim/aei_long.parquet",
    *(
        path.relative_to(paths.ROOT).as_posix()
        for path in (regional.POPULATION_FILE, regional.WORKERS_FILE, regional.EMPLOYED_FILE)
    ),
    *(
        path.relative_to(paths.ROOT).as_posix()
        for path in (regional.WORKPLACE_FILE, regional.RESIDENCE_FILE, regional.GRDP_FILE)
    ),
)


def kosis_rows(tmp_path, rows):
    path = tmp_path / "table.json"
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return path


def test_kosis_table_joins_by_code_and_drops_totals_and_the_merged_region(tmp_path):
    rows = [
        {"C1": "ZONE2017A000000", "C1_NM": "전국", "DT": "100"},
        {"C1": "ZONE2017A202000", "C1_NM": "전남광주통합특별시", "DT": "9"},
        {"C1": "ZONE2017A111100", "C1_NM": "서울특별시", "DT": "60"},
        {"C1": "ZONE2017A292900", "C1_NM": "세종특별자치시", "DT": "1.5"},
    ]
    table = regional.kosis_table(kosis_rows(tmp_path, rows), "moel")
    assert table[["region", "value"]].values.tolist() == [["KR-11", 60.0], ["KR-50", 1.5]]


@pytest.mark.parametrize(
    ("row", "error"),
    [
        ({"C1": "36110", "C1_NM": "세종특별자치시", "DT": "1"}, KeyError),  # a 시군구 code
        ({"C1": "26", "C1_NM": "울산광역시", "DT": "1"}, ValueError),  # admin 26 is Busan
    ],
)
def test_kosis_table_refuses_unknown_codes_and_contradicting_labels(tmp_path, row, error):
    with pytest.raises(error):
        regional.kosis_table(kosis_rows(tmp_path, [row]), "admin")


def test_wilson_interval_matches_textbook_values():
    low, high = regional.wilson(pd.Series([50.0, 0.0]), 100)
    assert low.round(2).tolist() == [40.38, 0.0]
    assert high.round(2).tolist() == [59.62, 3.70]


def test_indices_divide_the_usage_share_by_each_denominator_share():
    usage = pd.DataFrame(
        {"share": [60.0, 40.0], "share_low": [55.0, 35.0], "share_high": [65.0, 45.0]},
        index=["KR-11", "KR-26"],
    )
    denominators = pd.DataFrame(
        {"population": [20.0, 80.0], "workers": [30.0, 70.0], "employed": [25.0, 75.0]},
        index=["KR-11", "KR-26"],
    )
    table = regional.indices(usage, denominators)
    assert table.loc["KR-11", "population_share"] == 20
    assert table.loc["KR-11", "index_population"] == pytest.approx(3.0)
    assert table.loc["KR-26", "index_workers"] == pytest.approx(40 / 70)
    assert table.loc["KR-11", "index_employed_low"] == pytest.approx(55 / 25)


def use_case_rows(region, work, personal, coursework=None):
    nodes = {"work": work, "personal": personal, "coursework": coursework}
    return [
        {
            "geo_level": "subregion",
            "geo_id": region,
            "facet": "use_case",
            "hierarchy_level": 0,
            "node_id": node,
            "node_name": node,
            "metric": "use_case_pct",
            "value": value,
        }
        for node, value in nodes.items()
        if value is not None
    ]


def test_work_usage_weights_usage_by_the_classified_work_share():
    frame = pd.DataFrame(use_case_rows("KR-11", 60, 30, 10) + use_case_rows("KR-26", 30, 50, 20))
    shares = pd.Series({"KR-11": 50.0, "KR-26": 50.0})
    table = regional.work_usage(frame, shares)
    assert table["work_share"].tolist() == pytest.approx([60, 30])
    assert table["work_usage"].tolist() == pytest.approx([100 * 60 / 90, 100 * 30 / 90])
    assert set(table["work_basis"]) == {"classified use cases"}


def test_work_usage_falls_back_to_all_conversations_when_a_use_case_is_unpublished():
    frame = pd.DataFrame(use_case_rows("KR-11", 54, 36, 9) + use_case_rows("KR-31", 45, 50))
    table = regional.work_usage(frame, pd.Series({"KR-11": 50.0, "KR-31": 50.0}))
    assert table["work_share"].tolist() == [54, 45]  # published shares of all conversations
    assert table["work_usage"].sum() == pytest.approx(100)
    assert set(table["work_basis"]) == {"all conversations"}


def test_spearman_uses_average_ranks():
    assert regional.spearman(pd.Series([1, 2, 3]), pd.Series([10, 20, 30])) == pytest.approx(1)
    assert regional.spearman(pd.Series([1, 2, 3]), pd.Series([3, 2, 1])) == pytest.approx(-1)
    assert regional.spearman(pd.Series([1, 2, 3, 4]), pd.Series([1, 1, 2, 3])) == pytest.approx(
        0.9486833
    )


def test_stability_flags_moves_of_more_than_a_third():
    def table(shares, index):
        return pd.DataFrame({"share": shares, "index_population": index}, index=["A", "B", "C"])

    tables = {
        "t1": table([50.0, 30.0, 20.0], [3.0, 1.0, 0.5]),
        "t2": table([40.0, 45.0, 15.0], [1.0, 1.5, 0.4]),  # B +50%, C -25%; A and B swap
        "t3": table([40.0, 45.0, 15.0], [2.5, 1.2, 0.3]),
    }
    rho, moves = regional.stability(tables)
    assert list(zip(rho["first"], rho["second"], strict=True)) == [
        ("t1", "t2"),
        ("t1", "t3"),
        ("t2", "t3"),
    ]
    assert rho.loc[0, "rho"] == pytest.approx(0.5)
    assert moves[["region", "from", "to"]].values.tolist() == [["B", "t1", "t2"]]
    assert moves.loc[0, "change"] == pytest.approx(0.5)


def test_capital_shares_and_ranks_outside_the_capital_region():
    codes = list(regional.REGION_CODES)
    table = pd.DataFrame(
        {
            "share": [100 / 17] * 17,
            "population_share": [100 / 17] * 17,
            "workers_share": [100 / 17] * 17,
            "employed_share": [100 / 17] * 17,
            "index_population": range(17, 0, -1),
        },
        index=codes,
    )
    capital = regional.capital_shares({"May 2026": table})
    assert capital.loc["May 2026", "usage_share"] == pytest.approx(300 / 17)
    ranks = regional.non_capital_ranks(table)
    assert len(ranks) == 14 and set(regional.CAPITAL).isdisjoint(ranks.index)
    assert ranks.iloc[0] == 1 and ranks.index[0] == "KR-26"  # Busan, the highest outside


@DATA
def test_denominators_cover_17_regions_and_match_the_national_population():
    denominators = regional.denominators()
    assert denominators.index.get_level_values("snapshot").unique().tolist() == [
        s.label for s in regional.SNAPSHOTS
    ]
    rows = json.loads(regional.POPULATION_FILE.read_text(encoding="utf-8"))
    for snapshot in regional.SNAPSHOTS:
        month = snapshot.period_start[:4] + snapshot.period_start[5:7]
        national = sum(
            float(r["DT"])
            for r in rows
            if r["C1"] == "00" and r["PRD_DE"] == month and r["C2"] in regional.AGES_15_64
        )
        assert denominators.loc[snapshot.label, "population"].sum() == national
    ratio = regional.commuting_ratio()["ratio"]
    assert ratio.loc[("202601", "KR-11")] == pytest.approx(1.18, abs=0.01)  # ADR 0005
    assert "KR-50" not in ratio.index.get_level_values("region")  # no Sejong in the 시군구 tables


@DATA
def test_committed_denominators_are_current():
    assert regional.DENOMINATORS_CSV.read_text(encoding="utf-8") == regional.denominators_csv()
