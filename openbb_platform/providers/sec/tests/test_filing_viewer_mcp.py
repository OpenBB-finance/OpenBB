"""Tests for the SEC Filing Viewer MCP server."""

import asyncio
from unittest.mock import AsyncMock, patch

from starlette.requests import Request
from starlette.testclient import TestClient

from openbb_sec.utils import filing_viewer_mcp as mcp


def test_document_to_markdown_rejects_non_sec():
    """Non-SEC URLs are rejected."""
    out = mcp.document_to_markdown("https://example.com/x.htm")
    assert out.startswith("Only SEC")


def test_document_to_markdown_load_error():
    """A transport error is reported rather than raised."""
    with patch("openbb_sec.utils.cache.cached_bytes", side_effect=RuntimeError("boom")):
        out = mcp.document_to_markdown("https://www.sec.gov/a.htm")
    assert out.startswith("Could not load")


def test_document_to_markdown_pdf():
    """A PDF is described, not converted, by magic bytes or extension."""
    with patch("openbb_sec.utils.cache.cached_bytes", return_value=b"%PDF-1.7"):
        assert "PDF" in mcp.document_to_markdown("https://www.sec.gov/a.htm")
    with patch("openbb_sec.utils.cache.cached_bytes", return_value=b"x"):
        assert "PDF" in mcp.document_to_markdown("https://www.sec.gov/a.pdf")


def test_document_to_markdown_html():
    """HTML is converted to markdown."""
    with (
        patch(
            "openbb_sec.utils.cache.cached_bytes",
            return_value=b"<html><body>Hi</body></html>",
        ),
        patch("openbb_sec.utils.html2markdown.html_to_markdown", return_value="# Hi"),
    ):
        assert mcp.document_to_markdown("https://www.sec.gov/a.htm") == "# Hi"


def test_document_to_markdown_text():
    """A non-structural XML document is returned as-is."""
    with patch.object(mcp, "_bounded_get", return_value=b'<?xml version="1.0"?><x/>'):
        out = mcp.document_to_markdown("https://www.sec.gov/a.xml")
    assert out.startswith("<?xml")


def test_get_filing_document_uses_url():
    """A supplied URL is converted directly."""
    with patch.object(mcp, "document_to_markdown", return_value="MD"):
        assert mcp.get_filing_document("https://www.sec.gov/a.htm") == "MD"


def test_get_filing_document_uses_current(monkeypatch):
    """With no URL, the document currently in the viewer is used."""
    monkeypatch.setitem(mcp._CURRENT, "url", "https://www.sec.gov/cur.htm")
    with patch.object(mcp, "document_to_markdown", return_value="CUR"):
        assert mcp.get_filing_document() == "CUR"


def test_get_filing_document_no_document(monkeypatch):
    """With no URL and nothing open, an informative message is returned."""
    monkeypatch.setitem(mcp._CURRENT, "url", None)
    assert "No document" in mcp.get_filing_document()


def test_build_mcp_app_preflight_and_viewer_state(monkeypatch):
    """The app answers the PNA preflight and records pushed viewer state."""
    monkeypatch.setitem(mcp._CURRENT, "url", None)
    with TestClient(mcp.build_mcp_app()) as client:
        preflight = client.options(
            "/mcp",
            headers={
                "Origin": "https://pro.openbb.dev",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert preflight.status_code == 200
        assert preflight.headers.get("access-control-allow-private-network") == "true"
        client.post("/viewer-state", json={"url": "https://www.sec.gov/x.htm"})
    assert mcp._CURRENT["url"] == "https://www.sec.gov/x.htm"


def test_mcp_server_url(monkeypatch):
    """The internal subprocess base URL follows the configured port."""
    monkeypatch.setenv("OPENBB_SEC_MCP_PORT", "8123")
    assert mcp.mcp_server_url() == "http://127.0.0.1:8123"


def test_port_open_false_for_closed_port():
    """A port with nothing listening reports closed."""
    assert mcp._port_open("127.0.0.1", 65123) is False


def test_stop_mcp_subprocess(monkeypatch):
    """A running subprocess is terminated and the handle cleared; idempotent."""

    class _Proc:
        def __init__(self):
            self.terminated = False
            self._alive = True

        def poll(self):
            return None if self._alive else 0

        def terminate(self):
            self.terminated = True
            self._alive = False

    proc = _Proc()
    monkeypatch.setattr(mcp, "_mcp_process", proc)
    mcp.stop_mcp_subprocess()
    assert proc.terminated is True
    assert mcp._mcp_process is None
    mcp.stop_mcp_subprocess()  # no-op when already stopped


def test_await_ready(monkeypatch):
    """Polling resolves true once the port opens, false when it never does."""
    monkeypatch.setattr(mcp, "_port_open", lambda *a: True)
    assert asyncio.run(mcp._await_ready(timeout=0.4)) is True
    monkeypatch.setattr(mcp, "_port_open", lambda *a: False)
    assert asyncio.run(mcp._await_ready(timeout=0.2)) is False


def test_extract_mcp_request():
    """Only forwardable headers/body/method/query are captured from the request."""

    async def _receive():
        return {"type": "http.request", "body": b"hello", "more_body": False}

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"accept", b"text/event-stream"), (b"host", b"drop.me")],
        "query_string": b"a=1",
        "path": "/mcp",
    }
    data = asyncio.run(mcp._extract_mcp_request(Request(scope, _receive)))
    assert data["method"] == "POST"
    assert data["body"] == b"hello"
    assert data["headers"] == {"accept": "text/event-stream"}
    assert data["query"] == {"a": "1"}


def test_exit_when_orphaned_starts_watcher(monkeypatch):
    """A daemon watcher thread is started; it reaps the process once orphaned."""
    import pytest

    started: dict = {}

    class _Thread:
        def __init__(self, target=None, daemon=None):
            started["target"] = target

        def start(self):
            started["started"] = True

    monkeypatch.setattr("threading.Thread", _Thread)
    mcp._exit_when_orphaned()
    assert started["started"] is True

    # Drive one watcher iteration where the parent has gone away.
    monkeypatch.setattr("time.sleep", lambda _s: None)
    monkeypatch.setattr("os.getppid", lambda: -1)

    class _Exit(Exception):
        pass

    def _fake_exit(_code):
        raise _Exit

    monkeypatch.setattr("os._exit", _fake_exit)
    with pytest.raises(_Exit):
        started["target"]()


def test_serve_runs_uvicorn(monkeypatch):
    """The subprocess entry point arms orphan-cleanup and runs uvicorn."""
    ran: dict = {}
    monkeypatch.setattr(
        mcp, "_exit_when_orphaned", lambda: ran.setdefault("orphan", True)
    )
    monkeypatch.setattr(mcp, "build_mcp_app", object)
    monkeypatch.setattr("uvicorn.run", lambda *a, **k: ran.setdefault("ran", True))
    mcp._serve("127.0.0.1", 12345)
    assert ran == {"orphan": True, "ran": True}


def _proxy_data():
    return {"method": "POST", "body": b"{}", "headers": {}, "query": {}}


def test_mcp_reverse_proxy_unavailable(monkeypatch):
    """When the subprocess never comes up, the proxy returns 503."""
    monkeypatch.setattr(mcp, "ensure_mcp_subprocess", lambda: None)
    monkeypatch.setattr(mcp, "_await_ready", AsyncMock(return_value=False))
    resp = asyncio.run(mcp.mcp_reverse_proxy("mcp", _proxy_data()))
    assert resp.status_code == 503


def test_mcp_reverse_proxy_upstream_error(monkeypatch):
    """A connection error to the subprocess surfaces as 502."""
    import aiohttp

    class _Session:
        def __init__(self, *a, **k):
            pass

        async def request(self, *a, **k):
            raise aiohttp.ClientError("boom")

        async def close(self):
            pass

    monkeypatch.setattr(mcp, "ensure_mcp_subprocess", lambda: None)
    monkeypatch.setattr(mcp, "_await_ready", AsyncMock(return_value=True))
    monkeypatch.setattr("aiohttp.ClientSession", _Session)
    resp = asyncio.run(mcp.mcp_reverse_proxy("mcp", _proxy_data()))
    assert resp.status_code == 502


def test_mcp_reverse_proxy_streams_response(monkeypatch):
    """A live subprocess response is streamed back; hop-by-hop headers dropped."""

    class _Upstream:
        status = 200
        headers = {"content-type": "text/event-stream", "content-length": "2"}

        def __init__(self):
            self.content = self
            self.released = False

        async def iter_any(self):
            yield b"hi"

        def release(self):
            self.released = True

    class _Session:
        def __init__(self, *a, **k):
            pass

        async def request(self, *a, **k):
            return _Upstream()

        async def close(self):
            pass

    monkeypatch.setattr(mcp, "ensure_mcp_subprocess", lambda: None)
    monkeypatch.setattr(mcp, "_await_ready", AsyncMock(return_value=True))
    monkeypatch.setattr("aiohttp.ClientSession", _Session)

    async def _run():
        resp = await mcp.mcp_reverse_proxy("mcp", _proxy_data())
        body = b""
        async for chunk in resp.body_iterator:
            body += chunk if isinstance(chunk, bytes) else chunk.encode()
        return resp, body

    resp, body = asyncio.run(_run())
    assert resp.status_code == 200
    assert body == b"hi"
    assert "content-length" not in {k.lower() for k in resp.headers}
    assert "mcp-session-id" in resp.headers["access-control-expose-headers"].lower()


def test_mcp_port_invalid_env(monkeypatch):
    """A non-integer port env falls back to the default."""
    monkeypatch.setenv("OPENBB_SEC_MCP_PORT", "not-a-number")
    assert mcp.mcp_port() == 7769


def test_ensure_mcp_subprocess_handles_launch_error(monkeypatch):
    """A failure to spawn the subprocess is swallowed and the handle cleared."""
    monkeypatch.setattr(mcp, "_mcp_process", None)
    monkeypatch.setattr(mcp, "_port_open", lambda *a: False)
    monkeypatch.setattr("atexit.register", lambda *a, **k: None)

    def _boom(*a, **kwargs):
        raise OSError("no exec")

    monkeypatch.setattr("subprocess.Popen", _boom)
    mcp.ensure_mcp_subprocess()
    assert mcp._mcp_process is None


def test_bounded_get_truncates(monkeypatch):
    """The bounded fetch stops once the byte limit is reached."""

    class _Resp:
        def iter_content(self, _n):
            yield b"a" * 40
            yield b"b" * 40

        def close(self):
            pass

    monkeypatch.setattr(
        "openbb_sec.utils.ratelimit.sec_make_request", lambda *a, **k: _Resp()
    )
    assert mcp._bounded_get("https://www.sec.gov/x.xml", 50) == b"a" * 40 + b"b" * 10


def test_document_to_markdown_financial_report(monkeypatch):
    """An XBRL _htm.xml renders via the financial-report assembler."""

    async def _fake_report(directory, *a, **k):
        return "<div class='ob-fr'>R</div>"

    monkeypatch.setattr(
        "openbb_sec.utils.financial_report.render_financial_report", _fake_report
    )
    monkeypatch.setattr(
        "openbb_sec.utils.html2markdown.html_to_markdown", lambda h, **k: "REPORT"
    )
    assert mcp.document_to_markdown("https://www.sec.gov/a/x_htm.xml") == "REPORT"


def test_document_to_markdown_structured_xml(monkeypatch):
    """ABS-EE asset data renders as structured tables."""
    monkeypatch.setattr(mcp, "_bounded_get", lambda u, n: b"<assetData/>")
    monkeypatch.setattr(
        "openbb_sec.utils.xml_render.render_xml_as_html", lambda c, **k: "<table/>"
    )
    monkeypatch.setattr(
        "openbb_sec.utils.html2markdown.html_to_markdown", lambda h, **k: "TABLES"
    )
    assert mcp.document_to_markdown("https://www.sec.gov/a/assets.xml") == "TABLES"


def test_document_to_markdown_xbrl_facts(monkeypatch):
    """An XBRL instance with no ABS-EE structure renders as facts tables."""
    monkeypatch.setattr(mcp, "_bounded_get", lambda u, n: b"<xbrl/>")
    monkeypatch.setattr(
        "openbb_sec.utils.xml_render.render_xml_as_html", lambda c, **k: None
    )
    monkeypatch.setattr(
        "openbb_sec.utils.xbrl_render.render_xbrl_facts", lambda c, **k: "<facts/>"
    )
    monkeypatch.setattr(
        "openbb_sec.utils.html2markdown.html_to_markdown", lambda h, **k: "FACTS"
    )
    assert mcp.document_to_markdown("https://www.sec.gov/a/data.xml") == "FACTS"


def test_document_to_markdown_plain_text(monkeypatch):
    """A plain-text document is returned verbatim."""
    monkeypatch.setattr(
        "openbb_sec.utils.cache.cached_bytes", lambda *a, **k: b"just text"
    )
    assert mcp.document_to_markdown("https://www.sec.gov/a/notes.txt") == "just text"
