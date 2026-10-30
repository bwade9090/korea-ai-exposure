# Data

| Location | Contents | In git |
| --- | --- | --- |
| `manifest.json` | One pin per downloaded file: source ID, URL, path, SHA-256, bytes, retrieval time (UTC) | Yes |
| `raw/` | Downloads from public sources, written by `make fetch` | No |
| `manual/` | Files the owner downloads by hand, for example from portals that need a login | No |
| `interim/` | Intermediate tables written by `make build` | No |
| `processed/` | Small derived tables, each with source attribution | Yes |

## Pinning a new download

Register the source in `docs/DATA_SOURCES.md` first; the fetcher refuses unregistered source IDs.
Then download and pin the file:

```sh
.venv/Scripts/python -m korea_ai_exposure.fetch --add SOURCE-ID URL path/under/raw   # Windows
.venv/bin/python -m korea_ai_exposure.fetch --add SOURCE-ID URL path/under/raw       # Linux, macOS
```

Add `--user-agent-env BLS_USER_AGENT` for bls.gov files. Local paths use letters, digits, `.`,
`_` and `-` only, so that they work on both Windows and Linux.

## Fetching and upstream changes

- `make fetch` downloads every pinned file that is missing or corrupt and verifies its SHA-256 and
  size. Files that already verify are not downloaded again.
- A downloaded file that differs from its pin is refused; the local file and the pin stay as they
  were. Rerun with `--update` to accept it, and record why in `docs/PROJECT_STATUS.md`.
- `--update` acts only on files that are downloaded. To check files that already verify against
  upstream, add `--refresh` (with `--update` to accept the changes it finds).
- Empty responses, and HTML pages where a data file was expected (block pages, login pages,
  moved files), are refused.

## Rules

- Pin immutable URLs where the host supports them. For Hugging Face, use a commit hash in place of
  `main` (`.../resolve/<commit>/...`).
- Never put credentials in a pinned URL. The fetcher refuses URLs with credential parameters
  (`apiKey`, `serviceKey`, `token`, ...) or containing the value of any variable in `.env`, and
  error messages omit query strings. Keyed APIs (KOSIS) are pinned without the key: pass
  `--key-env KOSIS_KEY` with `--add`, and the fetcher adds the key at request time, follows no
  redirect to another host, and refuses a KOSIS error object.
- TLS verification uses the operating system's trust store and is never disabled. Redirects are
  followed only to HTTPS, and a custom User-Agent is sent only to the pinned host.
