# Project status

Last updated: 2026-10-30

## Current state

- Phases 0–2 are complete. The AEI files are pinned at Hugging Face commit `4e5f69fa…`;
  `make build` writes the canonical table (`data/interim/aei_long.parquet`, 2,709,773 rows) and
  `data/processed/regions.csv`, also from a clean clone. Replication: 38 pass, 0 fail, 1 not run
  (the optional Australian state indices); the table is in `docs/replication.md`, and
  `make replicate` regenerates it.
- **Phase 3 — national profile (RQ1): next.**
- Checkpoint A approved 2026-10-30 (below).
- The repository is public by the owner's decision of 2026-10-29 (ADR 0002 amendment), so every
  push publishes. `outputs/` stays untracked until Checkpoint C.
- The Proportionality rules in `CLAUDE.md` apply from 2026-10-30.

## Next action

Phase 3 (`docs/PLAN.md` §8): build the peer sets of ADR 0003 (3.1); compute M9 for Korea against
each peer set in each release, and the series of share, AUI and rank across the five snapshots,
with method changes flagged (3.2); then figures F1–F4 and table T1 (3.3). Figures, tables and
`facts.json` go to `outputs/`, which stays untracked until Checkpoint C.

## Open decisions

- Checkpoint B, after Phase 4: regional measurement validity (IP geolocation, commuting,
  instability) and the headline denominator (ADR).
- Before Phase 5: the primary exposure measure for RQ4 (ADR; Anthropic's observed exposure is
  built from the same usage data, including the November 2025 sample; ILO WP140 is
  independent); the input for M5(a); handling of occupations without usage or exposure values
  (never as zero); the OEWS vintage and suppressed state cells; the remaining crosswalk weights;
  GRDP 2024 (preliminary) or waiting for 2025 (December 2026).
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

- 2026-10-30: code reads the KOSIS key as `KOSIS_KEY`, the name in the owner's `.env` (older
  docs say `KOSIS_API_KEY`).

## Blockers

None.

## Checkpoints

| Checkpoint | Scope | Status | Date | Decision |
| --- | --- | --- | --- | --- |
| Plan | Approve `docs/PLAN.md` | Approved | 2026-10-29 | Owner, in session: approve the plan, start with Phase 0, report Phase 1 results at Checkpoint A |
| Visibility | Repository public or private (ADR 0002) | Decided | 2026-10-29 | Owner: keep the repository public |
| A | Sources, regional occupation tier, denominators, peer sets | Approved | 2026-10-30 | Owner: approve A1–A8 as recommended; ADRs 0003–0007 accepted; `outputs/` untracked until Checkpoint C |
| B | Regional measurement validity; headline denominator | Pending | | |
| C | Publication | Pending | | |

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
