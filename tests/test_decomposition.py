"""Composition against adoption (Phase 5.3-5.6): regional exposure, predicted shares, usage per
worker, the fit and the Bank of Korea comparison on synthetic data; the data-marked test checks
the structure of the headline fits."""

import numpy as np
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


def test_predicted_usage_per_worker_is_the_mean_intensity_of_the_area_s_workers():
    employment = pd.DataFrame(
        {"a": [1.0, 3.0, 4.0], "b": [3.0, None, 4.0], "c": [5.0, 1.0, 1.0]},
        index=["X", "Y", "Z"],
    )
    intensity = pd.Series({"a": 1.0, "b": 3.0, "c": None})  # Y's b unpublished, c without a value
    predicted = decomposition.predicted_shares(employment, intensity)
    assert predicted.tolist() == pytest.approx([100 * 10 / 29, 100 * 3 / 29, 100 * 16 / 29])
    covered = decomposition.covered_employment(employment, intensity)
    assert covered.tolist() == [4.0, 3.0, 8.0]
    # mean intensities 2.5, 1 and 2 over that of all covered workers, 29 / 15: only the mix
    # counts, not Z's twice larger covered employment
    per_worker = decomposition.per_worker(predicted, covered)
    assert per_worker.tolist() == pytest.approx([2.5 * 15 / 29, 1 * 15 / 29, 2 * 15 / 29])


def test_the_fit_splits_the_variance_between_composition_and_residual():
    predicted = pd.Series(np.exp([1.0, -1.0, 1.0, -1.0]))
    residual = pd.Series(np.exp([1.0, 1.0, -1.0, -1.0]))  # uncorrelated with predicted
    result = decomposition.fit(predicted * residual, predicted)
    assert (result["r2"], result["slope"], result["composition_share"]) == pytest.approx(
        (0.5, 1, 50)
    )
    # Regions twice as far apart as composition predicts: a perfect fit, but composition
    # accounts for half of the variance at face value.
    result = decomposition.fit(predicted**2, predicted)
    assert (result["r2"], result["slope"], result["composition_share"]) == pytest.approx((1, 2, 50))
    assert (result["rho"], result["n"]) == pytest.approx((1, 4))


def test_bok_rank_orders_name_every_region_once():
    for order in decomposition.BOK_RANKS.values():
        assert sorted(regions.from_name(name).iso for name in order) == sorted(
            regional.REGION_CODES
        )


def test_bok_comparison_recovers_an_identical_ranking():
    order = decomposition.BOK_RANKS["generative"]
    values = pd.Series({regions.from_name(name).iso: 17 - i for i, name in enumerate(order)})
    columns = ("ilo", "observed", "index_population", "observed_per_worker")
    result = decomposition.bok_comparison(pd.DataFrame(dict.fromkeys(columns, values)))
    assert result.loc[result["bok"] == "generative", "rho"].round(9).eq(1).all()
    assert set(result["n"]) == {17}


@DATA
def test_the_decompositions_cover_every_area():
    # Structure only: the values are findings, held back from tracked files until Checkpoint C
    # (ADR 0002); they are in outputs/facts.json.
    frames = national.snapshots()
    korea, us = decomposition.korea(frames), decomposition.us_states(frames)
    assert korea.notna().all(axis=None) and len(korea) == 17
    for table in (korea, us):
        assert table["predicted_work"].sum() == pytest.approx(100)
        # per worker: the implied employment shares sum to 100 and the residual is unchanged
        shares = table["predicted_work"] / table["predicted_per_worker"]
        assert shares.sum() == pytest.approx(100)
        ratio = table["observed_per_worker"] / table["predicted_per_worker"]
        assert ratio.tolist() == pytest.approx(table["residual"].tolist())
    fits = decomposition.fits(korea, us)
    assert {area: result["n"] for area, result in fits.items()} == {
        "korea": 17,
        "korea_outside_capital": 14,
        "us": 51,
    }
    for result in fits.values():
        assert 0 <= result["r2"] <= 1
        assert result["r2"] == pytest.approx(result["slope"] * result["composition_share"] / 100)
    bok = decomposition.bok_comparison(korea).set_index(["bok", "project"])["rho"]
    assert bok[("generative", "ilo")] > 0  # the same exposure source as the note's ranking
