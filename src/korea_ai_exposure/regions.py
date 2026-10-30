"""Korea's 17 first-level regions (시도) and their codes in every system the project meets.

Region codes are a known trap: the same number means different regions in different systems.
26 is Busan in administrative codes but Ulsan in Statistics Korea's survey codes; 36 is Sejong in
one and Jeonnam in the other; Jeju is ISO KR-49 but administrative 50. Every join therefore goes
through this table, by name or by an explicitly named code system, and numeric codes from
different systems are never compared.

Code systems (``CODE_SYSTEMS``):

- ``iso``: ISO 3166-2:KR, used by the Anthropic Economic Index (KR-11 … KR-50).
- ``admin``: administrative (행정구역) codes of resident registration, as in force in 2026
  (Gangwon 51 since 2023-06-11, Jeonbuk 52 since 2024-01-18).
- ``survey``: Statistics Korea survey codes, two digits (지역별고용조사, 경제활동인구조사,
  지역소득).
- ``survey4``: the four-digit form of the survey code used by some KOSIS tables (2600 = Ulsan).
- ``moel``: Ministry of Employment and Labor codes (사업체노동력조사): the survey code doubled,
  then ``00`` (111100 = Seoul).

Gwangju and Jeonnam were merged into 전남광주통합특별시 (administrative code 12) on 2026-07-01
(Act No. 21446). The table describes the 17 regions of every AEI snapshot through May 2026;
``valid_to`` marks the two regions that ended on 2026-06-30.

Name lookup works for 시도-level names only: "광주" means Gwangju Metropolitan City, not the
city of 광주 in Gyeonggi.
"""

import csv
import io
from dataclasses import dataclass
from pathlib import Path

from korea_ai_exposure import paths

CODE_SYSTEMS = ("iso", "admin", "survey", "survey4", "moel")
MERGER_DATE = "2026-07-01"
MERGED_REGION = "전남광주통합특별시"
MERGED_ADMIN_CODE = "12"
CSV_PATH = paths.PROCESSED / "regions.csv"


@dataclass(frozen=True)
class Region:
    iso: str
    name: str  # English name used in figures and tables (CLAUDE.md)
    name_ko: str  # official Korean name in 2026
    short_ko: str
    admin: str
    survey: str
    aliases: tuple[str, ...] = ()
    valid_to: str | None = None

    @property
    def survey4(self) -> str:
        return f"{self.survey}00"

    @property
    def moel(self) -> str:
        return f"{self.survey}{self.survey}00"

    def code(self, system: str) -> str:
        if system not in CODE_SYSTEMS:
            raise ValueError(f"unknown code system {system!r}; use one of {CODE_SYSTEMS}")
        return getattr(self, system)

    def names(self) -> tuple[str, ...]:
        return (self.name, self.name_ko, self.short_ko, *self.aliases)


REGIONS: tuple[Region, ...] = (
    Region("KR-11", "Seoul", "서울특별시", "서울", "11", "11",
           ("Seoul-teukbyeolsi", "Seoul Special City", "서울시")),
    Region("KR-26", "Busan", "부산광역시", "부산", "26", "21",
           ("Busan-gwangyeoksi", "Busan Metropolitan City", "부산시")),
    Region("KR-27", "Daegu", "대구광역시", "대구", "27", "22",
           ("Daegu-gwangyeoksi", "Daegu Metropolitan City", "대구시")),
    Region("KR-28", "Incheon", "인천광역시", "인천", "28", "23",
           ("Incheon-gwangyeoksi", "Incheon Metropolitan City", "인천시")),
    Region("KR-29", "Gwangju", "광주광역시", "광주", "29", "24",
           ("Gwangju-gwangyeoksi", "Gwangju Metropolitan City"), valid_to="2026-06-30"),
    Region("KR-30", "Daejeon", "대전광역시", "대전", "30", "25",
           ("Daejeon-gwangyeoksi", "Daejeon Metropolitan City", "대전시")),
    Region("KR-31", "Ulsan", "울산광역시", "울산", "31", "26",
           ("Ulsan-gwangyeoksi", "Ulsan Metropolitan City", "울산시")),
    Region("KR-50", "Sejong", "세종특별자치시", "세종", "36", "29",
           ("Sejong-si", "Sejong City", "Sejong_si", "Sejong-teukbyeoljachisi", "세종시")),
    Region("KR-41", "Gyeonggi", "경기도", "경기", "41", "31",
           ("Gyeonggi-do", "Gyeonggi Province")),
    Region("KR-42", "Gangwon", "강원특별자치도", "강원", "51", "32",
           ("Gangwon-do", "Gangwon State", "Gangwon-State", "Gangwon-teukbyeoljachido",
            "강원도")),
    Region("KR-43", "Chungbuk", "충청북도", "충북", "43", "33",
           ("Chungcheongbuk-do", "North Chungcheong")),
    Region("KR-44", "Chungnam", "충청남도", "충남", "44", "34",
           ("Chungcheongnam-do", "South Chungcheong")),
    Region("KR-45", "Jeonbuk", "전북특별자치도", "전북", "52", "35",
           ("Jeollabuk-do", "Jeonbuk State", "Jeonbuk-State", "Jeonbuk-teukbyeoljachido",
            "North Jeolla", "전라북도")),
    Region("KR-46", "Jeonnam", "전라남도", "전남", "46", "36",
           ("Jeollanam-do", "South Jeolla"), valid_to="2026-06-30"),
    Region("KR-47", "Gyeongbuk", "경상북도", "경북", "47", "37",
           ("Gyeongsangbuk-do", "North Gyeongsang")),
    Region("KR-48", "Gyeongnam", "경상남도", "경남", "48", "38",
           ("Gyeongsangnam-do", "South Gyeongsang")),
    Region("KR-49", "Jeju", "제주특별자치도", "제주", "50", "39",
           ("Jeju-do", "Jeju-teukbyeoljachido", "Jeju Special Self-Governing Province",
            "제주도")),
)  # fmt: skip


def _normalize(name: str) -> str:
    return "".join(ch for ch in name.casefold() if ch.isalnum())


def _build_name_index() -> dict[str, Region]:
    index: dict[str, Region] = {}
    for region in REGIONS:
        for name in region.names():
            key = _normalize(name)
            if index.get(key, region) is not region:
                raise ValueError(f"name {name!r} is ambiguous between regions")
            index[key] = region
    return index


_BY_NAME = _build_name_index()


def by_code(system: str, code: str) -> Region:
    """The region with ``code`` in the named ``system``; never guess the system."""
    matches = [region for region in REGIONS if region.code(system) == code]
    if len(matches) != 1:
        raise KeyError(f"no region has {system} code {code!r}")
    return matches[0]


def by_iso(code: str) -> Region:
    return by_code("iso", code)


def from_name(name: str) -> Region:
    """The region a 시도-level name refers to, in English or Korean, ignoring case, spaces and
    punctuation (for example "Gangwon-State", "강원도", "Sejong_si")."""
    try:
        return _BY_NAME[_normalize(name)]
    except KeyError:
        raise KeyError(f"unknown region name {name!r}") from None


def regions_on(date: str) -> tuple[Region, ...]:
    """Regions in existence on ``date`` (ISO format); Gwangju and Jeonnam end on 2026-06-30."""
    return tuple(r for r in REGIONS if r.valid_to is None or date <= r.valid_to)


def to_csv() -> str:
    """The region table as CSV text, in the figure order of CLAUDE.md."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["iso", "name", "name_ko", "short_ko", *CODE_SYSTEMS[1:], "valid_to"])
    for r in REGIONS:
        writer.writerow(
            [r.iso, r.name, r.name_ko, r.short_ko, r.admin, r.survey, r.survey4, r.moel,
             r.valid_to or ""]
        )  # fmt: skip
    return out.getvalue()


def write_csv(path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_csv(), encoding="utf-8", newline="\n")
