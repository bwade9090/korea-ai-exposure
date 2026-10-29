# Data sources

Register every source here before code depends on it. Status values:

- **verified** — inspected on the date given;
- **to verify** — Phase 1;
- **blocked** or **replaced**, with a note.

Raw files are never committed. Downloads are pinned in `data/manifest.json`. Owner-supplied files
go to `data/manual/`.

## Anthropic Economic Index

Hugging Face dataset `Anthropic/EconomicIndex`. Base URL:
`https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/`

License: data CC-BY, code MIT (dataset card). Attribution: cite the release, using the BibTeX in
each release's `data_documentation.md`, and state that the project is not affiliated with
Anthropic.

| ID | Path | Period | Geography | Status |
| --- | --- | --- | --- | --- |
| AEI-2025-09 | `release_2025_09_15/` | 4–11 Aug 2025 | Global, country, US state; enriched file includes AUI | To verify: schema; Korea AUI 3.73 |
| AEI-2026-01 | `release_2026_01_15/data/intermediate/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv` (94.1 MB) | 13–20 Nov 2025 | Global, country (ISO-2), country-state (ISO 3166-2) | Verified 2026-10-29: 17 Korean regions with `usage_count`, `usage_pct`, and facets |
| AEI-2026-03 | `release_2026_03_24/data/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv` (103.3 MB) | 5–12 Feb 2026 | As AEI-2026-01 | Verified 2026-10-29 |
| AEI-2026-06 | `release_2026_06_26/data/aei_claude_ai_2026-06-26.csv` (219.2 MB) | Apr 2026, May 2026 (calendar months; `date_end` exclusive) | Global, country (ISO-3), subregion (ISO 3166-2) | Verified 2026-10-29: 17 Korean regions; no counts; values rounded to two decimals; AUI for countries and US states only |
| AEI-LMI | `labor_market_impacts/job_exposure.csv` (37 KB); `labor_market_impacts/task_penetration.csv` (1.9 MB) | — | — | Verified 2026-10-29: `occ_code,title,observed_exposure` (756 SOC 2018 occupations); `task,penetration` (17,998 tasks) |
| AEI-APX | `release_2026_01_15/aei_v4_appendix.pdf` (6.0 MB) | — | — | Methodology reference |

Schema notes:

- Raw files (AEI-2026-01, AEI-2026-03) have columns `geo_id, geography, date_start, date_end,
  platform_and_product, facet, level, variable, cluster_name, value`, with `geography` in
  {global, country, country-state} and two-letter country codes. The 2026-01-15 documentation
  states a floor of 200 conversations per country and 100 per region, applied at enrichment
  rather than in the raw files; apply the same floors in this pipeline.
- AEI-2026-06 has columns `date_start, date_end, geo_id, geo_level, category_name,
  hierarchy_level, metric_id, value, node_name, node_external_id`, with categories `overall`,
  `onet`, `request`, `soc_occupation`.
  - Country and subregion rows carry `pct` for the breakdown categories.
  - At country level, SOC major groups, request majors, and O*NET GWAs carry all metrics.
  - Detailed SOC nodes use O*NET-SOC 2019 codes (for example `15-1299.03`). Always filter on
    `metric_id`.
- Korean regions appear as KR-11 … KR-50 in ISO 3166-2, including KR-42 Gangwon, KR-45 Jeonbuk,
  KR-49 Jeju, and KR-50 Sejong.
- `job_exposure.csv` uses SOC 2018 codes: 2018-only codes such as `15-1252` and `15-2051` are
  present.

## Korean official statistics

Data come from KOSIS. The producer is 국가데이터처 (formerly Statistics Korea) unless noted.

Access: KOSIS OpenAPI (`KOSIS_API_KEY` in `.env`) or manual table download into `data/manual/`.
License: check each table's KOGL (공공누리) notice and record it here.

| ID | Content | Candidate table | Status |
| --- | --- | --- | --- |
| KR-POP | Resident registration population by region and single year of age, monthly (Ministry of the Interior and Safety) | `DT_1B04005N` (candidate) | To verify |
| KR-OCC | Employed persons by region × occupation at the finest public level (지역별고용조사, semiannual) | To find | To verify; decides tier T1 |
| KR-WORK | Employed persons by place of work, by region (지역별고용조사) | To find | To verify |
| KR-GRDP | GRDP per capita by region (지역소득), latest year | `DT_1C86` (candidate) | To verify |
| KR-MDIS | 지역별고용조사 microdata (MDIS); tier T2 only | Owner download; never committed | To verify terms and occupation detail |

## Classifications and crosswalks

| ID | Content | Source | Status |
| --- | --- | --- | --- |
| XW-SOC1018 | SOC 2010 ↔ SOC 2018 | BLS, 2018 SOC pages | To verify file name |
| XW-ISCO-SOC | ISCO-08 ↔ SOC 2010 | BLS `https://www.bls.gov/soc/ISCO_SOC_Crosswalk.xls`; process note `https://www.bls.gov/soc/ISCO_SOC_Crosswalk_process.pdf` | Listed on the BLS crosswalk page (2026-10-29); file to verify |
| XW-KSCO-ISCO | KSCO ↔ ISCO-08 correspondence | 통계분류포털 (KSSC) | To verify, for KSCO-7 and KSCO-8 |
| XW-KSCO87 | KSCO-8 ↔ KSCO-7 | 통계분류포털 (KSSC) | To verify. KSCO-8 was announced 2024-07-01 and took effect 2025-01-01 |
| XW-ONET | O*NET-SOC 2019 → SOC 2018 | O*NET Resource Center (CC BY 4.0) | To verify |

## US benchmark

| ID | Content | Source | Status |
| --- | --- | --- | --- |
| US-OEWS-NAT | OEWS national employment by SOC, latest May reference year | BLS (public domain) | To verify; scripted access needs `BLS_USER_AGENT` |
| US-OEWS-ST | OEWS state employment by SOC | BLS (public domain) | To verify |

## Optional

| ID | Content | Source | Status |
| --- | --- | --- | --- |
| ILO-WP140 | ISCO-08 4-digit exposure means and SDs (Appendix Table A1); task-level scores | Gmyrek et al. (2025), ILO Working Paper 140; `https://pgmyrek.github.io/2025_GenAI_scores_ISCO08/` | To verify format. No license stated, so no redistribution until checked |
| WB-POP | Population ages 15–64 by country (`SP.POP.1564.TO`) | World Bank WDI (CC BY 4.0) | To verify |
| ABS-ERP | Population by state and age, June quarter 2025 | Australian Bureau of Statistics | To verify; Australia replication only |

## Prior art (not data)

| ID | Item | Status |
| --- | --- | --- |
| BOK-2026-09 | 한국은행 조사국, BOK 이슈노트 「AI와 지역 노동시장: 지역간 격차 확대 위험과 새로운 기회」, released 2026-09-15 (press reports attribute it to 지역경제조사팀) | Record number, authors, and method in Phase 1.7 |
| BOK-2025-02 | 한국은행, BOK 이슈노트 제2025-2호 「AI와 한국경제」 (February 2025) | To verify |
| ANT-IN | India Country Brief: The Anthropic Economic Index (Appel, 2026-02-16) | Verified |
| ANT-AU | How Australia Uses Claude (McCrory, 2026-03-31) | Verified |
| ANT-LMI | Labor market impacts and observed exposure (Massenkoff and McCrory, 2026-03-05) | Page verified; title to confirm |
