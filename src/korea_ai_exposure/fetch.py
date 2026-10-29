"""Download registered public files and pin them in ``data/manifest.json``.

Each manifest entry records which registered source a file belongs to (``source``, an ID in
``docs/DATA_SOURCES.md``), where it comes from (``url``), where it is stored under ``data/raw/``
(``path``), what it must contain (``sha256``, ``bytes``), and when the pin was made
(``retrieved_at``, UTC).

Fetching is idempotent: a file already present with its pinned checksum is not downloaded again.
A download whose checksum differs from the pin is refused, leaving the local file and the pin
unchanged, unless ``--update`` is given. ``--update`` acts only on files that are downloaded, that
is, files that are missing or corrupt locally; add ``--refresh`` to re-download verified files as
well and so detect upstream revisions. Downloads stream into a temporary file beside the
destination and are moved into place only once accepted, so a failed or refused download never
leaves a partial file. Empty responses, and HTML pages where data were expected (block pages,
landing pages of moved files), are refused.

Safeguards: TLS verification uses the operating system's trust store
(``ssl.create_default_context``), which also works behind TLS-inspecting proxies whose root
certificate is installed in the OS. Redirects are followed only to HTTPS. A custom User-Agent
(for example ``BLS_USER_AGENT``, which carries contact details) is sent only to the pinned host.
URLs that carry credentials, including the value of any variable in ``.env``, are refused, and
error messages show URLs without their query strings.

Usage::

    python -m korea_ai_exposure.fetch                     # fetch and verify every pinned file
    python -m korea_ai_exposure.fetch --source AEI-LMI    # only the files of one source
    python -m korea_ai_exposure.fetch --refresh           # also re-check verified files upstream
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

from dotenv import dotenv_values, load_dotenv

from korea_ai_exposure import paths

SCHEMA_VERSION = 1
DEFAULT_USER_AGENT = "korea-ai-exposure/0.1 (public-data research; python-urllib)"
CHUNK_BYTES = 1 << 20
TIMEOUT_SECONDS = 120
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
CREDENTIAL_PARAMS = frozenset(
    {
        "access_key",
        "access_token",
        "api-key",
        "api_key",
        "apikey",
        "authkey",
        "client_secret",
        "crtfc_key",
        "key",
        "password",
        "registrationkey",
        "secret",
        "servicekey",
        "sig",
        "signature",
        "token",
        "x-amz-credential",
        "x-amz-signature",
    }
)
MIN_SECRET_LENGTH = 8
HTML_SUFFIXES = frozenset({".htm", ".html"})

_FIELDS = ("path", "source", "url", "sha256", "bytes", "retrieved_at")
_OPTIONAL_FIELDS = ("user_agent_env",)
_SHA256 = re.compile(r"[0-9a-f]{64}")
_SOURCE_ID = re.compile(r"[A-Z]+(?:-[A-Z0-9]+)+")
_TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_USER_AGENT_ENV = re.compile(r"[A-Z][A-Z0-9_]*_USER_AGENT")
_PATH_PART = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_WINDOWS_DEVICE = re.compile(r"(?i)(?:con|prn|aux|nul|com[0-9]|lpt[0-9])")

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
    def from_record(cls, record: object, secrets: Collection[str] = ()) -> Self:
        if not isinstance(record, dict):
            raise FetchError(f"manifest entry is not an object: {record!r}")
        missing = [field for field in _FIELDS if field not in record]
        if missing:
            raise FetchError(f"manifest entry {record.get('path')!r} lacks {', '.join(missing)}")
        unknown = sorted(set(record) - set(_FIELDS) - set(_OPTIONAL_FIELDS))
        if unknown:
            raise FetchError(f"manifest entry {record['path']!r} has unknown {', '.join(unknown)}")
        pin = cls(
            path=record["path"],
            source=record["source"],
            url=record["url"],
            sha256=record["sha256"],
            size=record["bytes"],
            retrieved_at=record["retrieved_at"],
            user_agent_env=record.get("user_agent_env"),
        )
        pin.validate(secrets)
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

    def validate(self, secrets: Collection[str] = ()) -> None:
        check_path(self.path)
        check_url(self.url, secrets)
        check_user_agent_env(self.user_agent_env)
        if not isinstance(self.source, str) or not _SOURCE_ID.fullmatch(self.source):
            raise FetchError(f"{self.path}: malformed source ID {self.source!r}")
        if not isinstance(self.sha256, str) or not _SHA256.fullmatch(self.sha256):
            raise FetchError(f"{self.path}: sha256 must be 64 lowercase hexadecimal characters")
        if isinstance(self.size, bool) or not isinstance(self.size, int) or self.size < 0:
            raise FetchError(f"{self.path}: bytes must be a non-negative integer")
        if not isinstance(self.retrieved_at, str) or not _TIMESTAMP.fullmatch(self.retrieved_at):
            raise FetchError(f"{self.path}: retrieved_at must look like 2026-01-31T12:00:00Z")


@dataclass(frozen=True)
class Download:
    """A completed download waiting in a temporary file beside its destination."""

    tmp: Path
    sha256: str
    size: int
    host: str


def check_path(rel: object) -> PurePosixPath:
    """Accept only a relative path whose components are portable between Linux and Windows:
    letters, digits, '.', '_' and '-', starting with a letter or digit, not ending in '.', and
    not a Windows device name. Such a path cannot leave ``data/raw/``."""
    if not isinstance(rel, str) or not all(_portable(part) for part in rel.split("/")):
        raise FetchError(f"unsafe or non-portable path: {rel!r}")
    return PurePosixPath(rel)


def check_url(url: object, secrets: Collection[str] = ()) -> None:
    """Accept an HTTPS URL (plain HTTP only for loopback hosts) that carries no credentials: no
    user information, no credential-like query or fragment parameter, and none of ``secrets``."""
    if not isinstance(url, str):
        raise FetchError("url must be a string")
    try:
        parts = urllib.parse.urlsplit(url)
        host = parts.hostname
    except ValueError:
        raise FetchError("malformed URL") from None
    if parts.username or parts.password:
        raise FetchError("URL carries user credentials; never pin credentials")
    names = {
        name.lower()
        for component in (parts.query, parts.fragment)
        for name, _ in urllib.parse.parse_qsl(component, keep_blank_values=True)
    }
    if names & CREDENTIAL_PARAMS:
        raise FetchError("URL carries a credential parameter; never pin credentials")
    decoded = urllib.parse.unquote(url)
    if any(secret in url or secret in decoded for secret in secrets):
        raise FetchError("URL contains the value of a variable in .env; never pin credentials")
    if not _allowed_target(parts.scheme, host):
        raise FetchError(f"not an HTTPS URL: {redact(url)}")


def check_user_agent_env(name: object) -> None:
    """A pin may name only a variable that holds a User-Agent, such as ``BLS_USER_AGENT``, so a
    manifest entry cannot send another secret from the environment to a server."""
    if name is not None and (not isinstance(name, str) or not _USER_AGENT_ENV.fullmatch(name)):
        raise FetchError(f"user_agent_env must name a *_USER_AGENT variable, not {name!r}")


def redact(url: str) -> str:
    """The URL without user information, query, or fragment, for messages."""
    try:
        parts = urllib.parse.urlsplit(url)
        netloc = parts.hostname or ""
        if ":" in netloc:
            netloc = f"[{netloc}]"
        if parts.port:
            netloc = f"{netloc}:{parts.port}"
    except ValueError:
        return "<malformed URL>"
    return urllib.parse.urlunsplit((parts.scheme, netloc, parts.path, "", ""))


def env_secrets(env_file: Path) -> frozenset[str]:
    """Values in ``env_file`` long enough to be credentials; they must never appear in a URL."""
    values = dotenv_values(env_file) if env_file.is_file() else {}
    return frozenset(v for v in values.values() if v and len(v) >= MIN_SECRET_LENGTH)


def registered_sources(registry: Path) -> frozenset[str]:
    """Source IDs in the first column of the tables in ``docs/DATA_SOURCES.md``. Tables under the
    'Prior art' heading list publications, not data sources, and are not counted."""
    ids = set()
    for line in registry.read_text(encoding="utf-8").splitlines():
        if line.lower().startswith("## prior art"):
            break
        cells = line.split("|")
        if line.startswith("|") and len(cells) > 2 and _SOURCE_ID.fullmatch(cells[1].strip()):
            ids.add(cells[1].strip())
    return frozenset(ids)


def load_manifest(manifest: Path, secrets: Collection[str] = ()) -> list[Pin]:
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
    pins = [Pin.from_record(record, secrets) for record in data["files"]]
    seen: set[str] = set()
    for pin in pins:
        if pin.path.casefold() in seen:
            raise FetchError(f"{manifest}: duplicate path {pin.path} (case-insensitive)")
        seen.add(pin.path.casefold())
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


def tls_context() -> ssl.SSLContext:
    """Certificate and hostname verification against the operating system's trust store."""
    return ssl.create_default_context()


def fetch(
    pins: Sequence[Pin],
    raw_dir: Path,
    *,
    update: bool = False,
    refresh: bool = False,
    now: Callable[[], str] = utc_now,
    log: Log = print,
) -> tuple[list[Pin], list[str]]:
    """Make each pinned file present and verified. Return the pins, re-pinned where accepted,
    and one message per file that failed; a failure does not stop the other files."""
    result: list[Pin] = []
    errors: list[str] = []
    for pin in pins:
        try:
            result.append(
                _fetch_one(pin, raw_dir, update=update, refresh=refresh, now=now, log=log)
            )
        except (FetchError, OSError) as exc:
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
    secrets: Collection[str] = (),
    now: Callable[[], str] = utc_now,
    log: Log = print,
) -> list[Pin]:
    """Download a new file and return the pins with its entry added (or replaced, with
    ``update``). Everything is checked before the first request is made."""
    if source not in registered:
        raise FetchError(f"source {source!r} is not registered in docs/DATA_SOURCES.md")
    check_url(url, secrets)
    dest = _destination(raw_dir, path)
    by_path = {pin.path.casefold(): pin for pin in pins}
    previous = by_path.get(path.casefold())
    if previous and not update:
        raise FetchError(f"{previous.path} is already pinned; pass --update to re-pin it")
    if user_agent_env is None and previous:
        user_agent_env = previous.user_agent_env
    check_user_agent_env(user_agent_env)
    got = _download(url, dest, _user_agent(user_agent_env))
    _place(got.tmp, dest)
    by_path[path.casefold()] = Pin(path, source, url, got.sha256, got.size, now(), user_agent_env)
    log(f"pinned    {path} ({got.size:,} bytes, sha256 {got.sha256[:12]}..., from {got.host})")
    return list(by_path.values())


def _fetch_one(
    pin: Pin, raw_dir: Path, *, update: bool, refresh: bool, now: Callable[[], str], log: Log
) -> Pin:
    dest = _destination(raw_dir, pin.path)
    verified = _matches(dest, pin)
    if verified and not refresh:
        log(f"verified  {pin.path}")
        return pin
    got = _download(pin.url, dest, _user_agent(pin.user_agent_env))
    if (got.sha256, got.size) == (pin.sha256, pin.size):
        if verified:
            got.tmp.unlink()
            log(f"unchanged {pin.path}")
        else:
            _place(got.tmp, dest)
            log(f"fetched   {pin.path} ({got.size:,} bytes)")
        return pin
    if update:
        _place(got.tmp, dest)
        log(f"re-pinned {pin.path} (sha256 {pin.sha256[:12]}... -> {got.sha256[:12]}...)")
        return replace(pin, sha256=got.sha256, size=got.size, retrieved_at=now())
    got.tmp.unlink()
    raise FetchError(
        f"{pin.path}: the upstream file differs from its pin (pinned {pin.size:,} bytes, sha256 "
        f"{pin.sha256[:12]}...; downloaded {got.size:,} bytes, sha256 {got.sha256[:12]}...). The "
        "local file and the pin are unchanged; rerun with --update to accept the new file."
    )


def _portable(part: str) -> bool:
    return (
        bool(_PATH_PART.fullmatch(part))
        and not part.endswith(".")
        and not _WINDOWS_DEVICE.fullmatch(part.split(".")[0])
    )


def _allowed_target(scheme: str, host: str | None) -> bool:
    return bool(host) and (scheme == "https" or (scheme == "http" and host in LOOPBACK_HOSTS))


def _destination(raw_dir: Path, rel: str) -> Path:
    check_path(rel)
    dest = raw_dir / rel
    if not dest.resolve().is_relative_to(raw_dir.resolve()):
        raise FetchError(f"{rel!r} resolves outside {raw_dir}")
    return dest


def _matches(dest: Path, pin: Pin) -> bool:
    return dest.is_file() and dest.stat().st_size == pin.size and sha256_file(dest) == pin.sha256


def _place(tmp: Path, dest: Path) -> None:
    try:
        os.replace(tmp, dest)
    except OSError as exc:
        tmp.unlink(missing_ok=True)
        raise FetchError(
            f"cannot write {dest}: {exc.strerror or exc}; close any program using it and rerun"
        ) from None


def _user_agent(env_var: str | None) -> str:
    if not env_var:
        return DEFAULT_USER_AGENT
    value = os.environ.get(env_var, "").strip()
    if not value:
        raise FetchError(f"{env_var} is not set; add it to .env (see .env.example)")
    return value


def _looks_like_html(head: bytes) -> bool:
    start = head.removeprefix(b"\xef\xbb\xbf").lstrip().lower()
    return start.startswith((b"<!doctype html", b"<html"))


class _StrictRedirect(urllib.request.HTTPRedirectHandler):
    """Follow redirects only to HTTPS (plain HTTP only between loopback hosts), and send a custom
    User-Agent only to the pinned host."""

    def __init__(self, origin_host: str | None) -> None:
        super().__init__()
        self.origin_host = origin_host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urlsplit(newurl)
        if not _allowed_target(target.scheme, target.hostname):
            raise urllib.error.HTTPError(
                req.full_url,
                code,
                f"refused redirect to {target.scheme}://{target.hostname}",
                headers,
                fp,
            )
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and target.hostname != self.origin_host:
            new.remove_header("User-agent")
            new.add_header("User-Agent", DEFAULT_USER_AGENT)
        return new


def _download(url: str, dest: Path, user_agent: str) -> Download:
    """Stream ``url`` into a temporary file beside ``dest``; the caller moves it into place or
    deletes it."""
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=tls_context()),
        _StrictRedirect(urllib.parse.urlsplit(url).hostname),
    )
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    tmp: Path | None = None
    done = False
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        handle, name = tempfile.mkstemp(dir=dest.parent, prefix=f".{dest.name}.", suffix=".part")
        tmp = Path(name)
        digest = hashlib.sha256()
        size = 0
        head = b""
        with os.fdopen(handle, "wb") as out, opener.open(request, timeout=TIMEOUT_SECONDS) as resp:
            host = urllib.parse.urlsplit(resp.geturl()).hostname or ""
            expected = _expected_length(resp.headers)
            while chunk := resp.read(CHUNK_BYTES):
                if len(head) < 512:
                    head += chunk[: 512 - len(head)]
                out.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        if expected is not None and expected != size:
            raise FetchError(
                f"{redact(url)}: received {size:,} bytes; the server announced {expected:,}"
            )
        if size == 0:
            raise FetchError(f"{redact(url)}: the response is empty")
        if _looks_like_html(head) and dest.suffix.lower() not in HTML_SUFFIXES:
            raise FetchError(
                f"{redact(url)}: the response is an HTML page, not the expected file (a block "
                "page, a login page, or a moved file?)"
            )
        done = True
    except urllib.error.HTTPError as exc:
        exc.close()
        raise FetchError(f"{redact(url)}: HTTP {exc.code} {exc.reason}") from None
    except (OSError, http.client.HTTPException) as exc:
        raise FetchError(f"{redact(url)}: {exc}") from None
    finally:
        if not done and tmp is not None:
            tmp.unlink(missing_ok=True)
    return Download(tmp, digest.hexdigest(), size, host)


def _expected_length(headers: http.client.HTTPMessage) -> int | None:
    if "chunked" in headers.get("Transfer-Encoding", "").lower():
        return None
    announced = headers.get("Content-Length")
    if announced and announced.isascii() and announced.isdigit():
        return int(announced)
    return None


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
        "--refresh",
        action="store_true",
        help="re-download files that already verify, to detect upstream revisions",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="accept downloaded files whose checksum changed, and re-pin them; it acts only on "
        "files that are downloaded (missing or corrupt ones, or all with --refresh)",
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
    if args.add and (args.source or args.refresh):
        parser.error("--source and --refresh cannot be combined with --add")
    load_dotenv(args.env_file)

    errors: list[str] = []
    try:
        secrets = env_secrets(args.env_file)
        pins = load_manifest(args.manifest, secrets)
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
                secrets=secrets,
            )
            save_manifest(args.manifest, pins)
            return 0
        selected = [pin for pin in pins if not args.source or pin.source in args.source]
        if args.source and not selected:
            raise FetchError(f"no files registered for {', '.join(args.source)}")
        if not selected:
            print(f"No files registered in {args.manifest.name}; nothing to fetch.")
            return 0
        fetched, errors = fetch(selected, args.raw_dir, update=args.update, refresh=args.refresh)
        merged = {pin.path: pin for pin in pins} | {pin.path: pin for pin in fetched}
        if list(merged.values()) != pins:
            save_manifest(args.manifest, merged.values())
    except (FetchError, OSError) as exc:
        errors.append(str(exc))
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
