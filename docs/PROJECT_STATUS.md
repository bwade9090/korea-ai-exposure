# Project status

Last updated: 2026-11-02

## Current state

- Phases 0–5 are complete; Checkpoints A and B are approved (below). `make build`, `make figures`
  and `make facts` run from 24 pinned inputs; the results (F1–F9, T1–T3, `outputs/facts.json`)
  stay in `outputs/`, untracked until Checkpoint C. Replication of published values:
  `docs/replication.md`. Methodology draft: `report/methodology.md`.
- External review (2026-11-02), applied before the brief: RQ3–RQ4 compare regions per worker, not
  on shares, which scale with size (ADR 0010: the RQ3 fit, the T3 usage rows, the Bank of Korea
  comparison, F8–F9); the regional pattern is set beside the 2025 인터넷이용실태조사
  (`regional.survey_check`, MSIT-NIA-2026).
- **Phase 6 — brief: first draft written** (2026-11-02): `outputs/brief/brief.docx`, a Word
  document in the form of a central-bank policy note (summary, six sections, six figures, one
  table, annex). Every number is resolved from `outputs/facts.json` by the generator in
  `outputs/brief/source/`; both stay untracked until Checkpoint C. Word renders it in nine pages
  (`outputs/brief/brief.pdf`, exported from Word); exhibits follow the paragraphs that cite them
  so that pages fill before an exhibit moves on.
- The repository is public (ADR 0002 amendment), so every push publishes.

## Next action

The owner reviews and edits `outputs/brief/brief.docx` in Word (layout, wording, the author line
and disclaimer). Then one independent check of every number in the brief against
`outputs/facts.json`, and Checkpoint C (ADR 0002, items 1–5).

## Open decisions

- Checkpoint C: publication, after the ADR 0002 review.

## Owner actions

- [ ] Rotate the KOSIS OpenAPI key: it appeared once in a local session log (no file, no commit).
- [ ] ADR 0002 review before any public release of findings.
- [ ] Optional: install CPython 3.12 next to 3.13 (`winget install Python.Python.3.12`) and run
      `make setup`, to rebuild outside the Claude app (GNU Make: `C:\rtools45\usr\bin\make.exe`).
- [ ] Optional: ask Anthropic about the data licence (CC BY in the card text, MIT in its metadata)
      and whether April 2026 is a partial month; ask the Bank of Korea about reusing values from
      its figures (ADR 0007).
- [ ] Optional: pin the 17-region generative-AI rates of the 2025 인터넷이용실태조사 (KOSIS; needs
      the KOSIS key) to turn the survey check into a rank correlation over all regions.

## Choices

One line each; choices that change results are ADRs 0001–0010.

- Data: the small pinned inputs are committed under `data/raw/`, the AEI files fetched (ADR 0007
  amendment); KOSIS keys are added at request time (`key_env: KOSIS_KEY`).
- National (RQ1): P2 uses the headline AUI, P4 the ten countries nearest in published share
  (ties by code), Korea excluded; the April–May 2026 headline AUI is the published value
  (ADR 0006); use cases are shares of classified use cases, collaboration of the five patterns
  (which reproduces Anthropic's buckets), mixes of published classified rows; task concentration
  is the share of all conversations in the 100 largest published tasks, compared with P4.
- Regional (RQ2): Wilson 95% intervals from counts (weekly releases); M4 over classified use cases,
  February 2026 over all conversations (coursework unpublished for Ulsan and Jeju); GRDP per
  capita 2024 (preliminary); facets only where all 17 regions publish them.
- Composition (RQ3–RQ4; owner, D2–D5): M5(a) from the USA's May 2026 detailed-SOC shares over OEWS
  employment, global shares as the sensitivity; missing values left out and coverage reported;
  OEWS May 2025, suppressed state cells left out; equal splits from SOC 2018 to SOC 2010 to ISCO,
  OEWS aggregates as single units, KSCO 8631 without a value, the first listed ISCO link as the
  one-to-one sensitivity; ILO scores unadjusted; M5(a) kept as defined although small,
  much-discussed occupations get extreme values (T3 reports the alternatives).
- Findings (owner): the results quoted in the Checkpoint B record and ADR 0008 stay; from
  Phase 5 on, findings stay out of tracked files until Checkpoint C.
- Engineering (owner, 2026-10-30): plumbing tests, the duplicate Windows CI job, the brief
  placeholder and unused code paths were removed under the Proportionality rules.
- Brief (owner, 2026-10-30): the rule that the owner drafts the narrative sections first is
  dropped; Claude may draft any section, and the owner reviews it.
- Brief (owner, 2026-11-02): written for policy readers in plain English, in Word, with the feel
  of a central-bank note but no institution's branding; software, internal labels and research
  history are left out. Figures use Okabe-Ito blue with orange for contrast; F9 is split into F9
  (composition) and F10 (exposure against usage ranks), and RQ4 gains the rho of ILO exposure
  with usage and each region's two ranks (`rq4.rho.*`, `rq4.rank.*`).
- Survey check (2026-11-02): the six values the MSIT release publishes (national rates, three
  highest regions of each), transcribed like the Bank of Korea ranks; stability across snapshots
  is reported as consistency, not as evidence of valid location. IP location itself is a stated
  limitation, not analysed further (owner).

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
