# Project status

Last updated: 2026-10-30

## Current state

- Phases 0–2 are complete. The AEI files are pinned at Hugging Face commit `4e5f69fa…`;
  `make build` writes the canonical table (`data/interim/aei_long.parquet`, 2,709,773 rows) and
  `data/processed/regions.csv`, also from a clean clone. Replication: 38 pass, 0 fail, 1 not run
  (the optional Australian state indices); the table is in `docs/replication.md`, and
  `make replicate` regenerates it.
- Phase 3 — national profile (RQ1): complete (2026-10-30). `make figures` draws F1–F4 with
  captions; `make facts` writes `outputs/facts.json` (336 facts) and T1. Outputs are
  deterministic and stay in `outputs/` (untracked).
- Phase 4 — regional usage (RQ2): complete (2026-10-30). Six KOSIS tables are pinned through the
  fetcher's key path (`key_env: KOSIS_KEY`); `make build` also writes
  `data/processed/denominators.csv`; `make figures` adds F5–F7 and `make facts` adds T2 and the
  RQ2 facts (620 facts in all).
- Checkpoint B approved 2026-10-30 (below); ADR 0008 accepted.
- Phase 5 — composition versus adoption (RQ3–RQ4): complete (2026-10-30), with D1–D5 as decided
  by the owner (ADR 0009; Choices). Nine more inputs are pinned; `crosswalk.py` maps the three
  occupation measures to KSCO-8 sub-major groups and `decomposition.py` computes M6–M8, the
  comparison with the Bank of Korea's rank orders and the robustness checks; `make figures`
  adds F8–F9 and `make facts` adds T3 and the RQ3–RQ4 facts. Results stay in `outputs/`
  (untracked) until Checkpoint C.
- **Phase 6 — brief (owner-led): next.**
- Checkpoint A approved 2026-10-30 (below).
- The repository is public by the owner's decision of 2026-10-29 (ADR 0002 amendment), so every
  push publishes. `outputs/` stays untracked until Checkpoint C.
- The Proportionality rules in `CLAUDE.md` apply from 2026-10-30.

## Next action

Phase 6 (`docs/PLAN.md` §8, owner-led): the owner drafts the brief's narrative from
`outputs/facts.json`, the figures (captions in `outputs/figures/captions.md`) and T1–T3; Claude
writes the methodology section and edits prose on request. Under the Proportionality rules
`facts.json` stays and there is no brief renderer. Then one independent check of every number in
the brief against its source, and Checkpoint C.

## Open decisions

- Findings in tracked files: the Checkpoint B record below and ADR 0008 quote regional results,
  which ADR 0002 holds back until Checkpoint C. Options: replace the numbers with pointers to the
  untracked tables (the public history keeps them), or leave them.
- Checkpoint C: publication, after the ADR 0002 review of findings.

## Owner actions

- [ ] Rotate the KOSIS OpenAPI key. Its value appears once in a local Claude session log of the
      Phase 1 verification; it is in no tracked file and no commit.
- [ ] Optional: to run the pipeline from your own terminal, install CPython 3.12 next to 3.13
      (`winget install Python.Python.3.12`) and rebuild `.venv` with `make setup` (GNU Make is
      at `C:\rtools45\usr\bin\make.exe`). The current `.venv` uses a Python that exists only
      inside the Claude app.
- [ ] Optional: ask Anthropic (econ-research@anthropic.com) about the data licence (CC-BY in the
      card text, MIT in its metadata) and whether April 2026 is a partial month.
- [ ] Optional: ask the Bank of Korea for approval to reuse values from the issue note's figures
      (ADR 0007).
- [ ] ADR 0002 review before any public release of findings.

## Choices

One line each; ADRs only for choices that change results (`CLAUDE.md`, Proportionality).

- 2026-10-30: code reads the KOSIS key as `KOSIS_KEY`, the name in the owner's `.env`.
- 2026-10-30 (owner): KOSIS tables come through a fetcher path that adds `KOSIS_KEY` at request
  time and pins the URL without it; keyed requests follow no redirect to another host, and a
  KOSIS error object is refused.
- 2026-10-30: M4 uses the work share of classified use cases; in February 2026, where coursework
  is unpublished for Ulsan and Jeju, every region uses its work share of all conversations.
- 2026-10-30: intervals for regional shares are Wilson 95% intervals from conversation counts
  (weekly releases only), carried to the index with the denominator taken as exact.
- 2026-10-30: the GRDP association (4.6) uses GRDP per capita 2024 (preliminary), the latest
  published; 2025 is due in December 2026.
- 2026-10-30: regional facets (4.5) keep the metrics published for all 17 regions; task
  concentration is left out (sparse regional task breakdowns).
- 2026-10-30 (owner, D2): M5(a) uses the USA's detailed-SOC shares in release 2026-06-26, May
  2026 (O*NET-SOC 2019 truncated to SOC 2018), over OEWS national employment shares; global
  shares are the sensitivity.
- 2026-10-30 (owner, D3): occupations without a value are left out, weights renormalized over the
  rest, and coverage reported at each step; never zero (observed exposure's 411 zeros are values).
- 2026-10-30 (owner, D4): OEWS May 2025, national and state; suppressed state cells are left out,
  with each state's coverage reported.
- 2026-10-30 (owner, D5): a SOC 2018 code split across SOC 2010 codes divides its employment
  equally; each OEWS aggregate is one unit (usage share summed, exposure averaged equally, ISCO
  links pooled over its components); KSCO-8 unit 8631 gets no value; the KSSC one-to-one rules
  are a sensitivity (PLAN §7: rank rho below 0.9 is not robust).
- 2026-10-30: the one-to-one sensitivity takes the first ISCO link listed for each KSCO unit, a
  mechanical stand-in for the KSSC/ILO rules, which need judgment.
- 2026-10-30: the five OEWS-specific aggregates take their components from the OEWS occupation
  definitions (a constant in `crosswalk.py`), the seven broad-code aggregates from the SOC
  structure; BLS links to 3-digit ISCO groups and the KSCO armed-forces units fall outside the
  unit-group chain, and the audit table lists what drops out.
- 2026-10-30: M5(a) keeps its definition although occupations with few wage-and-salary workers
  and common conversation topics get extreme usage per worker (AEI classifies content, not
  users' occupations); T3 reports the observed-exposure and ILO intensities as variants.
- 2026-10-30: US state work usage is each state's usage share times its work share, May 2026,
  for the 50 states and DC; the ILO scores are used unadjusted (no complementarity adjustment).
- 2026-10-30: P2 uses the headline AUI; P4 is the ten nearest countries in published
  `usage_pct`, ties by country code; Korea is excluded from every peer set.
- 2026-10-30: for April–May 2026 the headline AUI is the published value (ADR 0006 item 4b);
  recomputing it from shares rounded to two decimals moves Korea from 14th to 13th in May.
- 2026-10-30: use cases are shares of work, personal and coursework; collaboration buckets and
  patterns are shares of the five patterns, which reproduces Anthropic's buckets (largest gap
  1e-14 in August 2025, 0.011 in May 2026); SOC, request-topic and artifact mixes are shares of
  published, classified rows. A metric with an unpublished input is missing, not zero.
- 2026-10-30: task concentration is the share of all conversations in the 100 largest published
  O*NET tasks, compared with P4.
- 2026-10-30: F2 and F3 show the P1a and P1b economies one by one; F4 shows every SOC major
  group and the five largest gaps each way among the major request topics (level 2).

## Blockers

None.

## Checkpoints

| Checkpoint | Scope | Status | Date | Decision |
| --- | --- | --- | --- | --- |
| Plan | Approve `docs/PLAN.md` | Approved | 2026-10-29 | Owner, in session: approve the plan, start with Phase 0, report Phase 1 results at Checkpoint A |
| Visibility | Repository public or private (ADR 0002) | Decided | 2026-10-29 | Owner: keep the repository public |
| A | Sources, regional occupation tier, denominators, peer sets | Approved | 2026-10-30 | Owner: approve A1–A8 as recommended; ADRs 0003–0007 accepted; `outputs/` untracked until Checkpoint C |
| B | Regional measurement validity; headline denominator | Approved | 2026-10-30 | Owner: approve B1 and B2 as recommended; ADR 0008 accepted |
| C | Publication | Pending | | |

## Checkpoint B — decisions (owner, 2026-10-30)

The owner approved both items as recommended.

| # | Decision | Decided | Record |
| --- | --- | --- | --- |
| B1 | Regional measurement validity | Proceed to Phase 5 with May 2026 as the headline month; report the workplace-based index and the ranks outside the capital region as robustness; report February 2026 (Incheon's 4.8% → 10.6% → 6.9%) as instability, not for levels; state that IP effects (gateways, VPNs) cannot be measured. Evidence: ranking stable across snapshots (rho 0.96–0.99) and denominators (0.97–0.99), N = 17; capital region 79–83% of usage against 53% of residents aged 15–64; Seoul's workplace-to-residence employment ratio 1.18 | This file |
| B2 | Headline denominator | Residents aged 15–64 at month end, with the workplace-based index beside it (Seoul: 3.38 and 2.63 in May 2026) | ADR 0008 |

## Checkpoint A — decisions (owner, 2026-10-30)

The owner approved every item as recommended. The ADRs carry the evidence and are now accepted.
For A7, result tables go to `outputs/tables/` (untracked); `data/processed/` holds only derived
inputs such as region codes and denominators.

| # | Decision | Decided | Record |
| --- | --- | --- | --- |
| A1 | Regional occupation tier | T1: KOSIS `DT_1ES3B06J`, 17 regions × 56 KSCO-8 sub-major groups. MDIS is no finer by region; an MDIS workplace-region sensitivity stays optional and owner-run | ADR 0004 |
| A2 | Crosswalk route | ISCO-08 → KSCO-8 directly with the official November 2025 table (revises PLAN §7, which went through KSCO-7) | ADR 0004 |
| A3 | Denominators for M3 | 15–64 resident population at month end; workplace-based workers from the establishment survey (17 regions; employees of industries B–S); residence-based employment; a 16-region commuting check. Headline choice at Checkpoint B | ADR 0005 |
| A4 | Peer sets | P1a advanced Asia-Pacific (Japan, Singapore, Taiwan, Australia, New Zealand); P1b BIS Asian Consultative Council economies with data; P2, P3 as planned; P4 size-matched for facet metrics | ADR 0003 |
| A5 | AEI conventions | Pin commit `4e5f69fa…`; apply the 200/100 floors; exclude pseudo-geographies from rankings; headline AUI series on one renormalized basis with Anthropic's 2024 population file, published values alongside; May 2026 as the headline month of release 2026-06-26; traits and mixes compared within a release | ADR 0006 |
| A6 | Derived data in the public repository | Commit derived tables with attribution; rebuild KSSC crosswalks at build time; use only the Bank of Korea's published rank orders | ADR 0007 |
| A7 | Outputs before Checkpoint C | `outputs/` (figures, result tables, facts) stays untracked until Checkpoint C, because the repository is public and findings wait for the ADR 0002 review | `.gitignore`; ADR 0002 |
| A8 | Approve Phase 2 | Approved | This file |

The smaller choices inside the ADRs were accepted with their defaults: survey periods paired with
snapshots (ADR 0004, item 2); flagged and missing cells (ADR 0004, item 3); targets published to
one decimal checked on rank, with the level gap documented (ADR 0006); no in-house SOC map for
November 2025 and February 2026 (ADR 0006, item 7); the M4 work share over classified use cases
(ADR 0006, item 9); and the "to our knowledge" framing in `docs/discovery/02_prior_art.md`.
