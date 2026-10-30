# ADR 0004 — Regional occupation data and crosswalk route

- Status: accepted, 2026-10-30 (Checkpoint A: the owner approved the proposal as written).
  Proposed 2026-10-29.
- Decider: Hyungbae Cho
- Evidence: `docs/discovery/01_source_verification.md` §1.2 and §1.4

## Context

PLAN §5 left a choice between tier T1 (public KOSIS tables) and tier T2 (MDIS microdata, for
finer occupations), and PLAN §7 routed the crosswalk through KSCO-7. Phase 1 found:

- KOSIS `DT_1ES3B06J` (지역별고용조사, 시도/직업별 취업자) publishes regions by the 9 KSCO-8 major
  groups and 56 sub-major groups (중분류), half-yearly to 2026 1/2, in thousand persons. KOSIS
  back-cast the series to KSCO-8 from 2013 1/2, so every period uses one classification. All 17
  regions are separate from 2017 1/2 (before that Sejong is inside Chungnam). No public table
  gives regions by minor group (소분류).
- MDIS is no finer for regions by occupation: its public files pair 시도 with 2-digit codes and
  시군구 with 1-digit codes; 3-digit codes come only in a national file, and 4-digit codes only
  under authorized access. Its additions are a workplace-region variable (workplace 시도 ×
  sub-major) and 시군구 × major groups. The 2026 first-half file with sub-majors is due in
  December 2026. Use brings registration, non-redistributable data, and consultation and copy
  obligations before publication.
- Reliability is flagged, not suppressed: a separate `*` item marks cells with a relative
  standard error of 25% or more. In 2026 1/2 they hold about 10% of Sejong's employment and under
  5% elsewhere. Some periods omit a few region × sub-major rows.
- The survey's reference weeks contain 15 April (1/2) and 15 October (2/2). The monthly
  경제활동인구조사 table `DT_1DA7E34S_NEW` gives KSCO-8 major groups by region for every month.
- The official KSCO-8 ↔ ISCO-08 correspondence (KSSC, November 2025) links 4-digit unit groups;
  unit 8631 has no link. No official KSCO-7 ↔ ISCO-08 table is published.

## Decision

1. **Tier T1.** Regional occupation structure comes from `DT_1ES3B06J` at the sub-major level.
   No MDIS data are used. Optional, owner-run: a workplace-based sensitivity from the MDIS public
   C형 file, only if Checkpoint B shows commuting matters and the owner accepts the obligations.
2. **Period pairing.** November 2025 and February 2026 use 2025 2/2; April and May 2026 use
   2026 1/2. Sensitivity: major-group shares from the monthly survey for the exact month.
3. **Flagged and missing cells.** Flagged cells stay in the main estimate; robustness collapses
   each region's flagged sub-major cells into their major group. A missing row is treated as not
   published, never as zero, and each region's coverage is reported.
4. **Crosswalk route (revises PLAN §7).** SOC 2018 → SOC 2010 → ISCO-08 (BLS) → KSCO-8 unit
   group (official KSSC table) → KSCO-8 sub-major. The weighting rules of PLAN §7 still apply;
   unit groups aggregate to sub-majors with national minor-group employment weights
   (`DT_1ES3B32J`) and equal weights within minor groups. The remaining weighting rules (SOC
   2018 → 2010 splits, OEWS aggregate codes, the KSSC one-to-one rules as a sensitivity, unit
   8631) are fixed in a Phase 5 ADR.
5. **Optional robustness:** workplace-based regional composition by major group from the 2020
   census (`DT_1PC2012`, KSCO-7), labelled as such.

## Consequences

- The pipeline reproduces from a clean clone with a free KOSIS key, and processed tables can be
  committed with attribution (ADR 0007).
- The decomposition (M7) works with 56 occupation groups; PLAN §10 already lists coarse
  occupation data as a risk, and the limitation is stated.
- Time series of regional occupation structure start in 2017 if they need all 17 regions.
