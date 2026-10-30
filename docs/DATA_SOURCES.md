# Data sources

Register every source here before code depends on it. Status values:

- **verified** — inspected on the date given;
- **to verify** — not yet checked;
- **assessed**, **blocked**, **replaced**, or **out of scope**, with a note.

Raw files are never committed. Downloads are pinned in `data/manifest.json`. Owner-supplied files
go to `data/manual/`. Evidence for every status below: `docs/discovery/01_source_verification.md`
(Phase 1, 2026-10-29); checksums: `docs/discovery/01a_checksums.md`. What derived data may be
committed: ADR 0007.

## Anthropic Economic Index

Hugging Face dataset `Anthropic/EconomicIndex`. Files change after release (one did on
2026-05-21), so every URL is pinned to a commit:
`https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6/`

License: the dataset card text says data CC-BY (no version) and code MIT; the card metadata says
MIT. Attribution: cite each release with the BibTeX in the dataset's root README (release
2026-06-26 also carries it in its `data_documentation.md`), and state that the project is not
affiliated with Anthropic.

| ID | Path | Period | Geography | Status |
| --- | --- | --- | --- | --- |
| AEI-2025-09 | `release_2025_09_15/data/output/aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv` (26.8 MB; a superset of the raw file, `not_classified` included); `data/intermediate/iso_country_codes.csv` (ISO-2 to ISO-3) | 4–11 Aug 2025 | Global, country, US state | Verified 2026-10-29: Korea AUI 3.725, rank 5 of 115; no Korean subregions. Pinned 2026-10-30 |
| AEI-WAP2024 | `release_2025_09_15/data/intermediate/working_age_pop_2024_country.csv`; `working_age_pop_2024_us_state.csv` | 2024 | Country (incl. Taiwan); US state | Verified 2026-10-29: the population input that reproduces the published AUI ranks and the April–May 2026 values (ADR 0006) |
| AEI-ONET20 | `release_2025_09_15/data/intermediate/onet_task_statements.csv`; `soc_structure.csv` | O*NET 20.1 | — | Verified 2026-10-29: matches every task name in the raw releases; needed only for an in-house task-to-SOC map |
| AEI-2026-01 | `release_2026_01_15/data/intermediate/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv` (94.1 MB) | 13–20 Nov 2025 | Global, country (ISO-2), country-state (ISO 3166-2) | Verified 2026-10-29: PLAN §3 values reproduce; no AUI in the release |
| AEI-2026-03 | `release_2026_03_24/data/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv` (103.3 MB, version of 2026-05-21) | 5–12 Feb 2026 | As AEI-2026-01 | Verified 2026-10-29: PLAN §3 values reproduce; the original 96.0 MB upload lacks the country- and region-level numeric task traits |
| AEI-2026-06 | `release_2026_06_26/data/aei_claude_ai_2026-06-26.csv` (219.2 MB) | Apr 2026, May 2026 (calendar months; `date_end` exclusive) | Global, country (ISO-3), subregion (ISO 3166-2) | Verified 2026-10-29: PLAN §3 values reproduce; rank 14 of 121 holds for May only |
| AEI-LMI | `labor_market_impacts/job_exposure.csv` (37 KB); `labor_market_impacts/task_penetration.csv` (1.9 MB) | — | — | Verified 2026-10-29: 756 SOC 2018 occupations (111 of 867 absent); 17,998 tasks keyed by text |
| AEI-APX | `release_2026_01_15/aei_v4_appendix.pdf` (6.0 MB) | Nov 2025 | — | Verified: source of Korea's November 2025 AUI (3.12, rank 7 of 116, Fig. 3) |
| AEI-ROBOT | `robot_exposure/` (added 2026-09-30) | — | No geography | Out of scope (proposed; backlog at most) |

Schema notes:

- Raw files (AEI-2025-09 raw, AEI-2026-01, AEI-2026-03) have columns `geo_id, geography,
  date_start, date_end, platform_and_product, facet, level, variable, cluster_name, value`, with
  two-letter country codes. Read them with `keep_default_na=False`: Namibia's code is `NA`.
- The raw files apply only a 15-conversation cell floor. The pipeline applies the documented
  floors of 200 conversations per country and 100 per region (ADR 0006).
- The AEI-2025-09 enriched file adds every country that has a population but no published usage,
  with zero usage values (28 countries; `merge_population_data` in the release's preprocessing
  notebook). Those zeros mean "not published", so the adapter drops their 140 usage rows (count,
  share, per capita, per-capita index, tier) and keeps their population and GDP rows. August
  2025 then has the 173 country rows of the raw file (172 countries and `not_classified`).
- Pseudo-geographies: `not_classified` (unlocated conversations), `NONE` (February 2026),
  Seychelles (described by Anthropic as VPN or abusive traffic), and countries without
  population (Reunion). They are excluded from rankings (ADR 0006).
- The raw releases classify tasks with O*NET 20.1 (SOC 2010 codes) and have no SOC facet;
  release 2026-06-26 uses O*NET 30.2 and SOC 2018.
- AEI-2026-06 has columns `date_start, date_end, geo_id, geo_level, category_name,
  hierarchy_level, metric_id, value, node_name, node_external_id`, with categories `overall`,
  `onet`, `request`, `soc_occupation`; no counts; values to two decimals, so `0.00` is published
  and differs from a missing row. Detailed SOC nodes use O*NET-SOC 2019 codes (for example
  `15-1299.03`); SOC major groups use two-digit IDs. Always filter on `metric_id`, and join O*NET
  tasks on `node_external_id` (task statements are not unique).
- AEI-2026-06 units (its `data_documentation.md`): `ai_autonomy_mean` on a 1–5 scale, education
  in years, `human_only_time_mean` in hours, `human_with_ai_time_mean` in minutes, `*_pct` in
  percent. Request levels are 0 detailed, 1 minor, 2 major. The weekly releases document no
  units, and their trait levels differ (ADR 0006).
- Korean regions appear as KR-11 … KR-50 in ISO 3166-2, including KR-42 Gangwon, KR-45 Jeonbuk,
  KR-49 Jeju, and KR-50 Sejong.
- `job_exposure.csv` uses SOC 2018 codes: 2018-only codes such as `15-1252` and `15-2051` are
  present.

## Korean official statistics

Data come from KOSIS. The producer is 국가데이터처 (formerly Statistics Korea) unless noted. Access:
KOSIS OpenAPI with a free key (`KOSIS_KEY` in `.env`), which the fetcher adds at request time;
pins record the URL without it (`key_env`). Terms: the KOSIS use guide allows free use, reuse and redistribution with citation
(producer, survey, period, access date, table, URL); no table-level KOGL mark is shown. KOSIS
revises tables in place, so pinned checksums can drift. Region codes differ by table; map regions
by name. Gwangju and Jeonnam merged into 전남광주통합특별시 on 2026-07-01 (Act No. 21446); tables
handle it differently (notes below), and naive sums can double-count.

| ID | Content | Table | Status |
| --- | --- | --- | --- |
| KR-POP | Resident registration population by region and age, monthly, month end (행정안전부); excludes foreign residents | `DT_1B04005N` (5-year groups, 읍면동); `DT_1B04006` (single years, 시군구) | Verified 2026-10-29: exact 15–64 sums for 17 regions, 2025.08–2026.05; latest 2026.09. From 2026.07 code 12 replaces 29 and 46. The statistical description notes the data are for viewing and reference, without processing or for-profit use (ADR 0007). Pinned 2026-10-30: 15–64 classes, 2025.11–2026.05 |
| KR-OCC | 지역별고용조사, employed persons by 시도 × occupation (KSCO-8: 9 major, 56 sub-major groups), half-yearly | `DT_1ES3B06J` (2013 1/2–2026 1/2, back-cast to KSCO-8; 17 regions from 2017 1/2); legacy KSCO-7 `DT_1ES3B06S` ends 2024 1/2 | Verified 2026-10-29; recommended tier T1 (ADR 0004). Reliability flags are a separate `*` item. Pinned 2026-10-30 |
| KR-OCC-NAT | 지역별고용조사, national employment by KSCO-8 minor group (소분류) | `DT_1ES3B32J` | Verified 2026-10-29; weights for aggregating to sub-major groups. Pinned 2026-10-30 |
| KR-OCC-EAPS | 경제활동인구조사, employed persons by 시도 × KSCO-8 major group, monthly | `DT_1DA7E34S_NEW` | Verified 2026-10-29; exact-month sensitivity. Code 12 is an extra aggregate next to Gwangju and Jeonnam |
| KR-OCC-WORK | 지역별고용조사, workplace-based employment by 시군구 × 6 broad occupation groups | `DT_1ES3C07S` | Verified 2026-10-29: no Sejong, no 시도 level; not used |
| KR-WORK | 지역별고용조사: workplace-based employment (시군구 only, 16 regions, no Sejong) and residence-based employment by 시도 | `DT_1ES3C01S` (workplace); `DT_1ES3B01J` (residence, 17 regions, benchmarked); `DT_1ES3A01S` (residence by 시군구, for the commuting check of ADR 0005) | Partly available 2026-10-29: no 시도-level workplace table; 시군구 sums are not benchmarked. Pinned 2026-10-30: `DT_1ES3B01J`, `DT_1ES3C01S`, `DT_1ES3A01S`, 2025 2/2–2026 1/2 |
| KR-WORK-EST | 사업체노동력조사 (Ministry of Employment and Labor), workers by workplace 시도, monthly; employees of industries B–S (no agriculture, forestry or fishing) | `DT_118N_MOND66` (orgId 118) | Verified 2026-10-29: 17 regions, 2024.01–2026.08; 2025 onward provisional; coverage of civil servants not yet checked. Pinned 2026-10-30: all industries, 2025.11–2026.05 |
| KR-PROJ | 장래인구추계, population by 시도 on 1 July, including foreign residents | `DT_1BPB001` | Verified 2026-10-29: the population behind GRDP per capita; optional sensitivity |
| KR-GRDP | 지역소득, GRDP per capita by 시도, thousand won at current prices | `DT_1C96` (2020 base) | Replaced 2026-10-29: candidate `DT_1C86` is the superseded 2015-base table; latest year 2024 (preliminary). Pinned 2026-10-30: 2024 |
| KR-CENSUS2020-OCC | 2020 인구주택총조사 (20% sample): 시도 × KSCO-7 minor group; workplace-based 시도 × major group | `DT_1PD2002`; `DT_1PC2012` | Verified 2026-10-29; robustness only. The 2025 census sample tables are not yet released |
| KR-MDIS | 지역별고용조사 microdata (MDIS) | Owner download; never committed | Assessed 2026-10-29: no finer 시도 × occupation detail than KR-OCC; adds a workplace-region variable; optional owner-run sensitivity (ADR 0004) |

## Classifications and crosswalks

BLS publications are in the public domain; cite BLS as the source.

| ID | Content | Source | Status |
| --- | --- | --- | --- |
| XW-SOC1018 | SOC 2010 ↔ SOC 2018 | BLS `https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx` (linked from `crosswalks_used_by_agencies.htm`) | Verified 2026-10-29: 900 links; needs `BLS_USER_AGENT`. Pinned 2026-10-30 |
| XW-ISCO-SOC | ISCO-08 ↔ SOC 2010 | BLS `https://www.bls.gov/soc/ISCO_SOC_Crosswalk.xls`; process note `ISCO_SOC_Crosswalk_process.pdf` | Verified 2026-10-29: 1,125 links; two links to 3-digit ISCO groups; 14 weak matches listed only in the note. Pinned 2026-10-30 |
| XW-ONET | O*NET-SOC 2019 → SOC 2018 | O*NET Resource Center `https://www.onetcenter.org/taxonomy/2019/soc/2019_to_SOC_Crosswalk.csv?fmt=csv` (CC BY 4.0) | Verified 2026-10-29: 1,016 → 867 codes; files generated per request |
| XW-KSCO-ISCO | KSCO-8 ↔ ISCO-08 (4-digit unit groups) | 통계분류포털 `https://kssc.mods.go.kr:8443/ksscNew_web/` (KOGL Type 3) | Verified 2026-10-29 for KSCO-8 (November 2025 table); no KSCO-7 table published. Pinned 2026-10-30 |
| XW-KSCO87 | KSCO-8 ↔ KSCO-7 (5-digit) | 통계분류포털 (KOGL Type 3) | Verified 2026-10-29: editions with small differences and range rows; needed only if KSCO-7 data are used |
| CL-KSCO8 | KSCO-8 code lists (10/57/167/495/1,270), Korean and English names | 통계분류포털 (linkage files, English tree, 해설서 PDF) | Verified 2026-10-29 |
| CL-KSCO7 | KSCO-7 code lists (10/52/156/450/1,231) | 통계분류포털 | Verified 2026-10-29 |

## US benchmark

| ID | Content | Source | Status |
| --- | --- | --- | --- |
| US-OEWS-NAT | OEWS national employment by SOC, May 2025 | BLS `https://www.bls.gov/oes/special-requests/oesm25nat.zip` (public domain) | Verified 2026-10-29: 830 detailed occupations; scripted access with `BLS_USER_AGENT`. Pinned 2026-10-30 |
| US-OEWS-ST | OEWS state employment by SOC, May 2025 | BLS `https://www.bls.gov/oes/special-requests/oesm25st.zip` | Verified 2026-10-29: 50 states, DC and 3 territories; 0.79% of employment unpublished. Pinned 2026-10-30 |
| US-SOC2018 | 2018 SOC structure | BLS `https://www.bls.gov/soc/2018/soc_structure_2018.xlsx` | Verified 2026-10-29: needed to read broad parents (not derivable from codes). Pinned 2026-10-30 |
| US-OEWS-OCCDEF | OEWS occupation list with definitions (documents the 12 OEWS aggregate codes) | BLS `occupation_definitions_m2021.xlsx` | Verified 2026-10-29 |

## Optional

| ID | Content | Source | Status |
| --- | --- | --- | --- |
| ILO-WP140 | ISCO-08 4-digit exposure means and SDs; task-level scores | Gmyrek et al. (2025), ILO Working Paper 140 (CC BY 4.0); companion repository `pgmyrek/2025_GenAI_scores_ISCO08`, commit `ce5fc25c2a0db2757c5bfa797c4cfc8b408431ea` (CC BY 4.0 since 2026-10-12) | Verified 2026-10-29: the companion Excel file reproduces Table A1; 427 of 436 unit groups scored. Pinned 2026-10-30 |
| WB-POP | Population ages 15–64 by country (`SP.POP.1564.TO`) | World Bank WDI (CC BY 4.0) | Verified 2026-10-29: through 2025, 217 economies; no Taiwan; sensitivity for AUI (ADR 0006) |
| ABS-ERP | Population by state and age (dataflow `ERP_Q`) | Australian Bureau of Statistics Data API, Beta (CC BY 4.0) | Verified 2026-10-29: through 2026-Q1; Australia replication only |

## Prior art (not data)

Details and summaries: `docs/discovery/02_prior_art.md`.

| ID | Item | Status |
| --- | --- | --- |
| BOK-2026-09 | 김보성·정민수·정유정·장수빈 (2026), 「AI와 지역 노동시장 - 지역간 격차 확대 위험과 새로운 기회」, BOK 이슈노트 제2026-25호, 한국은행 조사국 지역경제조사팀, 2026-09-15 (All rights reserved) | Verified 2026-10-29 |
| BOK-2025-02 | 오삼일·이수민·이하민·장수정·Zexi Sun·Xin Cindy Xu (2025), 「AI와 한국경제」, BOK 이슈노트 제2025-2호, 2025-02-10 | Verified 2026-10-29 |
| ANT-AEI3 | Appel et al., Anthropic Economic Index report: Uneven geographic and enterprise AI adoption, 2025-09-15 | Verified 2026-10-29 |
| ANT-AEI4 | Anthropic Economic Index report: Economic primitives, 2026-01-15, with online appendix (AEI-APX) | Verified 2026-10-29 |
| ANT-AEI5 | Anthropic Economic Index report: Learning curves, 2026-03-24 | Verified 2026-10-29 |
| ANT-AEI6 | Anthropic Economic Index report: Cadences, 2026-06-26 | Verified 2026-10-29 |
| ANT-IN | Appel, India Country Brief: The Anthropic Economic Index, 2026-02-16 | Verified |
| ANT-AU | McCrory, How Australia Uses Claude: Findings from the Anthropic Economic Index, 2026-03-31 (`/research/how-australia-uses-claude`) | Verified |
| ANT-CA | McCrory, How Canada Uses Claude, 2026-07-14 (`/research/how-canada-uses-claude`) | Verified 2026-10-29 |
| ANT-LMI | Massenkoff and McCrory, Labor market impacts of AI: A new measure and early evidence, 2026-03-05 | Verified 2026-10-29 |
| ANT-KR | Anthropic news on Korea: Seoul office announcement (2025-10-23), Korea representative director (2026-05-26), Seoul office opening (2026-06-17) | Verified 2026-10-29 |
| KIEP-2026-01 | 송하윤·이병준, 「주요국의 AI 사용 실태와 한국의 현황」, KIEP 세계경제 포커스 9(4), 2026-01-29 (KOGL Type 4) | Verified 2026-10-29 |
| ATLAS-KR | Arce, Claude Adoption Atlas (GitHub Pages), Korean regional shares and mixes since 2026-09-13 | Verified 2026-10-29 |
| NAVARRO-2026 | Navarro, More service jobs, less technical AI use: a subnational look, August 2026 (no Korean regions) | Verified 2026-10-29 |
| MURUGAN-2026 | Murugan, Aguirre, Nagaraj and Bommasani, arXiv:2607.05404, June 2026 (national exposure against adoption) | Seen 2026-10-29; to read before Phase 5 |
| PAULLAB-2026 | 이호준 (paullabkorea), Anthropic Economic Index 분석 리포트, March 2026 | Verified 2026-10-29 |
| KISDI-2025 | 이으뜸·문아람, 지역별 AI 준비도, KISDI Premium Report 25-12, December 2025 | To verify (seen through citations) |
| MSIT-NIA-2026 | 과학기술정보통신부·한국지능정보사회진흥원, 2025 인터넷이용실태조사, 2026-03-31 (generative-AI experience by 시도) | To verify (press reports only); a candidate check for Checkpoint B |
| ELOUNDOU-2024 | Eloundou, Manning, Mishkin and Rock (2024), GPTs are GPTs, Science 384(6702): 1306–1308 | Verified 2026-10-29 |
