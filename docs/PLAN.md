# Project plan

- Project: korea-ai-exposure
- Owner: Hyungbae Cho
- Status: proposed, 2026-10-29. Approval is recorded in `docs/PROJECT_STATUS.md`.

## 1. Objective

Build a reproducible research brief on AI usage and AI exposure across Korea's 17 regions from
public data only. The format follows the Anthropic Economic Index country briefs (India, February
2026; Australia, March 2026). It adds a regional decomposition those briefs do not have: how much
of Korea's regional usage pattern occupational structure accounts for.

Target: about 2,000–2,500 words and 6–9 figures, plus a methodology note.

## 2. Research questions

- **RQ1 — National profile.** How does Korea's Claude.ai usage compare with peer economies in
  intensity, use-case mix, task and occupation mix, collaboration mode, and task traits? How stable
  is that profile across the five public snapshots from August 2025 to May 2026?
- **RQ2 — Regional distribution.** How is Korean usage distributed across the 17 regions relative
  to working-age population and to workplace-based employment? How stable is the distribution
  across the four snapshots with regional data?
- **RQ3 — Composition versus adoption.** How much of the regional variation in work-related usage
  does occupational composition account for, and which regions deviate most? The same
  decomposition on US states, where Anthropic publishes state usage indices, is the benchmark.
- **RQ4 — Usage versus exposure.** Where do usage rankings diverge from exposure rankings: this
  project's occupation-weighted exposure and the Bank of Korea's September 2026 regional rankings?

### Pre-specified expectations

Recorded before analysis. Report the results whichever way they go.

- **E1.** Usage is more concentrated in Seoul than occupational composition predicts
  (agglomeration, plus commuting and IP-geolocation effects).
- **E2.** Across regions, usage per capita is weakly related to GRDP per capita.
  Manufacturing-heavy, high-GRDP regions such as Ulsan and Chungnam use less. The Australia brief
  reports this pattern across states.
- **E3.** Sejong's usage falls short of its exposure-implied level, consistent with public-sector
  adoption constraints. Exploratory: Sejong is small and its measurement is fragile.

## 3. Starting facts (verified 2026-10-29)

These are raw values read directly from the AEI files. The pipeline must reproduce them in
Phase 2 before any analysis uses them. Snapshot order: 13–20 Nov 2025; 5–12 Feb 2026; Apr 2026;
May 2026.

| Item | Value |
| --- | --- |
| Korean regions with published usage | All 17 (KR-11 … KR-50) in releases 2026-01-15, 2026-03-24, 2026-06-26 |
| Korea's share of global Claude.ai conversations | 3.06%; 2.91%; 3.19%; 3.24% |
| Korea's AUI | 3.92 (Apr 2026); 3.78 (May 2026), rank 14 of 121 countries with a published index |
| Korean conversations in the sample | 30,618; 29,075 (counts are not published in release 2026-06-26) |
| Regional allocation | Regional counts sum exactly to the national count in both raw releases |
| Smallest regional counts | 175 (Ulsan, Nov 2025); 174 (Jeju, Feb 2026) |
| Seoul's share of Korean usage | 58.23%; 56.09%; 63.53%; 63.65% |
| Seoul + Gyeonggi + Incheon | 79.09%; 81.91%; 83.34%; 82.78% |
| Incheon's share (instability flag) | 4.82%; 10.56%; 6.94%; 6.75% |
| Anthropic `observed_exposure` | 756 SOC 2018 occupations; 411 equal zero; maximum 0.745 |

The capital region holds about half of Korea's population, so usage is far more concentrated than
population. How much of that concentration is real, and how much reflects commuting and IP
geolocation, is the first question Phase 4 must answer.

## 4. Scope

In scope:

- National profile of Korea in the AEI, against peer sets.
- Regional usage across the 17 regions: level, stability, correlates.
- Decomposition of regional work usage into occupational composition and a residual, benchmarked
  on US states.
- Comparison of usage with exposure rankings.

Out of scope:

- Youth employment in AI-exposed occupations. The Bank of Korea's September 2026 issue note covers
  it; repeating it adds little.
- Restricted microdata and any linkage to administrative records.
- Causal estimates.
- 1P API traffic (no geographic breakdown) and Claude Code traffic (not in these releases).
- Forecasts and scenarios.

## 5. Data

Full registry with URLs, licenses, and status: `docs/DATA_SOURCES.md`.

| Block | Sources | Used for |
| --- | --- | --- |
| AEI usage | Releases 2025-09-15, 2026-01-15, 2026-03-24, 2026-06-26 | RQ1–RQ4 |
| Occupation measures | AEI `labor_market_impacts/job_exposure.csv`; AEI SOC-occupation usage shares | M5 |
| Korean statistics | 15–64 population by region and month; employment by region × occupation; workplace-based employment; GRDP per capita (KOSIS) | M3, M6, M7 |
| Crosswalks | BLS SOC 2010↔2018 and ISCO-08↔SOC 2010; KSCO↔ISCO-08; KSCO-8↔KSCO-7; O*NET-SOC 2019→SOC 2018 | M5–M7 |
| US benchmark | BLS OEWS national and state | M5, M8 |
| Optional | ILO (2025) ISCO-08 exposure scores; World Bank 15–64 population; ABS population by state and age | Robustness, replication |

Regional occupation data come in two tiers. Checkpoint A picks one.

- **T1 — public tables.** The finest occupation level KOSIS publishes by region: at least KSCO
  major groups, possibly sub-major groups. Fully reproducible from a clean clone.
- **T2 — MDIS microdata.** 지역별고용조사 microdata the owner downloads into `data/manual/`.
  Finer occupations. Only aggregates leave the owner's machine, under a minimum-cell rule.

## 6. Measures

Notation: r = region, c = country, o = SOC occupation, k = KSCO group, t = snapshot.

- **M1 — Country share and AUI.** `s_ct` is country c's share of global conversations;
  `AUI_ct = s_ct / (c's share of working-age population)`. Use published values where they exist
  (releases 2025-09-15 and 2026-06-26). For the raw 2026-01-15 and 2026-03-24 files, recompute with
  World Bank 15–64 population and the 200-conversation country floor, then validate against
  reported values.
- **M2 — Regional usage share.** `u_rt` is the published `usage_pct` for Korean subregions; it sums
  to 100 within Korea.
- **M3 — Within-Korea usage index.** `I_rt = u_rt / p_rt`, where `p_rt` is region r's share of
  Korea's 15–64 resident population in the snapshot month. 1.0 means parity, as in the Australia
  brief. Alternative denominators: share of workplace-based employment (addresses commuting);
  share of total employment.
- **M4 — Work-usage share.** `w_rt = u_rt × work_rt / Σ_s (u_st × work_st)`, where `work_rt` is the
  region's work use-case share.
- **M5 — Occupation intensity.** Two variants. Both assume that workers generate conversations
  about their own occupation's tasks; state the assumption wherever M5 is used.
  - (a) Usage per worker: `v_o` = US usage share of SOC o (AEI, country USA) ÷ US employment share
    of o (OEWS national). Global usage shares are a sensitivity.
  - (b) Anthropic observed exposure `x_o` (`job_exposure.csv`). It is zero for 411 of 756
    occupations, so it concentrates on a minority of occupations.
- **M6 — Regional exposure.** `X_r = Σ_k s_rk × x_k`: the employment-weighted mean exposure of
  region r's workers, where `s_rk` is the employment share of KSCO group k in region r.
- **M7 — Predicted work usage and residual.** `ŵ_r = Σ_k E_rk v_k / Σ_s Σ_k E_sk v_k`; residual
  `R_r = w_r / ŵ_r`. Report the share of cross-regional variance in `log w_r` accounted for by
  `log ŵ_r` (R² and Spearman ρ, N = 17).
- **M8 — US benchmark.** M7 for the 50 states and DC, using OEWS state employment by SOC (no
  crosswalk needed), against AEI state usage and published state AUIs.
- **M9 — National profile metrics, Korea against peers.**
  - Use-case mix.
  - Collaboration: automation and augmentation buckets, and the five patterns.
  - Task traits: `ai_autonomy_mean`, `human_education_years_mean`, `ai_education_years_mean`,
    `human_only_time_mean`, `human_with_ai_time_mean`, `human_only_ability_pct`,
    `multitasking_pct`.
  - Task concentration: share of usage in the top 100 O*NET tasks.
  - SOC major-group mix against global, in percentage points.
  - Over- and under-represented request clusters against global.
  - Artifact mix (release 2026-06-26 only).

Known measurement issues, handled explicitly:

- Task concentration depends mechanically on how many tasks clear the privacy threshold, and that
  number grows with sample size. Compare Korea with countries of similar conversation counts.
- Regional facet breakdowns (tasks, requests, occupations) are sparse for small regions. Use them
  only where all 17 regions are published, or report coverage.
- Binomial intervals from conversation counts understate uncertainty, because conversations
  cluster by user. Say so wherever intervals appear.

## 7. Crosswalk design (SOC 2018 → KSCO)

Chain: SOC 2018 detailed → SOC 2010 detailed (BLS) → ISCO-08 unit group (BLS) → KSCO-7 unit group
(국가데이터처, formerly Statistics Korea) → KSCO-8 where the regional data use it → the KSCO level
at which regional employment is published.

AEI SOC-occupation nodes carry O*NET-SOC 2019 codes (e.g., `15-1299.03`). Aggregate them to
6-digit SOC 2018 first.

Weights:

- SOC → ISCO: split each SOC occupation's US employment equally across its ISCO matches. An ISCO
  group's value is the employment-weighted mean over the SOC employment allocated to it.
- ISCO → KSCO: equal-weight mean over ISCO matches, since no Korean employment exists at ISCO
  level. The sensitivity uses the minimum and the maximum.
- Fine KSCO → coarse KSCO: Korean national employment weights at the finest level available;
  equal weights as the fallback.

Invariants, unit-tested:

- Allocation weights from each source code sum to 1.
- Coverage is reported as the share of US employment mapped and the share of Korean employment
  with an assigned value.
- Unmapped codes are listed in an audit table.

Robustness rule, fixed in advance: report the Spearman ρ between regional rankings under
alternative weightings. A ranking with ρ < 0.9 across reasonable alternatives is reported as not
robust.

## 8. Work plan

Every phase ends with a green `make check`, an updated `docs/PROJECT_STATUS.md`, and pushed
commits. Time estimates assume Claude Code does the engineering and the owner reviews.

### Phase 0 — Bootstrap (≈1–2 h)

- 0.1 GitHub remote. If `origin` is missing, confirm with the owner, then run
  `gh repo create korea-ai-exposure --private --source=. --remote=origin --push`. Never make the
  repository public.
- 0.2 Tooling: Python 3.12 venv; `requirements.in` → `requirements.txt`; `pyproject.toml` with the
  ruff and pytest settings in CLAUDE.md; package skeleton; `tests/`; `Makefile`; `.env.example`
  with `KOSIS_API_KEY` and `BLS_USER_AGENT`; GitHub Actions running ruff and offline pytest.
- 0.3 Fetch helper and `data/manifest.json`: download → SHA-256 → manifest entry. Idempotent;
  refuses checksum drift unless explicitly told to update.

Acceptance: `make setup && make check` passes locally and in CI; `make fetch` with no registered
sources is a no-op.

### Phase 1 — Source verification spike (≈2–4 h, no analysis code)

- 1.1 AEI: confirm the four release schemas, the Korean rows in each, and the subregion facets.
  Record row counts and checksums.
- 1.2 Regional employment by occupation: find the finest occupation level KOSIS publishes by region
  (지역별고용조사; census sample tables as a fallback). Record table IDs, periods, and KSCO
  version. Assess the MDIS option (occupation detail, terms of use) without downloading anything.
- 1.3 Monthly 15–64 population by region; workplace-based employment by region; GRDP per capita
  by region for the latest year.
- 1.4 Crosswalk files: BLS SOC 2010↔2018 and ISCO-08↔SOC 2010; KSCO↔ISCO-08; KSCO-8↔KSCO-7;
  O*NET-SOC 2019→SOC 2018.
- 1.5 BLS OEWS national and state files for the latest May reference year. Test scripted access
  with `BLS_USER_AGENT`.
- 1.6 Optional sources: ILO WP140 Table A1 (format and license); World Bank `SP.POP.1564.TO`; ABS
  population by state and age.
- 1.7 Prior art: record the full citation of the Bank of Korea issue note of 15 September 2026.
  Summarize its exposure method and regional results in `docs/discovery/02_prior_art.md`. Check
  for any published analysis of the Korean regional AEI data.

Deliverables: `docs/discovery/01_source_verification.md`; `docs/DATA_SOURCES.md` entries updated to
verified, blocked, or replaced.

**Checkpoint A (owner):** choose the regional occupation tier (T1 or T2); confirm denominators;
approve peer sets (ADR); approve Phase 2.

### Phase 2 — AEI ingestion and replication (≈3–5 h)

- 2.1 Fetchers for the four releases and `labor_market_impacts`, checksummed.
- 2.2 Schema adapters to one canonical long table (Parquet) with columns `release`,
  `period_start`, `period_end` (exclusive), `geo_level` ∈ {global, country, subregion}, `geo_id`
  (ISO-3 for countries, ISO 3166-2 for regions), `facet`, `hierarchy_level`, `node_id`,
  `node_name`, `metric`, `value`. Map raw two-letter country codes to ISO-3. Map `country-state`
  and `state_us` to `subregion`.
- 2.3 Korean region dimension table: ISO code, Korean name, English name, KOSIS code or codes. A
  test covers all 17 regions.
- 2.4 Replication tests, marked `data`. Tolerances: ±0.05 for indices, ±0.1 pp for shares, exact
  for ranks.
  - Korea AUI 3.73, rank 5 (August 2025; September 2025 report).
  - Korea rank 7 of 116 (November 2025; as reported from the January 2026 report).
  - Korea AUI above 3.5 (February 2026; Anthropic's May 2026 announcement).
  - Australia: 1.6% share, rank 11; AUI 4.1, rank 7 (February 2026; Australia brief).
  - India: 5.8% share, rank 2 (November 2025; India brief).
  - Every value in §3.
  - Optional: the Australia brief's within-country state indices (NSW 1.20, VIC 1.19, WA 0.68).
    They validate M3 directly but need ABS population by state and age.

Acceptance: the canonical table builds from a clean clone; replication results, failures included,
are logged in `docs/PROJECT_STATUS.md`.

### Phase 3 — National profile, RQ1 (≈3–4 h)

- 3.1 Peer sets, fixed by ADR. Proposed:
  - P1, Asia-Pacific advanced economies with data: Japan, Singapore, Taiwan, Australia, New
    Zealand.
  - P2, high-adoption economies: AUI > 1 and at least 200 conversations.
  - P3, all countries with at least 200 conversations.
- 3.2 M9 for Korea against peers in each release. Time series of share, AUI, and rank across the
  five snapshots, with method changes flagged.
- 3.3 Figures F1–F4 and table T1.

Acceptance: each figure has one generating function and a caption with period and source, and
every plotted headline number is in `outputs/facts.json`.

### Phase 4 — Regional usage, RQ2 (≈3–4 h)

- 4.1 Denominators for each snapshot month.
- 4.2 M2–M4 for the four regional snapshots, with binomial 95% intervals where counts exist. The
  intervals are understated (§6).
- 4.3 Stability: Spearman ρ of regional indices across snapshots. Flag any region whose share
  moves by more than a third between snapshots (for example, Incheon in February 2026).
- 4.4 Capital-region and non-capital aggregates. Rankings within the non-capital regions, which
  Seoul-centered gateway bias distorts less.
- 4.5 Regional facets (use case, collaboration, task traits, SOC major groups), only where all 17
  regions are published.
- 4.6 Association with GRDP per capita: scatter plot and Spearman ρ, N = 17.
- 4.7 Figures F5–F7 and table T2.

**Checkpoint B (owner):** judge regional measurement validity (IP geolocation, commuting,
instability) before the decomposition; choose the headline denominator (ADR).

### Phase 5 — Composition versus adoption, RQ3–RQ4 (≈6–10 h)

- 5.1 Crosswalks per §7, with invariant tests and audit tables.
- 5.2 Occupation intensities `v_o` and `x_o`, and their values at KSCO level.
- 5.3 US benchmark (M8).
- 5.4 Korea: `X_r`, `ŵ_r`, `R_r`; variance accounted for; residual ranking.
- 5.5 Rank comparison with the Bank of Korea's published regional exposure rankings, using
  published material only.
- 5.6 Robustness: intensity variant (`v`, `x`, ILO), weighting scheme, denominator, snapshot.
  Report rank stability.
- 5.7 Figures F8–F9 and table T3.

### Phase 6 — Brief and release preparation (owner-led)

- 6.1 Complete `outputs/facts.json`. Create `report/brief.src.md` with section headings and fact
  placeholders (`{{fact_id}}`). Write a renderer that fails on unknown or unused facts, and a CI
  check that `report/brief.md` is current.
- 6.2 The owner drafts the narrative. Claude edits on request and runs the consistency checks.
- 6.3 `docs/METHODOLOGY.md`; final README (summary, key figures, how to reproduce, attribution,
  disclaimers); LICENSE (the owner's choice).
- 6.4 Publication checklist (ADR 0002).

**Checkpoint C (owner):** approve publication.

## 9. Outputs

Figures:

- F1 Korea's share of global usage and AUI across snapshots, with rank.
- F2 Use-case mix and collaboration mode, Korea against peers.
- F3 Task traits, Korea against peers (dot plot).
- F4 SOC major-group mix against global (pp), and the most over- and under-represented request
  clusters.
- F5 Within-Korea usage index by region in the latest month, with earlier snapshots as markers.
- F6 Capital region against the rest: shares of usage, population, and employment.
- F7 Usage index against GRDP per capita, 17 regions.
- F8 US states: observed against predicted work usage.
- F9 Korea: observed against predicted work usage, residuals, and exposure rank.

Tables:

- T1 National metrics against peers.
- T2 Regional shares, denominators, indices, and intervals.
- T3 Robustness.

`outputs/facts.json` entries carry: `id`, `value`, `display`, `unit`, `period`, source IDs from
`docs/DATA_SOURCES.md`, and the producing function.

Brief outline (headings only; the owner writes the text):

1. Key findings
2. Korea among the leading adopters
3. What Korean users use Claude for
4. Usage is concentrated in the capital region
5. Composition or adoption?
6. Usage and exposure
7. Implications
8. Methodology and limitations
9. Data and code availability; citation

## 10. Risks

| Risk | Mitigation |
| --- | --- |
| Regional pattern driven by IP geolocation or commuting | Stability checks; workplace-based denominator; capital-region aggregate; non-capital rankings; explicit caveat |
| Crosswalk noise | Alternative weights; coverage audit; robustness rule fixed in §7 |
| Regional occupation data too coarse | Tier T2 (MDIS), or results at the coarse level with the limitation stated |
| AEI schema changes between releases | One adapter per release, each with fixture tests |
| Seventeen observations | Descriptive framing; N reported everywhere |
| Overlap with the Bank of Korea issue note | Usage-first framing; citation; explicit comparison |
| Employer rules on outside publication | ADR 0002 before anything goes public |
| Time | Minimum viable brief = Phases 0–4 plus basic F8–F9; robustness beyond §7's rule is optional |

## 11. Definition of done

- `make all` on a clean clone reproduces every figure, table, and fact, given the owner-supplied
  files listed in `docs/DATA_SOURCES.md`.
- Replication tests pass, or each discrepancy is documented.
- Every number in `report/brief.md` resolves to `outputs/facts.json`, and the render check passes
  in CI.
- `docs/METHODOLOGY.md`, the README, and `docs/DATA_SOURCES.md` are complete, with licenses and
  attribution.
- Checkpoint C is approved.

## 12. Owner actions

- Approve this plan or request changes.
- Create the GitHub remote, or approve Phase 0.1.
- Put `KOSIS_API_KEY` and `BLS_USER_AGENT` in `.env`.
- Tier T2 only: download 지역별고용조사 microdata from MDIS into `data/manual/`.
- Draft the brief's narrative (Phase 6).
- Complete the employer review (ADR 0002) before any public release.

## 13. Backlog (after the brief)

- Korean-language summary.
- Industry-based regional index as a second composition check.
- Refresh when new AEI releases appear.

## References

Citations to verify in Phase 1.7.

- Anthropic Economic Index reports and data. Hugging Face `Anthropic/EconomicIndex`; reports of
  September 2025, January 2026, March 2026, and June 2026.
- Appel, R. (2026). India Country Brief: The Anthropic Economic Index. Anthropic, 16 February 2026.
- McCrory, P. (2026). How Australia Uses Claude: Findings from the Anthropic Economic Index.
  Anthropic, 31 March 2026.
- Massenkoff, M., and McCrory, P. (2026). Research on labor market impacts and observed exposure.
  Anthropic, 5 March 2026 (title to confirm).
- 한국은행 조사국 (2026). AI와 지역 노동시장: 지역간 격차 확대 위험과 새로운 기회. BOK 이슈노트,
  2026년 9월 15일 (number and authors to confirm).
- 한국은행 (2025). AI와 한국경제. BOK 이슈노트 제2025-2호.
- Eloundou, T., Manning, S., Mishkin, P., and Rock, D. (2024). GPTs are GPTs: Labor market impact
  potential of LLMs. Science.
- Gmyrek, P., et al. (2025). Generative AI and Jobs: A Refined Global Index of Occupational
  Exposure. ILO Working Paper 140.
