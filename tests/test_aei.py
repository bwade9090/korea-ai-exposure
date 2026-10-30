"""Schema adapters for the AEI releases, on small synthetic files."""

import json

import pandas as pd
import pytest

from korea_ai_exposure import aei, paths

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


def test_every_release_file_is_pinned_under_its_source_id():
    manifest = json.loads(paths.MANIFEST.read_text(encoding="utf-8"))
    pins = {entry["path"]: entry["source"] for entry in manifest["files"]}
    for release in aei.RELEASES:
        assert pins.get(release.path) == release.source
    assert pins.get(aei.ISO_CODES.relative_to(paths.RAW).as_posix()) == "AEI-2025-09"
