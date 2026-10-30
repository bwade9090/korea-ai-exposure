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
| `survey`, `survey4` | Statistics Korea survey code, two- and four-digit forms | KOSIS `DT_1ES3B06J`, `DT_1ES3B01J`, `DT_1C96` |
| `moel` | Ministry of Employment and Labor region code | KOSIS `DT_118N_MOND66` |
| `valid_to` | Last day of existence; Gwangju and Jeonnam merged into 전남광주통합특별시 on 2026-07-01 | 전남광주통합특별시 설치를 위한 특별법 (Act No. 21446) |

The codes are facts compiled from the code lists of the tables named above, retrieved on
2026-10-29 (`docs/discovery/01_source_verification.md`).
