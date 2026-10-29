# Phase 1 — Source verification

- Date: 2026-10-29. Scope: `docs/PLAN.md` §8, tasks 1.1–1.6. Prior art (1.7) is in
  [`02_prior_art.md`](02_prior_art.md); full checksums are in [`01a_checksums.md`](01a_checksums.md).
- Method: ten verification passes, one per source block. Six independent skeptics then re-derived
  the claims behind the Checkpoint A decisions with their own code, and a completeness critic
  checked the result against the Phase 1 task list. Their corrections are folded in below. No
  analysis code was written.
- Downloads sit in `data/raw/` (gitignored). Nothing is pinned in `data/manifest.json` yet; the
  Phase 2 fetchers will pin these files and must reproduce the checksums.
- Hugging Face pin for all AEI files: dataset `Anthropic/EconomicIndex`, commit
  `4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6` (2026-09-30).

## Summary

| Task | Source IDs | Status | Main finding |
| --- | --- | --- | --- |
| 1.1 | AEI-2025-09 | Verified | Korea AUI 3.73, rank 5 of 115, reproduces exactly; no Korean subregions |
| 1.1 | AEI-2026-01, AEI-2026-03 | Verified | Every PLAN §3 value reproduces; no AUI in these releases; the February file was replaced on 2026-05-21 |
| 1.1 | AEI-2026-06 | Verified | Every PLAN §3 value reproduces; "rank 14 of 121" holds for May only |
| 1.1 | AEI-LMI | Verified | 756 occupations, 411 zeros, maximum 0.7451; 111 SOC 2018 occupations absent |
| 1.1 | AEI-WAP2024 | Verified | Anthropic's 2024 working-age population file; the only population input that reproduces the published AUI ranks |
| 1.2 | KR-OCC | Verified | 17 regions (from 2017 1/2) × 56 KSCO-8 sub-major groups, half-yearly to 2026 1/2, one classification |
| 1.2 | KR-MDIS | Assessed | No finer 시도 × occupation detail than KOSIS; adds a workplace-region variable |
| 1.3 | KR-POP | Verified (table corrected) | Exact monthly 15–64 sums for all 17 regions |
| 1.3 | KR-WORK, KR-WORK-EST | Partly available | No 시도-level workplace table; an establishment survey covers 17 regions (employees, industries B–S) |
| 1.3 | KR-GRDP | Replaced | `DT_1C96` (2020 base), 2024 preliminary |
| 1.4 | XW-SOC1018, XW-ISCO-SOC, XW-ONET | Verified | The chain to ISCO-08 reaches all 867 SOC 2018 codes |
| 1.4 | XW-KSCO-ISCO | Verified for KSCO-8 | Official KSCO-8 ↔ ISCO-08 table (November 2025); none for KSCO-7 |
| 1.4 | XW-KSCO87 | Verified | Editions differ slightly; KOGL Type 3 (no derivatives) |
| 1.5 | US-OEWS-NAT, US-OEWS-ST | Verified | May 2025 vintage; scripted access works with `BLS_USER_AGENT` |
| 1.6 | ILO-WP140, WB-POP, ABS-ERP | Verified | ILO scores are CC BY 4.0 with a machine-readable file; no Taiwan in WDI |

## 1.1 Anthropic Economic Index

### Repository

- Six release folders (`release_2025_02_10` … `release_2026_06_26`), `labor_market_impacts`, and
  `robot_exposure` (added 2026-09-30; occupation and task scores, no geography). No release is
  newer than 2026-06-26; the June 2026 report ("Cadences") is the latest.
- Files change after release: `release_2026_03_24/data/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv`
  was replaced on 2026-05-21 (commit `db51ecb1`, "Append restored per-country/country-state
  numeric distributions (additions-only)"). The new file is the original 425,257 rows unchanged
  plus 52,460 rows of country- and region-level numeric task-trait summaries. `resolve/main` URLs
  are therefore not stable; every fetch uses the commit pin and verifies the LFS SHA-256.
- Licence: the dataset card text says data CC-BY (no version) and code MIT; its YAML metadata
  says `license: mit`. Citations: the root README carries BibTeX for every release; only
  `release_2026_06_26/data_documentation.md` carries its own.
- Product scope in the documentation: "Free and Pro" (2025-09-15, 2026-01-15), "Free, Pro, and
  Max" (2026-03-24, corrected on 2026-05-21), chat and Cowork on Free, Pro and Max (2026-06-26).
  The January 2026 appendix already describes the November data as Free, Pro and Max.

| ID | File | Bytes | Rows |
| --- | --- | --- | --- |
| AEI-2025-09 | `release_2025_09_15/data/output/aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv` | 26,840,881 | 136,845 |
| AEI-2025-09 | `release_2025_09_15/data/intermediate/aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv` | 18,894,517 | 100,062 |
| AEI-WAP2024 | `release_2025_09_15/data/intermediate/working_age_pop_2024_country.csv` | 6,321 | 194 |
| AEI-2026-01 | `release_2026_01_15/data/intermediate/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv` | 94,086,309 | 458,778 |
| AEI-2026-03 | `release_2026_03_24/data/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv` (current) | 103,287,181 | 477,717 |
| AEI-2026-06 | `release_2026_06_26/data/aei_claude_ai_2026-06-26.csv` | 219,174,671 | 1,636,573 |
| AEI-LMI | `labor_market_impacts/job_exposure.csv` | 37,176 | 756 |
| AEI-LMI | `labor_market_impacts/task_penetration.csv` | 1,889,822 | 17,998 |
| AEI-APX | `release_2026_01_15/aei_v4_appendix.pdf` | 6,036,245 | 19 pages |

Every LFS file's SHA-256 equals its `lfs.oid` in the tree API; small files are plain git blobs,
whose SHA-256 comes from the download. Full hashes: `01a_checksums.md`.

### AEI-2025-09 (4–11 August 2025)

- Geographies: global, country (ISO-2 in the raw file, ISO-3 in the enriched file), and US states
  as bare USPS codes. No subnational rows for any other country.
- Korea: 35,285 conversations; `usage_pct` 3.658 (its denominator, 964,494, includes the 150,999
  conversations that could not be geolocated); AUI 3.725, rank 5 of 115 countries with at least
  200 conversations, behind Israel, Singapore, Australia and New Zealand.
- AUI rule, re-derived exactly: usage total over every row with at least 200 conversations,
  `not_classified` included; population total over the ranked countries. This scales every AUI
  by 0.8428 relative to a geolocated-only basis, on which Korea is 4.42; ranks are unchanged.
- Facets: collaboration, O*NET tasks (O*NET 20.1, SOC 2010 codes), request clusters, SOC major
  groups. No use-case, task-trait or detailed-SOC facets, so the August snapshot contributes
  share, AUI, collaboration, SOC majors and requests only.
- Small samples clear fewer privacy thresholds: unclassified task usage is 18.6% for Korea,
  19.4% for Japan, 45.5% for Singapore and 58.7% for New Zealand.

### AEI-2026-01 (13–20 November 2025) and AEI-2026-03 (5–12 February 2026)

Both raw files have the ten documented columns, 34 facets and 166 variables, geographies
`global`, `country` (ISO-2) and `country-state` (ISO 3166-2), and no AUI or per-capita variable.

| PLAN §3 item | November 2025 | February 2026 | Result |
| --- | --- | --- | --- |
| Korea's share of global conversations | 3.06% | 2.91% | Reproduced |
| Korean conversations | 30,618 | 29,075 | Reproduced |
| Regional counts sum to the national count | Yes | Yes | Reproduced; no `KR-not_classified` row |
| Smallest regional count | 175 (Ulsan) | 174 (Jeju) | Reproduced |
| Seoul's share of Korean usage | 58.23% | 56.09% | Reproduced |
| Seoul + Gyeonggi + Incheon | 79.09% | 81.91% | Reproduced |
| Incheon | 4.82% | 10.56% | Reproduced; Incheon's count doubles (1,476 → 3,070) while the national count falls |

Other findings:

- Pseudo-geographies: `not_classified` (15.7% of conversations in November, 18.2% in February),
  `NONE` (February only, 2,340 conversations, undocumented), Seychelles (24,715 conversations in
  November, which Anthropic describes as VPN or abusive traffic; in February only as region
  rows), and Reunion (at least 200 conversations but no population, so never ranked). Shares
  use different bases: 999,875 in November (the sum of all rows) and exactly 1,000,000 in
  February (rows sum to 989,313).
- Countries at or above 200 conversations with population data: 116 in both snapshots.
- Privacy: the raw files apply only a 15-conversation cell floor. The 2026-01-15 documentation
  states floors of 200 conversations per country and 100 per region, applied at enrichment; the
  current 2026-03-24 documentation no longer states them.
- Task classification: every global task name in both files matches the O*NET 20.1 task text
  shipped with release 2025-09-15 (SOC 2010 codes). Release 2026-06-26 uses O*NET 30.2. The raw
  files have no SOC facet, so a SOC mix for these snapshots would need an in-house task map.
- Regional facets: use case, collaboration, multitasking, human-only ability, task success and
  the numeric task traits are published for all 17 regions in both snapshots. O*NET task and
  fine request facets are effectively limited to Seoul, Gyeonggi and Incheon: the task facet is
  absent for 5 regions (November) and 4 (February), and 59–94% of non-capital task usage is
  unclassified. In February the coursework cluster is folded into `not_classified` in Ulsan and
  Jeju.
- Seasonality: Korea's coursework share falls from 15.6% to 6.5%; the February window falls in
  the Korean school break.
- US benchmark: in February the US subdivisions include Guam, Puerto Rico and the Virgin
  Islands, so M8 filters to the 50 states and DC.
- Reading the ISO-2 files with pandas defaults turns Namibia (`NA`) into a missing value; use
  `keep_default_na=False`.

### AEI-2026-06 (April and May 2026)

- Ten documented columns; calendar months with exclusive `date_end`; countries in ISO-3,
  subregions in ISO 3166-2; categories `overall`, `onet`, `request`, `soc_occupation`; 53
  metrics, none of them a count; values with at most two decimals, so `0.00` means "published,
  below 0.005" and differs from a missing row.
- AUI is published for 114 countries (April) and 121 (May), and for the 50 states plus DC. Its
  basis, re-derived: usage share renormalized over the published countries, divided by the
  share of 15–64 population (2024) over the same set. This reproduces 111 of 114 and 119 of 121
  values within rounding. Published countries account for only 82.0% (April) and 87.5% (May) of
  global usage.

| PLAN §3 item | April 2026 | May 2026 | Result |
| --- | --- | --- | --- |
| Korea's share of global conversations | 3.19% | 3.24% | Reproduced |
| Korea's AUI | 3.92 | 3.78 | Reproduced |
| AUI rank | Tied with Norway, 9–10 of 114 | 14 of 121 | PLAN §3 holds for May only |
| Seoul | 63.53% | 63.65% | Reproduced |
| Seoul + Gyeonggi + Incheon | 83.34% | 82.78% | Reproduced |
| Incheon | 6.94% | 6.75% | Reproduced |
| 17 regional shares sum to 100 | 100.01 | 100.01 | Within rounding |

- All 17 regions carry all 51 subregion overall metrics in both months (use case, collaboration,
  task traits, 32 artifact labels). Breakdowns are percentage-only and sparse: only 8–9 of the
  20–22 SOC major groups are published for every region. No Korean region has a per-capita
  index; any regional index is the project's own computation.
- Method changes against earlier releases: continuous hourly sampling aggregated by month, O*NET
  30.2 with a new task classifier, a new request taxonomy, a new artifact classifier, Cowork in
  scope, `task_success` dropped, time traits in different units (hours and minutes), and no
  numeric privacy floor stated. Task-trait levels shift sharply (global AI autonomy 3.38 in
  November 2025, 2.72 in April 2026), so traits are compared within a release only. The June
  2026 report says chat data were sampled from 10 April, so April may be partial.
- Detailed SOC nodes use O*NET-SOC 2019 codes (718 globally in May). The USA has 627 nodes in
  May, 112 published as 0.00, and its percentages sum to 98.29, not 100.

### AUI across releases

The published AUI levels are not on one basis:

| Snapshot | Published Korea AUI (rank) | Published basis, re-derived | Korea on one renormalized basis |
| --- | --- | --- | --- |
| August 2025 | 3.73 (5 of 115) | Usage total includes unlocated conversations; ×0.843 | 4.42 |
| November 2025 | 3.12 (7 of 116; appendix Fig. 3) | Same rule as August; the usage total also includes Seychelles and Reunion | 3.82 |
| February 2026 | "more than 3.5" (announcement) | Consistent with bases that exclude unlocated usage; exact basis not pinned | 3.69 (12 of 116) |
| April 2026 | 3.92 (9–10 of 114) | Renormalized over published countries | 3.92 |
| May 2026 | 3.78 (14 of 121) | Renormalized over published countries | 3.78 |

Within a snapshot every basis is a uniform rescaling, so ranks do not depend on it; levels and
cross-release comparisons do. The apparent rise from 3.12 (November) to 3.92 (April) in the
published values is mostly this method change. Population: Anthropic's 2024 working-age file
(AEI-WAP2024) reproduces the published ranks and the April–May values; World Bank 2025 data
shift Korea's level by about 0.1 and change some ranks (November: Korea 6th). The current WDI
2024 column differs from Anthropic's file for 50 of 193 economies.

### Published values for Phase 2 replication

| Target (PLAN 2.4) | Primary source found | Note |
| --- | --- | --- |
| Korea AUI 3.73, rank 5 (August 2025) | September 2025 report, Fig. 2.2; enriched file | Exact |
| Korea AUI 3.12, rank 7 of 116 (November 2025) | January 2026 online appendix, Fig. 3 | Exact under the August rule (30 of 30 labels match at two decimals) |
| Korea AUI above 3.5 (February 2026) | Anthropic announcement, 2026-05-26 | Its period is inferred from "latest"; consistent with 3.61–3.69 |
| Australia 1.6%, rank 11; AUI 4.1, rank 7 (February 2026) | How Australia Uses Claude | Share and ranks match; AUI recomputes to 4.09–4.18 depending on the basis; truncation fits 4.1 |
| India 5.8%, rank 2 (November 2025) | India Country Brief | Matches with the 999,875 denominator; the brief's captions give N = 975,160 |

### AEI-LMI (observed exposure)

- `job_exposure.csv`: 756 unique SOC 2018 detailed codes, 411 zeros, maximum 0.7451 (15-1251
  Computer Programmers); no duplicates or aggregate codes. It covers 756 of the 867 SOC 2018
  detailed occupations. Of the 111 missing, 19 are military and 51 are "All Other" codes; of
  the remaining 41, 24 are components of OEWS aggregate codes and one is not published by OEWS.
  Together the gaps hold about 9.6% of OEWS detailed employment. Missing means missing, not zero.
- `task_penetration.csv`: 17,998 rows keyed by task text only.
- The research page is "Labor market impacts of AI: A new measure and early evidence"
  (Massenkoff and McCrory, 2026-03-05). Observed exposure is built from global Claude usage in
  the August and November 2025 samples, including the November snapshot this project uses, so
  it is labelled exposure, not usage, and is not independent of the usage data.

## 1.2 Regional employment by occupation

- **KR-OCC — `DT_1ES3B06J`** (orgId 101, 지역별고용조사 시도/직업별 취업자): national total and
  regions by 9 KSCO-8 major and 56 sub-major groups, half-yearly from 2013 1/2 to 2026 1/2
  (released 2026-10-27), thousand persons. The table comment states that KSIC-11 and KSCO-8 are
  applied retroactively from 2013 1/2; the KSCO-7 table `DT_1ES3B06S` ends at 2024 1/2.
- Sejong is a separate region only from 2017 1/2; from 2013 to 2016 it is inside Chungnam and
  the table has 16 regions, which its comments do not mention. Some periods omit a few region ×
  sub-major rows (2026 1/2 is complete), so a missing row means not published. Majors sum to
  regional totals within ±0.2 thousand, and regions to the national total within ±0.1.
- Reliability: no suppression. A separate item (`T001`, value `*`) flags cells with a relative
  standard error of 25% or more; no numeric RSE is published. In 2026 1/2, flagged sub-major
  cells hold 10.0% of Sejong's employment, 4.7% of Jeju's and under 3.6% elsewhere.
- No public table gives regions by minor group (a walk of all 402 tables of the survey). The
  workplace-based occupation table (`DT_1ES3C07S`) is at 시군구 level, uses 6 broad groups and
  omits Sejong.
- Monthly major groups by region: `DT_1DA7E34S_NEW` (경제활동인구조사), equal to the regional survey
  within ±0.1 thousand in April and October.
- Census: the sample census gives regions by minor group in 2010, 2015 and 2020 (KSCO-7 in 2020,
  `DT_1PD2002`) and workplace-based regions by major group (`DT_1PC2012`). The 2025 census sample
  tables are not on KOSIS yet.
- **KR-MDIS:** public-use files (free after registration) pair 시도 with 2-digit occupation codes
  (C형, which also carries the workplace 시도) and 시군구 with 1-digit codes (A형, D형); 3-digit codes
  appear only in a national file without region (B형), and 4-digit codes only under authorized
  remote or on-site access. So MDIS is no finer than KOSIS for regions by occupation; its
  additions are workplace-region × sub-major and 시군구 × major groups. The 2026 first-half C형
  file is scheduled for December 2026. Publication brings consultation and copy obligations.

## 1.3 Denominators and correlates

- **KR-POP:** `DT_1B04005N` is the 5-year age-group table (읍면동 level); the single-year table is
  `DT_1B04006`. Both are monthly to 2026.09 and give identical 15–64 sums, and the 17 regions sum
  exactly to the national total in every month from August 2025 to May 2026. End of May 2026:
  34,787,205 residents aged 15–64 (51,095,330 in total). Resident registration excludes foreign
  residents. The Ministry of the Interior's statistical description carries a note limiting the
  data to viewing and reference and excluding processing and for-profit use (ADR 0007).
- **KR-WORK:** no 시도-level workplace-based employment table exists. `DT_1ES3C01S` gives
  workplace-based employment for 228 시군구 in 16 regions, without Sejong, and only from 2021 1/2
  for the districts of the metropolitan cities. Its sums run 3.3–4.1% below the benchmarked 시도
  totals (`DT_1ES3B01J`); about 0.75 points of that is Sejong and the rest is the unbenchmarked
  시군구 basis, which the residence-based 시군구 table shares, so it is not a commuting effect.
  Within the 시군구 basis, workplace to residence employment is 1.18 for Seoul, 0.87 for Incheon
  and 0.91 for Gyeonggi (2026 1/2).
- **KR-WORK-EST:** the Ministry of Employment and Labor's establishment survey (`DT_118N_MOND66`)
  gives workers by workplace region monthly for all 17 regions: employees of establishments with
  at least one worker, industries B–S only (no agriculture, forestry or fishing), self-employed
  excluded; 2025 onward provisional. It understates the agricultural provinces.
- **KR-GRDP:** the candidate `DT_1C86` is the superseded 2015-base table; the current table is
  `DT_1C96` (2020 base), latest year 2024 (preliminary, released 2025-12-23), thousand won at
  current prices. Per-capita values use the July projected population, which includes foreign
  residents (`DT_1BPB001`).

## 1.4 Crosswalks

- **XW-SOC1018** (`soc_2010_to_2018_crosswalk.xlsx`, BLS): 900 links, 840 → 867 codes, 85% one to
  one.
- **XW-ISCO-SOC** (`ISCO_SOC_Crosswalk.xls`, BLS): 1,125 links; 436 four-digit ISCO-08 unit groups
  plus two three-digit minor groups; all 840 SOC 2010 codes covered. Every SOC 2018 code reaches
  at least one ISCO-08 group (78% exactly one). Fourteen weak matches are listed in the process
  note but not flagged in the file. BLS publications are in the public domain.
- **XW-ONET** (`2019_to_SOC_Crosswalk`, O*NET, CC BY 4.0): 1,016 O*NET-SOC 2019 codes map many to
  one onto the 867 SOC 2018 codes; truncating to 7 characters reproduces it exactly.
- **XW-KSCO-ISCO:** the KSSC portal now answers at `https://kssc.mods.go.kr:8443/ksscNew_web/`
  (port 443 presents another host's certificate). The official KSCO-8 ↔ ISCO-08 table (posted
  2025-11-03, re-posted 2026-01-27 unchanged) links 4-digit unit groups: 700 distinct pairs
  covering 494 of 495 KSCO-8 units (8631 missing) and 431 of 436 ISCO-08 units. It recommends ILO
  rules for collapsing to one-to-one links, which differs from PLAN §7's equal weights. No
  KSCO-7 ↔ ISCO-08 table is published, so the route goes to KSCO-8 directly (ADR 0004).
- **XW-KSCO87:** KSSC editions of the KSCO-8 ↔ KSCO-7 linkage at 5-digit level differ in small ways,
  contain range rows, and need a fixture-tested parser. Same-numbered 2-digit codes mean
  different groups in the two revisions (for example 25–28, 31–33, 42–44).
- Licence: the KSSC portal designates its correspondence tables and downloads KOGL Type 3
  (attribution, no derivatives). The data.go.kr file is a combined KSIC and KSCO linkage under
  KOGL Type 4 and is not needed.

## 1.5 BLS OEWS

- Latest vintage: May 2025, released 2026-05-15 (USDL-26-0725); `oesm25nat.zip` and
  `oesm25st.zip`, identical on a second download.
- Access: HTTP 403 without contact details in the User-Agent, HTTP 200 with `BLS_USER_AGENT`; no
  manual download is needed.
- National: 830 detailed occupations, all with employment, summing to 99.99% of total
  employment. 12 codes are OEWS aggregates (7 SOC broad codes used as detailed, and 5
  OEWS-specific codes) that absorb 28 SOC 2018 detailed codes. Legislators (11-1031) are not in
  May 2025. OEWS counts wage-and-salary jobs only.
- States: 50 states, DC, Guam, Puerto Rico and the Virgin Islands; suppressed or unlisted cells
  hold 0.79% of employment in the 50 states and DC (0.12% to 5.84% by state).
- Joins: `job_exposure.csv` has values for 755 of its 756 codes in OEWS and none for the 12
  aggregates, so 90.4% of OEWS detailed employment has an exposure value. AEI US detailed nodes
  reach 529 of the 830 OEWS codes in May 2026 (85% of employment).

## 1.6 Optional sources

- **ILO-WP140:** the paper and, since 2026-10-12, its companion repository are CC BY 4.0. The
  companion Excel file (3,265 tasks in 427 ISCO-08 unit groups) reproduces all 427 rows of
  Table A1, so no PDF parsing is needed. Nine unit groups are not scored.
- **WB-POP:** `SP.POP.1564.TO`, CC BY 4.0, last updated 2026-10-08, values for 217 economies
  through 2025. No Taiwan series. For replication the project uses Anthropic's 2024 file
  (AEI-WAP2024), with World Bank data as a sensitivity (§1.1, AUI across releases).
- **ABS-ERP:** dataflow `ERP_Q` (Beta API, CC BY 4.0), 15–64 by state through 2026-Q1, including
  June quarter 2025 (Australia 17,967,701).

## Cross-cutting findings

- **Region codes.** Four systems are in use, and their numbers collide: ISO 3166-2 (AEI),
  administrative codes (resident registration: 36 Sejong, 50 Jeju, 51 Gangwon, 52 Jeonbuk),
  Statistics Korea survey codes (지역별고용조사, 지역소득: 26 Ulsan, 29 Sejong, 31 Gyeonggi, 39 Jeju;
  four-digit forms such as 2600 in some tables), and the employment ministry's six-digit codes.
  Gunwi county is coded under Gyeongbuk in some tables and Daegu in others. The region table maps
  by name, and a test covers all 17 regions in every system.
- **Gwangju–Jeonnam merger.** 전남광주통합특별시 설치를 위한 특별법 (Act No. 21446, promulgated
  2026-03-05) merged Gwangju and Jeonnam into one special city from 2026-07-01. KOSIS handles it
  differently by table: resident registration replaces codes 29 and 46 with code 12 from July
  2026; the monthly labour force table adds code 12 as an extra aggregate next to Gwangju and
  Jeonnam; the establishment survey adds a parent code from January 2025. Naive sums can
  double-count. The former regions can be rebuilt from 시군구 codes. ISO 3166-2:KR still lists
  KR-29 and KR-46. All snapshots through May 2026 keep 17 regions.
- **KOSIS fetching.** The OpenAPI key goes in the query string, which the fetcher refuses to pin,
  so KOSIS needs its own fetch path that adds the key at request time and pins a redacted query.
  KOSIS revises tables in place without notice, so checksum drift is expected and reviewed.
- **Security.** During the spike one helper script printed the URL-encoded KOSIS key once to an
  agent's console. No saved file contains it (a scan of 15,691 files found none), but the key
  should be rotated.

## Open items

Low priority unless noted; none blocks Checkpoint A.

- The 2026 first-half 지역별고용조사 press release was not read; KSCO-8 statements rest on KOSIS
  metadata.
- Six other Bank of Korea AI issue notes (2025-22, 2025-30, 2025-36, 2026-12, 2026-19, 2026-27)
  were screened from summaries only.
- India's February 2026 AUI rank (98 of 116) comes from a search snippet and is not used as
  evidence.
- ILO task-level values were not compared with the May 2025 version of the companion files.
- The coverage of civil servants in the establishment survey (relevant to Sejong) is unchecked;
  check before Checkpoint B.
