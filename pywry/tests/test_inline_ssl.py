"""Tests for SSL/TLS support in PyWry inline widgets."""

import asyncio
import os
import ssl

from datetime import datetime, timedelta
from ipaddress import ip_address
from unittest.mock import MagicMock, patch

import anyio
import pytest
import requests
import websockets

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from pywry.inline import InlineWidget, _get_pywry_bridge_js, _make_server_request, stop_server


def _build_test_html(content: str, widget_id: str) -> str:
    """Build a full HTML document with pywry bridge for testing."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test</title>
    {_get_pywry_bridge_js(widget_id)}
</head>
<body>
    {content}
</body>
</html>"""


# pylint: disable=redefined-outer-name


# Generate self-signed certs for testing
@pytest.fixture(scope="function")
def ssl_certs(tmp_path):
    """Generate self-signed certificate and key for testing."""
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Create a self-signed certificate with multiple IP SANs
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PyWry Test"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now() - timedelta(days=1))
        .not_valid_after(datetime.now() + timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("localhost"),
                    x509.IPAddress(ip_address("127.0.0.1")),
                    x509.IPAddress(ip_address("0.0.0.0")),
                ]
            ),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # Write to files
    cert_path = tmp_path / "server.crt"
    key_path = tmp_path / "server.key"

    with key_path.open("wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with cert_path.open("wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return str(cert_path), str(key_path)


@pytest.fixture(autouse=True)
def cleanup_server():
    """Ensure server is stopped after tests."""
    stop_server()
    yield
    stop_server()


def test_https_server_configuration(ssl_certs):
    """Test that the server starts with HTTPS when configured."""
    cert_path, key_path = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        settings_server = settings_root.server

        settings_server.ssl_certfile = cert_path
        settings_server.ssl_keyfile = key_path
        settings_server.ssl_keyfile_password = None
        settings_server.ssl_ca_certs = cert_path
        settings_server.port = 8766
        settings_server.host = "127.0.0.1"
        settings_server.widget_prefix = "/widget"

        # Helper / Uvicorn settings
        settings_server.limit_max_requests = None
        settings_server.timeout_graceful_shutdown = None
        settings_server.limit_concurrency = None
        settings_server.access_log = False
        settings_server.timeout_keep_alive = 5
        settings_server.backlog = 2048

        # CORS settings
        settings_server.cors_origins = ["*"]
        settings_server.cors_allow_credentials = True
        settings_server.cors_allow_methods = ["*"]
        settings_server.cors_allow_headers = ["*"]

        # Security settings (required for server to run)
        settings_server.websocket_allowed_origins = []
        settings_server.websocket_require_token = True
        settings_server.internal_api_header = "X-PyWry-Token"
        settings_server.internal_api_token = None  # Auto-generated
        settings_server.strict_widget_auth = False

        widget = InlineWidget("<h1>Test</h1>", port=8766, browser_only=True)

        try:
            assert widget.url.startswith("https://")
            assert "8766" in widget.url

            # Internal helper includes auth token automatically
            internal_resp = _make_server_request("GET", "/health", port=8766, host="127.0.0.1")
            assert internal_resp.status_code == 200
            assert internal_resp.json() == {"status": "ok"}

        finally:
            stop_server()


def test_client_verification_settings_proxy_override(ssl_certs):
    """Test that proxy settings disable verification if overriding CA."""
    cert_path, _ = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        settings_server = settings_root.server
        settings_server.ssl_certfile = cert_path
        settings_server.ssl_ca_certs = None

        with (
            patch.dict(os.environ, {"HTTP_PROXY": "http://proxy.example.com"}, clear=True),
            patch("urllib.request.getproxies", return_value={"http": "http://proxy.example.com"}),
        ):
            from pywry.inline import _get_verification_settings

            assert _get_verification_settings(settings_server) is False


def test_client_verification_settings_localhost_default(ssl_certs):
    """Test that verification is True (system CA) for localhost by default if no CA provided."""
    cert_path, _ = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        settings_server = settings_root.server
        settings_server.ssl_certfile = cert_path
        settings_server.ssl_ca_certs = None

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("urllib.request.getproxies", return_value={}),
        ):
            from pywry.inline import _get_verification_settings

            assert _get_verification_settings(settings_server) is True


@pytest.mark.asyncio
async def test_e2e_wss_callback_flow(  # noqa: PLR0915  # pylint: disable=too-many-statements
    ssl_certs,
):
    """Test true E2E flow: HTTPS init -> WSS connect -> Client logic triggers callback."""
    cert_path, key_path = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        settings_server = settings_root.server

        settings_server.ssl_certfile = cert_path
        settings_server.ssl_keyfile = key_path
        settings_server.ssl_ca_certs = cert_path
        settings_server.port = 8769
        settings_server.host = "127.0.0.1"
        settings_server.ssl_keyfile_password = None
        settings_server.widget_prefix = "/widget"
        settings_server.limit_max_requests = None
        settings_server.timeout_graceful_shutdown = None
        settings_server.limit_concurrency = None
        settings_server.access_log = False
        settings_server.timeout_keep_alive = 5
        settings_server.backlog = 2048

        # CORS settings
        settings_server.cors_origins = ["*"]
        settings_server.cors_allow_credentials = True
        settings_server.cors_allow_methods = ["*"]
        settings_server.cors_allow_headers = ["*"]

        # Security settings (required for server to run)
        settings_server.websocket_allowed_origins = []
        settings_server.websocket_require_token = True
        settings_server.internal_api_header = "X-PyWry-Token"
        settings_server.internal_api_token = None  # Auto-generated
        settings_server.strict_widget_auth = False

        # 1. Setup widget with a callback (browser_only=True skips IPython requirement)
        callback_mock = MagicMock()
        widget_id = "e2e_test_widget"

        # We need to ensure we use unique ports/IDs to prevent collision if concurrent
        widget = InlineWidget(
            _build_test_html("<h1>E2E Test</h1>", widget_id),
            callbacks={"test_event": callback_mock},
            port=8769,
            widget_id=widget_id,
            browser_only=True,
        )
        wid = widget.widget_id

        try:
            # 2. Emulate Browser: Verify HTTPS content serving first
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_ctx.load_verify_locations(cert_path)
            ssl_ctx.check_hostname = False

            # Use anyio for async HTTPS request
            async with await anyio.connect_tcp(
                "127.0.0.1", 8769, ssl_context=ssl_ctx, tls_hostname="127.0.0.1"
            ) as stream:
                await stream.send(
                    b"GET /widget/"
                    + wid.encode()
                    + b" HTTP/1.1\r\nHost: 127.0.0.1:8769\r\nConnection: close\r\n\r\n"
                )
                response_data = b""
                async for chunk in stream:
                    response_data += chunk
                resp_text = response_data.decode("utf-8", errors="replace")
                assert "200 OK" in resp_text or "HTTP/1.1 200" in resp_text
                assert "window.pywry" in resp_text

            # 3. Emulate Browser: Connect to WSS with token auth
            from pywry.inline import _state

            uri = f"wss://127.0.0.1:8769/ws/{wid}"
            token = _state.widget_tokens.get(wid)
            subprotocol = f"pywry.token.{token}" if token else None
            subprotocols = [subprotocol] if subprotocol else None
            async with websockets.connect(uri, ssl=ssl_ctx, subprotocols=subprotocols) as websocket:
                # 4. Simulate browser sending 'pywry:ready'
                await websocket.send('{"type": "pywry:ready", "data": {}}')

                # 5. Simulate browser triggering 'test_event' (e.g. valid user click)
                msg = f'{{"type": "test_event", "data": {{"foo": "bar"}}, "widgetId": "{wid}"}}'
                await websocket.send(msg)

                # Give server a moment to process the queue in background thread
                start = asyncio.get_running_loop().time()
                while asyncio.get_running_loop().time() - start < 2.0:
                    # Check if callback was called
                    if callback_mock.called:
                        break
                    await asyncio.sleep(0.1)

                assert callback_mock.called, "Callback was not triggered within timeout"
                # Callback signature is (data, event_name, widget_id)
                callback_mock.assert_called_with({"foo": "bar"}, "test_event", wid)

        finally:
            stop_server()


def test_content_generation_https(ssl_certs):
    """Test that content is properly wrapped and accessible via HTTPS."""
    cert_path, key_path = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        settings_server = settings_root.server
        settings_server.ssl_certfile = cert_path
        settings_server.ssl_keyfile = key_path
        settings_server.ssl_ca_certs = cert_path
        settings_server.port = 8768
        settings_server.host = "127.0.0.1"
        settings_server.widget_prefix = "/widget"
        settings_server.limit_max_requests = None
        settings_server.timeout_graceful_shutdown = None
        settings_server.limit_concurrency = None
        settings_server.access_log = False
        settings_server.timeout_keep_alive = 5
        settings_server.backlog = 2048

        # CORS settings
        settings_server.cors_origins = ["*"]
        settings_server.cors_allow_credentials = True
        settings_server.cors_allow_methods = ["*"]
        settings_server.cors_allow_headers = ["*"]

        # Security settings (required for server to run)
        settings_server.websocket_allowed_origins = []
        settings_server.websocket_require_token = True
        settings_server.internal_api_header = "X-PyWry-Token"
        settings_server.internal_api_token = None  # Auto-generated
        settings_server.strict_widget_auth = False

        # browser_only=True skips IPython requirement
        widget_id = "content_test_widget"
        widget = InlineWidget(
            _build_test_html("<h1>Content Test</h1>", widget_id),
            port=8768,
            widget_id=widget_id,
            browser_only=True,
        )

        try:
            resp = requests.get(widget.url, verify=cert_path, timeout=5.0)
            assert resp.status_code == 200
            content = resp.text
            assert "h1>Content Test</h1>" in content
            assert "<script>" in content
            assert "window.pywry" in content
        finally:
            stop_server()
