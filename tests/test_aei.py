"""Schema adapters for the AEI releases, on small synthetic files."""

import pandas as pd
import pytest

from korea_ai_exposure import aei

WEEKLY = "geo_id,geography,date_start,date_end,platform_and_product,facet,level,variable,cluster_name,value\n"  # noqa: E501
MONTHLY = "date_start,date_end,geo_id,geo_level,category_name,hierarchy_level,metric_id,value,node_name,node_external_id\n"  # noqa: E501
WEEK = "2025-11-13,2025-11-20,Claude AI (Free and Pro)"
ISO = {"KR": "KOR", "NA": "NAM", "US": "USA"}


def write(tmp_path, text, name="file.csv"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def weekly(tmp_path, *rows):
    return write(tmp_path, WEEKLY + "\n".join(rows) + "\n")


def test_weekly_rows_become_canonical(tmp_path):
    path = weekly(
        tmp_path,
        f"GLOBAL,global,{WEEK},country,0,usage_count,,1000",
        f"KR,country,{WEEK},country,0,usage_count,,30",
        f"NA,country,{WEEK},country,0,usage_count,,20",
        f"not_classified,country,{WEEK},country,0,usage_count,,5",
        f"KR-11,country-state,{WEEK},country-state,0,usage_count,,12",
        f"CA,state_us,{WEEK},state_us,0,usage_count,,7",
        f"KR,country,{WEEK},onet_task,0,onet_task_pct,write code.,1.5",
    )
    frame = aei.read_weekly(path, "2026-01-15", ISO)
    assert tuple(frame.columns) == aei.COLUMNS
    assert list(frame["geo_id"]) == [
        "GLOBAL", "KOR", "NAM", "not_classified", "KR-11", "US-CA", "KOR",
    ]  # fmt: skip
    assert list(frame["geo_level"]) == ["global"] + ["country"] * 3 + ["subregion"] * 2 + [
        "country"
    ]
    assert set(frame["period_end"]) == {"2025-11-20"}
    assert frame.loc[6, ["node_id", "node_name", "metric", "value"]].tolist() == [
        "write code.", "write code.", "onet_task_pct", 1.5,
    ]  # fmt: skip
    assert frame["hierarchy_level"].dtype == "int64"
    aei.check_long(frame)


def test_weekly_rejects_country_codes_without_a_mapping(tmp_path):
    path = weekly(tmp_path, f"ZZ,country,{WEEK},country,0,usage_count,,30")
    with pytest.raises(ValueError, match="ZZ"):
        aei.read_weekly(path, "2026-01-15", ISO)


def test_weekly_rejects_unknown_geographies(tmp_path):
    path = weekly(tmp_path, f"EU,continent,{WEEK},country,0,usage_count,,30")
    with pytest.raises(ValueError, match="continent"):
        aei.read_weekly(path, "2026-01-15", ISO)


def test_weekly_rejects_windows_other_than_one_week(tmp_path):
    path = weekly(tmp_path, "KR,country,2025-11-13,2025-11-21,Claude AI,country,0,usage_count,,30")
    with pytest.raises(ValueError, match="one-week"):
        aei.read_weekly(path, "2026-01-15", ISO)


def test_weekly_rejects_mixed_products(tmp_path):
    path = weekly(
        tmp_path,
        "KR,country,2025-11-13,2025-11-20,Claude AI (Free and Pro),country,0,usage_count,,30",
        "KR,country,2025-11-13,2025-11-20,1P API,country,0,usage_count,,30",
    )
    with pytest.raises(ValueError, match="platform_and_product"):
        aei.read_weekly(path, "2026-01-15", ISO)


def test_monthly_rows_become_canonical(tmp_path):
    path = write(
        tmp_path,
        MONTHLY
        + "2026-05-01,2026-06-01,KOR,country,overall,0,usage_pct,3.24,Overall,-\n"
        + "2026-05-01,2026-06-01,KR-11,subregion,overall,0,usage_pct,63.65,Overall,-\n"
        + "2026-05-01,2026-06-01,GLOBAL,global,soc_occupation,0,pct,0.0,Desktop Publishers,"
        + "43-9031.00\n",
    )
    frame = aei.read_monthly(path, "2026-06-26")
    assert tuple(frame.columns) == aei.COLUMNS
    assert list(frame["node_id"]) == ["", "", "43-9031.00"]
    assert list(frame["value"]) == [3.24, 63.65, 0.0]
    assert list(frame["facet"]) == ["overall", "overall", "soc_occupation"]
    aei.check_long(frame)


def test_monthly_rejects_unknown_geo_levels(tmp_path):
    path = write(
        tmp_path, MONTHLY + "2026-05-01,2026-06-01,KR,province,overall,0,pct,1,Overall,-\n"
    )
    with pytest.raises(ValueError, match="province"):
        aei.read_monthly(path, "2026-06-26")


def canonical(**overrides):
    row = {
        "release": "2026-06-26",
        "period_start": "2026-05-01",
        "period_end": "2026-06-01",
        "geo_level": "country",
        "geo_id": "KOR",
        "facet": "overall",
        "hierarchy_level": 0,
        "node_id": "",
        "node_name": "Overall",
        "metric": "usage_pct",
        "value": 3.24,
    }
    return pd.DataFrame([row | overrides])


@pytest.mark.parametrize(
    "overrides",
    [
        {"geo_id": "KR"},
        {"geo_level": "subregion", "geo_id": "11"},
        {"geo_level": "global", "geo_id": "WORLD"},
        {"geo_level": "province"},
        {"period_end": "2026-05-01"},
        {"value": None},
    ],
)
def test_check_long_rejects_invalid_rows(overrides):
    with pytest.raises(ValueError):
        aei.check_long(canonical(**overrides))


def test_geo_values_selects_whole_geography_rows():
    frame = pd.concat(
        [
            canonical(),
            canonical(geo_id="JPN", value=3.28),
            canonical(facet="soc_occupation", node_id="15", metric="usage_pct", value=9.0),
            canonical(period_start="2026-04-01", period_end="2026-05-01", value=3.19),
        ],
        ignore_index=True,
    )
    values = aei.geo_values(frame, "country", "usage_pct", "2026-05-01")
    assert values.to_dict() == {"KOR": 3.24, "JPN": 3.28}
    with pytest.raises(ValueError, match="period"):
        aei.geo_values(frame, "country", "usage_pct")


def test_iso_table_keeps_namibia(tmp_path):
    path = write(tmp_path, "iso_alpha_2,iso_alpha_3,country_name\nNA,NAM,Namibia\nKR,KOR,Korea\n")
    assert aei.iso2_to_iso3(path) == {"NA": "NAM", "KR": "KOR"}


def test_geo_values_reads_whole_geography_rows_of_any_facet(tmp_path):
    path = weekly(
        tmp_path,
        f"GLOBAL,global,{WEEK},ai_autonomy,0,ai_autonomy_mean,,3.38",
        f"KR,country,{WEEK},ai_autonomy,0,ai_autonomy_mean,,3.29",
        f"KR-11,country-state,{WEEK},ai_autonomy,0,ai_autonomy_mean,,3.30",
        f"KR,country,{WEEK},human_only_ability,0,human_only_ability_pct,yes,40.0",
    )
    frame = aei.read_weekly(path, "2026-01-15", ISO)
    assert aei.geo_values(frame, "global", "ai_autonomy_mean").to_dict() == {"GLOBAL": 3.38}
    assert aei.geo_values(frame, "country", "ai_autonomy_mean").to_dict() == {"KOR": 3.29}
    assert aei.geo_values(frame, "subregion", "ai_autonomy_mean").to_dict() == {"KR-11": 3.30}
    with pytest.raises(ValueError, match="no whole-geography"):
        aei.geo_values(frame, "country", "human_only_ability_pct")  # categorical: select a node
    with pytest.raises(ValueError, match="no whole-geography"):
        aei.geo_values(frame, "country", "ai_autonomy_maen")


def test_zero_filled_usage_is_dropped_but_population_kept(tmp_path):
    path = weekly(
        tmp_path,
        f"ASM,country,{WEEK},country,0,usage_count,,0",
        f"ASM,country,{WEEK},country,0,usage_pct,,0",
        f"ASM,country,{WEEK},country,0,usage_per_capita_index,,0",
        f"ASM,country,{WEEK},country,0,usage_tier,Minimal,0",
        f"ASM,country,{WEEK},country,0,working_age_pop,,30373",
        f"KR,country,{WEEK},country,0,usage_count,,30",
        f"KR,country,{WEEK},country,0,working_age_pop,,36307699",
    )
    frame = aei.read_weekly(path, "2025-09-15", ISO)
    kept = sorted(zip(frame["geo_id"], frame["metric"], strict=True))
    assert kept == [
        ("ASM", "working_age_pop"), ("KOR", "usage_count"), ("KOR", "working_age_pop"),
    ]  # fmt: skip


def test_korean_regions_in_weekly_and_monthly_frames(tmp_path):
    from korea_ai_exposure import replication

    path = weekly(
        tmp_path,
        f"KR-11,country-state,{WEEK},country-state,0,usage_pct,,58.2",
        f"KR-26,country-state,{WEEK},country-state,0,usage_pct,,3.5",
        f"US-CA,country-state,{WEEK},country-state,0,usage_pct,,15.0",
    )
    weekly_frame = aei.read_weekly(path, "2026-01-15", ISO)
    assert replication.korean_regions(weekly_frame, "usage_pct").to_dict() == {
        "KR-11": 58.2, "KR-26": 3.5,
    }  # fmt: skip
    monthly_frame = pd.concat(
        [
            canonical(geo_level="subregion", geo_id="KR-11", value=63.65),
            canonical(geo_level="subregion", geo_id="JP-13", value=40.0),
        ],
        ignore_index=True,
    )
    regions = replication.korean_regions(monthly_frame, "usage_pct", "2026-05-01")
    assert regions.to_dict() == {"KR-11": 63.65}
