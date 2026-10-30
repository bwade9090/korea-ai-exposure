"""Composition against adoption (Phase 5.3-5.6): regional exposure, predicted shares, the fit and
the Bank of Korea comparison on synthetic data; the data-marked test pins the headline fits."""

import pandas as pd
import pytest

from korea_ai_exposure import decomposition, national, regional, regions

DATA = pytest.mark.data(
    "data/interim/aei_long.parquet",
    "data/raw/kosis/KR-OCC/DT_1ES3B06J_202502_202601.json",
    "data/raw/bls/US-OEWS-ST/oesm25st.zip",
    "data/raw/ilo/ILO-WP140/Final_Scores_ISCO08_Gmyrek_et_al_2025.xlsx",
)


def test_regional_exposure_renormalizes_over_published_cells_with_a_value():
    employment = pd.DataFrame(
        {"11": [10.0, 30.0], "12": [30.0, None], "13": [5.0, 5.0]}, index=["KR-11", "KR-26"]
    )
    values = pd.DataFrame(
        {"ilo": [0.2, 0.6, None], "observed": [0.1, 0.1, 0.1]}, index=["11", "12", "13"]
    )
    table = decomposition.regional_exposure(employment, values)
    assert table.loc["KR-11", "ilo"] == pytest.approx((10 * 0.2 + 30 * 0.6) / 40)
    assert table.loc["KR-26", "ilo"] == pytest.approx(0.2)  # 12 unpublished, 13 without a value
    assert table.loc["KR-26", "observed"] == pytest.approx(0.1)


def test_predicted_shares_and_the_fit():
    employment = pd.DataFrame({"a": [1.0, 3.0, 2.0], "b": [3.0, 1.0, 2.0]}, index=["X", "Y", "Z"])
    predicted = decomposition.predicted_shares(employment, pd.Series({"a": 1.0, "b": 3.0}))
    assert predicted.tolist() == pytest.approx([100 * 10 / 24, 100 * 6 / 24, 100 * 8 / 24])
    result = decomposition.fit(predicted * 2, predicted)
    assert (result["r2"], result["rho"], result["n"]) == pytest.approx((1, 1, 3))


def test_bok_rank_orders_name_every_region_once():
    for order in decomposition.BOK_RANKS.values():
        assert sorted(regions.from_name(name).iso for name in order) == sorted(
            regional.REGION_CODES
        )


def test_bok_comparison_recovers_an_identical_ranking():
    order = decomposition.BOK_RANKS["generative"]
    values = pd.Series({regions.from_name(name).iso: 17 - i for i, name in enumerate(order)})
    columns = ("ilo", "observed", "index_population", "observed_work")
    result = decomposition.bok_comparison(pd.DataFrame(dict.fromkeys(columns, values)))
    assert result.loc[result["bok"] == "generative", "rho"].round(9).eq(1).all()
    assert set(result["n"]) == {17}


@DATA
def test_the_decompositions_cover_every_area():
    # Structure only: the values are findings, held back from tracked files until Checkpoint C
    # (ADR 0002); they are in outputs/facts.json.
    frames = national.snapshots()
    korea = decomposition.korea(frames)
    assert korea.notna().all(axis=None) and len(korea) == 17
    for table, n in ((korea, 17), (decomposition.us_states(frames), 51)):
        result = decomposition.fit(table["observed_work"], table["predicted_work"])
        assert result["n"] == n and 0 <= result["r2"] <= 1
        assert table["predicted_work"].sum() == pytest.approx(100)
    bok = decomposition.bok_comparison(korea).set_index(["bok", "project"])["rho"]
    assert bok[("generative", "ilo")] > 0  # the same exposure source as the note's ranking
