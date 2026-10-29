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

Add `--user-agent-env BLS_USER_AGENT` for bls.gov files.

`make fetch` downloads every pinned file that is missing, verifies its SHA-256 and size, and refuses
a file that changed upstream; rerun with `--update` only when the change is intended, and record
why in `docs/PROJECT_STATUS.md`.

Rules:

- Pin immutable URLs where the host supports them. For Hugging Face, use a commit hash in place of
  `main` (`.../resolve/<commit>/...`).
- Never put credentials in a pinned URL. The fetcher rejects query parameters such as `apiKey`,
  `key`, and `token`.
- TLS verification uses the operating system's trust store and is never disabled.
