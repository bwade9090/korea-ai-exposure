# Project status

Last updated: 2026-10-29

## Current state

- Phase: 0 — bootstrap, complete locally. Phase 1 — source verification spike, in progress.
- Plan: `docs/PLAN.md` approved by the owner on 2026-10-29.
- Repository: GitHub `origin` (`bwade9090/korea-ai-exposure`) is public by the owner's decision of
  2026-10-29 (ADR 0002 amendment). Every push publishes; the hard stops apply to every commit.

## Next action

Phase 1 (`docs/PLAN.md` §8), ending at Checkpoint A.

## Checkpoints

| Checkpoint | Scope | Status | Date | Decision |
| --- | --- | --- | --- | --- |
| Plan | Approve `docs/PLAN.md` | Approved | 2026-10-29 | Owner, in session: approve the plan, start with Phase 0, report Phase 1 results at Checkpoint A |
| Visibility | Repository public or private (ADR 0002) | Decided | 2026-10-29 | Owner: keep the repository public |
| A | Sources, regional occupation tier, denominators, peer sets | Pending | | |
| B | Regional measurement validity; headline denominator | Pending | | |
| C | Publication | Pending | | |

## Owner actions

- [x] Approve or amend `docs/PLAN.md` (2026-10-29)
- [x] GitHub remote: `origin` exists
- [x] Repository visibility: keep public (2026-10-29; ADR 0002 amendment)
- [ ] `.env`: `BLS_USER_AGENT` is set. The KOSIS key is stored as `KOSIS_KEY`; the docs and
      `.env.example` use `KOSIS_API_KEY`. Rename it, or code will accept both names.
- [ ] Install python.org CPython 3.12 from your own terminal (for example
      `winget install Python.Python.3.12`), then rebuild the environment with `make setup`. The
      current `.venv` was built inside the Claude desktop app from a uv-managed Python that lives
      in the app's private storage, so it may not run from an ordinary terminal.
- [ ] Optional: put GNU Make on PATH. Make 4.4.1 is already installed with Rtools
      (`C:\rtools45\usr\bin\make.exe`); it works from Git Bash.
- [ ] Tier T2 only: MDIS microdata into `data/manual/`
- [ ] ADR 0002 review before any public release

## Blockers

None.

## Replication log

Empty until Phase 2.

## Validation evidence

At the end of each phase, record the commands run and their results.

### Phase 0 — 2026-10-29

- Interpreter: CPython 3.12.16 (uv-managed build, Windows x86-64). Pinned environment in
  `requirements.txt` (pip-tools 7.6.2, with hashes): pandas 3.1.0, numpy 2.5.4, pyarrow 26.0.0,
  matplotlib 3.11.2, openpyxl 3.1.5, xlrd 2.0.2, python-dotenv 1.2.4, pytest 9.2.0, ruff 0.17.3.
- GNU Make is not installed on the development machine, so the recipe commands were run directly
  in Git Bash, on a fresh copy of the tracked files:
  - `make setup`: `python -m venv .venv`; `pip install --require-hashes -r requirements.txt`;
    `pip install --no-deps --no-build-isolation -e .` — succeeded.
  - `make check`: `ruff check .` — all checks passed; `ruff format --check .` — all files
    formatted; `pytest` — 39 passed.
  - `make fetch` with the empty manifest: "No files registered in manifest.json; nothing to
    fetch.", exit code 0, manifest unchanged.
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
no-op; `make all` — stops at the `build` placeholder with exit code 2, as intended.
