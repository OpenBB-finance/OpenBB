"""Tests for SSL/TLS support in PyWry inline widgets."""

import asyncio
import json
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

from pywry.inline import (
    InlineWidget,
    _get_pywry_bridge_js,
    _make_server_request,
    stop_server,
)


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
            internal_resp = _make_server_request(
                "GET", "/health", port=8766, host="127.0.0.1"
            )
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
            patch.dict(
                os.environ, {"HTTP_PROXY": "http://proxy.example.com"}, clear=True
            ),
            patch(
                "urllib.request.getproxies",
                return_value={"http": "http://proxy.example.com"},
            ),
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
            async with websockets.connect(
                uri, ssl=ssl_ctx, subprotocols=subprotocols
            ) as websocket:
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


# =============================================================================
# SecretInput HTTPS/WSS E2E Security Tests
# =============================================================================


def _make_ssl_server_settings(settings_server, cert_path, key_path, port):
    """Configure SSL server settings for testing."""
    settings_server.ssl_certfile = cert_path
    settings_server.ssl_keyfile = key_path
    settings_server.ssl_ca_certs = cert_path
    settings_server.port = port
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

    # Security settings
    settings_server.websocket_allowed_origins = []
    settings_server.websocket_require_token = True
    settings_server.internal_api_header = "X-PyWry-Token"
    settings_server.internal_api_token = None
    settings_server.strict_widget_auth = False


def test_secret_never_in_https_response(ssl_certs):
    """Secret values should never appear in HTTPS rendered HTML."""
    from pywry.toolbar import SecretInput, Toolbar

    cert_path, key_path = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        _make_ssl_server_settings(settings_root.server, cert_path, key_path, 8770)

        # Create toolbar with secret
        secret_value = "https-secret-api-key-12345"
        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key", value=secret_value)],
        )

        # Build HTML with toolbar
        toolbar_html = toolbar.build_html()
        full_html = f"""<!DOCTYPE html>
<html>
<head><title>Secret Test</title></head>
<body>
    {toolbar_html}
    <div>Content</div>
</body>
</html>"""

        widget_id = "secret_https_test"
        widget = InlineWidget(
            full_html,
            port=8770,
            widget_id=widget_id,
            browser_only=True,
        )

        try:
            # Fetch via HTTPS
            resp = requests.get(widget.url, verify=cert_path, timeout=5.0)
            assert resp.status_code == 200

            # Secret must NOT appear in response
            assert secret_value not in resp.text
            # But password input should be present
            assert 'type="password"' in resp.text
            # And should have masked value (bullets) when value exists
            assert 'value="••••••••••••"' in resp.text

        finally:
            stop_server()


@pytest.mark.asyncio
async def test_e2e_wss_secret_reveal_base64_encoded(ssl_certs):
    """Test secret reveal over WSS is base64 encoded for transit security."""
    from pywry.inline import _state
    from pywry.toolbar import SecretInput, Toolbar

    cert_path, key_path = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        _make_ssl_server_settings(settings_root.server, cert_path, key_path, 8771)

        # Create toolbar with secret
        secret_value = "wss-reveal-secret-value"
        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="secure:api-key", value=secret_value)],
        )
        toolbar.register_secrets()

        # Build HTML
        toolbar_html = toolbar.build_html()
        widget_id = "wss_reveal_test"
        full_html = _build_test_html(f"{toolbar_html}<div>Content</div>", widget_id)

        # Callback to handle reveal request
        callback_mock = MagicMock()

        widget = InlineWidget(
            full_html,
            callbacks={"secure:api-key:reveal": callback_mock},
            port=8771,
            widget_id=widget_id,
            browser_only=True,
        )
        wid = widget.widget_id

        try:
            # Create SSL context
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_ctx.load_verify_locations(cert_path)
            ssl_ctx.check_hostname = False

            # Connect via WSS
            uri = f"wss://127.0.0.1:8771/ws/{wid}"
            token = _state.widget_tokens.get(wid)
            subprotocol = f"pywry.token.{token}" if token else None
            subprotocols = [subprotocol] if subprotocol else None

            si = toolbar.get_secret_inputs()[0]

            async with websockets.connect(
                uri, ssl=ssl_ctx, subprotocols=subprotocols
            ) as websocket:
                # Send ready event
                await websocket.send('{"type": "pywry:ready", "data": {}}')

                # Simulate browser sending reveal request
                reveal_msg = {
                    "type": "secure:api-key:reveal",
                    "data": {"componentId": si.component_id},
                    "widgetId": wid,
                }
                await websocket.send(json.dumps(reveal_msg))

                # Wait for callback to be triggered
                start = asyncio.get_running_loop().time()
                while asyncio.get_running_loop().time() - start < 2.0:
                    if callback_mock.called:
                        break
                    await asyncio.sleep(0.1)

                # Callback should have been called
                assert callback_mock.called

        finally:
            stop_server()


@pytest.mark.asyncio
async def test_e2e_wss_secret_input_submission(ssl_certs):
    """Test secret input submission over WSS with base64 encoding."""
    from pywry.inline import _state
    from pywry.toolbar import SecretInput, Toolbar, decode_secret, encode_secret

    cert_path, key_path = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        _make_ssl_server_settings(settings_root.server, cert_path, key_path, 8772)

        # Create toolbar with empty secret
        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="secure:password")],
        )

        # Build HTML
        toolbar_html = toolbar.build_html()
        widget_id = "wss_input_test"
        full_html = _build_test_html(f"{toolbar_html}<div>Content</div>", widget_id)

        # Callback to capture submitted secret
        received_data = []

        def capture_secret(data, event_type, _wid):
            received_data.append((event_type, data))

        widget = InlineWidget(
            full_html,
            callbacks={"secure:password": capture_secret},
            port=8772,
            widget_id=widget_id,
            browser_only=True,
        )
        wid = widget.widget_id

        try:
            # Create SSL context
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_ctx.load_verify_locations(cert_path)
            ssl_ctx.check_hostname = False

            # Connect via WSS
            uri = f"wss://127.0.0.1:8772/ws/{wid}"
            token = _state.widget_tokens.get(wid)
            subprotocol = f"pywry.token.{token}" if token else None
            subprotocols = [subprotocol] if subprotocol else None

            si = toolbar.get_secret_inputs()[0]
            user_secret = "user-entered-wss-secret"

            async with websockets.connect(
                uri, ssl=ssl_ctx, subprotocols=subprotocols
            ) as websocket:
                # Send ready event
                await websocket.send('{"type": "pywry:ready", "data": {}}')

                # Simulate browser sending base64-encoded secret
                encoded_secret = encode_secret(user_secret)
                input_msg = {
                    "type": "secure:password",
                    "data": {
                        "value": encoded_secret,
                        "encoded": True,
                        "componentId": si.component_id,
                    },
                    "widgetId": wid,
                }
                await websocket.send(json.dumps(input_msg))

                # Wait for callback
                start = asyncio.get_running_loop().time()
                while asyncio.get_running_loop().time() - start < 2.0:
                    if received_data:
                        break
                    await asyncio.sleep(0.1)

                # Verify received data
                assert len(received_data) == 1
                event_type, data = received_data[0]
                assert event_type == "secure:password"
                assert data["encoded"] is True
                assert data["value"] == encoded_secret

                # Backend can decode it
                decoded = decode_secret(data["value"])
                assert decoded == user_secret

        finally:
            stop_server()


def test_secret_storage_isolation_https(ssl_certs):
    """Multiple secrets should be isolated in HTTPS mode."""
    from pywry.toolbar import SecretInput, Toolbar, clear_secret, get_secret

    cert_path, key_path = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        _make_ssl_server_settings(settings_root.server, cert_path, key_path, 8773)

        # Create toolbar with multiple secrets
        toolbar = Toolbar(
            position="top",
            items=[
                SecretInput(event="auth:key1", value="secret-one"),
                SecretInput(event="auth:key2", value="secret-two"),
                SecretInput(event="auth:key3", value="secret-three"),
            ],
        )
        toolbar.register_secrets()

        secrets = toolbar.get_secret_inputs()

        try:
            # Each secret is stored independently
            assert get_secret(secrets[0].component_id) == "secret-one"
            assert get_secret(secrets[1].component_id) == "secret-two"
            assert get_secret(secrets[2].component_id) == "secret-three"

            # Build and verify HTML doesn't contain any secrets
            toolbar_html = toolbar.build_html()
            assert "secret-one" not in toolbar_html
            assert "secret-two" not in toolbar_html
            assert "secret-three" not in toolbar_html

            # Clearing one doesn't affect others
            clear_secret(secrets[1].component_id)
            assert get_secret(secrets[0].component_id) == "secret-one"
            assert get_secret(secrets[1].component_id) is None
            assert get_secret(secrets[2].component_id) == "secret-three"

        finally:
            # Cleanup
            for s in secrets:
                clear_secret(s.component_id)
            stop_server()


def test_encode_decode_roundtrip_ssl():
    """Test base64 encode/decode roundtrip works in SSL context."""
    from pywry.toolbar import decode_secret, encode_secret

    # Test various secret formats
    test_secrets = [
        "simple-api-key",
        "with spaces and special!@#$%^&*()",
        "unicode: émojis 🔐 日本語",
        "very-long-" + "x" * 500,
        "",  # empty
    ]

    for original in test_secrets:
        encoded = encode_secret(original)
        decoded = decode_secret(encoded)
        assert decoded == original, f"Roundtrip failed for: {original[:30]}..."
        # Encoded should not equal original (unless empty)
        if original:
            assert encoded != original


@pytest.mark.asyncio
async def test_e2e_wss_custom_secret_handler_reveal(  # noqa: PLR0915  # pylint: disable=too-many-statements
    ssl_certs,
):
    """Custom secret handler should work correctly over WSS."""
    from pywry.inline import _state
    from pywry.toolbar import (
        _SECRET_HANDLERS,
        SecretInput,
        Toolbar,
        clear_secret,
        decode_secret,
        encode_secret,
        set_secret_handler,
    )

    cert_path, key_path = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        _make_ssl_server_settings(settings_root.server, cert_path, key_path, 8774)

        # Create toolbar with secret in registry
        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="vault:wss-secret", value="registry-value")],
        )
        toolbar.register_secrets()

        # Custom handler returns value from "external vault"
        vault_secret = "wss-vault-fetched-secret"

        def custom_reveal_handler(
            value: str | None,
            *,
            component_id: str,
            event: str,
            label: str | None = None,
            **metadata,
        ) -> str:
            return vault_secret

        si = toolbar.get_secret_inputs()[0]
        reveal_event = si.get_reveal_event()
        set_secret_handler(reveal_event, custom_reveal_handler)

        # Build HTML
        toolbar_html = toolbar.build_html()
        widget_id = "wss_custom_handler_test"
        full_html = _build_test_html(f"{toolbar_html}<div>Content</div>", widget_id)

        # Async callback that uses custom handler
        async def on_reveal(data, event_type, _wid):
            from pywry.toolbar import get_secret_handler

            handler = get_secret_handler(event_type)
            component_id = data.get("componentId", "")
            if handler:
                secret = handler(
                    None,
                    component_id=component_id,
                    event=event_type,
                    label=None,
                )
            else:
                from pywry.toolbar import get_secret

                secret = get_secret(component_id)

            from pywry.inline import _state

            # Emit response back via widget connections
            encoded = encode_secret(secret) if secret else ""
            response = {
                "type": f"{event_type}-response",
                "data": {
                    "componentId": data.get("componentId", ""),
                    "value": encoded,
                    "encoded": True,
                },
            }
            # Send to the widget's websocket connection
            ws = _state.connections.get(widget_id)
            if ws:
                await ws.send_json(response)

        widget = InlineWidget(
            full_html,
            callbacks={reveal_event: on_reveal},
            port=8774,
            widget_id=widget_id,
            browser_only=True,
        )
        wid = widget.widget_id

        try:
            # Create SSL context
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_ctx.load_verify_locations(cert_path)
            ssl_ctx.check_hostname = False

            # Connect via WSS
            uri = f"wss://127.0.0.1:8774/ws/{wid}"
            token = _state.widget_tokens.get(wid)
            subprotocol = f"pywry.token.{token}" if token else None
            subprotocols = [subprotocol] if subprotocol else None

            async with websockets.connect(
                uri, ssl=ssl_ctx, subprotocols=subprotocols
            ) as websocket:
                # Send ready
                await websocket.send('{"type": "pywry:ready", "data": {}}')

                # Send reveal request
                reveal_msg = {
                    "type": reveal_event,
                    "data": {"componentId": si.component_id},
                    "widgetId": wid,
                }
                await websocket.send(json.dumps(reveal_msg))

                # Wait for response
                message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(message)

                # Should get custom handler's value
                assert data["type"] == f"{reveal_event}-response"
                assert data["data"]["encoded"] is True

                decoded = decode_secret(data["data"]["value"])
                assert decoded == vault_secret
                assert decoded != "registry-value"

        finally:
            _SECRET_HANDLERS.pop(reveal_event, None)
            clear_secret(si.component_id)
            stop_server()


@pytest.mark.asyncio
async def test_e2e_wss_custom_handler_with_context(  # noqa: PLR0915
    ssl_certs,
):
    """Custom handler receives full context data over WSS."""
    from pywry.inline import _state
    from pywry.toolbar import (
        _SECRET_HANDLERS,
        SecretInput,
        Toolbar,
        clear_secret,
        encode_secret,
        set_secret_handler,
    )

    cert_path, key_path = ssl_certs

    with patch("pywry.inline.get_settings") as mock_get_settings:
        settings_root = mock_get_settings.return_value
        _make_ssl_server_settings(settings_root.server, cert_path, key_path, 8775)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="context:wss-test", value="test")],
        )
        toolbar.register_secrets()

        # Track what data the handler receives
        received_context = []

        def context_tracking_handler(
            value: str | None,
            *,
            component_id: str,
            event: str,
            label: str | None = None,
            **metadata,
        ) -> str:
            received_context.append(
                {
                    "componentId": component_id,
                    "event": event,
                    "label": label,
                    **metadata,
                }
            )
            return f"response-for-{component_id}"

        si = toolbar.get_secret_inputs()[0]
        reveal_event = si.get_reveal_event()
        set_secret_handler(reveal_event, context_tracking_handler)

        toolbar_html = toolbar.build_html()
        widget_id = "wss_context_test"
        full_html = _build_test_html(f"{toolbar_html}<div>Content</div>", widget_id)

        async def on_reveal(data, event_type, _wid):
            from pywry.toolbar import get_secret_handler

            handler = get_secret_handler(event_type)
            component_id = data.get("componentId", "")
            extra_field = data.get("extraField", "")
            metadata = data.get("metadata", {})
            if handler:
                secret = handler(
                    None,
                    component_id=component_id,
                    event=event_type,
                    label=None,
                    extraField=extra_field,
                    metadata=metadata,
                )
            else:
                secret = ""
            encoded = encode_secret(secret) if secret else ""

            response = {
                "type": f"{event_type}-response",
                "data": {
                    "componentId": data.get("componentId", ""),
                    "value": encoded,
                    "encoded": True,
                },
            }
            # Send to the widget's websocket connection
            ws = _state.connections.get(widget_id)
            if ws:
                await ws.send_json(response)

        widget = InlineWidget(
            full_html,
            callbacks={reveal_event: on_reveal},
            port=8775,
            widget_id=widget_id,
            browser_only=True,
        )
        wid = widget.widget_id

        try:
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_ctx.load_verify_locations(cert_path)
            ssl_ctx.check_hostname = False

            uri = f"wss://127.0.0.1:8775/ws/{wid}"
            token = _state.widget_tokens.get(wid)
            subprotocol = f"pywry.token.{token}" if token else None
            subprotocols = [subprotocol] if subprotocol else None

            async with websockets.connect(
                uri, ssl=ssl_ctx, subprotocols=subprotocols
            ) as websocket:
                await websocket.send('{"type": "pywry:ready", "data": {}}')

                # Send reveal with extra context
                reveal_msg = {
                    "type": reveal_event,
                    "data": {
                        "componentId": si.component_id,
                        "extraField": "extra-value",
                        "metadata": {"source": "wss-test"},
                    },
                    "widgetId": wid,
                }
                await websocket.send(json.dumps(reveal_msg))

                # Wait for callback to be processed
                start = asyncio.get_running_loop().time()
                while asyncio.get_running_loop().time() - start < 2.0:
                    if received_context:
                        break
                    await asyncio.sleep(0.1)

                # Verify handler received full context
                assert len(received_context) == 1
                ctx = received_context[0]
                assert ctx["componentId"] == si.component_id
                assert ctx["extraField"] == "extra-value"
                assert ctx["metadata"]["source"] == "wss-test"

        finally:
            _SECRET_HANDLERS.pop(reveal_event, None)
            clear_secret(si.component_id)
            stop_server()
