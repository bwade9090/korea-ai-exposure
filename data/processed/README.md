# Processed data

Small derived tables, committed so readers can check them without rebuilding. Each is written by
`make build` from code in `src/korea_ai_exposure/`, and a test checks that the committed file is
current. What may be committed here: ADR 0007. Result tables go to `outputs/tables/`, which stays
untracked until Checkpoint C.

## `regions.csv`

Korea's 17 first-level regions (시도) and their codes in each system the project uses, in the
figure order of `CLAUDE.md`. Written from `korea_ai_exposure.regions`.

| Column | Meaning | Source |
| --- | --- | --- |
| `iso` | ISO 3166-2:KR code, as used by the Anthropic Economic Index | ISO 3166-2:KR |
| `name`, `name_ko`, `short_ko` | English name used in figures; official Korean name in 2026; short Korean name | Ministry of the Interior and Safety |
| `admin` | Administrative (행정구역) code of resident registration, as in force in 2026 | KOSIS `DT_1B04005N` |
| `survey`, `survey4` | Statistics Korea survey code: two-digit form, and the four-digit form of the 지역별고용조사 tables (`2600` = Ulsan) | KOSIS `DT_1C96`, `DT_1DA7E34S_NEW` (two-digit); `DT_1ES3B06J`, `DT_1ES3B01J` (four-digit) |
| `moel` | Ministry of Employment and Labor region code: the survey code doubled, then `00` (`111100` = Seoul). KOSIS item IDs add the prefix `ZONE2017A` (`ZONE2017A111100`), which `regions.from_kosis` removes | KOSIS `DT_118N_MOND66` |
| `valid_to` | Last day of existence; Gwangju and Jeonnam merged into 전남광주통합특별시 on 2026-07-01 | 전남광주통합특별시 설치를 위한 특별법 (Act No. 21446) |

The codes are facts compiled from the code lists of the tables named above, retrieved on
2026-10-29 (`docs/discovery/01_source_verification.md`).

## `denominators.csv`

The denominators of the within-Korea usage index (ADR 0005) for each regional snapshot, in
persons. Written from `korea_ai_exposure.regional` (`make build`) from the KOSIS tables pinned in
`data/manifest.json`, retrieved on 2026-10-30 through the KOSIS OpenAPI (kosis.kr).

| Column | Meaning | Source |
| --- | --- | --- |
| `snapshot`, `region` | Snapshot label; ISO 3166-2:KR code | — |
| `population` | Residents aged 15-64 at the end of the snapshot month (sum of the 5-year age groups 15-19 … 60-64); excludes foreign residents | 행정안전부, 주민등록인구현황, KOSIS `DT_1B04005N` (KR-POP) |
| `workers` | Workers by workplace region in the snapshot month: employees of establishments in industries B-S (no agriculture, forestry or fishing; no self-employed); 2025 onward provisional | 고용노동부, 사업체노동력조사, KOSIS `DT_118N_MOND66` (KR-WORK-EST) |
| `employed` | Employed persons by region of residence, from the half-year paired with the snapshot (ADR 0004: 2025 second half for November 2025 and February 2026, 2026 first half for April and May 2026); published in thousands | 국가데이터처, 지역별고용조사, KOSIS `DT_1ES3B01J` (KR-WORK) |

The 17 regions sum exactly to the national 15-64 total in every month. The resident registration
statistics carry a note from the Ministry of the Interior and Safety that they are provided for
viewing and reference; ADR 0007 records the decision to commit these regional totals with
citation.

## Joining KOSIS rows

Join KOSIS rows to this table by code, with `regions.from_kosis`, which also checks the row's
label. A join by name can take Sejong's single 시군구 row for the province, since KOSIS labels
it like the province (세종특별자치시, or 세종시 in census tables). Some tables also carry
전남광주통합특별시 as an extra aggregate row, in months
before the merger as well (administrative and survey code `12`, employment-ministry code
`202000`; `regions.MERGED_CODES`). It matches no row here, so a join through this table drops it
and sums over regions do not count Gwangju and Jeonnam twice.
