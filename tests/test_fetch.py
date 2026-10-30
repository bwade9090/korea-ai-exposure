"""The fetcher's guards for a public repository: credentials are never pinned, the KOSIS key
stays out of the manifest and off other hosts, and pinned files are verified by checksum. Run
offline against a local HTTP server."""

import http.server
import json
import threading
from dataclasses import dataclass, field

import pytest

from korea_ai_exposure import fetch, paths

SOURCE = "TEST-SRC"
REGISTERED = frozenset({SOURCE})
ORIGINAL = b"original\n"
REVISED = b"revised!\n"  # same length: only the checksum tells them apart


@dataclass
class FakeServer:
    url: str = ""
    files: dict[str, bytes] = field(default_factory=dict)
    redirects: dict[str, str] = field(default_factory=dict)
    requests: list[str] = field(default_factory=list)


@pytest.fixture
def server(monkeypatch):
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setattr(fetch, "TIMEOUT_SECONDS", 5)
    state = FakeServer()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            state.requests.append(self.path)
            route = self.path.split("?")[0]
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
            self.send_header("Content-Length", str(len(body)))
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


@pytest.fixture
def keyed(monkeypatch):
    """The local server stands in for a keyed API such as KOSIS; TEST_KEY holds its key."""
    monkeypatch.setattr(fetch, "KEY_PARAMS", {"127.0.0.1": "apiKey"})
    monkeypatch.setenv("TEST_KEY", "k3y/with+chars")
    return "TEST_KEY"


def add_one(server, raw, body=ORIGINAL, path="test/table.csv", **kwargs):
    server.files[f"/{path}"] = body
    return fetch.add(
        [],
        source=SOURCE,
        url=f"{server.url}/{path}",
        path=path,
        raw_dir=raw,
        registered=REGISTERED,
        log=lambda _: None,
        **kwargs,
    )


def test_a_pinned_file_is_verified_without_downloading_and_drift_is_refused(server, tmp_path):
    [pin] = add_one(server, tmp_path)
    _, errors = fetch.fetch([pin], tmp_path, log=lambda _: None)
    assert errors == [] and len(server.requests) == 1  # verified locally, not downloaded again
    server.files["/test/table.csv"] = REVISED
    _, errors = fetch.fetch([pin], tmp_path / "elsewhere", log=lambda _: None)
    assert errors and "differs from its pin" in errors[0]
    assert not (tmp_path / "elsewhere" / "test/table.csv").exists()


@pytest.mark.parametrize(
    "url",
    [
        "https://kosis.kr/openapi/data.do?apiKey=SECRET123&format=json",
        "https://example.org/file?token=SECRET123",
        "https://user:pass@example.org/file.csv",
        "https://example.org/file?q=SECRET-VALUE-1",  # the value of a variable in .env
    ],
)
def test_urls_with_credentials_are_refused_without_echoing_them(url):
    with pytest.raises(fetch.FetchError) as caught:
        fetch.check_url(url, secrets={"SECRET-VALUE-1"})
    assert "SECRET" not in str(caught.value) and "pass" not in str(caught.value)


def test_the_key_is_added_at_request_time_and_never_pinned(server, tmp_path, keyed):
    [pin] = add_one(server, tmp_path, key_env=keyed)
    assert server.requests[0] == "/test/table.csv?apiKey=k3y%2Fwith%2Bchars"
    assert pin.key_env == keyed and "k3y" not in fetch.dump_manifest([pin])


def test_a_keyed_request_follows_no_redirect_to_another_host(server, tmp_path, keyed):
    server.redirects["/test/table.csv"] = "https://cdn.example/table.csv"
    with pytest.raises(fetch.FetchError, match="refused redirect") as caught:
        add_one(server, tmp_path, key_env=keyed)
    assert "k3y" not in str(caught.value)


def test_an_api_error_object_is_refused_and_the_key_removed(server, tmp_path, keyed):
    body = json.dumps({"err": "20", "errMsg": "invalid apiKey k3y/with+chars"}).encode()
    with pytest.raises(fetch.FetchError, match="API error 20") as caught:
        add_one(server, tmp_path, body=body, path="test/table.json", key_env=keyed)
    assert "k3y" not in str(caught.value)
    assert not (tmp_path / "test/table.json").exists()


@pytest.mark.parametrize(
    ("name", "url"),
    [("KOSIS_TOKEN", "https://kosis.kr/x.do"), ("KOSIS_KEY", "https://example.org/x.do")],
)
def test_a_key_needs_a_key_variable_and_a_keyed_host(name, url):
    with pytest.raises(fetch.FetchError, match="key_env"):
        fetch.check_key_env(name, url)


def test_every_pinned_file_belongs_to_a_registered_source():
    pins = fetch.load_manifest(paths.MANIFEST)
    registered = fetch.registered_sources(paths.SOURCES_REGISTRY)
    assert {pin.source for pin in pins} <= registered
    assert paths.MANIFEST.read_text(encoding="utf-8") == fetch.dump_manifest(pins)
