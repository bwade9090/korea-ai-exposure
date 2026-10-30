# korea-ai-exposure — guide for Claude Code and contributors

At the start of every session run `git status --short --branch` (if the tree holds changes you
did not make, stop and report), then read this file and `docs/PROJECT_STATUS.md`: current state,
next action and decisions.

## Mission

Compare observed Claude.ai usage (Anthropic Economic Index, AEI) with occupational AI exposure
across Korea's 17 regions (시도), from public data only. The output is a reproducible brief in
which every number traces to committed code and a pinned source. Exposure-only regional rankings
already exist (Bank of Korea issue note, 15 September 2026); this project adds observed usage.

## Proportionality

This is a one-off study, not a system to operate; after Checkpoint C the repository is a frozen
snapshot.

- Choose the simplest implementation that gives a correct, reproducible number. Do not extend
  infrastructure (fetch, CI, Makefile, lockfile) unless something is broken.
- Test only what can change a reported number: AEI adapters, region mapping, crosswalk weights,
  measure formulas. No tests for plotting or file plumbing.
- ADRs (`docs/decisions/`) only for choices that change results; record other choices in one line
  in `docs/PROJECT_STATUS.md`.
- No multi-agent review rounds on code; one independent check at the end of every number in the
  brief against its source.
- Small commits with conventional prefixes (`feat:`, `fix:`, `docs:`, `data:`, `chore:`), pushed
  after `make check` passes.

## Hard stops

- Never commit secrets (`.env`, API keys, tokens) or restricted data (administrative microdata,
  Bank of Korea internal data, MDIS microdata). Do not read or write sibling repositories.
- Ask the owner before publishing anything or changing repository visibility, passing
  Checkpoint C, any paid API call, or downloads that need the owner's login (they go to
  `data/manual/`).
- Until Checkpoint C (ADR 0002), findings stay out of tracked files: results live in `outputs/`,
  which is gitignored.

## Evidence rules

- Every number in the brief comes from `outputs/facts.json`.
- Label each measure as usage (observed conversations), exposure (an occupation-level measure) or
  predicted usage. AEI classifies conversation content; it does not observe users' occupations.
- Usage is located by IP address and can be shifted toward Seoul; report it with the robustness
  checks (other denominators, ranks outside the capital region, stability across snapshots).
- Seventeen regions is a small sample: report N, describe associations, use no causal language.
- Compare within a release and flag every cross-release comparison; methods change between
  releases.
- A missing AEI row means "not published", never zero. Keep null and negative results.
- Qualify any "first" claim and cite prior art; imply no endorsement by Anthropic, the Bank of
  Korea or anyone else.

## Data rules

- Register every source in `docs/DATA_SOURCES.md` and pin each file in `data/manifest.json` (URL,
  SHA-256). Small pinned inputs are committed under `data/raw/`; the large AEI files are fetched
  with `make fetch` from a pinned Hugging Face commit.
- Pin KOSIS URLs without the key (`python -m korea_ai_exposure.fetch --add SOURCE URL PATH
  --key-env KOSIS_KEY`); BLS downloads need `--user-agent-env BLS_USER_AGENT`.
- Join Korean regions by code through `korea_ai_exposure.regions`, never across code systems
  (Jeju is ISO KR-49 but administrative 50; Sejong is ISO KR-50 but administrative 36).
- Korean occupations are KSCO-8 throughout.

## Commands

| Command | Purpose |
| --- | --- |
| `make setup` | `.venv` with Python 3.12 and the hash-pinned requirements (`PYTHON=...` picks the interpreter) |
| `make check` | ruff lint, ruff format check, offline tests |
| `make fetch` | download and verify the pinned files that are not committed |
| `make build` | the canonical AEI table (`data/interim/`) and the `data/processed/` tables |
| `make replicate` | replication of published values (`docs/replication.md`) |
| `make figures`, `make facts` | figures, tables and `outputs/facts.json` (after `make build`) |
| `make all` | build, figures and facts |

Make needs a POSIX shell (Git Bash on Windows); without make, run the recipes with
`.venv/Scripts/python -m ...`. CI runs `make check` on Linux.

## Conventions

- Python 3.12, `src/` layout (package `korea_ai_exposure`), ruff with line length 100. Tests that
  need downloaded data are marked `data` and skip without it.
- Figures: matplotlib with the shared style in `figures.py`, a colour-blind-safe palette, English
  labels, PNG and SVG, captions with period and source.
- Outputs are deterministic: stable sort orders, fixed float formats, no timestamps.
