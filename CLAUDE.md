# korea-ai-exposure — guide for Claude Code and contributors

This file applies to the whole repository. Read it at the start of every session.

## Mission

Measure where AI is used, and where AI-exposed work sits, across Korea's 17 metropolitan cities
and provinces (시도), using public data only: the Anthropic Economic Index (AEI), Anthropic's
occupation-level exposure data, and Korean official statistics. The output is a reproducible
research brief in which every number traces to committed code and a pinned public source.

The distinctive evidence is **observed usage**. Public AEI releases from January 2026 onward
report Claude.ai usage for all 17 Korean regions (ISO 3166-2 `KR-xx`). Exposure-based regional
rankings already exist (Bank of Korea issue note, 15 September 2026). This project asks how
observed usage compares with occupational exposure; it does not repeat the exposure-only analysis.

## Current checkpoint

- Phase: **0 — bootstrap**, not started. `docs/PLAN.md` is proposed. The owner's instruction to
  start Phase 0 counts as plan approval; record it in `docs/PROJECT_STATUS.md`.
- Next unit: Phase 0, then the Phase 1 source-verification spike, which ends at **Checkpoint A**.
- Authority files, in order:
  1. `docs/PLAN.md` — scope, measures, phases, acceptance criteria.
  2. `docs/PROJECT_STATUS.md` — current state, next action, blockers, checkpoint decisions.
  3. `docs/DATA_SOURCES.md` — source registry and verification status.
  4. `docs/decisions/` — ADRs.

## New-session procedure

1. Run `git status --short --branch`. If the worktree is dirty, stop and report. Never reset,
   stash, or discard changes you did not make.
2. Read the authority files. Do not rely on earlier chat transcripts.
3. Run `make check` (once Phase 0 has created it).
4. Before implementing, state back: current phase, the exact next unit, and the hard stops that
   apply to it.

## Hard stops

Absolute:

- No restricted or confidential data, ever: no National Pension Service or other administrative
  microdata, no Bank of Korea internal data, no raw MDIS microdata in git. Do not read from or
  write to sibling repositories (for example `../nps-youth-mobility`).
- Never commit raw downloads, `.env`, API keys, or tokens.

Ask the owner first:

- Changing repository visibility, creating releases, or publishing anything externally.
- Downloading files that require the owner's login (MDIS or any authenticated portal). Ask the
  owner to place them in `data/manual/`.
- Writing the narrative sections of the brief (key findings, interpretation, implications). The
  owner writes the first draft. Claude produces code, figures, tables, the facts sheet, and
  methodology documentation, and edits prose when asked.
- Any paid API call. The project needs none.
- Passing a checkpoint (A, B, C) before the owner's decision is recorded in
  `docs/PROJECT_STATUS.md`.

## Working protocol

- Small, reviewable units, each with one stated outcome.
- Tests change in the same commit as behavior.
- Update `docs/PROJECT_STATUS.md` when the phase, a blocker, or the next action changes.
- Record consequential choices (definitions, weights, peer sets, thresholds, denominators) as
  ADRs in `docs/decisions/`.
- Conventional commit prefixes: `feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`, `data:`.
- After green checks, commit in semantic units, push, and confirm local and remote commit IDs
  match.

## Evidence rules

- Every number in the brief is rendered from `outputs/facts.json`, which code produces from pinned
  inputs. No hand-typed numbers.
- Reproduce published values before relying on a dataset (targets: `docs/PLAN.md` §3 and
  Phase 2.4). If a value does not reproduce, document why; never tune the method to force
  agreement.
- Keep three terms distinct and label every measure with exactly one:
  - **usage** — observed Claude.ai conversations (AEI);
  - **exposure** — an occupation-level measure (e.g., Anthropic `observed_exposure`);
  - **predicted usage** — usage implied by occupational composition.

  AEI classifies conversation content into O*NET tasks; it does not observe users' occupations.
- Region of usage is IP-based. Commuting, mobile-carrier and corporate gateways, and VPNs can
  shift measured usage toward Seoul. Report stability across snapshots and results under
  alternative denominators.
- Seventeen regions is a small sample. Report N with every cross-regional statistic, describe
  associations, and use no causal language.
- Cross-release comparisons mix real change with method change (classifier model, sampling
  window, product scope, schema). Prefer within-release comparisons and flag every cross-release
  one.
- A missing AEI row means "not published" (privacy threshold or sample floor), not zero.
- Qualify any "first" claim ("to our knowledge") and cite prior art, including the Bank of
  Korea's September 2026 issue note.
- Preserve null and negative results.
- Do not imply endorsement by Anthropic, the Bank of Korea, or any other institution.

## Data rules

- Public sources only. Register each source in `docs/DATA_SOURCES.md` (URL, version, access,
  license, attribution) before code depends on it.
- Pin downloads in `data/manifest.json` (URL, SHA-256, bytes, retrieval time). Fetchers verify
  checksums and are idempotent. Pin Hugging Face URLs to a commit hash, not `main`. Never put
  credentials in a pinned URL. TLS verification uses the OS trust store and is never disabled.
- Korean region codes are a known trap. ISO 3166-2:KR uses KR-49 for Jeju and KR-50 for Sejong;
  Korean legal-dong province codes use 50 for Jeju and 36 for Sejong. ISO kept KR-42 (Gangwon) and
  KR-45 (Jeonbuk) after their legal-dong codes changed to 51 (2023) and 52 (2024). Build the
  mapping from names, cover all 17 regions in a unit test, and never join on numeric codes from
  different systems.
- KSCO revision break: the 8th KSCO took effect on 2025-01-01. Do not mix KSCO-7 and KSCO-8 codes
  without an explicit crosswalk.
- Derived data committed in `data/processed/` carry source attribution. Anything derived from
  microdata follows the source's disclosure terms and a minimum-cell rule set in an ADR.
- BLS may block scripted downloads that carry no contact information. Read the User-Agent from `BLS_USER_AGENT` in `.env`;
  if still blocked, ask the owner to download into `data/manual/`.

## Commands

Phase 0 created these; keep the list current.

| Command | Purpose |
| --- | --- |
| `make setup` | Create `.venv` (Python 3.12) and install pinned requirements; `PYTHON=...` picks the interpreter |
| `make lock` | Re-pin `requirements.txt` from `requirements.in` (pip-tools, with hashes) |
| `make check` | `ruff check`, `ruff format --check`, offline `pytest` |
| `make fetch` | Download and checksum the files pinned in `data/manifest.json` |
| `make build` | Canonical tables in `data/interim/` and `data/processed/` (placeholder until Phase 2) |
| `make figures`, `make facts`, `make brief` | Figures, facts sheet, rendered brief (placeholders until Phases 3–6) |
| `make all` | fetch → build → figures → facts → brief |

Recipes need GNU Make and a POSIX shell (Git Bash on Windows). Where make is missing, run the
recipe commands directly; on Windows `make check` is `.venv/Scripts/python -m ruff check .`,
`.venv/Scripts/python -m ruff format --check .`, `.venv/Scripts/python -m pytest`. CI runs the
checks on Linux (with make) and on Windows (without). Register a download with
`python -m korea_ai_exposure.fetch --add SOURCE-ID URL PATH` (`data/README.md`).

## Conventions

- Python 3.12; `requirements.in` → pinned `requirements.txt` via pip-tools; `src/` layout,
  package `korea_ai_exposure`.
- Ruff: line length 100; rules B, E, F, I, RUF, SIM, UP. Tests that need downloaded data are
  marked `@pytest.mark.data` and skip when the data are absent; CI runs offline.
- Deterministic outputs: stable sort orders, no run timestamps inside generated tables, fixed
  float formatting.
- Figures: matplotlib with one shared style module, a color-blind-safe palette, English labels,
  and these region names: Seoul, Busan, Daegu, Incheon, Gwangju, Daejeon, Ulsan, Sejong,
  Gyeonggi, Gangwon, Chungbuk, Chungnam, Jeonbuk, Jeonnam, Gyeongbuk, Gyeongnam, Jeju. Save PNG
  and SVG.
- Prose in docs and captions: plain and precise; give units, periods, and sources.

## Repository map (target after Phase 0)

```text
CLAUDE.md                  this guide
README.md                  public summary (finalized in Phase 6)
docs/PLAN.md               project plan
docs/PROJECT_STATUS.md     state, next action, checkpoint log
docs/DATA_SOURCES.md       source registry
docs/decisions/            ADRs
docs/discovery/            verification notes (Phase 1)
data/manifest.json         pinned downloads (committed)
data/raw/, data/manual/    downloads and owner-supplied files (gitignored)
data/interim/              intermediate tables (gitignored)
data/processed/            small derived tables (committed, attributed)
src/korea_ai_exposure/     fetch, aei, regions, crosswalk, measures, figures, facts
tests/                     offline unit tests and data-marked replication tests
outputs/                   figures/, tables/, facts.json
report/brief.src.md        owner-written brief with fact placeholders
report/brief.md            rendered brief
```
