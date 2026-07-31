import runpy
import socket
import sys
import types

import pytest
from starlette.requests import Request

from openbb_us_eia import eia_mcp


@pytest.fixture(autouse=True)
def reset_process():
    prev = eia_mcp._mcp_process
    eia_mcp._mcp_process = None
    yield
    eia_mcp._mcp_process = prev


def _request(method="GET", query="", body=b"", headers=None):
    headers = headers or []

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    return Request(
        scope={
            "type": "http",
            "method": method,
            "scheme": "http",
            "server": ("test", 80),
            "path": "/api/v1/eia/eia_mcp",
            "query_string": query.encode(),
            "headers": headers,
        },
        receive=receive,
    )


def test_mcp_port_from_env(monkeypatch):
    monkeypatch.setenv("OPENBB_EIA_MCP_PORT", "7777")
    assert eia_mcp.mcp_port() == 7777


def test_mcp_port_invalid_env(monkeypatch):
    monkeypatch.setenv("OPENBB_EIA_MCP_PORT", "bad")
    assert eia_mcp.mcp_port() == eia_mcp._DEFAULT_MCP_PORT


def test_mcp_server_url(monkeypatch):
    monkeypatch.setenv("OPENBB_EIA_MCP_PORT", "7001")
    assert eia_mcp.mcp_server_url() == "http://127.0.0.1:7001/mcp"


def test_port_open_true_and_false():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        host, port = s.getsockname()
        assert eia_mcp._port_open(host, port) is True
    assert eia_mcp._port_open(host, port) is False


def test_api_state_url(monkeypatch):
    monkeypatch.setenv("OPENBB_API_HOST", "127.0.0.9")
    monkeypatch.setenv("OPENBB_API_PORT", "7770")
    assert eia_mcp._api_state_url("electricity", "u9").startswith(
        "http://127.0.0.9:7770/api/v1/eia/eia_mcp_state?browser=electricity&user=u9"
    )


def test_ensure_mcp_subprocess_skips_when_running():
    class Proc:
        def poll(self):
            return None

    eia_mcp._mcp_process = Proc()
    eia_mcp.ensure_mcp_subprocess()
    assert isinstance(eia_mcp._mcp_process, Proc)


def test_ensure_mcp_subprocess_skips_when_port_open(monkeypatch):
    called = {"popen": False}

    def fake_open(_h, _p):
        return True

    def fake_popen(*_a, **_k):
        called["popen"] = True
        raise AssertionError("should not run")

    monkeypatch.setattr(eia_mcp, "_port_open", fake_open)
    monkeypatch.setattr("subprocess.Popen", fake_popen)
    eia_mcp.ensure_mcp_subprocess()
    assert called["popen"] is False


def test_ensure_mcp_subprocess_launches(monkeypatch):
    reg = {"called": False}

    class Proc:
        def poll(self):
            return None

    def fake_open(_h, _p):
        return False

    def fake_popen(*_a, **_k):
        return Proc()

    def fake_register(_fn):
        reg["called"] = True

    monkeypatch.setattr(eia_mcp, "_port_open", fake_open)
    monkeypatch.setattr("subprocess.Popen", fake_popen)
    monkeypatch.setattr("atexit.register", fake_register)
    eia_mcp.ensure_mcp_subprocess()
    assert eia_mcp._mcp_process is not None
    assert reg["called"] is True


def test_ensure_mcp_subprocess_handles_launch_error(monkeypatch):
    def fake_open(_h, _p):
        return False

    def fake_popen(*_a, **_k):
        raise RuntimeError("boom")

    monkeypatch.setattr(eia_mcp, "_port_open", fake_open)
    monkeypatch.setattr("subprocess.Popen", fake_popen)
    eia_mcp.ensure_mcp_subprocess()
    assert eia_mcp._mcp_process is None


def test_stop_mcp_subprocess_terminates():
    class Proc:
        def __init__(self):
            self.terminated = False

        def poll(self):
            return None

        def terminate(self):
            self.terminated = True

    proc = Proc()
    eia_mcp._mcp_process = proc
    eia_mcp.stop_mcp_subprocess()
    assert proc.terminated is True
    assert eia_mcp._mcp_process is None


@pytest.mark.asyncio
async def test_await_ready_true(monkeypatch):
    seq = iter([False, False, True])

    def fake_open(_h, _p):
        return next(seq)

    async def fake_sleep(_t):
        return None

    monkeypatch.setattr(eia_mcp, "_port_open", fake_open)
    monkeypatch.setattr("asyncio.sleep", fake_sleep)
    assert await eia_mcp._await_ready(timeout=1.0) is True


@pytest.mark.asyncio
async def test_await_ready_false(monkeypatch):
    def fake_open(_h, _p):
        return False

    async def fake_sleep(_t):
        return None

    monkeypatch.setattr(eia_mcp, "_port_open", fake_open)
    monkeypatch.setattr("asyncio.sleep", fake_sleep)
    assert await eia_mcp._await_ready(timeout=0.4) is False


@pytest.mark.asyncio
async def test_extract_mcp_request_filters_headers():
    req = _request(
        method="POST",
        query="a=1",
        body=b"{}",
        headers=[
            (b"accept", b"application/json"),
            (b"x-openbb-user", b"alice@example.com"),
            (b"authorization", b"secret"),
        ],
    )
    out = await eia_mcp._extract_mcp_request(req)
    assert out["method"] == "POST"
    assert out["body"] == b"{}"
    assert out["query"] == {"a": "1"}
    assert "accept" in out["headers"]
    assert "x-openbb-user" in out["headers"]
    assert "authorization" not in out["headers"]


@pytest.mark.asyncio
async def test_mcp_reverse_proxy_startup_failure(monkeypatch):
    monkeypatch.setattr(eia_mcp, "ensure_mcp_subprocess", lambda: None)

    async def not_ready():
        return False

    monkeypatch.setattr(eia_mcp, "_await_ready", not_ready)
    resp = await eia_mcp.mcp_reverse_proxy(_request())
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_mcp_reverse_proxy_client_error(monkeypatch):
    import aiohttp

    monkeypatch.setattr(eia_mcp, "ensure_mcp_subprocess", lambda: None)

    async def ready():
        return True

    monkeypatch.setattr(eia_mcp, "_await_ready", ready)

    class Session:
        def __init__(self, **_k):
            self.closed = False

        async def request(self, *_a, **_k):
            raise aiohttp.ClientError("x")

        async def close(self):
            self.closed = True

    monkeypatch.setattr("aiohttp.ClientSession", Session)
    resp = await eia_mcp.mcp_reverse_proxy(_request())
    assert resp.status_code == 502


@pytest.mark.asyncio
async def test_mcp_reverse_proxy_stream_success(monkeypatch):
    monkeypatch.setattr(eia_mcp, "ensure_mcp_subprocess", lambda: None)

    async def ready():
        return True

    monkeypatch.setattr(eia_mcp, "_await_ready", ready)

    state = {"released": False, "closed": False}

    class Content:
        async def iter_any(self):
            yield b"a"
            yield b"b"

    class Upstream:
        status = 207
        headers = {
            "content-type": "application/json",
            "x-test": "ok",
            "content-length": "2",
        }
        content = Content()

        def release(self):
            state["released"] = True

    class Session:
        def __init__(self, **_k):
            pass

        async def request(self, *_a, **_k):
            return Upstream()

        async def close(self):
            state["closed"] = True

    monkeypatch.setattr("aiohttp.ClientSession", Session)
    resp = await eia_mcp.mcp_reverse_proxy(_request())
    body = b""
    async for chunk in resp.body_iterator:
        body += chunk
    assert resp.status_code == 207
    assert resp.headers.get("x-test") == "ok"
    assert "content-length" not in resp.headers
    assert body == b"ab"
    assert state["released"] is True
    assert state["closed"] is True


@pytest.mark.asyncio
async def test_mcp_reverse_proxy_stream_iter_error(monkeypatch):
    import aiohttp

    monkeypatch.setattr(eia_mcp, "ensure_mcp_subprocess", lambda: None)

    async def ready():
        return True

    monkeypatch.setattr(eia_mcp, "_await_ready", ready)

    state = {"released": False, "closed": False}

    class Content:
        async def iter_any(self):
            raise aiohttp.ClientError("x")
            yield b"x"

    class Upstream:
        status = 200
        headers = {"content-type": "application/json"}
        content = Content()

        def release(self):
            state["released"] = True

    class Session:
        def __init__(self, **_k):
            pass

        async def request(self, *_a, **_k):
            return Upstream()

        async def close(self):
            state["closed"] = True

    monkeypatch.setattr("aiohttp.ClientSession", Session)
    resp = await eia_mcp.mcp_reverse_proxy(_request())
    body = b""
    async for chunk in resp.body_iterator:
        body += chunk
    assert body == b""
    assert state["released"] is True
    assert state["closed"] is True


def test_serve_wires_and_runs(monkeypatch):
    calls = {"middleware": False, "exit": False, "run": False}

    class App:
        def add_middleware(self, *_a, **_k):
            calls["middleware"] = True

    class M:
        def http_app(self, **_k):
            return App()

    def fake_build():
        return M()

    def fake_exit_when_orphaned():
        calls["exit"] = True

    monkeypatch.setattr(eia_mcp, "_build_mcp_server", fake_build)
    monkeypatch.setattr(eia_mcp, "_exit_when_orphaned", fake_exit_when_orphaned)

    def fake_run(_app, host, port, log_level):
        calls["run"] = host == "127.0.0.1" and port == 7000 and log_level == "warning"

    monkeypatch.setattr("uvicorn.run", fake_run)
    eia_mcp._serve("127.0.0.1", 7000)
    assert calls == {"middleware": True, "exit": True, "run": True}


def test_exit_when_orphaned_starts_watcher(monkeypatch):
    calls = {"thread": False, "target": None, "daemon": None}

    class T:
        def __init__(self, target=None, daemon=None):
            calls["target"] = target
            calls["daemon"] = daemon

        def start(self):
            calls["thread"] = True

    monkeypatch.setattr("os.getppid", lambda: 123)
    monkeypatch.setattr("threading.Thread", T)
    eia_mcp._exit_when_orphaned()
    assert calls["thread"] is True
    assert calls["daemon"] is True
    assert callable(calls["target"])


def test_exit_when_orphaned_watch_exits(monkeypatch):
    calls = {"target": None, "sleep": 0, "exit": None}

    class ExitNow(Exception):
        pass

    seq = iter([300, 301])

    class T:
        def __init__(self, target=None, daemon=None):
            calls["target"] = target

        def start(self):
            return None

    def fake_sleep(_t):
        calls["sleep"] += 1

    def fake_exit(code):
        calls["exit"] = code
        raise ExitNow

    monkeypatch.setattr("os.getppid", lambda: next(seq))
    monkeypatch.setattr("threading.Thread", T)
    monkeypatch.setattr("time.sleep", fake_sleep)
    monkeypatch.setattr("os._exit", fake_exit)
    eia_mcp._exit_when_orphaned()
    with pytest.raises(ExitNow):
        calls["target"]()
    assert calls["sleep"] == 1
    assert calls["exit"] == 0


@pytest.mark.asyncio
async def test_build_mcp_server_tool_returns_rows(monkeypatch):
    seen = {}

    class FMCP:
        def __init__(self, **_k):
            self.tool_fn = None

        def tool(self, fn):
            self.tool_fn = fn
            return fn

    monkeypatch.setitem(
        __import__("sys").modules, "fastmcp", types.SimpleNamespace(FastMCP=FMCP)
    )

    class Resp:
        status = 200

        async def read(self):
            return b'[{"x":1}]'

    class Ctx:
        async def __aenter__(self):
            return Resp()

        async def __aexit__(self, *_a):
            return False

    class Session:
        def __init__(self, **_k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_a):
            return False

        def get(self, url):
            seen["url"] = url
            return Ctx()

    monkeypatch.setattr("aiohttp.ClientSession", Session)
    monkeypatch.setitem(
        __import__("sys").modules,
        "fastmcp.server.dependencies",
        types.SimpleNamespace(
            get_http_headers=lambda include=None: {"x-openbb-user": "x@x.com"}
        ),
    )
    monkeypatch.setattr(eia_mcp, "_api_state_url", lambda b, u: f"http://x/{b}/{u}")
    mcp = eia_mcp._build_mcp_server()
    rows = await mcp.tool_fn("electricity")
    assert rows == [{"x": 1}]
    assert seen["url"].startswith("http://x/electricity/")


@pytest.mark.asyncio
async def test_build_mcp_server_tool_non_200(monkeypatch):
    class FMCP:
        def __init__(self, **_k):
            self.tool_fn = None

        def tool(self, fn):
            self.tool_fn = fn
            return fn

    monkeypatch.setitem(
        __import__("sys").modules, "fastmcp", types.SimpleNamespace(FastMCP=FMCP)
    )

    class Resp:
        status = 500

        async def read(self):
            return b"[]"

    class Ctx:
        async def __aenter__(self):
            return Resp()

        async def __aexit__(self, *_a):
            return False

    class Session:
        def __init__(self, **_k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_a):
            return False

        def get(self, _url):
            return Ctx()

    monkeypatch.setattr("aiohttp.ClientSession", Session)
    monkeypatch.setitem(
        __import__("sys").modules,
        "fastmcp.server.dependencies",
        types.SimpleNamespace(get_http_headers=lambda include=None: {}),
    )
    mcp = eia_mcp._build_mcp_server()
    assert await mcp.tool_fn("coal") == []


@pytest.mark.asyncio
async def test_build_mcp_server_tool_non_list_payload(monkeypatch):
    class FMCP:
        def __init__(self, **_k):
            self.tool_fn = None

        def tool(self, fn):
            self.tool_fn = fn
            return fn

    monkeypatch.setitem(
        __import__("sys").modules, "fastmcp", types.SimpleNamespace(FastMCP=FMCP)
    )

    class Resp:
        status = 200

        async def read(self):
            return b'{"x":1}'

    class Ctx:
        async def __aenter__(self):
            return Resp()

        async def __aexit__(self, *_a):
            return False

    class Session:
        def __init__(self, **_k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_a):
            return False

        def get(self, _url):
            return Ctx()

    monkeypatch.setattr("aiohttp.ClientSession", Session)
    monkeypatch.setitem(
        __import__("sys").modules,
        "fastmcp.server.dependencies",
        types.SimpleNamespace(get_http_headers=lambda include=None: {}),
    )
    mcp = eia_mcp._build_mcp_server()
    assert await mcp.tool_fn("coal") == []


@pytest.mark.asyncio
async def test_build_mcp_server_tool_invalid_json(monkeypatch):
    class FMCP:
        def __init__(self, **_k):
            self.tool_fn = None

        def tool(self, fn):
            self.tool_fn = fn
            return fn

    monkeypatch.setitem(
        __import__("sys").modules, "fastmcp", types.SimpleNamespace(FastMCP=FMCP)
    )

    class Resp:
        status = 200

        async def read(self):
            return b"{"

    class Ctx:
        async def __aenter__(self):
            return Resp()

        async def __aexit__(self, *_a):
            return False

    class Session:
        def __init__(self, **_k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_a):
            return False

        def get(self, _url):
            return Ctx()

    monkeypatch.setattr("aiohttp.ClientSession", Session)
    monkeypatch.setitem(
        __import__("sys").modules,
        "fastmcp.server.dependencies",
        types.SimpleNamespace(get_http_headers=lambda include=None: {}),
    )
    mcp = eia_mcp._build_mcp_server()
    assert await mcp.tool_fn("coal") == []


def test_module_main_invokes_serve(monkeypatch):
    calls = {"run": False}

    class App:
        def add_middleware(self, *_a, **_k):
            return None

    class FMCP:
        def __init__(self, **_k):
            self.tool_fn = None

        def tool(self, fn):
            self.tool_fn = fn
            return fn

        def http_app(self, **_k):
            return App()

    monkeypatch.setitem(sys.modules, "fastmcp", types.SimpleNamespace(FastMCP=FMCP))
    monkeypatch.setitem(
        sys.modules,
        "starlette.middleware.cors",
        types.SimpleNamespace(CORSMiddleware=object),
    )
    monkeypatch.setitem(
        sys.modules,
        "uvicorn",
        types.SimpleNamespace(run=lambda *_a, **_k: calls.__setitem__("run", True)),
    )
    monkeypatch.setattr(sys, "argv", ["eia_mcp.py"])
    monkeypatch.setattr("threading.Thread.start", lambda self: None)
    source = eia_mcp.__file__
    runpy.run_path(source, run_name="__main__")
    assert calls["run"] is True
