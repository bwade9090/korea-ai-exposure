"""AUI bases and ranks (ADR 0006), on synthetic counts."""

import pandas as pd
import pytest

from korea_ai_exposure import aui

USAGE = pd.Series(
    {"AAA": 600.0, "BBB": 300.0, "CCC": 100.0, "DDD": 50.0, "not_classified": 150.0, "SYC": 400.0}
)
POPULATION = pd.Series({"AAA": 1000.0, "BBB": 1000.0, "CCC": 500.0, "DDD": 100.0, "SYC": 1.0})


def test_ranked_countries_clear_the_floor_have_population_and_are_not_excluded():
    assert list(aui.ranked(USAGE, POPULATION, floor=100)) == ["AAA", "BBB", "CCC"]
    assert list(aui.ranked(USAGE, POPULATION, floor=None)) == ["AAA", "BBB", "CCC", "DDD"]


def test_renormalized_basis():
    frame = aui.compute(USAGE, POPULATION, basis="renormalized", floor=100)
    # usage over AAA+BBB+CCC = 1000; population over them = 2500
    assert frame["aui"].round(12).to_dict() == {"AAA": 1.5, "BBB": 0.75, "CCC": 0.5}
    assert list(frame["rank_min"]) == [1, 2, 3]


def test_anthropic_2025_basis_counts_every_row_above_the_floor():
    frame = aui.compute(USAGE, POPULATION, basis="anthropic_2025", floor=100)
    usage_total = 600 + 300 + 100 + 150 + 400  # unlocated and Seychelles included
    population_total = 1000 + 1000 + 500 + 1  # every row above the floor with a population
    expected = (600 / usage_total) / (1000 / population_total)
    assert frame.loc["AAA", "aui"] == pytest.approx(expected)
    assert "SYC" not in frame.index


def test_bases_differ_by_a_constant_factor_so_ranks_agree():
    renormalized = aui.compute(USAGE, POPULATION, basis="renormalized", floor=100)
    rule = aui.compute(USAGE, POPULATION, basis="anthropic_2025", floor=100)
    ratio = rule["aui"] / renormalized["aui"]
    assert ratio.max() == pytest.approx(ratio.min())
    assert list(rule.index) == list(renormalized.index)


def test_ties_show_as_rank_ranges():
    frame = aui.with_ranks(pd.DataFrame({"aui": {"NOR": 3.92, "KOR": 3.92, "SGP": 6.44}}), "aui")
    assert frame[["rank_min", "rank_max"]].to_dict("index") == {
        "SGP": {"rank_min": 1, "rank_max": 1},
        "NOR": {"rank_min": 2, "rank_max": 3},
        "KOR": {"rank_min": 2, "rank_max": 3},
    }


def test_published_values_use_the_floor_only_with_counts():
    values = pd.Series({"AAA": 2.0, "DDD": 9.0, "SYC": 99.0, "not_classified": 1.0})
    assert list(aui.published(values, USAGE, floor=100).index) == ["AAA"]
    assert list(aui.published(values, floor=None).index) == ["DDD", "AAA"]
    with pytest.raises(ValueError, match="counts"):
        aui.published(values)


def test_share_ranks_exclude_pseudo_geographies_and_seychelles():
    shares = pd.Series({"USA": 20.0, "not_classified": 15.0, "SYC": 2.5, "IND": 5.8, "KOR": 3.1})
    frame = aui.share_ranks(shares)
    assert list(frame.index) == ["USA", "IND", "KOR"]
    assert list(frame["rank_min"]) == [1, 2, 3]


def test_invalid_bases_and_floors():
    with pytest.raises(ValueError, match="basis"):
        aui.compute(USAGE, POPULATION, basis="raw")
    with pytest.raises(ValueError, match="counts"):
        aui.compute(USAGE, POPULATION, basis="anthropic_2025", floor=None)


def test_working_age_population_reads_the_aei_file(tmp_path):
    path = tmp_path / "wap.csv"
    path.write_text(
        "iso_alpha_3,year,working_age_pop,country_code,country_name\n"
        'KOR,2024,36307699.0,KR,"Korea, Rep."\nNAM,2024,1798301.0,NA,Namibia\n',
        encoding="utf-8",
    )
    population = aui.working_age_population(path)
    assert population.to_dict() == {"KOR": 36307699.0, "NAM": 1798301.0}
    path.write_text(path.read_text(encoding="utf-8") + "KOR,2024,1.0,KR,Korea\n", "utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        aui.working_age_population(path)
