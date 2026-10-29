"""Download registered public files and pin them in ``data/manifest.json``.

Each manifest entry records which registered source a file belongs to (``source``, an ID in
``docs/DATA_SOURCES.md``), where it comes from (``url``), where it is stored under ``data/raw/``
(``path``), what it must contain (``sha256``, ``bytes``), and when the pin was made
(``retrieved_at``, UTC).

Fetching is idempotent: a file already present with its pinned checksum is not downloaded again.
A download whose checksum differs from the pin is refused, leaving the local file and the pin
unchanged, unless ``--update`` is given. Downloads stream into a temporary file beside the
destination and are moved into place only once accepted, so a failed or refused download never
leaves a partial file.

TLS verification uses the operating system's trust store (``ssl.create_default_context``), so it
also works behind a TLS-inspecting proxy whose root certificate is installed in the OS.

Usage::

    python -m korea_ai_exposure.fetch                     # fetch and verify every pinned file
    python -m korea_ai_exposure.fetch --source AEI-LMI    # only the files of one source
    python -m korea_ai_exposure.fetch --update            # accept and re-pin changed files
    python -m korea_ai_exposure.fetch --add SOURCE URL PATH [--user-agent-env BLS_USER_AGENT]
"""

import argparse
import hashlib
import http.client
import json
import os
import re
import ssl
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Collection, Iterable, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Self

from dotenv import load_dotenv

from korea_ai_exposure import paths

SCHEMA_VERSION = 1
DEFAULT_USER_AGENT = "korea-ai-exposure/0.1 (public-data research; python-urllib)"
CHUNK_BYTES = 1 << 20
TIMEOUT_SECONDS = 120
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
CREDENTIAL_PARAMS = frozenset({"access_token", "api_key", "apikey", "key", "secret", "token"})

_FIELDS = ("path", "source", "url", "sha256", "bytes", "retrieved_at")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_SOURCE_ID = re.compile(r"[A-Z]+(?:-[A-Z0-9]+)+")
_TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

Log = Callable[[str], None]


class FetchError(RuntimeError):
    """A download failed, or a file or manifest entry is not acceptable."""


@dataclass(frozen=True)
class Pin:
    """One pinned file: ``data/raw/<path>`` must have this SHA-256 and size."""

    path: str
    source: str
    url: str
    sha256: str
    size: int
    retrieved_at: str
    user_agent_env: str | None = None

    @classmethod
    def from_record(cls, record: object) -> Self:
        if not isinstance(record, dict):
            raise FetchError(f"manifest entry is not an object: {record!r}")
        missing = [field for field in _FIELDS if field not in record]
        if missing:
            raise FetchError(f"manifest entry {record.get('path')!r} lacks {', '.join(missing)}")
        pin = cls(
            path=record["path"],
            source=record["source"],
            url=record["url"],
            sha256=record["sha256"],
            size=record["bytes"],
            retrieved_at=record["retrieved_at"],
            user_agent_env=record.get("user_agent_env"),
        )
        pin.validate()
        return pin

    def to_record(self) -> dict[str, str | int]:
        record: dict[str, str | int] = {
            "path": self.path,
            "source": self.source,
            "url": self.url,
            "sha256": self.sha256,
            "bytes": self.size,
            "retrieved_at": self.retrieved_at,
        }
        if self.user_agent_env:
            record["user_agent_env"] = self.user_agent_env
        return record

    def validate(self) -> None:
        check_path(self.path)
        check_url(self.url)
        if not isinstance(self.source, str) or not _SOURCE_ID.fullmatch(self.source):
            raise FetchError(f"{self.path}: malformed source ID {self.source!r}")
        if not isinstance(self.sha256, str) or not _SHA256.fullmatch(self.sha256):
            raise FetchError(f"{self.path}: sha256 must be 64 lowercase hexadecimal characters")
        if isinstance(self.size, bool) or not isinstance(self.size, int) or self.size < 0:
            raise FetchError(f"{self.path}: bytes must be a non-negative integer")
        if not isinstance(self.retrieved_at, str) or not _TIMESTAMP.fullmatch(self.retrieved_at):
            raise FetchError(f"{self.path}: retrieved_at must look like 2026-01-31T12:00:00Z")


def check_path(rel: object) -> PurePosixPath:
    """Accept only a canonical relative POSIX path, which therefore stays inside ``data/raw/``."""
    if not isinstance(rel, str):
        raise FetchError(f"path must be a string: {rel!r}")
    pure = PurePosixPath(rel)
    if (
        not pure.parts
        or "\\" in rel
        or ":" in rel
        or pure.is_absolute()
        or ".." in pure.parts
        or rel != pure.as_posix()
    ):
        raise FetchError(f"unsafe or non-canonical path: {rel!r}")
    return pure


def check_url(url: object) -> None:
    """Accept HTTPS URLs (plain HTTP only for loopback hosts) that carry no credentials."""
    if not isinstance(url, str):
        raise FetchError(f"url must be a string: {url!r}")
    parts = urllib.parse.urlsplit(url)
    if parts.username or parts.password:
        raise FetchError("URL carries credentials; never pin credentials")
    names = {name.lower() for name, _ in urllib.parse.parse_qsl(parts.query, True)}
    if names & CREDENTIAL_PARAMS:
        raise FetchError("URL carries a credential in its query string; never pin credentials")
    if parts.scheme == "https" and parts.hostname:
        return
    if parts.scheme == "http" and parts.hostname in LOOPBACK_HOSTS:
        return
    raise FetchError(f"not an HTTPS URL: {url!r}")


def registered_sources(registry: Path) -> frozenset[str]:
    """Source IDs in the first column of the tables in ``docs/DATA_SOURCES.md``."""
    ids = set()
    for line in registry.read_text(encoding="utf-8").splitlines():
        cells = line.split("|")
        if line.startswith("|") and len(cells) > 2 and _SOURCE_ID.fullmatch(cells[1].strip()):
            ids.add(cells[1].strip())
    return frozenset(ids)


def load_manifest(manifest: Path) -> list[Pin]:
    """Read and validate the manifest. A missing file counts as an empty manifest."""
    if not manifest.exists():
        return []
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FetchError(f"{manifest}: invalid JSON ({exc})") from None
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise FetchError(f"{manifest}: expected an object with schema_version {SCHEMA_VERSION}")
    if not isinstance(data.get("files"), list):
        raise FetchError(f"{manifest}: 'files' must be a list")
    pins = [Pin.from_record(record) for record in data["files"]]
    seen: set[str] = set()
    for pin in pins:
        if pin.path in seen:
            raise FetchError(f"{manifest}: duplicate path {pin.path}")
        seen.add(pin.path)
    return pins


def dump_manifest(pins: Iterable[Pin]) -> str:
    """Canonical manifest text: entries sorted by path, two-space indent, final newline."""
    records = [pin.to_record() for pin in sorted(pins, key=lambda pin: pin.path)]
    document = {"schema_version": SCHEMA_VERSION, "files": records}
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def save_manifest(manifest: Path, pins: Iterable[Pin]) -> None:
    text = dump_manifest(pins)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(dir=manifest.parent, prefix=f".{manifest.name}.", suffix=".tmp")
    with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as out:
        out.write(text)
    os.replace(name, manifest)


def sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(
    pins: Sequence[Pin],
    raw_dir: Path,
    *,
    update: bool = False,
    now: Callable[[], str] = utc_now,
    log: Log = print,
) -> tuple[list[Pin], list[str]]:
    """Make each pinned file present and verified. Return the pins, re-pinned where accepted,
    and one message per file that failed."""
    result: list[Pin] = []
    errors: list[str] = []
    for pin in pins:
        try:
            result.append(_fetch_one(pin, raw_dir, update=update, now=now, log=log))
        except FetchError as exc:
            errors.append(str(exc))
            result.append(pin)
    return result, errors


def add(
    pins: Sequence[Pin],
    *,
    source: str,
    url: str,
    path: str,
    raw_dir: Path,
    registered: Collection[str],
    user_agent_env: str | None = None,
    update: bool = False,
    now: Callable[[], str] = utc_now,
    log: Log = print,
) -> list[Pin]:
    """Download a new file and return the pins with its entry added (or replaced, with
    ``update``)."""
    if source not in registered:
        raise FetchError(f"source {source!r} is not registered in docs/DATA_SOURCES.md")
    check_url(url)
    dest = _destination(raw_dir, path)
    by_path = {pin.path: pin for pin in pins}
    if path in by_path and not update:
        raise FetchError(f"{path} is already pinned; pass --update to re-pin it")
    tmp, sha256, size = _download(url, dest, _user_agent(user_agent_env))
    os.replace(tmp, dest)
    by_path[path] = Pin(path, source, url, sha256, size, now(), user_agent_env)
    log(f"pinned    {path} ({size:,} bytes, sha256 {sha256[:12]}...)")
    return list(by_path.values())


def _fetch_one(pin: Pin, raw_dir: Path, *, update: bool, now: Callable[[], str], log: Log) -> Pin:
    dest = _destination(raw_dir, pin.path)
    if _matches(dest, pin):
        log(f"verified  {pin.path}")
        return pin
    tmp, sha256, size = _download(pin.url, dest, _user_agent(pin.user_agent_env))
    if (sha256, size) == (pin.sha256, pin.size):
        os.replace(tmp, dest)
        log(f"fetched   {pin.path} ({size:,} bytes)")
        return pin
    if update:
        os.replace(tmp, dest)
        log(f"re-pinned {pin.path} (sha256 {pin.sha256[:12]}... -> {sha256[:12]}...)")
        return replace(pin, sha256=sha256, size=size, retrieved_at=now())
    tmp.unlink()
    raise FetchError(
        f"{pin.path}: the upstream file differs from its pin (pinned {pin.size:,} bytes, sha256 "
        f"{pin.sha256[:12]}...; downloaded {size:,} bytes, sha256 {sha256[:12]}...). The local "
        "file and the pin are unchanged; rerun with --update to accept the new file."
    )


def _destination(raw_dir: Path, rel: str) -> Path:
    check_path(rel)
    dest = raw_dir / rel
    if not dest.resolve().is_relative_to(raw_dir.resolve()):
        raise FetchError(f"{rel!r} resolves outside {raw_dir}")
    return dest


def _matches(dest: Path, pin: Pin) -> bool:
    return dest.is_file() and dest.stat().st_size == pin.size and sha256_file(dest) == pin.sha256


def _user_agent(env_var: str | None) -> str:
    if not env_var:
        return DEFAULT_USER_AGENT
    value = os.environ.get(env_var, "").strip()
    if not value:
        raise FetchError(f"{env_var} is not set; add it to .env (see .env.example)")
    return value


def _download(url: str, dest: Path, user_agent: str) -> tuple[Path, str, int]:
    """Stream ``url`` into a temporary file beside ``dest``. Return (temporary file, SHA-256,
    bytes); the caller moves the file into place or deletes it."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(dir=dest.parent, prefix=f".{dest.name}.", suffix=".part")
    tmp = Path(name)
    digest = hashlib.sha256()
    size = 0
    done = False
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    context = ssl.create_default_context()
    try:
        with (
            os.fdopen(handle, "wb") as out,
            urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS, context=context) as response,
        ):
            announced = response.headers.get("Content-Length")
            while chunk := response.read(CHUNK_BYTES):
                out.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        if announced is not None and announced.isdigit() and int(announced) != size:
            raise FetchError(f"{url}: received {size:,} bytes; the server announced {announced}")
        done = True
    except urllib.error.HTTPError as exc:
        exc.close()
        raise FetchError(f"{url}: HTTP {exc.code} {exc.reason}") from None
    except (OSError, http.client.HTTPException) as exc:
        raise FetchError(f"{url}: {exc}") from None
    finally:
        if not done:
            tmp.unlink(missing_ok=True)
    return tmp, digest.hexdigest(), size


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m korea_ai_exposure.fetch",
        description="Download registered public files and verify them against data/manifest.json.",
    )
    parser.add_argument(
        "--add",
        nargs=3,
        metavar=("SOURCE", "URL", "PATH"),
        help="download URL to data/raw/PATH and pin it under the registered source ID SOURCE",
    )
    parser.add_argument(
        "--user-agent-env",
        metavar="VAR",
        help="with --add: environment variable holding the User-Agent, e.g. BLS_USER_AGENT",
    )
    parser.add_argument(
        "--source",
        action="append",
        metavar="ID",
        help="fetch only the files of this source ID (repeatable)",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="accept upstream files whose checksum changed, and re-pin them",
    )
    parser.add_argument("--manifest", type=Path, default=paths.MANIFEST, help=argparse.SUPPRESS)
    parser.add_argument("--raw-dir", type=Path, default=paths.RAW, help=argparse.SUPPRESS)
    parser.add_argument("--env-file", type=Path, default=paths.ENV_FILE, help=argparse.SUPPRESS)
    parser.add_argument(
        "--registry", type=Path, default=paths.SOURCES_REGISTRY, help=argparse.SUPPRESS
    )
    args = parser.parse_args(argv)
    if args.user_agent_env and not args.add:
        parser.error("--user-agent-env requires --add")
    if args.add and args.source:
        parser.error("--source cannot be combined with --add")
    load_dotenv(args.env_file)

    errors: list[str] = []
    try:
        pins = load_manifest(args.manifest)
        if args.add:
            source, url, path = args.add
            pins = add(
                pins,
                source=source,
                url=url,
                path=path,
                raw_dir=args.raw_dir,
                registered=registered_sources(args.registry),
                user_agent_env=args.user_agent_env,
                update=args.update,
            )
            save_manifest(args.manifest, pins)
            return 0
        selected = [pin for pin in pins if not args.source or pin.source in args.source]
        if args.source and not selected:
            raise FetchError(f"no files registered for {', '.join(args.source)}")
        if not selected:
            print(f"No files registered in {args.manifest.name}; nothing to fetch.")
            return 0
        fetched, errors = fetch(selected, args.raw_dir, update=args.update)
        merged = {pin.path: pin for pin in pins} | {pin.path: pin for pin in fetched}
        if list(merged.values()) != pins:
            save_manifest(args.manifest, merged.values())
    except FetchError as exc:
        errors.append(str(exc))
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
