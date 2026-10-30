# ADR 0009 — Primary exposure measure for RQ4

- Status: accepted, 2026-10-30 (the owner approved the proposal as written, with D2–D5 in
  `docs/PROJECT_STATUS.md`). Proposed 2026-10-30.
- Decider: Hyungbae Cho
- Evidence: `docs/discovery/01_source_verification.md` (AEI-LMI, ILO-WP140, crosswalks);
  `docs/discovery/02_prior_art.md` (Bank of Korea note)

## Context

RQ4 asks where usage rankings diverge from exposure rankings: the project's
occupation-weighted exposure (M6) and the Bank of Korea's September 2026 regional rankings.
Two occupation-level measures are pinned or verified:

- **Anthropic observed exposure** (`job_exposure.csv`, AEI-LMI): SOC 2018, 756 occupations
  (90.4% of OEWS detailed employment), 411 of them zero. It is built from global Claude usage,
  including the November 2025 sample, so part of any agreement with regional usage is
  mechanical. Reaching KSCO-8 takes SOC 2018 → SOC 2010 → ISCO-08 → KSCO-8, with US employment
  weights.
- **ILO WP140** (Gmyrek et al. 2025, ILO-WP140; CC BY 4.0): generative-AI exposure scores for 427
  of 436 ISCO-08 unit groups, rated from task statements and independent of Claude usage.
  Reaching KSCO-8 takes one official step (the KSSC KSCO-8 ↔ ISCO-08 table).
- The Bank of Korea note builds its generative-AI ranking on the ILO WP140 scores (adjusted for
  complementarity following Pizzinelli et al. 2023; the adjustment and its crosswalk are not
  published in enough detail to rebuild).

## Options

1. **ILO WP140 as primary, observed exposure as secondary (recommended).** Usage and exposure
   come from independent sources; the crosswalk to KSCO-8 is official and short; the source is
   the one behind the Bank of Korea's generative ranking, so rank comparisons with the note
   differ mainly in the adjustment and aggregation choices.
2. **Observed exposure as primary (PLAN M5b).** Closest to observed AI use, but not independent
   of the usage side of RQ4, and it needs the longer, US-weighted crosswalk.

## Decision

Option 1. M6 uses the ILO WP140 unit-group means (unadjusted), mapped to KSCO-8 sub-major groups
with the PLAN §7 weights; observed exposure is computed the same way and reported beside it.
Rank comparisons with the Bank of Korea note are comparisons of measures, not a replication.

## Consequences

- PLAN §5 lists ILO WP140 as optional; under this decision it becomes a core input, pinned
  from the companion repository at commit `ce5fc25c…` (ILO-WP140).
- Every RQ4 statement names the exposure measure, and results are given under both measures.
