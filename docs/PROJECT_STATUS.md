# Project status

Last updated: 2026-10-29

## Current state

- Phase 0 — bootstrap: complete. CI passes on Linux and Windows.
- Phase 1 — source verification: complete. Findings in `docs/discovery/01_source_verification.md`
  (checksums in `01a_checksums.md`) and `docs/discovery/02_prior_art.md`; registry updated in
  `docs/DATA_SOURCES.md`; proposed ADRs 0003–0007.
- **Checkpoint A: awaiting the owner's decisions** (below). Phase 2 does not start before they
  are recorded here.
- Plan: `docs/PLAN.md` approved by the owner on 2026-10-29.
- Repository: GitHub `origin` (`bwade9090/korea-ai-exposure`) is public by the owner's decision of
  2026-10-29 (ADR 0002 amendment). Every push publishes; the hard stops apply to every commit.

## Next action

The owner decides the Checkpoint A items. Then Phase 2 (AEI ingestion and replication).

## Checkpoint A — decisions requested

Each item has a proposed ADR with the evidence and a recommendation. Accepting an ADR means
changing its status to accepted, with the date; amendments go into the ADR before acceptance.

| # | Decision | Recommendation | Record |
| --- | --- | --- | --- |
| A1 | Regional occupation tier | T1: KOSIS `DT_1ES3B06J`, 17 regions × 56 KSCO-8 sub-major groups. MDIS is no finer by region; an MDIS workplace-region sensitivity stays optional and owner-run | ADR 0004 |
| A2 | Crosswalk route | ISCO-08 → KSCO-8 directly with the official November 2025 table (revises PLAN §7, which went through KSCO-7) | ADR 0004 |
| A3 | Denominators for M3 | 15–64 resident population at month end; workplace-based workers from the establishment survey (17 regions; employees of industries B–S); residence-based employment; a 16-region commuting check. Headline choice at Checkpoint B | ADR 0005 |
| A4 | Peer sets | P1a advanced Asia-Pacific (Japan, Singapore, Taiwan, Australia, New Zealand); P1b BIS Asian Consultative Council economies with data; P2, P3 as planned; P4 size-matched for facet metrics | ADR 0003 |
| A5 | AEI conventions | Pin commit `4e5f69fa…`; apply the 200/100 floors; exclude pseudo-geographies from rankings; headline AUI series on one renormalized basis with Anthropic's 2024 population file, published values alongside; May 2026 as the headline month of release 2026-06-26; traits and mixes compared within a release | ADR 0006 |
| A6 | Derived data in the public repository | Commit derived tables with attribution; rebuild KSSC crosswalks at build time; use only the Bank of Korea's published rank orders | ADR 0007 |
| A7 | Outputs before Checkpoint C | The repository is public, so committing figures and facts from Phase 3 on publishes findings before the ADR 0002 review. Either keep `outputs/` untracked until Checkpoint C, or accept publication as work proceeds | Owner (ADR 0002) |
| A8 | Approve Phase 2 | — | This file |

Smaller choices inside the ADRs, with proposed defaults: survey periods paired with snapshots
(ADR 0004, item 2); flagged and missing cells (ADR 0004, item 3); targets published to one
decimal checked on rank, with the level gap documented (ADR 0006); no in-house SOC map for
November 2025 and February 2026 unless asked (ADR 0006, item 7); the M4 work share over
classified use cases (ADR 0006, item 9); and the "to our knowledge" framing in
`docs/discovery/02_prior_art.md`.

When ADRs 0004 and 0006 are accepted, PLAN §5 (the T2 rationale), §7 (the crosswalk route), M1
(the population source) and 2.4 (tolerances) are updated to match.

Later decisions, needed before Phase 5 only: the primary exposure measure for RQ4 (Anthropic's
observed exposure is built from the same usage data, including the November 2025 sample; ILO
WP140 is independent); the input for M5(a); handling of occupations without usage or exposure
values (never as zero); the OEWS vintage and suppressed state cells; the remaining crosswalk
weights; GRDP 2024 (preliminary) or waiting for 2025 (December 2026).

## Checkpoints

| Checkpoint | Scope | Status | Date | Decision |
| --- | --- | --- | --- | --- |
| Plan | Approve `docs/PLAN.md` | Approved | 2026-10-29 | Owner, in session: approve the plan, start with Phase 0, report Phase 1 results at Checkpoint A |
| Visibility | Repository public or private (ADR 0002) | Decided | 2026-10-29 | Owner: keep the repository public |
| A | Sources, regional occupation tier, denominators, peer sets | Awaiting owner | 2026-10-29 (report) | |
| B | Regional measurement validity; headline denominator | Pending | | |
| C | Publication | Pending | | |

## Owner actions

- [x] Approve or amend `docs/PLAN.md` (2026-10-29)
- [x] GitHub remote: `origin` exists
- [x] Repository visibility: keep public (2026-10-29; ADR 0002 amendment)
- [ ] Checkpoint A decisions A1–A8
- [ ] Rotate the KOSIS OpenAPI key. During the spike a helper printed it once to an agent's
      console; no saved file contains it.
- [ ] `.env`: `BLS_USER_AGENT` is set. The KOSIS key is stored as `KOSIS_KEY`; the docs and
      `.env.example` use `KOSIS_API_KEY`. Rename it, or code will accept both names.
- [ ] Install python.org CPython 3.12 from your own terminal (for example
      `winget install Python.Python.3.12`), then rebuild the environment with `make setup`. The
      current `.venv` was built inside the Claude desktop app from a uv-managed Python that lives
      in the app's private storage, so it may not run from an ordinary terminal.
- [ ] Optional: put GNU Make on PATH. Make 4.4.1 is already installed with Rtools
      (`C:\rtools45\usr\bin\make.exe`); it works from Git Bash.
- [ ] Optional, your call: ask Anthropic (econ-research@anthropic.com) about the data licence
      (CC-BY in the card text, MIT in its metadata) and whether April 2026 is a partial month.
- [ ] Optional, your call: ask the Bank of Korea for approval to reuse values from the issue
      note's figures (ADR 0007).
- [ ] ADR 0002 review before any public release of findings

## Blockers

None. Phase 2 waits for Checkpoint A.

## Replication log

Empty until Phase 2. Phase 1 already reproduced every value in PLAN §3 from the raw files, and
the published AUIs of August 2025, November 2025 and April–May 2026 under their own bases
(`docs/discovery/01_source_verification.md` §1.1).

## Validation evidence

At the end of each phase, record the commands run and their results.

### Phase 1 — 2026-10-29

- Ten verification passes, one per source block. Six independent skeptics then re-derived 42
  claims behind the Checkpoint A decisions with their own code: 33 confirmed, 8 partly correct
  (corrected in the documents, for example the November 2025 AUI rule, the period from which
  `DT_1ES3B06J` has 17 regions, and the scope of MDIS), 1 unverifiable (whether ISO 3166-2:KR
  has been updated for the Gwangju–Jeonnam merger; secondary sources say not). A completeness
  critic listed 13 gaps and 11 inconsistencies; all are resolved in the documents or listed as
  open items in `01_source_verification.md`.
- Downloads: 764 MB in `data/raw/` (gitignored), with SHA-256 for every file
  (`01a_checksums.md`); AEI files match their Hugging Face LFS hashes at commit `4e5f69fa…`.
- No secret values in any downloaded or scratch file (scan of 15,691 files for the raw and
  URL-encoded values of every `.env` variable).
- `make check` after the Phase 1 documents: ruff clean; 101 passed.

### Phase 0 — 2026-10-29

- Interpreter: CPython 3.12.16 (uv-managed build, Windows x86-64). Pinned environment in
  `requirements.txt` (pip-tools 7.6.2, with hashes): pandas 3.1.0, numpy 2.5.4, pyarrow 26.0.0,
  matplotlib 3.11.2, openpyxl 3.1.5, xlrd 2.0.2, python-dotenv 1.2.4, pytest 9.2.0, ruff 0.17.3.
- First pass, without make (GNU Make had not yet been found on the machine), on a fresh copy of
  the tracked files: the setup commands succeeded; `ruff check`, `ruff format --check` and
  `pytest` (39 passed) were clean; `make fetch`'s command with the empty manifest printed "No
  files registered in manifest.json; nothing to fetch." and exited 0.
- Live smoke test against Hugging Face, using a scratch manifest outside the repository:
  `--add AEI-LMI .../resolve/4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6/labor_market_impacts/job_exposure.csv`
  pinned 37,176 bytes (sha256 `4f0a3adf5fee…`) through the CDN redirect; a second run verified
  the file without downloading; after deleting the file, a run restored and verified it.
- CI (`.github/workflows/ci.yml`): run 40841248422 on commit `2a0d277` succeeded on
  ubuntu-latest with Python 3.12.15 — `make setup PYTHON=python` (hash-checked install) and
  `make check` (ruff clean; 39 passed).
- TLS: the fetcher verifies certificates against the OS trust store
  (`ssl.create_default_context`), which also works behind TLS-inspecting proxies.

#### Independent review of Phase 0

Three reviewers (fetch correctness, tests, tooling) each followed by an adversarial verifier
reported 24 findings; the verifiers confirmed all of them, most at low severity. Fixed:

- Fetcher: redirects only to HTTPS and a custom User-Agent only to the pinned host; credential
  detection by parameter name and by the values in `.env`, with query strings left out of error
  messages; `user_agent_env` limited to `*_USER_AGENT` variables; unknown manifest keys refused;
  OS errors (a file open in Excel, a read-only file) reported per file without aborting the
  batch; empty and HTML responses refused; chunked and malformed `Content-Length` handled;
  portable, case-insensitive paths; `--refresh` to re-check verified files upstream.
- Tests: 39 → 101, covering the CLI paths that write the manifest, same-length drift,
  truncation, redirects, the verifying TLS context, and the `data` marker hook (in a separate
  pytest process); the local test server bypasses any configured proxy.
- Tooling: `requires-python` capped at 3.12 and checked first in `make setup`; colorama pinned
  explicitly so the lock installs on Windows wherever it is compiled; ruff no longer formats
  Markdown; `.gitattributes` keeps LF line endings on every platform; placeholder targets fail
  and make runs serially; Windows detection also works with MSYS builds of make; a Windows CI job.

After the fixes, on a fresh copy of the tracked files with GNU Make 4.4.1 (Rtools build):
`make setup PYTHON=python` (Python 3.13) stops at the version check, as intended;
`make setup` with Python 3.12.16 succeeds; `make check` — ruff clean, 101 passed; `make fetch` —
no-op; `make all` — stops at the `build` placeholder with exit code 2, as intended. CI runs
40847981314 (commit `ec25707`) and 40848137330 (commit `8e36616`) succeeded on ubuntu-latest
and windows-latest.

Commit `67bd2f6`, titled as the marker-hook test change, also contains the fetcher hardening:
the commit meant for it failed on a transient write error. Commit `8e36616` records this; the
published history was not rewritten.
