"""Offline tests for the checksummed fetch helper, run against a local HTTP server."""

import hashlib
import http.server
import json
import os
import ssl
import sys
import threading
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from korea_ai_exposure import fetch, paths

NOW = "2026-01-01T00:00:00Z"
LATER = "2026-02-01T00:00:00Z"
SOURCE = "TEST-SRC"
OTHER = "TEST-OTHER"
REGISTERED = frozenset({SOURCE, OTHER})
ORIGINAL = b"original\n"
REVISED = b"revised!\n"  # same length as ORIGINAL, so only the checksum can tell them apart


@dataclass
class FakeServer:
    url: str = ""
    files: dict[str, bytes] = field(default_factory=dict)
    lengths: dict[str, str] = field(default_factory=dict)  # announced Content-Length overrides
    chunked: set[str] = field(default_factory=set)
    redirects: dict[str, str] = field(default_factory=dict)
    requests: list[tuple[str, str | None]] = field(default_factory=list)


@pytest.fixture
def server(monkeypatch):
    # Keep requests to the local server away from any proxy configured on the machine, and fail
    # fast if something goes wrong.
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setattr(fetch, "TIMEOUT_SECONDS", 5)
    state = FakeServer()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            state.requests.append((self.path, self.headers.get("User-Agent")))
            route = self.path.split("?")[0]  # routes ignore the query, as a keyed API's would
            if route in state.redirects:
                self.send_response(302)
                self.send_header("Location", state.redirects[route])
                self.end_headers()
                return
            body = state.files.get(route)
            if body is None:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Length", state.lengths.get(route, str(len(body))))
            if route in state.chunked:
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                self.wfile.write(b"%x\r\n%s\r\n0\r\n\r\n" % (len(body), body))
                return
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    state.url = f"http://127.0.0.1:{httpd.server_address[1]}"
    yield state
    httpd.shutdown()
    httpd.server_close()
    thread.join()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def quiet(_: str) -> None:
    pass


def add_one(server, raw, body=ORIGINAL, path="test/table.csv", source=SOURCE, **kwargs):
    server.files[f"/{path}"] = body
    return fetch.add(
        kwargs.pop("pins", []),
        source=source,
        url=f"{server.url}/{path}",
        path=path,
        raw_dir=raw,
        registered=REGISTERED,
        now=lambda: NOW,
        log=quiet,
        **kwargs,
    )


def files_under(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def write_registry(directory: Path, *ids: str) -> Path:
    registry = directory / "DATA_SOURCES.md"
    rows = "".join(f"| {source} | test |\n" for source in ids)
    registry.write_text(f"| ID | Content |\n| --- | --- |\n{rows}", encoding="utf-8")
    return registry


def run_cli(tmp_path, *args, env_file=None):
    return fetch.main(
        [
            *args,
            "--manifest",
            str(tmp_path / "manifest.json"),
            "--raw-dir",
            str(tmp_path / "raw"),
            "--env-file",
            str(env_file or tmp_path / "absent.env"),
            "--registry",
            str(write_registry(tmp_path, *REGISTERED)),
        ]
    )


# Downloading, pinning, idempotency, drift


def test_add_downloads_and_pins(server, tmp_path):
    [pin] = add_one(server, tmp_path)
    assert (tmp_path / "test" / "table.csv").read_bytes() == ORIGINAL
    assert pin == fetch.Pin(
        "test/table.csv", SOURCE, f"{server.url}/test/table.csv", sha256(ORIGINAL), 9, NOW
    )


def test_fetch_skips_verified_files(server, tmp_path):
    pins = add_one(server, tmp_path)
    requests_before = len(server.requests)
    assert fetch.fetch(pins, tmp_path, log=quiet) == (pins, [])
    assert len(server.requests) == requests_before


def test_fetch_restores_missing_file(server, tmp_path):
    pins = add_one(server, tmp_path)
    (tmp_path / "test" / "table.csv").unlink()
    assert fetch.fetch(pins, tmp_path, log=quiet) == (pins, [])
    assert fetch.sha256_file(tmp_path / "test" / "table.csv") == pins[0].sha256


def test_fetch_repairs_corrupted_local_file(server, tmp_path):
    pins = add_one(server, tmp_path)
    (tmp_path / "test" / "table.csv").write_bytes(b"tampered\n")
    assert fetch.fetch(pins, tmp_path, log=quiet) == (pins, [])
    assert (tmp_path / "test" / "table.csv").read_bytes() == ORIGINAL


def test_fetch_refuses_same_length_upstream_drift(server, tmp_path):
    pins = add_one(server, tmp_path)
    (tmp_path / "test" / "table.csv").unlink()
    server.files["/test/table.csv"] = REVISED
    result, errors = fetch.fetch(pins, tmp_path, log=quiet)
    assert result == pins
    assert len(errors) == 1
    assert "differs from its pin" in errors[0]
    assert files_under(tmp_path) == []


def test_fetch_keeps_local_file_when_upstream_drifts(server, tmp_path):
    pins = add_one(server, tmp_path)
    (tmp_path / "test" / "table.csv").write_bytes(b"tampered\n")
    server.files["/test/table.csv"] = REVISED
    _, errors = fetch.fetch(pins, tmp_path, log=quiet)
    assert len(errors) == 1
    assert (tmp_path / "test" / "table.csv").read_bytes() == b"tampered\n"


def test_update_accepts_drift_of_a_missing_file_and_repins(server, tmp_path):
    pins = add_one(server, tmp_path)
    server.files["/test/table.csv"] = REVISED
    (tmp_path / "test" / "table.csv").unlink()
    [repinned], errors = fetch.fetch(pins, tmp_path, update=True, now=lambda: LATER, log=quiet)
    assert errors == []
    assert (repinned.sha256, repinned.size, repinned.retrieved_at) == (sha256(REVISED), 9, LATER)
    assert (tmp_path / "test" / "table.csv").read_bytes() == REVISED


def test_update_without_refresh_leaves_verified_files_alone(server, tmp_path):
    pins = add_one(server, tmp_path)
    server.files["/test/table.csv"] = REVISED
    requests_before = len(server.requests)
    assert fetch.fetch(pins, tmp_path, update=True, log=quiet) == (pins, [])
    assert len(server.requests) == requests_before


def test_refresh_detects_upstream_revision_of_a_verified_file(server, tmp_path):
    pins = add_one(server, tmp_path)
    assert fetch.fetch(pins, tmp_path, refresh=True, log=quiet) == (pins, [])
    server.files["/test/table.csv"] = REVISED
    _, errors = fetch.fetch(pins, tmp_path, refresh=True, log=quiet)
    assert len(errors) == 1
    assert (tmp_path / "test" / "table.csv").read_bytes() == ORIGINAL
    [repinned], errors = fetch.fetch(pins, tmp_path, refresh=True, update=True, log=quiet)
    assert errors == []
    assert repinned.sha256 == sha256(REVISED)
    assert files_under(tmp_path) == ["test/table.csv"]


def test_add_refuses_a_pinned_path_unless_update(server, tmp_path):
    pins = add_one(server, tmp_path)
    with pytest.raises(fetch.FetchError, match="already pinned"):
        add_one(server, tmp_path, pins=pins)
    server.files["/test/table.csv"] = REVISED
    [repinned] = fetch.add(
        pins,
        source=SOURCE,
        url=f"{server.url}/test/table.csv",
        path="test/table.csv",
        raw_dir=tmp_path,
        registered=REGISTERED,
        update=True,
        now=lambda: LATER,
        log=quiet,
    )
    assert (repinned.sha256, repinned.retrieved_at) == (sha256(REVISED), LATER)


def test_paths_are_compared_case_insensitively(server, tmp_path):
    pins = add_one(server, tmp_path, path="test/Table.csv")
    with pytest.raises(fetch.FetchError, match="already pinned"):
        add_one(server, tmp_path, path="test/table.csv", pins=pins)
    manifest = tmp_path / "manifest.json"
    twins = [pins[0], fetch.Pin("test/table.csv", SOURCE, pins[0].url, "a" * 64, 1, NOW)]
    manifest.write_text(
        json.dumps({"schema_version": 1, "files": [p.to_record() for p in twins]}), "utf-8"
    )
    with pytest.raises(fetch.FetchError, match="duplicate path"):
        fetch.load_manifest(manifest)


def test_add_refuses_unregistered_source_before_any_request(server, tmp_path):
    with pytest.raises(fetch.FetchError, match="not registered"):
        add_one(server, tmp_path, source="NOT-REGISTERED")
    assert server.requests == []


def test_add_checks_the_url_before_any_request(server, tmp_path):
    with pytest.raises(fetch.FetchError, match="credential"):
        fetch.add(
            [],
            source=SOURCE,
            url=f"{server.url}/x.csv?token=SECRET123",
            path="test/x.csv",
            raw_dir=tmp_path,
            registered=REGISTERED,
            log=quiet,
        )
    assert server.requests == []
    assert files_under(tmp_path) == []


# Failed and suspicious responses


def test_http_error_leaves_no_partial_file(server, tmp_path):
    with pytest.raises(fetch.FetchError, match="HTTP 404"):
        fetch.add(
            [],
            source=SOURCE,
            url=f"{server.url}/missing.csv?page=2",
            path="test/missing.csv",
            raw_dir=tmp_path,
            registered=REGISTERED,
            log=quiet,
        )
    assert files_under(tmp_path) == []


def test_error_messages_omit_query_strings(server, tmp_path):
    with pytest.raises(fetch.FetchError) as caught:
        fetch.add(
            [],
            source=SOURCE,
            url=f"{server.url}/missing.csv?page=2",
            path="test/missing.csv",
            raw_dir=tmp_path,
            registered=REGISTERED,
            log=quiet,
        )
    assert "/missing.csv" in str(caught.value)
    assert "page=2" not in str(caught.value)


def test_truncated_download_is_refused(server, tmp_path):
    server.lengths["/test/table.csv"] = "20"
    with pytest.raises(fetch.FetchError, match="announced 20"):
        add_one(server, tmp_path)
    assert files_under(tmp_path) == []
    pins = [fetch.Pin("test/table.csv", SOURCE, f"{server.url}/test/table.csv", "a" * 64, 9, NOW)]
    result, errors = fetch.fetch(pins, tmp_path, update=True, log=quiet)
    assert result == pins
    assert len(errors) == 1
    assert "announced" in errors[0]
    assert files_under(tmp_path) == []


def test_chunked_response_ignores_content_length(server, tmp_path):
    server.chunked.add("/test/table.csv")
    server.lengths["/test/table.csv"] = "999"
    [pin] = add_one(server, tmp_path)
    assert pin.size == len(ORIGINAL)


def test_non_ascii_content_length_is_ignored(server, tmp_path):
    server.lengths["/test/table.csv"] = "\u00b2"
    [pin] = add_one(server, tmp_path)
    assert pin.size == len(ORIGINAL)


@pytest.mark.parametrize(
    "body", [b"", b"<!DOCTYPE html><title>Blocked</title>", b"\xef\xbb\xbf  <html>Moved</html>"]
)
def test_empty_and_html_responses_are_refused_for_data_files(server, tmp_path, body):
    with pytest.raises(fetch.FetchError, match=r"empty|HTML"):
        add_one(server, tmp_path, body=body)
    assert files_under(tmp_path) == []


def test_html_is_accepted_for_an_html_path(server, tmp_path):
    [pin] = add_one(server, tmp_path, body=b"<!doctype html><p>notes</p>", path="docs/page.html")
    assert pin.size == 27


def test_a_failure_does_not_stop_the_batch_and_temporary_files_are_removed(server, tmp_path):
    pins = add_one(server, tmp_path, path="test/a.csv")
    pins = add_one(server, tmp_path, path="test/b.csv", pins=pins)
    for name in ("a.csv", "b.csv"):
        (tmp_path / "test" / name).unlink()
    (tmp_path / "test" / "a.csv").mkdir()  # the destination cannot be replaced
    result, errors = fetch.fetch(sorted(pins, key=lambda p: p.path), tmp_path, log=quiet)
    assert len(errors) == 1
    assert "cannot write" in errors[0]
    assert (tmp_path / "test" / "b.csv").read_bytes() == ORIGINAL
    assert files_under(tmp_path) == ["test/b.csv"]
    assert len(result) == 2


# Redirects and User-Agent


def test_same_host_redirect_is_followed(server, tmp_path):
    server.redirects["/test/old.csv"] = f"{server.url}/test/new.csv"
    server.files["/test/new.csv"] = ORIGINAL
    [pin] = fetch.add(
        [],
        source=SOURCE,
        url=f"{server.url}/test/old.csv",
        path="test/table.csv",
        raw_dir=tmp_path,
        registered=REGISTERED,
        log=quiet,
    )
    assert pin.sha256 == sha256(ORIGINAL)


def test_redirect_to_plain_http_elsewhere_is_refused(server, tmp_path):
    server.redirects["/test/table.csv"] = "http://192.0.2.1/table.csv"
    with pytest.raises(fetch.FetchError, match="refused redirect"):
        add_one(server, tmp_path)
    assert files_under(tmp_path) == []


def test_custom_user_agent_is_sent_only_to_the_pinned_host():
    handler = fetch._StrictRedirect("127.0.0.1")
    request = urllib.request.Request("http://127.0.0.1:1/a", headers={"User-Agent": "Jane"})
    same = handler.redirect_request(request, None, 302, "Found", {}, "http://127.0.0.1:1/b")
    other = handler.redirect_request(request, None, 302, "Found", {}, "https://cdn.example/b")
    assert same.get_header("User-agent") == "Jane"
    assert other.get_header("User-agent") == fetch.DEFAULT_USER_AGENT


def test_user_agent_comes_from_the_named_environment_variable(server, tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_USER_AGENT", "Jane Doe jane@example.org")
    add_one(server, tmp_path, user_agent_env="TEST_USER_AGENT")
    assert server.requests == [("/test/table.csv", "Jane Doe jane@example.org")]


def test_missing_user_agent_variable_is_an_error(server, tmp_path, monkeypatch):
    monkeypatch.delenv("TEST_USER_AGENT", raising=False)
    with pytest.raises(fetch.FetchError, match="TEST_USER_AGENT is not set"):
        add_one(server, tmp_path, user_agent_env="TEST_USER_AGENT")


@pytest.fixture
def keyed(monkeypatch):
    """The local server stands in for a keyed API such as KOSIS; TEST_KEY holds its key."""
    monkeypatch.setattr(fetch, "KEY_PARAMS", {"127.0.0.1": "apiKey"})
    monkeypatch.setenv("TEST_KEY", "k3y/with+chars")
    return "TEST_KEY"


def test_key_is_added_at_request_time_and_never_pinned(server, tmp_path, keyed):
    [pin] = add_one(server, tmp_path, key_env=keyed)
    assert server.requests[0][0] == "/test/table.csv?apiKey=k3y%2Fwith%2Bchars"
    assert pin.key_env == keyed
    assert "k3y" not in fetch.dump_manifest([pin])
    _, errors = fetch.fetch([pin], tmp_path / "elsewhere", log=quiet)
    assert errors == []
    assert server.requests[-1][0].endswith("?apiKey=k3y%2Fwith%2Bchars")


def test_a_keyed_request_is_not_redirected_to_another_host(server, tmp_path, keyed):
    server.redirects["/test/table.csv"] = "https://cdn.example/table.csv"
    with pytest.raises(fetch.FetchError, match="refused redirect") as caught:
        add_one(server, tmp_path, key_env=keyed)
    assert "k3y" not in str(caught.value)


def test_an_api_error_object_is_refused_and_the_key_removed(server, tmp_path, keyed):
    body = json.dumps({"err": "20", "errMsg": "invalid apiKey k3y/with+chars"}).encode()
    with pytest.raises(fetch.FetchError, match="API error 20") as caught:
        add_one(server, tmp_path, body=body, path="test/table.json", key_env=keyed)
    assert "k3y" not in str(caught.value)
    assert files_under(tmp_path) == []


def test_missing_key_variable_is_an_error(server, tmp_path, keyed, monkeypatch):
    monkeypatch.delenv("TEST_KEY")
    with pytest.raises(fetch.FetchError, match="TEST_KEY is not set"):
        add_one(server, tmp_path, key_env=keyed)


@pytest.mark.parametrize(
    ("name", "url"),
    [
        ("KOSIS_TOKEN", "https://kosis.kr/openapi/x.do"),
        ("KOSIS_KEY", "https://example.org/openapi/x.do"),
        (7, "https://kosis.kr/openapi/x.do"),
    ],
)
def test_key_env_needs_a_key_variable_and_a_keyed_host(name, url):
    with pytest.raises(fetch.FetchError, match="key_env"):
        fetch.check_key_env(name, url)


@pytest.mark.parametrize("name", ["KOSIS_API_KEY", "GITHUB_TOKEN", "bls_user_agent", 7, True])
def test_user_agent_env_must_name_a_user_agent_variable(server, tmp_path, name):
    with pytest.raises(fetch.FetchError, match="user_agent_env"):
        add_one(server, tmp_path, user_agent_env=name)
    assert server.requests == []


# Paths, URLs, and credentials


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
        "a.csv.",
        "a.csv ",
        "a b.csv",
        "a?b.csv",
        "NUL",
        "con.csv",
        "aux/x.csv",
        7,
    ],
)
def test_unsafe_or_non_portable_paths_are_rejected(rel):
    with pytest.raises(fetch.FetchError):
        fetch.check_path(rel)


def test_paths_through_links_outside_raw_are_refused(tmp_path):
    raw, outside = tmp_path / "raw", tmp_path / "outside"
    raw.mkdir()
    outside.mkdir()
    try:
        (raw / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        if sys.platform != "win32":
            raise
        import _winapi

        _winapi.CreateJunction(str(outside), str(raw / "link"))
    with pytest.raises(fetch.FetchError, match="resolves outside"):
        fetch._destination(raw, "link/x.csv")


@pytest.mark.parametrize(
    "url",
    [
        "https://kosis.kr/openapi/data.do?apiKey=SECRET123&format=json",
        "https://example.org/file?token=SECRET123",
        "https://example.org/api?serviceKey=SECRET123",
        "https://example.org/api?registrationkey=SECRET123",
        "https://example.org/api?crtfc_key=SECRET123",
        "https://example.org/file#access_token=SECRET123",
        "https://user:SECRET123@example.org/file",
    ],
)
def test_urls_with_credentials_are_rejected_without_echoing_them(url):
    with pytest.raises(fetch.FetchError) as caught:
        fetch.check_url(url)
    assert "SECRET123" not in str(caught.value)


@pytest.mark.parametrize(
    "url",
    [
        "https://ecos.example.org/api/StatisticSearch/SECRETVALUE123/json",
        "https://example.org/api/SECRETVALUE%31%32%33/json",
    ],
)
def test_urls_containing_an_env_value_are_rejected(url):
    with pytest.raises(fetch.FetchError, match=r"\.env") as caught:
        fetch.check_url(url, secrets={"SECRETVALUE123"})
    assert "SECRETVALUE" not in str(caught.value)


@pytest.mark.parametrize(
    "url", ["http://example.org/file.csv", "ftp://example.org/f", "file.csv", "https://[::1/x"]
)
def test_non_https_or_malformed_urls_are_rejected(url):
    with pytest.raises(fetch.FetchError):
        fetch.check_url(url)


def test_tls_verification_uses_certificates_and_hostnames():
    context = fetch.tls_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


def test_downloads_use_the_verifying_context(server, tmp_path, monkeypatch):
    contexts = []
    real = fetch.tls_context
    monkeypatch.setattr(fetch, "tls_context", lambda: contexts.append(real()) or contexts[-1])
    add_one(server, tmp_path)
    assert len(contexts) == 1


def test_env_secrets_reads_long_values_only(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("LONG_KEY=abcdefgh123\nSHORT=abc\nEMPTY=\n", encoding="utf-8")
    assert fetch.env_secrets(env_file) == {"abcdefgh123"}
    assert fetch.env_secrets(tmp_path / "absent.env") == frozenset()


# Manifest


def test_manifest_round_trip_is_canonical(tmp_path):
    first = fetch.Pin("b/second.csv", SOURCE, "https://example.org/2", "b" * 64, 2, NOW)
    second = fetch.Pin(
        "a/first.csv", SOURCE, "https://example.org/1", "a" * 64, 1, NOW, "BLS_USER_AGENT"
    )
    manifest = tmp_path / "manifest.json"
    fetch.save_manifest(manifest, [first, second])
    assert fetch.load_manifest(manifest) == [second, first]
    assert manifest.read_bytes().decode("utf-8") == fetch.dump_manifest([second, first])
    assert manifest.read_bytes().endswith(b"}\n")
    assert b"\r" not in manifest.read_bytes()


GOOD = {
    "path": "a.csv",
    "source": SOURCE,
    "url": "https://example.org/1",
    "sha256": "a" * 64,
    "bytes": 1,
    "retrieved_at": NOW,
}


@pytest.mark.parametrize(
    "change",
    [
        {"sha256": "A" * 64},
        {"bytes": "3"},
        {"bytes": True},
        {"bytes": -1},
        {"source": "test-src"},
        {"retrieved_at": "2026-01-01 00:00:00"},
        {"retrieved_at": "2026-01-01T00:00:00+00:00"},
        {"user_agent_env": "KOSIS_API_KEY"},
        {"user_agent_env": 7},
        {"comment": "unknown keys are refused"},
        {"url": "https://example.org/x?apiKey=SECRET123"},
    ],
)
def test_malformed_records_are_rejected(tmp_path, change):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"schema_version": 1, "files": [GOOD | change]}), "utf-8")
    with pytest.raises(fetch.FetchError):
        fetch.load_manifest(manifest)


def test_a_wellformed_record_loads():
    assert fetch.Pin.from_record(GOOD).path == "a.csv"


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


def test_utc_now_produces_a_valid_timestamp():
    fetch.Pin("a.csv", SOURCE, "https://example.org/1", "a" * 64, 1, fetch.utc_now()).validate()


def test_registered_sources_reads_first_columns_before_prior_art(tmp_path):
    registry = tmp_path / "DATA_SOURCES.md"
    registry.write_text(
        "| ID | Content |\n| --- | --- |\n| AEI-2026-01 | x |\n| KR-POP | y |\n"
        "Text | NOT-AN-ID |\n\n## Prior art (not data)\n\n| BOK-2026-09 | note |\n",
        encoding="utf-8",
    )
    assert fetch.registered_sources(registry) == {"AEI-2026-01", "KR-POP"}


def test_committed_manifest_is_canonical_and_uses_registered_sources():
    registered = fetch.registered_sources(paths.SOURCES_REGISTRY)
    assert {"AEI-2026-01", "AEI-LMI", "KR-POP"} <= registered
    assert "BOK-2026-09" not in registered
    pins = fetch.load_manifest(paths.MANIFEST)
    assert paths.MANIFEST.read_bytes().decode("utf-8") == fetch.dump_manifest(pins)
    assert {pin.source for pin in pins} <= registered


# Command line


def test_cli_with_empty_manifest_is_a_no_op(tmp_path, capsys):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(fetch.dump_manifest([]), encoding="utf-8")
    assert run_cli(tmp_path) == 0
    assert "nothing to fetch" in capsys.readouterr().out
    assert manifest.read_text(encoding="utf-8") == fetch.dump_manifest([])
    assert not (tmp_path / "raw").exists()


def test_cli_add_pins_and_refuses_a_repeat(server, tmp_path, capsys):
    server.files["/a.csv"] = ORIGINAL
    assert run_cli(tmp_path, "--add", SOURCE, f"{server.url}/a.csv", "t/a.csv") == 0
    [pin] = fetch.load_manifest(tmp_path / "manifest.json")
    assert (pin.path, pin.sha256) == ("t/a.csv", sha256(ORIGINAL))
    before = (tmp_path / "manifest.json").read_bytes()
    assert run_cli(tmp_path, "--add", SOURCE, f"{server.url}/a.csv", "t/a.csv") == 1
    assert "already pinned" in capsys.readouterr().err
    assert (tmp_path / "manifest.json").read_bytes() == before


def test_cli_reports_drift_with_exit_code_1(server, tmp_path, capsys):
    raw = tmp_path / "raw"
    fetch.save_manifest(tmp_path / "manifest.json", add_one(server, raw))
    before = (tmp_path / "manifest.json").read_bytes()
    (raw / "test" / "table.csv").unlink()
    server.files["/test/table.csv"] = REVISED
    assert run_cli(tmp_path) == 1
    assert "rerun with --update" in capsys.readouterr().err
    assert (tmp_path / "manifest.json").read_bytes() == before


def test_cli_update_of_one_source_keeps_the_other_pins(server, tmp_path):
    raw = tmp_path / "raw"
    pins = add_one(server, raw, path="t/a.csv")
    pins = add_one(server, raw, path="t/b.csv", source=OTHER, pins=pins)
    fetch.save_manifest(tmp_path / "manifest.json", pins)
    for name in ("a.csv", "b.csv"):
        (raw / "t" / name).unlink()
        server.files[f"/t/{name}"] = REVISED
    requests_before = len(server.requests)
    assert run_cli(tmp_path, "--source", SOURCE, "--update") == 0
    after = {pin.path: pin for pin in fetch.load_manifest(tmp_path / "manifest.json")}
    assert after["t/a.csv"].sha256 == sha256(REVISED)
    assert after["t/a.csv"].retrieved_at != NOW
    assert after["t/b.csv"] == next(pin for pin in pins if pin.path == "t/b.csv")
    assert [path for path, _ in server.requests[requests_before:]] == ["/t/a.csv"]


def test_cli_refetch_sends_the_user_agent_from_the_env_file(server, tmp_path, monkeypatch):
    env_file = tmp_path / "test.env"
    env_file.write_text("TEST_CLI_USER_AGENT=Jane Doe jane@example.org\n", encoding="utf-8")
    monkeypatch.setenv("TEST_CLI_USER_AGENT", "placeholder")
    monkeypatch.delenv("TEST_CLI_USER_AGENT")  # monkeypatch now restores the variable afterwards
    server.files["/t/a.csv"] = ORIGINAL
    pin = fetch.Pin(
        "t/a.csv", SOURCE, f"{server.url}/t/a.csv", sha256(ORIGINAL), 9, NOW, "TEST_CLI_USER_AGENT"
    )
    fetch.save_manifest(tmp_path / "manifest.json", [pin])
    assert run_cli(tmp_path, env_file=env_file) == 0
    assert server.requests == [("/t/a.csv", "Jane Doe jane@example.org")]
    assert os.environ.get("TEST_CLI_USER_AGENT") == "Jane Doe jane@example.org"


def test_cli_refuses_a_url_that_contains_an_env_value(server, tmp_path, capsys, monkeypatch):
    env_file = tmp_path / "test.env"
    env_file.write_text("TEST_CLI_KEY=supersecretvalue123\n", encoding="utf-8")
    monkeypatch.setenv("TEST_CLI_KEY", "placeholder")
    monkeypatch.delenv("TEST_CLI_KEY")  # monkeypatch now removes what load_dotenv sets
    url = f"{server.url}/api/supersecretvalue123/a.csv"
    assert run_cli(tmp_path, "--add", SOURCE, url, "t/a.csv", env_file=env_file) == 1
    assert "supersecretvalue123" not in capsys.readouterr().err
    assert server.requests == []
    assert not (tmp_path / "manifest.json").exists()


@pytest.mark.parametrize(
    "args",
    [
        ["--user-agent-env", "BLS_USER_AGENT"],
        ["--add", SOURCE, "https://example.org/a", "a.csv", "--source", SOURCE],
        ["--add", SOURCE, "https://example.org/a", "a.csv", "--refresh"],
    ],
)
def test_cli_rejects_invalid_argument_combinations(tmp_path, args):
    with pytest.raises(SystemExit) as caught:
        run_cli(tmp_path, *args)
    assert caught.value.code == 2


def test_cli_reports_an_unknown_source(tmp_path, capsys):
    fetch.save_manifest(
        tmp_path / "manifest.json",
        [fetch.Pin("a.csv", SOURCE, "https://example.org/1", "a" * 64, 1, NOW)],
    )
    assert run_cli(tmp_path, "--source", "NOT-REGISTERED") == 1
    assert "no files registered" in capsys.readouterr().err
