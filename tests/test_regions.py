"""The Korean region table covers all 17 regions in every code system (CLAUDE.md data rules)."""

import pytest

from korea_ai_exposure import regions

FIGURE_ORDER = [
    "Seoul", "Busan", "Daegu", "Incheon", "Gwangju", "Daejeon", "Ulsan", "Sejong", "Gyeonggi",
    "Gangwon", "Chungbuk", "Chungnam", "Jeonbuk", "Jeonnam", "Gyeongbuk", "Gyeongnam", "Jeju",
]  # fmt: skip
ISO_3166_2_KR = {
    "KR-11", "KR-26", "KR-27", "KR-28", "KR-29", "KR-30", "KR-31", "KR-41", "KR-42", "KR-43",
    "KR-44", "KR-45", "KR-46", "KR-47", "KR-48", "KR-49", "KR-50",
}  # fmt: skip


def test_seventeen_regions_in_figure_order():
    assert [region.name for region in regions.REGIONS] == FIGURE_ORDER


def test_iso_codes_are_the_iso_3166_2_list():
    assert {region.iso for region in regions.REGIONS} == ISO_3166_2_KR


@pytest.mark.parametrize("system", regions.CODE_SYSTEMS)
def test_codes_are_unique_within_each_system(system):
    codes = [region.code(system) for region in regions.REGIONS]
    assert len(set(codes)) == 17


@pytest.mark.parametrize(
    ("system", "code", "name"),
    [
        ("iso", "KR-26", "Busan"),
        ("admin", "26", "Busan"),
        ("survey", "26", "Ulsan"),
        ("survey4", "2600", "Ulsan"),
        ("admin", "36", "Sejong"),
        ("survey", "36", "Jeonnam"),
        ("survey", "29", "Sejong"),
        ("iso", "KR-29", "Gwangju"),
        ("iso", "KR-49", "Jeju"),
        ("iso", "KR-50", "Sejong"),
        ("admin", "50", "Jeju"),
        ("survey", "39", "Jeju"),
        ("iso", "KR-42", "Gangwon"),
        ("admin", "51", "Gangwon"),
        ("iso", "KR-45", "Jeonbuk"),
        ("admin", "52", "Jeonbuk"),
        ("survey4", "2900", "Sejong"),
        ("moel", "292900", "Sejong"),
        ("moel", "111100", "Seoul"),
        ("moel", "363600", "Jeonnam"),
    ],
)
def test_the_same_number_means_different_regions_by_system(system, code, name):
    assert regions.by_code(system, code).name == name


def test_unknown_codes_and_systems_are_errors():
    with pytest.raises(KeyError):
        regions.by_code("admin", "42")  # Gangwon's code before 2023-06-11
    with pytest.raises(KeyError):
        regions.by_code("admin", "12")  # 전남광주통합특별시, from 2026-07-01
    with pytest.raises(ValueError):
        regions.by_code("legal_dong", "11")


@pytest.mark.parametrize(
    ("alias", "name"),
    [
        ("Seoul", "Seoul"),
        ("SEOUL", "Seoul"),
        ("서울특별시", "Seoul"),
        ("서울", "Seoul"),
        ("Gangwon-State", "Gangwon"),
        ("Gangwon State", "Gangwon"),
        ("강원도", "Gangwon"),
        ("강원특별자치도", "Gangwon"),
        ("Jeonbuk-State", "Jeonbuk"),
        ("Jeollabuk-do", "Jeonbuk"),
        ("전라북도", "Jeonbuk"),
        ("Sejong_si", "Sejong"),
        ("Sejong City", "Sejong"),
        ("세종특별자치시", "Sejong"),
        ("제주도", "Jeju"),
        ("Gyeonggi-do", "Gyeonggi"),
        ("Chungcheongbuk-do", "Chungbuk"),
        ("경상남도", "Gyeongnam"),
        ("광주광역시", "Gwangju"),
    ],
)
def test_names_in_english_and_korean(alias, name):
    assert regions.from_name(alias).name == name


@pytest.mark.parametrize("name", ["광주시", "Gwangju-si", "Korea", "전남광주통합특별시", ""])
def test_unknown_or_sub_provincial_names_are_errors(name):
    with pytest.raises(KeyError):
        regions.from_name(name)


def test_regions_before_and_after_the_gwangju_jeonnam_merger():
    assert len(regions.regions_on("2026-05-31")) == 17
    assert len(regions.regions_on("2026-06-30")) == 17
    after = {region.name for region in regions.regions_on(regions.MERGER_DATE)}
    assert len(after) == 15
    assert {"Gwangju", "Jeonnam"}.isdisjoint(after)


def test_committed_csv_is_current():
    assert regions.CSV_PATH.read_text(encoding="utf-8") == regions.to_csv()
