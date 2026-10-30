# Data

| Location | Contents | In git |
| --- | --- | --- |
| `manifest.json` | One pin per downloaded file: source ID, URL, path, SHA-256, bytes, retrieval time (UTC) | Yes |
| `raw/` | Pinned downloads: the small inputs below are committed; the AEI files are fetched by `make fetch` | Partly |
| `manual/` | Files the owner downloads by hand (portals that need a login) | No |
| `interim/` | Intermediate tables written by `make build` | No |
| `processed/` | Small derived tables, each with source attribution | Yes |

## Committed inputs

Stored unchanged, byte for byte as pinned (ADR 0007 amendment). Cite them as follows.

| Files in `raw/` | Source | Terms |
| --- | --- | --- |
| `kosis/` (8 tables) | KOSIS (kosis.kr), OpenAPI, retrieved 2026-10-30: 행정안전부 주민등록인구현황; 고용노동부 사업체노동력조사; 국가데이터처 지역별고용조사 and 지역소득. Table IDs are in the file names | Free use, reuse and redistribution with citation (producer, survey, period, access date, table); the resident registration statistics are provided for viewing and reference (MOIS note) |
| `bls/` (5 files) | U.S. Bureau of Labor Statistics: OEWS May 2025 national and state files, the 2018 SOC structure, the SOC 2010–2018 and ISCO-08–SOC 2010 crosswalks | Public domain; cite BLS |
| `ilo/` (1 file) | Gmyrek, P., et al. (2025), ILO Working Paper 140, companion repository `pgmyrek/2025_GenAI_scores_ISCO08` at commit `ce5fc25c` | CC BY 4.0 |
| `kssc/` (1 file) | Statistics Korea, KSCO-8 to ISCO-08 correspondence table (통계분류포털; posted 3 November 2025, re-posted 27 January 2026) | KOGL Type 3: attribution, no modification |

## Fetching and pinning

- `make fetch` downloads every pinned file that is missing or corrupt and verifies its SHA-256;
  files that verify are not downloaded again. A file that differs from its pin is refused unless
  `--update` is given; record why in `docs/PROJECT_STATUS.md`.
- To pin a new file, register its source in `docs/DATA_SOURCES.md`, then run
  `python -m korea_ai_exposure.fetch --add SOURCE-ID URL path/under/raw` with the venv's Python.
  Add `--user-agent-env BLS_USER_AGENT` for bls.gov, and `--key-env KOSIS_KEY` for the KOSIS
  OpenAPI: the key is added at request time and never pinned.
- Pin immutable URLs (for Hugging Face, a commit hash, not `main`). The fetcher refuses URLs that
  carry credentials, and TLS verification uses the operating system's trust store.
