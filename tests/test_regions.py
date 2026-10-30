"""The Korean region table covers all 17 regions in every code system (CLAUDE.md data rules).

EXPECTED is written out independently of the module, from the code lists of ISO 3166-2:KR,
KOSIS DT_1B04005N (administrative codes) and DT_1C96 / DT_1DA7E34S_NEW (survey codes), so a
swapped or mistyped code in the module fails here.
"""

import datetime

import pytest

from korea_ai_exposure import regions

EXPECTED = {  # name: (ISO 3166-2, administrative, survey, official Korean name)
    "Seoul": ("KR-11", "11", "11", "서울특별시"),
    "Busan": ("KR-26", "26", "21", "부산광역시"),
    "Daegu": ("KR-27", "27", "22", "대구광역시"),
    "Incheon": ("KR-28", "28", "23", "인천광역시"),
    "Gwangju": ("KR-29", "29", "24", "광주광역시"),
    "Daejeon": ("KR-30", "30", "25", "대전광역시"),
    "Ulsan": ("KR-31", "31", "26", "울산광역시"),
    "Sejong": ("KR-50", "36", "29", "세종특별자치시"),
    "Gyeonggi": ("KR-41", "41", "31", "경기도"),
    "Gangwon": ("KR-42", "51", "32", "강원특별자치도"),
    "Chungbuk": ("KR-43", "43", "33", "충청북도"),
    "Chungnam": ("KR-44", "44", "34", "충청남도"),
    "Jeonbuk": ("KR-45", "52", "35", "전북특별자치도"),
    "Jeonnam": ("KR-46", "46", "36", "전라남도"),
    "Gyeongbuk": ("KR-47", "47", "37", "경상북도"),
    "Gyeongnam": ("KR-48", "48", "38", "경상남도"),
    "Jeju": ("KR-49", "50", "39", "제주특별자치도"),
}


def test_seventeen_regions_in_figure_order():
    assert [region.name for region in regions.REGIONS] == list(EXPECTED)


@pytest.mark.parametrize("name", EXPECTED)
def test_every_code_of_every_region(name):
    iso, admin, survey, name_ko = EXPECTED[name]
    region = regions.from_name(name)
    assert (region.iso, region.admin, region.survey, region.name_ko) == (
        iso,
        admin,
        survey,
        name_ko,
    )
    assert region.survey4 == f"{survey}00"
    assert region.moel == f"{survey}{survey}00"
    for system in regions.CODE_SYSTEMS:
        assert regions.by_code(system, region.code(system)) is region
    assert regions.from_name(name_ko) is region


@pytest.mark.parametrize("system", regions.CODE_SYSTEMS)
def test_codes_are_unique_within_each_system(system):
    codes = [region.code(system) for region in regions.REGIONS]
    assert len(set(codes)) == 17


def test_unknown_codes_and_systems_are_errors():
    with pytest.raises(KeyError):
        regions.by_code("admin", "42")  # Gangwon's code before 2023-06-11
    with pytest.raises(ValueError):
        regions.by_code("legal_dong", "11")


@pytest.mark.parametrize(("system", "code"), regions.MERGED_CODES.items())
def test_the_merged_region_matches_no_region(system, code):
    with pytest.raises(KeyError):
        regions.by_code(system, code)


@pytest.mark.parametrize(
    ("alias", "name"),
    [
        ("SEOUL", "Seoul"),
        ("서울", "Seoul"),
        ("Gangwon-State", "Gangwon"),
        ("Gangwon State", "Gangwon"),
        ("강원도", "Gangwon"),
        ("Jeonbuk-State", "Jeonbuk"),
        ("Jeollabuk-do", "Jeonbuk"),
        ("전라북도", "Jeonbuk"),
        ("Sejong_si", "Sejong"),
        ("Sejong City", "Sejong"),
        ("sejong", "Sejong"),
        ("제주도", "Jeju"),
        ("Jeju-do", "Jeju"),
        ("Gyeonggi-do", "Gyeonggi"),
        ("Chungcheongbuk-do", "Chungbuk"),
    ],
)
def test_labels_in_english_and_korean(alias, name):
    assert regions.from_name(alias).name == name


@pytest.mark.parametrize("name", ["광주시", "Gwangju-si", "Korea", "전남광주통합특별시", ""])
def test_unknown_or_sub_provincial_names_are_errors(name):
    with pytest.raises(KeyError):
        regions.from_name(name)


@pytest.mark.parametrize(
    ("system", "code", "label", "name"),
    [
        ("survey4", "2900", "세종", "Sejong"),
        ("survey", "29", "세종특별자치시", "Sejong"),
        ("admin", "36", "세종특별자치시", "Sejong"),
        ("moel", "ZONE2017A292900", "세종특별자치시", "Sejong"),
        ("survey4", "2600", "울산", "Ulsan"),
        ("admin", "51", "강원특별자치도", "Gangwon"),
    ],
)
def test_kosis_rows_are_joined_by_code_and_checked_by_label(system, code, label, name):
    assert regions.from_kosis(system, code, label).name == name


@pytest.mark.parametrize(
    ("system", "code", "label"),
    [
        ("survey", "29010", "세종시"),  # Sejong's 시군구 row in the 2020 census tables
        ("admin", "36110", "세종특별자치시"),  # Sejong's 시군구 row in resident registration
        ("admin", "48130", "울산시"),  # a former city of Gyeongnam
        ("moel", "ZONE2017A202000", "전남광주통합특별시"),
    ],
)
def test_kosis_rows_below_province_level_are_refused(system, code, label):
    with pytest.raises(KeyError):
        regions.from_kosis(system, code, label)


def test_a_label_that_contradicts_the_code_is_refused():
    with pytest.raises(ValueError, match="label"):
        regions.from_kosis("survey", "26", "부산광역시")  # survey 26 is Ulsan


def test_regions_before_and_after_the_gwangju_jeonnam_merger():
    assert len(regions.regions_on("2026-05-31")) == 17
    assert len(regions.regions_on(datetime.date(2026, 6, 30))) == 17
    after = {region.name for region in regions.regions_on(regions.MERGER_DATE)}
    assert len(after) == 15
    assert {"Gwangju", "Jeonnam"}.isdisjoint(after)
    assert len(regions.regions_on(datetime.datetime(2026, 7, 1, 12))) == 15


@pytest.mark.parametrize("value", ["202605", "202601", "2026.05", "20260531", 202605])
def test_kosis_periods_must_be_converted_before_use(value):
    with pytest.raises(ValueError):
        regions.regions_on(value)


def test_committed_csv_is_current():
    assert regions.CSV_PATH.read_text(encoding="utf-8") == regions.to_csv()
