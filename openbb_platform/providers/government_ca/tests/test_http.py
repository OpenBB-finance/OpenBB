"""Tests for the resilient HTTP client in ``utils/_http.py``.

Uses ``unittest.mock`` to patch ``requests.get`` so no real network
calls happen. The tests cover:

- Happy path (200 OK with valid JSON)
- 4xx (not retried)
- 5xx (retried, then succeeds)
- 5xx (retried, exhausts retries → NetworkError)
- Connection error (retried, then succeeds)
- Connection error (retried, exhausts → NetworkError)
- Invalid JSON body (not retried)
- Backoff sleep is called with the right delays
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from openbb_government_ca.utils import _http
from openbb_government_ca.utils._http import NetworkError, http_get_json


def _mock_response(
    *,
    status_code: int = 200,
    json_data: object | None = None,
    body: str | None = None,
    reason: str = "OK",
) -> MagicMock:
    """Build a ``requests.Response``-shaped mock."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.reason = reason
    if body is not None:
        resp.text = body
        resp.json.side_effect = json.JSONDecodeError("expecting value", body, 0)
    else:
        resp.text = json.dumps(json_data)
        resp.json.return_value = json_data
    return resp


class TestHappyPath:
    """The common case — a single 200 OK with valid JSON."""

    def test_returns_parsed_json(self):
        """A 200 response with valid JSON is parsed and returned."""
        resp = _mock_response(json_data={"hello": "world"})
        with patch("openbb_government_ca.utils._http.requests.get", return_value=resp):
            result = http_get_json("https://example.com/api")
        assert result == {"hello": "world"}

    def test_user_agent_header_is_sent(self):
        """The default User-Agent identifies the build hook."""
        resp = _mock_response(json_data={})
        with patch(
            "openbb_government_ca.utils._http.requests.get", return_value=resp
        ) as mock_get:
            http_get_json("https://example.com/api")
        headers = mock_get.call_args.kwargs["headers"]
        assert "User-Agent" in headers
        assert "openbb-government-ca" in headers["User-Agent"]

    def test_custom_headers_override_defaults(self):
        """Caller-supplied headers override defaults."""
        resp = _mock_response(json_data={})
        with patch(
            "openbb_government_ca.utils._http.requests.get", return_value=resp
        ) as mock_get:
            http_get_json(
                "https://example.com/api",
                headers={"User-Agent": "custom-agent/1.0", "X-Custom": "yes"},
            )
        headers = mock_get.call_args.kwargs["headers"]
        assert headers["User-Agent"] == "custom-agent/1.0"
        assert headers["X-Custom"] == "yes"

    def test_params_are_passed_through(self):
        """Query params are forwarded to ``requests.get``."""
        resp = _mock_response(json_data={})
        with patch(
            "openbb_government_ca.utils._http.requests.get", return_value=resp
        ) as mock_get:
            http_get_json(
                "https://example.com/api",
                params={"start_date": "2024-01-01", "limit": 100},
            )
        assert mock_get.call_args.kwargs["params"] == {
            "start_date": "2024-01-01",
            "limit": 100,
        }


class TestClientErrors:
    """4xx errors are NOT retried — they mean the call is wrong."""

    def test_404_raises_immediately(self):
        """A 404 raises ``NetworkError`` without retrying."""
        resp = _mock_response(status_code=404, reason="Not Found")
        with patch(
            "openbb_government_ca.utils._http.requests.get", return_value=resp
        ) as mock_get:
            with pytest.raises(NetworkError, match="client error 404"):
                http_get_json("https://example.com/missing", retries=3)
        # Only one attempt — no retries on 4xx.
        assert mock_get.call_count == 1

    def test_400_raises_immediately(self):
        """A 400 raises ``NetworkError`` without retrying."""
        resp = _mock_response(status_code=400, reason="Bad Request")
        with patch(
            "openbb_government_ca.utils._http.requests.get", return_value=resp
        ) as mock_get:
            with pytest.raises(NetworkError, match="client error 400"):
                http_get_json("https://example.com/bad", retries=3)
        assert mock_get.call_count == 1

    def test_network_error_carries_status_code(self):
        """``NetworkError.status_code`` is populated for 4xx/5xx."""
        resp = _mock_response(status_code=403, reason="Forbidden")
        with patch("openbb_government_ca.utils._http.requests.get", return_value=resp):
            with pytest.raises(NetworkError) as exc_info:
                http_get_json("https://example.com/forbidden")
        assert exc_info.value.status_code == 403


class TestServerErrorsRetried:
    """5xx errors ARE retried — they're often transient."""

    def test_500_then_200_succeeds(self):
        """A 500 followed by a 200 succeeds after one retry."""
        err_resp = _mock_response(status_code=503, reason="Service Unavailable")
        ok_resp = _mock_response(json_data={"ok": True})
        with patch(
            "openbb_government_ca.utils._http.requests.get",
            side_effect=[err_resp, ok_resp],
        ) as mock_get:
            with patch("openbb_government_ca.utils._http._sleep_backoff"):
                result = http_get_json("https://example.com/api", retries=2)
        assert result == {"ok": True}
        assert mock_get.call_count == 2

    def test_500_exhausts_retries(self):
        """Repeated 500s exhaust retries and raise ``NetworkError``."""
        err_resp = _mock_response(status_code=500, reason="Internal Server Error")
        with patch(
            "openbb_government_ca.utils._http.requests.get", return_value=err_resp
        ) as mock_get:
            with patch("openbb_government_ca.utils._http._sleep_backoff"):
                with pytest.raises(NetworkError, match="server error 500"):
                    http_get_json("https://example.com/api", retries=2)
        # 1 initial + 2 retries = 3 attempts.
        assert mock_get.call_count == 3


class TestConnectionErrorsRetried:
    """``requests.ConnectionError`` is retryable (DNS, refused, etc.)."""

    def test_connection_error_then_success(self):
        """A connection error followed by a successful response."""
        ok_resp = _mock_response(json_data={"ok": True})
        with patch(
            "openbb_government_ca.utils._http.requests.get",
            side_effect=[requests.exceptions.ConnectionError("DNS failure"), ok_resp],
        ) as mock_get:
            with patch("openbb_government_ca.utils._http._sleep_backoff"):
                result = http_get_json("https://example.com/api", retries=2)
        assert result == {"ok": True}
        assert mock_get.call_count == 2

    def test_connection_error_exhausts_retries(self):
        """Repeated connection errors exhaust retries and raise."""
        with patch(
            "openbb_government_ca.utils._http.requests.get",
            side_effect=requests.exceptions.ConnectionError("DNS failure"),
        ) as mock_get:
            with patch("openbb_government_ca.utils._http._sleep_backoff"):
                with pytest.raises(NetworkError, match="connection failed"):
                    http_get_json("https://example.com/api", retries=2)
        assert mock_get.call_count == 3

    def test_timeout_is_retryable(self):
        """``requests.Timeout`` is retryable."""
        with patch(
            "openbb_government_ca.utils._http.requests.get",
            side_effect=requests.exceptions.Timeout("read timed out"),
        ):
            with patch("openbb_government_ca.utils._http._sleep_backoff"):
                with pytest.raises(NetworkError, match="connection failed"):
                    http_get_json("https://example.com/api", retries=1)


class TestInvalidJsonNotRetried:
    """A 200 with a non-JSON body is not retried — retrying won't help."""

    def test_invalid_json_raises_immediately(self):
        """A 200 with invalid JSON raises ``NetworkError`` without retrying."""
        resp = _mock_response(body="<html>not json</html>")
        with patch(
            "openbb_government_ca.utils._http.requests.get", return_value=resp
        ) as mock_get:
            with pytest.raises(NetworkError, match="not valid JSON"):
                http_get_json("https://example.com/api", retries=3)
        assert mock_get.call_count == 1

    def test_invalid_json_includes_body_preview(self):
        """The error message includes a preview of the body for debugging."""
        resp = _mock_response(body="<html>broken</html>")
        with patch("openbb_government_ca.utils._http.requests.get", return_value=resp):
            with pytest.raises(NetworkError) as exc_info:
                http_get_json("https://example.com/api")
        assert "broken" in str(exc_info.value)


class TestBackoff:
    """Backoff delays are exponential, capped at 10s."""

    def test_backoff_delay_grows_exponentially(self):
        """``_sleep_backoff(1.5, n)`` sleeps ``1.5 * 1.5^n`` seconds."""
        with patch("openbb_government_ca.utils._http.time.sleep") as mock_sleep:
            _http._sleep_backoff(1.5, 0)
            _http._sleep_backoff(1.5, 1)
            _http._sleep_backoff(1.5, 2)
        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert delays[0] == pytest.approx(1.5)
        assert delays[1] == pytest.approx(2.25)
        assert delays[2] == pytest.approx(3.375)

    def test_backoff_is_capped_at_10s(self):
        """Backoff never sleeps more than 10 seconds, even at high attempts."""
        with patch("openbb_government_ca.utils._http.time.sleep") as mock_sleep:
            _http._sleep_backoff(1.5, 20)  # would be 1.5 * 1.5^20 ≈ 5414s
        assert mock_sleep.call_args.args[0] == 10.0


class TestNetworkErrorShape:
    """``NetworkError`` carries useful debugging context."""

    def test_url_attribute_is_set(self):
        """``NetworkError.url`` is the URL that failed."""
        resp = _mock_response(status_code=404, reason="Not Found")
        with patch("openbb_government_ca.utils._http.requests.get", return_value=resp):
            with pytest.raises(NetworkError) as exc_info:
                http_get_json("https://example.com/missing")
        assert exc_info.value.url == "https://example.com/missing"

    def test_cause_attribute_preserves_original(self):
        """``NetworkError.cause`` is the original exception."""
        original = requests.exceptions.ConnectionError("DNS failure")
        with patch(
            "openbb_government_ca.utils._http.requests.get", side_effect=original
        ):
            with patch("openbb_government_ca.utils._http._sleep_backoff"):
                with pytest.raises(NetworkError) as exc_info:
                    http_get_json("https://example.com/api", retries=0)
        assert exc_info.value.cause is original
