"""Crosswalk weights and occupation measures (PLAN §7, Phase 5.1-5.2) on synthetic tables; the
data-marked test checks the invariants and coverage on the pinned files."""

import pandas as pd
import pytest

from korea_ai_exposure import crosswalk, national, paths

DATA = pytest.mark.data(
    "data/interim/aei_long.parquet",
    *(
        path.relative_to(paths.ROOT).as_posix()
        for path in (
            crosswalk.SOC1018_FILE,
            crosswalk.ISCO_SOC_FILE,
            crosswalk.SOC_STRUCTURE_FILE,
            crosswalk.OEWS_NATIONAL_FILE,
            crosswalk.ILO_FILE,
            crosswalk.KSSC_FILE,
            crosswalk.KR_OCC_NATIONAL_FILE,
            crosswalk.JOB_EXPOSURE_FILE,
        )
    ),
)


def test_soc_isco_weights_split_equally_and_sum_to_one(monkeypatch):
    monkeypatch.setattr(
        crosswalk, "_soc_2018_to_2010", lambda: {"A": ("a1", "a2"), "B": ("b1",), "C": ("c1",)}
    )
    monkeypatch.setattr(
        crosswalk,
        "_soc_2010_to_isco",
        lambda: {"a1": ("1111",), "a2": ("2222", "3333"), "b1": ("2222",)},
    )
    weights = crosswalk.soc_isco_weights({"A": ("A",), "AGG": ("A", "B"), "C": ("C",)})
    unit = weights.set_index(["unit", "isco"])["weight"]
    assert unit["A"].to_dict() == pytest.approx({"1111": 0.5, "2222": 0.25, "3333": 0.25})
    # an aggregate averages its components' allocations (D5)
    assert unit["AGG"].to_dict() == pytest.approx({"1111": 0.25, "2222": 0.625, "3333": 0.125})
    assert "C" not in set(weights["unit"])  # no ISCO link: left out and listed by the audit
    assert weights.groupby("unit")["weight"].sum().tolist() == pytest.approx([1, 1])


def test_isco_values_weight_by_the_allocated_employment(monkeypatch):
    monkeypatch.setattr(crosswalk, "ilo_scores", lambda: pd.Series({"1111": 0.4}, name="ilo"))
    soc = pd.DataFrame(
        {"employment": [100.0, 300.0], "usage_share": [10.0, 10.0], "observed": [0.2, 0.6]},
        index=["S1", "S2"],
    )
    weights = pd.DataFrame(
        {"unit": ["S1", "S2", "S2"], "isco": ["1111", "1111", "2222"], "weight": [1, 0.5, 0.5]}
    )
    table = crosswalk.isco_values(soc, weights)
    assert table.loc["1111", "observed"] == pytest.approx((100 * 0.2 + 150 * 0.6) / 250)
    # usage shares 15 and 5 of 20; allocated employment 250 and 150 of 400
    assert table.loc["1111", "usage"] == pytest.approx(0.75 / 0.625)
    assert table.loc["2222", "usage"] == pytest.approx(0.25 / 0.375)
    assert table.loc["1111", "ilo"] == 0.4 and pd.isna(table.loc["2222", "ilo"])


@pytest.mark.parametrize(
    ("rule", "value"), [("mean", 0.4), ("min", 0.2), ("max", 0.6), ("first", 0.6)]
)
def test_ksco_unit_rules(rule, value):
    isco = pd.DataFrame({m: [0.2, 0.6] for m in crosswalk.MEASURES}, index=["1111", "2222"])
    links = pd.DataFrame({"ksco": ["0101", "0101", "0102"], "isco": ["2222", "1111", "1111"]})
    table = crosswalk.ksco_unit_values(isco, links, rule)
    assert table.loc["0101", "ilo"] == pytest.approx(value)
    assert table.loc["0102", "ilo"] == pytest.approx(0.2)


def test_ksco_values_average_units_then_weight_minor_groups_by_employment():
    units = pd.DataFrame(
        {m: [1.0, 3.0, 10.0] for m in crosswalk.MEASURES}, index=["1111", "1112", "1121"]
    )
    minor_employment = pd.Series({"111": 30.0, "112": 10.0})
    table = crosswalk.ksco_values(units, minor_employment)
    assert table.loc["11", "usage"] == pytest.approx((2 * 30 + 10 * 10) / 40)


@DATA
def test_the_chain_keeps_its_invariants_and_covers_us_and_korean_employment():
    frames = national.snapshots()
    soc = crosswalk.soc_values(frames)
    weights = crosswalk.soc_isco_weights(crosswalk.components(soc.index))
    assert weights.groupby("unit")["weight"].sum().round(9).eq(1).all()
    coverage = crosswalk.coverage(frames)
    assert (coverage["us_mapped_to_isco"] > 0.999).all()
    assert (coverage["korea_with_value"] > 0.97).all()
    assert crosswalk.audit(frames)["oews_units_without_isco"] == ["19-2099", "53-2022"]
    values = crosswalk.occupation_values(frames)
    assert len(values) == 56 and values.notna().all(axis=None)
