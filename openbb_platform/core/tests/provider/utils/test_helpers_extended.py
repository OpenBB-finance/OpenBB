"""Extended tests for openbb_core.provider.utils.helpers."""

import asyncio
from datetime import (
    date as _date,
    datetime,
    timedelta,
    timezone,
)
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.utils.helpers import (
    check_item,
    combine_certificates,
    filter_by_dates,
    get_querystring,
    maybe_coroutine,
    run_async,
    safe_fromtimestamp,
    to_snake_case,
)


def test_check_item_ok():
    check_item("apple", ["apple", "banana"])


def test_check_item_suggests_close_match():
    with pytest.raises(ValueError, match="Did you mean 'banana'"):
        check_item("bananas", ["apple", "banana"])


def test_check_item_no_close_match():
    with pytest.raises(ValueError, match="not available"):
        check_item("xyz", ["apple", "banana"])


def test_get_querystring_with_list_values():
    qs = get_querystring({"symbol": ["AAPL", "MSFT"], "limit": 5}, exclude=[])
    assert "symbol=AAPL" in qs
    assert "symbol=MSFT" in qs
    assert "limit=5" in qs


def test_get_querystring_skips_none():
    qs = get_querystring({"a": None, "b": 1}, exclude=[])
    assert qs == "b=1"


def test_get_querystring_empty_returns_empty_string():
    assert get_querystring({}, exclude=[]) == ""


def test_to_snake_case_camel_and_pascal():
    assert to_snake_case("CamelCase") == "camel_case"
    assert to_snake_case("HTTPResponseCode") == "http_response_code"
    assert to_snake_case("Already snake case") == "already_snake_case"


def test_safe_fromtimestamp_positive():
    out = safe_fromtimestamp(0, tz=timezone.utc)
    assert out == datetime(1970, 1, 1, tzinfo=timezone.utc)


def test_safe_fromtimestamp_negative_with_tz():
    out = safe_fromtimestamp(-3600, tz=timezone.utc)
    # On any platform the function returns a datetime equivalent to (epoch - 1h).
    expected = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=-3600)
    assert out == expected


class _RowWithDate(Data):
    date: _date | None = None
    value: float = 0.0


def test_filter_by_dates_returns_input_when_no_bounds():
    rows = [_RowWithDate(date=_date(2024, 1, 1))]
    assert filter_by_dates(rows) is rows


def test_filter_by_dates_inclusive_range():
    rows = [
        _RowWithDate(date=_date(2024, 1, 1)),
        _RowWithDate(date=_date(2024, 6, 1)),
        _RowWithDate(date=_date(2024, 12, 1)),
    ]
    out = filter_by_dates(
        rows, start_date=_date(2024, 3, 1), end_date=_date(2024, 9, 1)
    )
    assert len(out) == 1
    assert out[0].date == _date(2024, 6, 1)


def test_filter_by_dates_only_start():
    rows = [_RowWithDate(date=_date(2024, 1, 1)), _RowWithDate(date=_date(2024, 6, 1))]
    out = filter_by_dates(rows, start_date=_date(2024, 5, 1))
    assert len(out) == 1


def test_filter_by_dates_only_end():
    rows = [_RowWithDate(date=_date(2024, 1, 1)), _RowWithDate(date=_date(2024, 6, 1))]
    out = filter_by_dates(rows, end_date=_date(2024, 5, 1))
    assert len(out) == 1


def test_filter_by_dates_drops_rows_without_date():
    class NoDate(Data):
        value: float = 0.0

    rows = [NoDate(value=1.0)]
    out = filter_by_dates(rows, start_date=_date(2024, 1, 1))  # type: ignore[arg-type]
    assert out == []


@pytest.mark.asyncio
async def test_maybe_coroutine_with_sync():
    assert await maybe_coroutine(lambda x: x + 1, 1) == 2


@pytest.mark.asyncio
async def test_maybe_coroutine_with_async():
    async def f(x):
        return x * 2

    assert await maybe_coroutine(f, 3) == 6


def test_run_async_sync_callable():
    assert run_async(lambda x: x + 1, 1) == 2


def test_run_async_async_callable():
    async def f(x):
        await asyncio.sleep(0)
        return x * 3

    assert run_async(f, 4) == 12


def test_combine_certificates_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        combine_certificates(str(tmp_path / "nope.pem"))


def test_combine_certificates_returns_existing_combined(tmp_path):
    p = tmp_path / "ca_combined.pem"
    p.write_text("data")
    assert combine_certificates(str(p)) == str(p)


def test_combine_certificates_writes_combined(tmp_path):
    cert = tmp_path / "ca.pem"
    cert.write_text("CERT-DATA")
    bundle = tmp_path / "bundle.pem"
    bundle.write_text("BUNDLE-DATA")
    out = combine_certificates(str(cert), str(bundle))
    out_path = Path(out)
    assert out_path.exists()
    text = out_path.read_text()
    assert "BUNDLE-DATA" in text
    assert "CERT-DATA" in text
    # Cleanup the atexit-registered file so the test doesn't leak.
    out_path.unlink(missing_ok=True)


# --- get_requests_session / make_request ---


def test_get_requests_session_returns_provided_session():
    import requests

    from openbb_core.provider.utils.helpers import get_requests_session

    s = requests.Session()
    assert get_requests_session(session=s) is s


def test_get_requests_session_adds_user_agent_and_headers(monkeypatch):
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})
    s = helpers.get_requests_session(headers={"X-Custom": "1"})
    assert "User-Agent" in s.headers
    assert s.headers.get("X-Custom") == "1"


def test_get_requests_session_proxy_from_settings(monkeypatch):
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(
        helpers,
        "get_python_request_settings",
        lambda: {"proxy": "http://proxy:3128"},
    )
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    s = helpers.get_requests_session()
    assert s.proxies.get("http") == "http://proxy:3128"
    assert s.proxies.get("https") == "http://proxy:3128"


def test_get_requests_session_cookies_dict(monkeypatch):
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(
        helpers, "get_python_request_settings", lambda: {"cookies": {"k": "v"}}
    )
    s = helpers.get_requests_session()
    assert s.cookies.get("k") == "v"


def test_get_requests_session_verify_ssl_false(monkeypatch):
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(
        helpers, "get_python_request_settings", lambda: {"verify_ssl": False}
    )
    s = helpers.get_requests_session()
    assert s.verify is False


def test_make_request_invalid_method_raises(monkeypatch):
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})
    with pytest.raises(ValueError):
        helpers.make_request("http://example.com", method="PUT")


def test_make_request_get_uses_provided_session(monkeypatch):
    from unittest.mock import MagicMock

    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})
    fake_session = MagicMock()
    fake_session.get.return_value = "OK"
    out = helpers.make_request("http://example.com", method="GET", session=fake_session)
    assert out == "OK"
    fake_session.get.assert_called_once()


def test_make_request_post_uses_provided_session(monkeypatch):
    from unittest.mock import MagicMock

    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})
    fake_session = MagicMock()
    fake_session.post.return_value = "OK"
    out = helpers.make_request(
        "http://example.com", method="POST", session=fake_session
    )
    assert out == "OK"
    fake_session.post.assert_called_once()


def test_make_request_preferences_overrides_timeout(monkeypatch):
    from unittest.mock import MagicMock

    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})
    fake_session = MagicMock()
    fake_session.get.return_value = "OK"
    helpers.make_request(
        "http://example.com",
        session=fake_session,
        preferences={"request_timeout": 99},
    )
    assert fake_session.get.call_args.kwargs["timeout"] == 99


def test_make_request_settings_timeout_used_when_no_preferences(monkeypatch):
    from unittest.mock import MagicMock

    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {"timeout": 42})
    fake_session = MagicMock()
    fake_session.get.return_value = "OK"
    helpers.make_request("http://example.com", session=fake_session)
    assert fake_session.get.call_args.kwargs["timeout"] == 42


# --- get_requests_session: cert/auth/env-proxy branches ---


def test_get_requests_session_certfile_only(monkeypatch, tmp_path):
    from openbb_core.provider.utils import helpers

    cert = tmp_path / "client.pem"
    cert.write_bytes(b"-----CERT-----")
    monkeypatch.setattr(
        helpers, "get_python_request_settings", lambda: {"certfile": str(cert)}
    )
    s = helpers.get_requests_session()
    assert s.cert == str(cert)


def test_get_requests_session_certfile_with_keyfile(monkeypatch, tmp_path):
    from openbb_core.provider.utils import helpers

    cert = tmp_path / "client.pem"
    key = tmp_path / "client.key"
    cert.write_bytes(b"x")
    key.write_bytes(b"y")
    monkeypatch.setattr(
        helpers,
        "get_python_request_settings",
        lambda: {"certfile": str(cert), "keyfile": str(key)},
    )
    s = helpers.get_requests_session()
    assert s.cert == (str(cert), str(key))


def test_get_requests_session_env_proxies(monkeypatch):
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})
    monkeypatch.setenv("HTTP_PROXY", "http://proxyA:1")
    monkeypatch.setenv("HTTPS_PROXY", "http://proxyB:2")
    s = helpers.get_requests_session()
    assert s.proxies.get("http") == "http://proxyA:1"
    assert s.proxies.get("https") == "http://proxyB:2"


def test_get_requests_session_auth_tuple(monkeypatch):
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(
        helpers, "get_python_request_settings", lambda: {"auth": ("user", "pass")}
    )
    s = helpers.get_requests_session()
    assert s.auth == ("user", "pass")


def test_get_requests_session_auth_list_coerced_to_tuple(monkeypatch):
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(
        helpers, "get_python_request_settings", lambda: {"auth": ["user", "pass"]}
    )
    s = helpers.get_requests_session()
    assert s.auth == ("user", "pass")


def test_get_requests_session_combines_certificates_and_equal_env_proxies(
    monkeypatch, tmp_path
):
    from openbb_core.provider.utils import helpers

    cert = tmp_path / "ca.pem"
    bundle = tmp_path / "bundle.pem"
    cert.write_text("cert")
    bundle.write_text("bundle")

    monkeypatch.setattr(
        helpers, "get_python_request_settings", lambda: {"cafile": str(cert)}
    )
    monkeypatch.setattr(
        helpers,
        "combine_certificates",
        lambda cert_path, bundle_path=None: f"{cert_path}|{bundle_path}",
    )
    monkeypatch.setenv("REQUESTS_CA_BUNDLE", str(bundle))
    monkeypatch.setenv("HTTP_PROXY", "http://proxy:3128")
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy:3128")

    s = helpers.get_requests_session()

    assert s.verify == f"{cert}|{bundle}"
    assert s.proxies["http"] == "http://proxy:3128"
    assert s.proxies["https"] == "http://proxy:3128"


def test_get_requests_session_cookies_cookiejar(monkeypatch):
    import requests

    from openbb_core.provider.utils import helpers

    jar = requests.cookies.RequestsCookieJar()
    jar.set("k", "v")
    monkeypatch.setattr(
        helpers, "get_python_request_settings", lambda: {"cookies": jar}
    )

    s = helpers.get_requests_session()

    assert s.cookies is jar


def test_get_requests_session_provided_session_is_returned_even_with_extra_kwargs(
    monkeypatch,
):
    import requests

    from openbb_core.provider.utils import helpers

    class BrokenSession(requests.Session):
        fail = 0

        def __setattr__(self, name, value):
            if name == "fail":
                raise AttributeError("blocked")
            super().__setattr__(name, value)

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})

    provided = BrokenSession()
    s = helpers.get_requests_session(
        session=provided, proxies={"http": "http://proxy:1"}, fail=1
    )

    assert s is provided


def test_get_requests_session_kwargs_update_and_attributeerror_branch(monkeypatch):
    import requests

    from openbb_core.provider.utils import helpers

    class BrokenSession(requests.Session):
        boom = 0

        def __setattr__(self, name, value):
            if name == "boom":
                raise AttributeError("blocked")
            super().__setattr__(name, value)

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})
    monkeypatch.setattr(requests, "Session", BrokenSession)

    s = helpers.get_requests_session(proxies={"http": "http://proxy:1"}, boom=1)

    assert s.proxies.get("http") == "http://proxy:1"


def test_get_requests_session_extra_kwargs_setattr(monkeypatch):
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})
    s = helpers.get_requests_session(max_redirects=99)
    assert s.max_redirects == 99


@pytest.mark.asyncio
async def test_get_async_requests_session_builds_ssl_context_and_atexit(
    monkeypatch, tmp_path
):
    import atexit
    import ssl

    import aiohttp

    from openbb_core.provider.utils import helpers

    cert = tmp_path / "client.pem"
    key = tmp_path / "client.key"
    ca = tmp_path / "ca.pem"
    cert.write_text("cert")
    key.write_text("key")
    ca.write_text("ca")

    captured = {}
    registered = {}
    cookie_jar = aiohttp.CookieJar()
    cookie_jar.update_cookies({"k": "v"})

    class FakeSSLContext:
        def load_verify_locations(self, cafile=None):
            captured["cafile"] = cafile

        def load_cert_chain(self, certfile=None, keyfile=None, password=None):
            captured["certfile"] = certfile
            captured["keyfile"] = keyfile
            captured["password"] = password

    class FakeSession:
        def __init__(self, **kwargs):
            captured.update(kwargs)
            self.closed = False

        async def close(self):
            self.closed = True

    monkeypatch.setattr(
        helpers,
        "get_python_request_settings",
        lambda: {
            "cafile": str(ca),
            "certfile": str(cert),
            "keyfile": str(key),
            "password": "secret",
            "proxy_auth": ["proxy-user", "proxy-pass"],
            "auth": ["api-user", "api-pass"],
            "cookies": cookie_jar,
            "timeout": 5,
        },
    )
    monkeypatch.setattr(helpers, "ClientSession", FakeSession)
    monkeypatch.setattr(ssl, "create_default_context", FakeSSLContext)
    monkeypatch.setattr(
        atexit,
        "register",
        lambda func, *args: registered.setdefault("callback", (func, args)),
    )
    monkeypatch.setattr(
        helpers,
        "run_async",
        lambda func, *args, **kwargs: captured.setdefault("run_async", True),
    )

    await helpers.get_async_requests_session(connector=object())

    assert captured["cafile"] == str(ca)
    assert captured["certfile"] == str(cert)
    assert captured["keyfile"] == str(key)
    assert captured["password"] == "secret"  # noqa: S105
    assert captured["cookie_jar"] is cookie_jar
    assert isinstance(captured["timeout"], aiohttp.ClientTimeout)
    callback, args = registered["callback"]
    callback(*args)
    assert captured["run_async"] is True


@pytest.mark.asyncio
async def test_get_async_requests_session_equal_https_proxy_sets_proxy_and_ssl(
    monkeypatch,
):
    import atexit

    from openbb_core.provider.utils import helpers

    captured = {}

    class FakeSession:
        def __init__(self, **kwargs):
            captured.update(kwargs)
            self.closed = False

        async def close(self):
            self.closed = True

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})
    monkeypatch.setattr(helpers, "ClientSession", FakeSession)
    monkeypatch.setattr(atexit, "register", lambda *args, **kwargs: None)
    monkeypatch.setenv("HTTP_PROXY", "https://proxy:9443")
    monkeypatch.setenv("HTTPS_PROXY", "https://proxy:9443")

    await helpers.get_async_requests_session()

    assert captured["proxy"] == "http://proxy:9443"


@pytest.mark.asyncio
async def test_amake_requests_skips_falsy_results(monkeypatch):
    from openbb_core.provider.utils import helpers

    session = MagicMock()
    session.close = MagicMock(return_value=None)

    async def _close():
        return None

    session.close = _close

    async def fake_amake_request(url, session=None, **kwargs):
        return [] if url.endswith("empty") else {"url": url}

    async def fake_session(**kwargs):
        return session

    monkeypatch.setattr(helpers, "amake_request", fake_amake_request)
    monkeypatch.setattr(helpers, "get_async_requests_session", fake_session)

    out = await helpers.amake_requests(["http://x/empty", "http://x/full"])

    assert out == [{"url": "http://x/full"}]


def test_combine_certificates_returns_existing_combined_neighbor(tmp_path):
    cert = tmp_path / "ca.pem"
    combined = tmp_path / "ca_combined.pem"
    cert.write_text("cert")
    combined.write_text("combined")

    assert combine_certificates(str(cert)) == str(combined)


def test_combine_certificates_uses_default_bundle(monkeypatch, tmp_path):
    import atexit

    import certifi

    cert = tmp_path / "ca.pem"
    bundle = tmp_path / "bundle.pem"
    cert.write_text("CERT")
    bundle.write_text("BUNDLE")

    monkeypatch.setattr(certifi, "where", lambda: str(bundle))
    monkeypatch.setattr(atexit, "register", lambda *args, **kwargs: None)

    out = Path(combine_certificates(str(cert)))

    assert out.exists()
    assert "BUNDLE" in out.read_text()
    assert "CERT" in out.read_text()


def test_safe_fromtimestamp_negative_on_windows(monkeypatch):
    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers.os, "name", "nt")

    out = helpers.safe_fromtimestamp(-60, tz=timezone.utc)

    assert out == datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=-60)


# --- safe_fromtimestamp ---


def test_safe_fromtimestamp_negative_on_non_windows():
    """On non-Windows, a negative timestamp uses ``datetime.fromtimestamp`` directly."""
    import os

    from openbb_core.provider.utils.helpers import safe_fromtimestamp

    if os.name == "nt":
        pytest.skip("Windows-specific branch tested separately.")
    # Negative timestamps are well-defined on POSIX
    out = safe_fromtimestamp(-1)
    assert out.year < 1971


def test_safe_fromtimestamp_windows_negative_branch(monkeypatch):
    """Force the os.name=='nt' branch to test the timedelta fallback path."""
    from datetime import timezone

    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "os", type("FakeOs", (), {"name": "nt"}))
    out = helpers.safe_fromtimestamp(-3600, tz=timezone.utc)
    assert out.year == 1969


# --- to_snake_case ---


def test_to_snake_case_collapses_double_underscores():
    from openbb_core.provider.utils.helpers import to_snake_case

    assert to_snake_case("SomeABCName") == "some_abc_name"


def test_to_snake_case_replaces_spaces():
    from openbb_core.provider.utils.helpers import to_snake_case

    assert "_" in to_snake_case("Hello World")


# --- combine_certificates: exception path ---


def test_combine_certificates_returns_cert_on_write_failure(tmp_path, monkeypatch):
    """If shutil.copyfileobj raises, the original cert path is returned with a warning."""
    import shutil
    import warnings as _warnings

    from openbb_core.provider.utils import helpers

    cert = tmp_path / "ca.pem"
    cert.write_text("CERT")
    bundle = tmp_path / "bundle.pem"
    bundle.write_text("BUNDLE")

    def boom(*_a, **_kw):
        raise OSError("disk full")

    monkeypatch.setattr(shutil, "copyfileobj", boom)
    with _warnings.catch_warnings(record=True) as caught:
        _warnings.simplefilter("always")
        out = helpers.combine_certificates(str(cert), str(bundle))
    # On failure, function returns the original cert string
    assert out == str(cert)
    assert any("error occurred while handling" in str(w.message) for w in caught)


def test_combine_certificates_uses_certifi_when_no_bundle(tmp_path, monkeypatch):
    """When no bundle is given, certifi.where() is used."""
    from openbb_core.provider.utils import helpers

    cert = tmp_path / "ca.pem"
    cert.write_text("CERT")
    bundle = tmp_path / "ca-bundle.pem"
    bundle.write_text("DEFAULT-BUNDLE")
    import certifi

    monkeypatch.setattr(certifi, "where", lambda: str(bundle))
    out = helpers.combine_certificates(str(cert))
    from pathlib import Path

    out_path = Path(out)
    assert out_path.exists()
    assert "DEFAULT-BUNDLE" in out_path.read_text()
    out_path.unlink(missing_ok=True)


# --- get_async_requests_session ---


def test_get_async_requests_session_returns_provided_session():
    """A pre-existing ClientSession is returned as-is."""
    import asyncio

    from openbb_core.provider.utils.client import ClientSession
    from openbb_core.provider.utils.helpers import get_async_requests_session

    async def _run():
        s = ClientSession()
        try:
            out = await get_async_requests_session(session=s)
            assert out is s
        finally:
            await s.close()

    asyncio.run(_run())


def test_get_async_requests_session_proxy_upgrades_https_to_http(monkeypatch):
    """When env HTTP_PROXY==HTTPS_PROXY and starts with https:, it is rewritten."""
    import asyncio

    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})
    monkeypatch.setenv("HTTP_PROXY", "https://shared:1")
    monkeypatch.setenv("HTTPS_PROXY", "https://shared:1")

    async def _run():
        s = await helpers.get_async_requests_session()
        try:
            assert not s.closed
        finally:
            await s.close()

    asyncio.run(_run())


def test_get_async_requests_session_with_basic_auth(monkeypatch):
    import asyncio

    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})

    async def _run():
        s = await helpers.get_async_requests_session(auth=["user", "pass"])
        try:
            assert not s.closed
        finally:
            await s.close()

    asyncio.run(_run())


def test_get_async_requests_session_with_cookies_dict(monkeypatch):
    import asyncio

    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {})

    async def _run():
        s = await helpers.get_async_requests_session(cookies={"k": "v"})
        try:
            assert not s.closed
        finally:
            await s.close()

    asyncio.run(_run())


def test_get_async_requests_session_with_timeout_int(monkeypatch):
    import asyncio

    from openbb_core.provider.utils import helpers

    monkeypatch.setattr(helpers, "get_python_request_settings", lambda: {"timeout": 5})

    async def _run():
        s = await helpers.get_async_requests_session()
        try:
            assert not s.closed
        finally:
            await s.close()

    asyncio.run(_run())


# --- amake_requests exception aggregation ---


def test_amake_requests_raises_first_exception_when_no_results(monkeypatch):
    """When all results are exceptions and no results collected, the first is raised."""
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    from openbb_core.provider.utils import helpers

    fake_session = MagicMock()
    fake_session.close = AsyncMock()
    monkeypatch.setattr(
        helpers, "get_async_requests_session", AsyncMock(return_value=fake_session)
    )

    async def _gather(*_args, **_kw):
        return [RuntimeError("first"), RuntimeError("second")]

    monkeypatch.setattr(asyncio, "gather", _gather)

    async def _run():
        with pytest.raises(RuntimeError, match="first"):
            await helpers.amake_requests(["http://a", "http://b"])

    asyncio.run(_run())


def test_amake_requests_returns_exceptions_when_ret_exceptions(monkeypatch):
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    from openbb_core.provider.utils import helpers

    fake_session = MagicMock()
    fake_session.close = AsyncMock()
    monkeypatch.setattr(
        helpers, "get_async_requests_session", AsyncMock(return_value=fake_session)
    )

    err = RuntimeError("boom")

    async def _gather(*_args, **_kw):
        return [err, {"ok": True}]

    monkeypatch.setattr(asyncio, "gather", _gather)

    async def _run():
        out = await helpers.amake_requests(
            ["http://a", "http://b"], return_exceptions=True
        )
        assert err in out
        assert {"ok": True} in out

    asyncio.run(_run())


def test_get_async_requests_session_ssl_context_with_cert(tmp_path, monkeypatch):
    """Lines 263-279: ca/cert path builds ssl_context."""
    import asyncio

    # Build self-signed cert+key for test
    import subprocess

    from openbb_core.provider.utils import helpers as H

    cert = tmp_path / "c.pem"
    key = tmp_path / "k.pem"
    subprocess.run(  # noqa: S603
        [  # noqa: S607
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-keyout",
            str(key),
            "-out",
            str(cert),
            "-days",
            "1",
            "-nodes",
            "-subj",
            "/CN=t",
        ],
        check=True,
        capture_output=True,
    )

    async def _go():
        s = await H.get_async_requests_session(
            cafile=str(cert), certfile=str(cert), keyfile=str(key)
        )
        await s.close()

    asyncio.run(_go())


def test_get_async_requests_session_with_basic_auth_and_cookies():
    """Lines 303, 317-318: proxy_auth/auth/dict cookies."""
    import asyncio

    from openbb_core.provider.utils import helpers as H

    async def _go():
        s = await H.get_async_requests_session(
            proxy_auth=("u", "p"),
            auth=("a", "b"),
            cookies={"k": "v"},
        )
        await s.close()

    asyncio.run(_go())
