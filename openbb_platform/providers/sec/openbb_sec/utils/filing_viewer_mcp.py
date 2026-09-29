"""MCP server backing the SEC Filing Viewer widget.

The server runs as a streamable-http subprocess, reverse-proxied through the
OpenBB API so the Workspace connects on the API's own host/port. The
streamable-http session manager must own its event loop and lifespan; mounting
it inside the API — whose lifespan it cannot extend — never finishes starting on
a real deployment, so it runs as its own process with a clean uvicorn lifecycle.
"""

from typing import Any

from fastapi import Depends
from starlette.requests import Request

_CURRENT: dict = {"url": None}

_MCP_HOST = "127.0.0.1"
_MCP_PATH = "/mcp"
_DEFAULT_MCP_PORT = 7769

_FORWARD_REQ_HEADERS = {
    "accept",
    "content-type",
    "mcp-session-id",
    "mcp-protocol-version",
}
_DROP_RESP_HEADERS = {
    "content-length",
    "transfer-encoding",
    "connection",
    "content-encoding",
}


def mcp_port() -> int:
    """Return the port the MCP subprocess listens on (``OPENBB_SEC_MCP_PORT``)."""
    import os

    try:
        return int(os.environ.get("OPENBB_SEC_MCP_PORT", str(_DEFAULT_MCP_PORT)))
    except ValueError:
        return _DEFAULT_MCP_PORT


def mcp_server_url() -> str:
    """Return the base URL of the local MCP subprocess."""
    return f"http://{_MCP_HOST}:{mcp_port()}"


def _port_open(host: str, port: int) -> bool:
    """Return True if something is already listening on host:port."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex((host, port)) == 0


def _bounded_get(url: str, limit: int) -> bytes:
    """Stream at most ``limit`` bytes so huge XML never loads in full."""
    import contextlib

    from openbb_sec.utils.definitions import SEC_HEADERS
    from openbb_sec.utils.ratelimit import sec_make_request

    headers = {**SEC_HEADERS, "Accept-Encoding": "identity"}
    resp = sec_make_request(url, headers=headers, stream=True, timeout=60)
    try:
        out = bytearray()
        for piece in resp.iter_content(65536):
            if piece:
                out += piece
            if len(out) >= limit:
                break
        return bytes(out[:limit])
    finally:
        with contextlib.suppress(Exception):
            resp.close()


def document_to_markdown(url: str) -> str:  # noqa: PLR0911
    """Return what the Filing Viewer shows for a document, as markdown.

    Mirrors the viewer's rendering: an XBRL instance becomes the as-filed
    financial report, ABS-EE asset data becomes its tables, HTML filings become
    markdown — so an agent reads the same thing the user sees.
    """
    import re

    from openbb_sec.utils.html2markdown import html_to_markdown

    if not url or not url.startswith(("https://www.sec.gov/", "https://efts.sec.gov/")):
        return "Only SEC EDGAR document URLs are supported."

    path = url.split("?", 1)[0].lower()
    directory = url.rsplit("/", 1)[0] + "/"
    limit = 5_000_000

    if path.endswith("_htm.xml"):
        import asyncio
        import contextlib

        from openbb_sec.utils.financial_report import render_financial_report

        report = None
        with contextlib.suppress(Exception):
            report = asyncio.run(render_financial_report(directory))
        if report:
            return html_to_markdown(report, base_url=directory)

    if path.endswith((".xml", ".xsd")):
        chunk = _bounded_get(url, limit)
        from openbb_sec.utils.xbrl_render import render_xbrl_facts
        from openbb_sec.utils.xml_render import render_xml_as_html

        structured = render_xml_as_html(chunk, source_url=url)
        if structured is not None:
            return html_to_markdown(structured, base_url=directory)
        facts = render_xbrl_facts(chunk, source_url=url)
        if facts is not None:
            return html_to_markdown(facts, base_url=directory)
        return chunk.decode("utf-8", errors="ignore")

    from openbb_sec.utils.cache import cached_bytes
    from openbb_sec.utils.definitions import SEC_HEADERS

    try:
        raw = cached_bytes(url, use_cache=True, headers=SEC_HEADERS) or b""
    except Exception as e:  # noqa: BLE001
        return f"Could not load the document: {e}"

    if path.endswith(".pdf") or raw[:5] == b"%PDF-":
        return f"This document is a PDF and is not convertible to text here: {url}"

    text = raw.decode("utf-8", errors="ignore")
    if path.endswith((".htm", ".html")) or re.search(
        r"(?i)<html|<body|<!doctype", text[:2000]
    ):
        return html_to_markdown(text, base_url=directory)
    return text


def get_filing_document(url: str | None = None) -> str:
    """Return the SEC filing document currently shown in the Filing Viewer."""
    target = url or _CURRENT["url"]
    if not target:
        return "No document is currently open in the Filing Viewer."
    return document_to_markdown(target)


def _build_mcp_server() -> Any:
    """Build the FastMCP server with the filing-viewer tools."""
    from fastmcp import FastMCP
    from starlette.responses import JSONResponse

    mcp: Any = FastMCP("SEC")
    mcp.tool(get_filing_document)

    @mcp.custom_route("/viewer-state", methods=["POST"])
    async def _set_viewer_state(request):
        """Record the URL of the document currently shown in the Filing Viewer."""
        import contextlib

        body: dict = {}
        with contextlib.suppress(Exception):
            body = await request.json()
        _CURRENT["url"] = (body or {}).get("url") or None
        return JSONResponse({"ok": True})

    return mcp


def build_mcp_app() -> Any:
    """Build the MCP ASGI app with CORS + Private Network Access headers."""
    from starlette.datastructures import Headers, MutableHeaders
    from starlette.middleware import Middleware

    expose = "mcp-session-id, mcp-protocol-version"

    class _Cors:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope["type"] != "http":
                await self.app(scope, receive, send)
                return
            headers = Headers(scope=scope)
            origin = headers.get("origin", "*")
            if (
                scope["method"] == "OPTIONS"
                and "access-control-request-method" in headers
            ):
                await send(
                    {
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [
                            (b"access-control-allow-origin", origin.encode()),
                            (b"access-control-allow-methods", b"*"),
                            (b"access-control-allow-headers", b"*"),
                            (b"access-control-allow-private-network", b"true"),
                            (b"access-control-max-age", b"600"),
                            (b"content-length", b"0"),
                        ],
                    }
                )
                await send({"type": "http.response.body", "body": b""})
                return

            async def _send(message):
                if message["type"] == "http.response.start":
                    out = MutableHeaders(scope=message)
                    out["access-control-allow-origin"] = origin
                    out["access-control-allow-private-network"] = "true"
                    out["access-control-expose-headers"] = expose
                await send(message)

            await self.app(scope, receive, _send)

    return _build_mcp_server().http_app(
        path=_MCP_PATH,
        middleware=[Middleware(_Cors)],
        json_response=True,
        transport="streamable-http",
    )


_mcp_process: Any = None


def ensure_mcp_subprocess() -> None:
    """Launch the MCP server in its own process (idempotent).

    The streamable-http session manager must own its event loop and lifespan, so
    it cannot be mounted in-process. Running it as a subprocess gives it a clean
    uvicorn lifecycle; the port-in-use guard keeps this safe across API workers.
    """
    global _mcp_process  # noqa: PLW0603 - process-wide singleton
    import atexit
    import os
    import subprocess
    import sys

    if _mcp_process is not None and _mcp_process.poll() is None:
        return
    port = mcp_port()
    if _port_open(_MCP_HOST, port):
        return  # already serving (this run or another worker)
    try:
        # Hand the child the parent's import paths so it can find the package even
        # in a dev checkout where it is path-injected rather than pip-installed.
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(p for p in sys.path if p)
        _mcp_process = subprocess.Popen(  # noqa: S603
            [
                sys.executable,
                "-m",
                "openbb_sec.utils.filing_viewer_mcp",
                "--host",
                _MCP_HOST,
                "--port",
                str(port),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        atexit.register(stop_mcp_subprocess)
    except Exception:  # noqa: BLE001
        _mcp_process = None


def stop_mcp_subprocess() -> None:
    """Terminate the MCP subprocess if this process started it."""
    global _mcp_process  # noqa: PLW0603 - process-wide singleton
    if _mcp_process is not None and _mcp_process.poll() is None:
        _mcp_process.terminate()
    _mcp_process = None


async def _await_ready(timeout: float = 10.0) -> bool:
    """Poll until the MCP subprocess is accepting connections."""
    import asyncio

    for _ in range(max(1, int(timeout / 0.2))):
        if _port_open(_MCP_HOST, mcp_port()):
            return True
        await asyncio.sleep(0.2)
    return False


async def _extract_mcp_request(request: Request) -> dict:
    """Pull plain values out of the request.

    The OpenBB router wraps endpoints as commands and deep-copies their kwargs; a
    starlette ``Request`` cannot be deep-copied (it walks the app ``State`` and
    recurses on Python 3.14), so the proxy takes this plain dict via a dependency
    instead of the ``Request`` itself.
    """
    return {
        "method": request.method,
        "body": await request.body(),
        "headers": {
            k: v
            for k, v in request.headers.items()
            if k.lower() in _FORWARD_REQ_HEADERS
        },
        "query": dict(request.query_params),
    }


async def mcp_reverse_proxy(
    path: str, data: dict = Depends(_extract_mcp_request)
) -> Any:
    """Proxy an MCP request to the local subprocess, streaming the response.

    Lets the Workspace connect at the OpenBB API's own host/port — the subprocess
    is an internal detail — while the subprocess still owns the streamable-http
    lifecycle that an in-process mount could not start. Both ``/mcp`` (the MCP
    transport) and ``/viewer-state`` (the iframe's current-document ping) are
    forwarded; the session-id header is exposed so the browser carries it.
    """
    import aiohttp
    from starlette.responses import JSONResponse, StreamingResponse

    ensure_mcp_subprocess()
    if not await _await_ready():
        return JSONResponse({"error": "MCP server failed to start"}, status_code=503)

    # No total/read cap: the server->client SSE stream is long-lived and must not
    # be aborted by aiohttp's default 300s timeout.
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None))
    try:
        upstream = await session.request(
            data["method"],
            f"{mcp_server_url()}/{path}",
            headers=data["headers"],
            data=data["body"] or None,
            params=data["query"],
        )
    except aiohttp.ClientError as exc:
        await session.close()
        return JSONResponse({"error": f"MCP proxy error: {exc}"}, status_code=502)

    out_headers = {
        k: v for k, v in upstream.headers.items() if k.lower() not in _DROP_RESP_HEADERS
    }
    out_headers["access-control-expose-headers"] = "mcp-session-id, Mcp-Session-Id"

    async def _stream() -> Any:
        try:
            async for chunk in upstream.content.iter_any():
                yield chunk
        finally:
            upstream.release()
            await session.close()

    return StreamingResponse(
        _stream(), status_code=upstream.status, headers=out_headers
    )


def _exit_when_orphaned() -> None:
    """Exit if the parent API process goes away.

    The launcher cannot fire ``atexit`` when uvicorn SIGKILLs its workers on a
    reload, which would otherwise leave this server running forever. Polling the
    parent pid lets the subprocess clean itself up so reloads never accumulate
    abandoned MCP servers.
    """
    import os
    import threading
    import time

    parent = os.getppid()

    def _watch() -> None:
        while True:
            time.sleep(2)
            if os.getppid() != parent:  # reparented → the launcher died
                os._exit(0)

    threading.Thread(target=_watch, daemon=True).start()


def _serve(host: str, port: int) -> None:
    """Run the MCP streamable-http server — the subprocess entry point."""
    import uvicorn

    _exit_when_orphaned()
    uvicorn.run(build_mcp_app(), host=host, port=port, log_level="warning")


if __name__ == "__main__":  # pragma: no cover - subprocess entry point
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=_MCP_HOST)
    parser.add_argument("--port", type=int, default=mcp_port())
    args = parser.parse_args()
    _serve(args.host, args.port)
