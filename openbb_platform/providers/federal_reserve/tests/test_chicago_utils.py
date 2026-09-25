"""Tests for the Federal Reserve Bank of Chicago HTTP client."""

from unittest.mock import MagicMock

from openbb_federal_reserve.utils import chicago


def _response(status=200, *, content=b"") -> MagicMock:
    """Build a fake response with a no-op ``raise_for_status``."""
    response = MagicMock()
    response.status_code = status
    response.content = content
    response.raise_for_status = MagicMock()
    return response


class TestSession:
    """Tests for the browser-impersonating fallback session."""

    def test_get_session_uses_chicago_key(self, monkeypatch):
        """``_get_session`` requests the ``chicago`` session."""
        calls = []
        sentinel = object()
        monkeypatch.setattr(
            chicago, "get_session", lambda key: calls.append(key) or sentinel
        )
        assert chicago._get_session() is sentinel
        assert calls == ["chicago"]


class TestGetBytes:
    """Tests for ``get_bytes`` and its 403 fallback."""

    def test_returns_content_on_200(self, monkeypatch):
        """A 200 from ``make_request`` returns the body bytes directly."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda url: _response(200, content=b"csv"),
        )
        assert chicago.get_bytes("https://x/data") == b"csv"

    def test_falls_back_to_session_on_403(self, monkeypatch):
        """A 403 retries through the impersonating session."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda url: _response(403),
        )
        session = MagicMock()
        session.get = MagicMock(return_value=_response(200, content=b"pdf"))
        monkeypatch.setattr(chicago, "_get_session", lambda: session)
        assert chicago.get_bytes("https://x/data") == b"pdf"
        session.get.assert_called_once_with("https://x/data", timeout=60)


class TestGetText:
    """Tests for ``get_text``."""

    def test_decodes_utf8_sig(self, monkeypatch):
        """``get_text`` decodes the bytes with the BOM stripped."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda url: _response(200, content=b"\xef\xbb\xbfa,b"),
        )
        assert chicago.get_text("https://x/data") == "a,b"
