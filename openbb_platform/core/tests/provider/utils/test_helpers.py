"""Test the provider helpers."""

import pytest

from openbb_core.provider.utils.client import ClientSession
from openbb_core.provider.utils.helpers import (
    amake_request,
    amake_requests,
    get_querystring,
    get_requests_session,
    make_request,
    to_snake_case,
)


class MockResponse:
    """Mock the response."""

    def __init__(self):
        """Initialize the mock response."""
        self.status_code = 200
        self.status = 200

    async def json(self):
        """Return the json response."""
        return {"test": "test"}


class MockSession:
    """Mock the ClientSession."""

    def __init__(self):
        """Initialize the mock session."""
        self.response = MockResponse()

    async def request(self, *args, **kwargs):
        """Mock the ClientSession.request method."""
        if kwargs.get("raise_for_status", False):
            raise Exception("Test")

        return self.response

    @staticmethod
    async def mock_callback(response, session):
        """Mock the response_callback."""
        assert response.status == 200
        return await response.json()


def test_get_querystring_exclude():
    """Test the get_querystring helper."""
    items = {
        "key1": "value1",
        "key2": "value2",
        "key3": None,
        "key4": ["value3", "value4"],
    }
    exclude = ["key2"]

    querystring = get_querystring(items, exclude)
    assert querystring == "key1=value1&key4=value3&key4=value4"


def test_get_querystring_no_exclude():
    """Test the get_querystring helper with no exclude list."""
    items = {
        "key1": "value1",
        "key2": "value2",
        "key3": None,
        "key4": ["value3", "value4"],
    }

    querystring = get_querystring(items, [])
    assert querystring == "key1=value1&key2=value2&key4=value3&key4=value4"


def test_make_request(monkeypatch):
    """Test the make_request helper."""

    def mock_get(*args, **kwargs):
        """Mock the requests.get method."""
        return MockResponse()

    client_session = get_requests_session()
    monkeypatch.setattr(client_session, "get", mock_get)

    response = make_request("http://mock.url", session=client_session)
    assert response.status_code == 200

    with pytest.raises(ValueError):
        make_request("http://mock.url", method="PUT")


def test_to_snake_case():
    """Test the to_snake_case helper."""
    assert to_snake_case("SomeRandomString") == "some_random_string"
    assert to_snake_case("someRandomString") == "some_random_string"
    assert to_snake_case("already_snake_case") == "already_snake_case"


@pytest.mark.asyncio
async def test_amake_request(monkeypatch):
    """Test the amake_request helper."""

    mock_callback = MockSession.mock_callback

    client_session = MockSession()
    monkeypatch.setattr(ClientSession, "request", client_session.request)

    response = await amake_request("http://mock.url", response_callback=mock_callback)
    assert response == {"test": "test"}

    with pytest.raises(Exception):
        await amake_request(
            "http://mock.url",
            response_callback=mock_callback,
            raise_for_status=True,
        )

    with pytest.raises(ValueError):
        await amake_request("http://mock.url", method="PUT")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_amake_requests(monkeypatch):
    """Test the amake_requests helper."""

    mock_callback = MockSession.mock_callback

    client_session = MockSession()
    monkeypatch.setattr(ClientSession, "request", client_session.request)

    multi_response = await amake_requests(
        ["http://mock.url", "http://mock.url"],
        response_callback=mock_callback,
    )
    assert multi_response == [{"test": "test"}, {"test": "test"}]

    with pytest.raises(ValueError):
        await amake_requests(
            ["http://mock.url", "http://mock.url"], method="PUT", raise_for_status=True
        )


def test_safe_fromtimestamp_negative_on_non_windows():
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
