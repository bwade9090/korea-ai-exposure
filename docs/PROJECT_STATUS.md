# Project status

Last updated: 2026-10-30

## Current state

- Phase 0 — bootstrap: complete. CI passes on Linux and Windows.
- Phase 1 — source verification: complete. Findings in `docs/discovery/01_source_verification.md`
  (checksums in `01a_checksums.md`) and `docs/discovery/02_prior_art.md`; registry updated in
  `docs/DATA_SOURCES.md`.
- Checkpoint A: **approved 2026-10-30** (below). ADRs 0003–0007 accepted; PLAN §5, §6 (M1, M3),
  §7, 2.1, 2.4 and 3.1 updated to match.
- Phase 2 — AEI ingestion and replication: complete (2026-10-30). The canonical table builds from
  a clean clone; 38 replication targets reproduce, none fails, and the optional Australian state
  target is not run (it needs ABS population). Log and evidence below.
- **Phase 3 — national profile (RQ1): next.**
- Plan: `docs/PLAN.md` approved by the owner on 2026-10-29.
- Repository: GitHub `origin` (`bwade9090/korea-ai-exposure`) is public by the owner's decision of
  2026-10-29 (ADR 0002 amendment). Every push publishes; the hard stops apply to every commit.
  `outputs/` is gitignored until Checkpoint C (decision A7).

## Next action

Phase 3 (`docs/PLAN.md` §8): build the peer sets of ADR 0003 (3.1); compute M9 for Korea against
each peer set in each release, and the series of share, AUI and rank across the five snapshots,
with method changes flagged (3.2); then figures F1–F4 and table T1 (3.3). Figures, tables and
`facts.json` go to `outputs/`, which stays untracked until Checkpoint C.

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
| A | Sources, regional occupation tier, denominators, peer sets | Approved | 2026-10-30 | Owner: approve A1–A8 as recommended; ADRs 0003–0007 accepted; `outputs/` untracked until Checkpoint C |
| B | Regional measurement validity; headline denominator | Pending | | |
| C | Publication | Pending | | |

## Owner actions

- [x] Approve or amend `docs/PLAN.md` (2026-10-29)
- [x] GitHub remote: `origin` exists
- [x] Repository visibility: keep public (2026-10-29; ADR 0002 amendment)
- [x] Checkpoint A decisions A1–A8 (2026-10-30)
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

None.

## Replication log

### Phase 2 — 2026-10-30

`make replicate` (`korea_ai_exposure.replication`) at commit `f8d9d0c`, on the files pinned in
`data/manifest.json` (Hugging Face commit `4e5f69fa…`); the data-marked test
`test_every_replication_check_passes_or_is_a_declared_optional_target` runs the same checks.
Tolerances follow PLAN 2.4. Basis: `published` compares the release's own AUI values;
`anthropic_2025` and `renormalized` are the bases of ADR 0006; `published usage_pct` is the
release's share of global usage.

| Target | Published | Reproduced | Basis | Result | Note |
| --- | --- | --- | --- | --- | --- |
| Korean conversations, Nov 2025 | 30,618 | 30,618 |  | pass |  |
| Korean regional counts sum to the national count, Nov 2025 | exact | 30,618 of 30,618 (17 regions) |  | pass |  |
| Smallest regional count, Nov 2025 | 175 (Ulsan) | 175 (Ulsan) |  | pass |  |
| Korean conversations, Feb 2026 | 29,075 | 29,075 |  | pass |  |
| Korean regional counts sum to the national count, Feb 2026 | exact | 29,075 of 29,075 (17 regions) |  | pass |  |
| Smallest regional count, Feb 2026 | 174 (Jeju) | 174 (Jeju) |  | pass |  |
| Korean regions with published usage, Nov 2025 | 17 | 17 |  | pass |  |
| Korea's share of global conversations, Nov 2025 | 3.06% | 3.0622% |  | pass |  |
| Seoul's share of Korean usage, Nov 2025 | 58.23% | 58.2305% |  | pass |  |
| Seoul + Gyeonggi + Incheon, Nov 2025 | 79.09% | 79.0940% |  | pass |  |
| Incheon's share of Korean usage, Nov 2025 | 4.82% | 4.8207% |  | pass |  |
| Korean regions with published usage, Feb 2026 | 17 | 17 |  | pass |  |
| Korea's share of global conversations, Feb 2026 | 2.91% | 2.9075% |  | pass |  |
| Seoul's share of Korean usage, Feb 2026 | 56.09% | 56.0929% |  | pass |  |
| Seoul + Gyeonggi + Incheon, Feb 2026 | 81.91% | 81.9089% |  | pass |  |
| Incheon's share of Korean usage, Feb 2026 | 10.56% | 10.5589% |  | pass |  |
| Korean regions with published usage, Apr 2026 | 17 | 17 |  | pass |  |
| Korea's share of global conversations, Apr 2026 | 3.19% | 3.1900% |  | pass |  |
| Seoul's share of Korean usage, Apr 2026 | 63.53% | 63.5300% |  | pass |  |
| Seoul + Gyeonggi + Incheon, Apr 2026 | 83.34% | 83.3400% |  | pass |  |
| Incheon's share of Korean usage, Apr 2026 | 6.94% | 6.9400% |  | pass |  |
| Korean regions with published usage, May 2026 | 17 | 17 |  | pass |  |
| Korea's share of global conversations, May 2026 | 3.24% | 3.2400% |  | pass |  |
| Seoul's share of Korean usage, May 2026 | 63.65% | 63.6500% |  | pass |  |
| Seoul + Gyeonggi + Incheon, May 2026 | 82.78% | 82.7800% |  | pass |  |
| Incheon's share of Korean usage, May 2026 | 6.75% | 6.7500% |  | pass |  |
| Korea's published AUI and rank, Apr 2026 | 3.92, rank 9–10 of 114 | 3.92, rank 9–10 of 114 | published | pass |  |
| Renormalized basis reproduces Korea's published AUI, Apr 2026 | 3.92 | 3.921 | renormalized | pass |  |
| Korea's published AUI and rank, May 2026 | 3.78, rank 14 of 121 | 3.78, rank 14 of 121 | published | pass |  |
| Renormalized basis reproduces Korea's published AUI, May 2026 | 3.78 | 3.774 | renormalized | pass |  |
| Korea's AUI and rank, Aug 2025 (September 2025 report) | 3.73, rank 5 | 3.725, rank 5 of 115 | published | pass |  |
| Rule anthropic_2025 reproduces every published AUI, Aug 2025 | 115 values | largest absolute difference 0.0e+00 over 115 countries | anthropic_2025 | pass |  |
| Korea's AUI and rank, Nov 2025 (January 2026 appendix, Fig. 3) | 3.12, rank 7 of 116 | 3.123, rank 7 of 116 | anthropic_2025 | pass |  |
| India's share of global usage and rank, Nov 2025 (India brief) | 5.8%, rank 2 | 5.81%, rank 2 of 116 | published usage_pct | pass |  |
| Korea's AUI, Feb 2026 (Anthropic, 2026-05-26: 'more than 3.5 times') | above 3.5 | 3.692, rank 12 of 116 | renormalized | pass |  |
| Australia's share of global usage and rank, Feb 2026 (Australia brief) | 1.6%, rank 11 | 1.59%, rank 11 of 116 | published usage_pct | pass |  |
| Australia's AUI rank, Feb 2026 (Australia brief: 4.1, rank 7) | rank 7 | rank 7 of 116 | renormalized | pass | Published to one decimal; the basis is not pinned. Level 4.183 renormalized (truncates to 4.1, rounds to 4.2); 4.094 with usage over all geolocated conversations (rounds to 4.1). |
| Australia's state indices, Feb 2026 (optional; NSW 1.20, VIC 1.19, WA 0.68) | NSW 1.20, VIC 1.19, WA 0.68 | not run |  | not run | Optional target: needs ABS state population (ABS-ERP), not pinned yet. |
| Anthropic observed_exposure: occupations, zeros, maximum | 756; 411; 0.745 | 756; 411; 0.7451 |  | pass |  |

38 pass, 0 fail, 1 not run.

- Australia's AUI level: the brief gives 4.1, to one decimal, without its basis. The renormalized
  value, 4.183, gives 4.1 only if truncated; usage over all geolocated conversations gives 4.094,
  which rounds to 4.1. Neither basis is confirmed, so the check is on rank (PLAN 2.4). The rank
  is the same on both bases, which differ by a constant factor.
- Australia's state indices are an optional target: they need ABS population by state and age
  (ABS-ERP), which is not pinned yet.
- Phase 1 had reproduced these values with scratch scripts
  (`docs/discovery/01_source_verification.md` §1.1); committed code now checks them.

## Validation evidence

At the end of each phase, record the commands run and their results.

### Phase 2 — 2026-10-30

- `make check`: ruff clean; 216 passed, the data-marked tests included (run on the pinned files).
- `make build`: `data/interim/aei_long.parquet` with 2,709,773 rows (2025-09-15: 136,705;
  2026-01-15: 458,778; 2026-03-24: 477,717; 2026-06-26: 1,636,573) and
  `data/processed/regions.csv` (17 regions, unchanged).
- `make replicate`: 38 pass, 0 fail, 1 not run (log above).
- Clean clone of commit `f8d9d0c`: `make setup` (CPython 3.12.16) installed the hash-checked
  environment; `make build` downloaded and verified the nine pinned files (445.3 MB) and built
  the table, in 55 s in all; `make replicate` printed the same table; `make check`: ruff clean,
  216 passed. The Parquet file is byte-identical to the working tree's (SHA-256
  `9711b8e2d1c5…`), and `make build` left the committed `regions.csv` unchanged.
- Each fix commit was tested in its own state before it was committed: 196 passed at `f74e63d`,
  205 at `0ac0cdc`, 216 at `f8d9d0c`.
- No `.env` value, raw or URL-encoded, in any file of the Phase 2 commits.
- CI: run 40984151111 on commit `f8d9d0c` succeeded on ubuntu-latest and windows-latest
  (offline: 205 passed, the 11 data-marked tests skipped).

#### Independent review of Phase 2

Three reviewers (the adapters; the AUI and the replication checks; the region table and the
tests), each followed by an adversarial verifier, reported 14 findings. The verifiers confirmed
12, two of them the same issue, and refuted 2. In April 2026 the asserted rank range 9–10 of 114
already pins Korea's tie at 3.92 to one other country, so no Norway-specific assertion was added.
The employment-ministry codes are right once KOSIS's `ZONE2017A` prefix is removed; the prefix
is now documented. Fixed in `f74e63d`, `0ac0cdc` and `f8d9d0c`:

- Adapter: the August 2025 enriched file fills 28 countries that the release did not publish
  with zero usage; those 140 rows are dropped, so a missing row stays "not published".
  `geo_values` selects every whole-geography metric, task traits included, and raises on an
  empty selection. `load` returns a copy of the cached release. `build` validates the table and
  its key.
- AUI and replication: share ranks use the AUI country set, which excludes Reunion and countries
  below the floor. Each check is pass, fail or not run, and `make replicate` exits 1 only on a
  failure, so the optional state target no longer counts as a pass. The August 2025 rule check
  also compares the country sets. The Australia note gives both bases.
- Region table and tests: every code of every region is tested against an independent literal.
  `from_kosis` joins KOSIS rows by code and checks their labels. `regions_on` refuses KOSIS
  periods such as `202605`. `MERGED_CODES` names the merged region's aggregate codes. Offline
  tests now cover the Korean regional path, the check statuses and the exit code of `main()`.

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
