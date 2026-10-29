"""Offline tests for the checksummed fetch helper, run against a local HTTP server."""

import hashlib
import http.server
import json
import threading
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from korea_ai_exposure import fetch, paths

NOW = "2026-01-01T00:00:00Z"
LATER = "2026-02-01T00:00:00Z"
SOURCE = "TEST-SRC"
REGISTERED = frozenset({SOURCE})


@dataclass
class FakeServer:
    url: str
    files: dict[str, bytes] = field(default_factory=dict)
    requests: list[tuple[str, str | None]] = field(default_factory=list)


@pytest.fixture
def server():
    state = FakeServer(url="")

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            state.requests.append((self.path, self.headers.get("User-Agent")))
            body = state.files.get(self.path)
            if body is None:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    state.url = f"http://127.0.0.1:{httpd.server_address[1]}"
    yield state
    httpd.shutdown()
    httpd.server_close()
    thread.join()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pin_one(server: FakeServer, raw: Path, body: bytes = b"a,b\n1,2\n") -> list[fetch.Pin]:
    server.files["/table.csv"] = body
    return fetch.add(
        [],
        source=SOURCE,
        url=f"{server.url}/table.csv",
        path="test/table.csv",
        raw_dir=raw,
        registered=REGISTERED,
        now=lambda: NOW,
        log=lambda _: None,
    )


def leftovers(directory: Path) -> list[str]:
    return sorted(p.name for p in directory.rglob("*") if p.name.endswith((".part", ".tmp")))


def quiet(_: str) -> None:
    pass


def test_add_downloads_and_pins(server, tmp_path):
    body = b"a,b\n1,2\n"
    [pin] = pin_one(server, tmp_path, body)
    assert (tmp_path / "test" / "table.csv").read_bytes() == body
    assert pin == fetch.Pin(
        "test/table.csv", SOURCE, f"{server.url}/table.csv", sha256(body), len(body), NOW
    )


def test_fetch_skips_verified_files(server, tmp_path):
    pins = pin_one(server, tmp_path)
    requests_before = len(server.requests)
    result, errors = fetch.fetch(pins, tmp_path, log=quiet)
    assert (result, errors) == (pins, [])
    assert len(server.requests) == requests_before


def test_fetch_restores_missing_file(server, tmp_path):
    pins = pin_one(server, tmp_path)
    (tmp_path / "test" / "table.csv").unlink()
    result, errors = fetch.fetch(pins, tmp_path, log=quiet)
    assert (result, errors) == (pins, [])
    assert fetch.sha256_file(tmp_path / "test" / "table.csv") == pins[0].sha256


def test_fetch_repairs_corrupted_local_file(server, tmp_path):
    pins = pin_one(server, tmp_path, b"original\n")
    (tmp_path / "test" / "table.csv").write_bytes(b"tampered\n")
    result, errors = fetch.fetch(pins, tmp_path, log=quiet)
    assert (result, errors) == (pins, [])
    assert (tmp_path / "test" / "table.csv").read_bytes() == b"original\n"


def test_fetch_refuses_upstream_drift(server, tmp_path):
    pins = pin_one(server, tmp_path, b"original\n")
    (tmp_path / "test" / "table.csv").unlink()
    server.files["/table.csv"] = b"revised upstream\n"
    result, errors = fetch.fetch(pins, tmp_path, log=quiet)
    assert result == pins
    assert len(errors) == 1
    assert "differs from its pin" in errors[0]
    assert not (tmp_path / "test" / "table.csv").exists()
    assert leftovers(tmp_path) == []


def test_fetch_keeps_local_file_when_upstream_drifts(server, tmp_path):
    pins = pin_one(server, tmp_path, b"original\n")
    (tmp_path / "test" / "table.csv").write_bytes(b"tampered\n")
    server.files["/table.csv"] = b"revised upstream\n"
    _, errors = fetch.fetch(pins, tmp_path, log=quiet)
    assert len(errors) == 1
    assert (tmp_path / "test" / "table.csv").read_bytes() == b"tampered\n"


def test_update_accepts_drift_and_repins(server, tmp_path):
    pins = pin_one(server, tmp_path, b"original\n")
    server.files["/table.csv"] = b"revised upstream\n"
    (tmp_path / "test" / "table.csv").unlink()
    [repinned], errors = fetch.fetch(pins, tmp_path, update=True, now=lambda: LATER, log=quiet)
    assert errors == []
    assert repinned.sha256 == sha256(b"revised upstream\n")
    assert repinned.size == len(b"revised upstream\n")
    assert repinned.retrieved_at == LATER
    assert (tmp_path / "test" / "table.csv").read_bytes() == b"revised upstream\n"


def test_add_refuses_pinned_path_unless_update(server, tmp_path):
    pins = pin_one(server, tmp_path)
    arguments = dict(
        source=SOURCE,
        url=f"{server.url}/table.csv",
        path="test/table.csv",
        raw_dir=tmp_path,
        registered=REGISTERED,
        log=quiet,
    )
    with pytest.raises(fetch.FetchError, match="already pinned"):
        fetch.add(pins, **arguments)
    assert len(fetch.add(pins, update=True, **arguments)) == 1


def test_add_refuses_unregistered_source(server, tmp_path):
    server.files["/table.csv"] = b"x"
    with pytest.raises(fetch.FetchError, match="not registered"):
        fetch.add(
            [],
            source="OTHER-SRC",
            url=f"{server.url}/table.csv",
            path="test/table.csv",
            raw_dir=tmp_path,
            registered=REGISTERED,
            log=quiet,
        )
    assert server.requests == []


def test_http_error_leaves_no_partial_file(server, tmp_path):
    with pytest.raises(fetch.FetchError, match="HTTP 404"):
        fetch.add(
            [],
            source=SOURCE,
            url=f"{server.url}/missing.csv",
            path="test/missing.csv",
            raw_dir=tmp_path,
            registered=REGISTERED,
            log=quiet,
        )
    assert not (tmp_path / "test" / "missing.csv").exists()
    assert leftovers(tmp_path) == []


def test_user_agent_comes_from_named_environment_variable(server, tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_USER_AGENT", "Jane Doe jane@example.org")
    server.files["/table.csv"] = b"x"
    fetch.add(
        [],
        source=SOURCE,
        url=f"{server.url}/table.csv",
        path="test/table.csv",
        raw_dir=tmp_path,
        registered=REGISTERED,
        user_agent_env="TEST_USER_AGENT",
        log=quiet,
    )
    assert server.requests == [("/table.csv", "Jane Doe jane@example.org")]


def test_missing_user_agent_variable_is_an_error(server, tmp_path, monkeypatch):
    monkeypatch.delenv("TEST_USER_AGENT", raising=False)
    with pytest.raises(fetch.FetchError, match="TEST_USER_AGENT is not set"):
        fetch.add(
            [],
            source=SOURCE,
            url=f"{server.url}/table.csv",
            path="test/table.csv",
            raw_dir=tmp_path,
            registered=REGISTERED,
            user_agent_env="TEST_USER_AGENT",
            log=quiet,
        )


@pytest.mark.parametrize(
    "rel",
    [
        "",
        ".",
        "../escape.csv",
        "a/../../escape.csv",
        "/abs.csv",
        "C:/x.csv",
        "a\\b.csv",
        "./a.csv",
        "a//b.csv",
        "dir/",
    ],
)
def test_unsafe_paths_are_rejected(rel):
    with pytest.raises(fetch.FetchError):
        fetch.check_path(rel)


@pytest.mark.parametrize(
    "url",
    [
        "https://kosis.kr/openapi/data.do?apiKey=SECRET123&format=json",
        "https://example.org/file?token=SECRET123",
        "https://user:SECRET123@example.org/file",
    ],
)
def test_urls_with_credentials_are_rejected_without_echoing_them(url):
    with pytest.raises(fetch.FetchError) as caught:
        fetch.check_url(url)
    assert "SECRET123" not in str(caught.value)


@pytest.mark.parametrize("url", ["http://example.org/file.csv", "ftp://example.org/f", "file.csv"])
def test_non_https_urls_are_rejected(url):
    with pytest.raises(fetch.FetchError):
        fetch.check_url(url)


def test_manifest_round_trip_is_canonical(tmp_path):
    first = fetch.Pin("b/second.csv", SOURCE, "https://example.org/2", "b" * 64, 2, NOW)
    second = fetch.Pin("a/first.csv", SOURCE, "https://example.org/1", "a" * 64, 1, NOW, "UA_VAR")
    manifest = tmp_path / "manifest.json"
    fetch.save_manifest(manifest, [first, second])
    assert fetch.load_manifest(manifest) == [second, first]
    assert manifest.read_bytes().decode("utf-8") == fetch.dump_manifest([second, first])
    assert manifest.read_bytes().endswith(b"}\n")
    assert b"\r" not in manifest.read_bytes()


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ('{"schema_version": 2, "files": []}', "schema_version"),
        ('{"schema_version": 1, "files": [{"path": "a.csv"}]}', "lacks"),
        ("not json", "invalid JSON"),
    ],
)
def test_malformed_manifests_are_rejected(tmp_path, text, message):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(text, encoding="utf-8")
    with pytest.raises(fetch.FetchError, match=message):
        fetch.load_manifest(manifest)


def test_duplicate_paths_are_rejected(tmp_path):
    record = fetch.Pin("a.csv", SOURCE, "https://example.org/1", "a" * 64, 1, NOW).to_record()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"schema_version": 1, "files": [record, record]}), "utf-8")
    with pytest.raises(fetch.FetchError, match="duplicate path"):
        fetch.load_manifest(manifest)


def test_cli_with_empty_manifest_is_a_no_op(tmp_path, capsys):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(fetch.dump_manifest([]), encoding="utf-8")
    before = manifest.read_bytes()
    code = fetch.main(
        [
            "--manifest",
            str(manifest),
            "--raw-dir",
            str(tmp_path / "raw"),
            "--env-file",
            str(tmp_path / "absent.env"),
        ]
    )
    assert code == 0
    assert "nothing to fetch" in capsys.readouterr().out
    assert manifest.read_bytes() == before
    assert not (tmp_path / "raw").exists()


def test_cli_reports_drift_with_exit_code_1(server, tmp_path, capsys):
    raw = tmp_path / "raw"
    manifest = tmp_path / "manifest.json"
    fetch.save_manifest(manifest, pin_one(server, raw, b"original\n"))
    before = manifest.read_bytes()
    (raw / "test" / "table.csv").unlink()
    server.files["/table.csv"] = b"revised upstream\n"
    code = fetch.main(
        [
            "--manifest",
            str(manifest),
            "--raw-dir",
            str(raw),
            "--env-file",
            str(tmp_path / "absent.env"),
        ]
    )
    assert code == 1
    assert "rerun with --update" in capsys.readouterr().err
    assert manifest.read_bytes() == before


def test_registered_sources_reads_the_first_table_column(tmp_path):
    registry = tmp_path / "DATA_SOURCES.md"
    registry.write_text(
        "| ID | Content |\n| --- | --- |\n| AEI-2026-01 | x |\n| KR-POP | y |\n"
        "Text | NOT-AN-ID |\n",
        encoding="utf-8",
    )
    assert fetch.registered_sources(registry) == {"AEI-2026-01", "KR-POP"}


def test_committed_manifest_is_canonical_and_uses_registered_sources():
    pins = fetch.load_manifest(paths.MANIFEST)
    assert paths.MANIFEST.read_text(encoding="utf-8") == fetch.dump_manifest(pins)
    registered = fetch.registered_sources(paths.SOURCES_REGISTRY)
    assert {pin.source for pin in pins} <= registered
