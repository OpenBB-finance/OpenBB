"""Tests for the Federal Reserve Bank of Kansas City HTTP client."""

from unittest.mock import MagicMock

from openbb_federal_reserve.utils import kansas_city


def _response(status=200, *, content=b"") -> MagicMock:
    """Build a fake response with a no-op ``raise_for_status``."""
    response = MagicMock()
    response.status_code = status
    response.content = content
    response.raise_for_status = MagicMock()
    return response


class TestSession:
    """Tests for the warmed session lifecycle."""

    def test_warmup_primes_home_page(self):
        """``_warmup`` fetches the site home page to seed the Akamai cookie."""
        session = MagicMock()
        kansas_city._warmup(session)
        session.get.assert_called_once_with(f"{kansas_city.SITE_HOST}/", timeout=30)

    def test_get_session_warms_kansas_city(self, monkeypatch):
        """``_get_session`` requests the ``kansas_city`` session with the warmup."""
        captured = {}
        sentinel = object()

        def _capture(key, warmup):
            captured.update(key=key, warmup=warmup)
            return sentinel

        monkeypatch.setattr(kansas_city, "get_session", _capture)
        assert kansas_city._get_session() is sentinel
        assert captured["key"] == "kansas_city"
        assert captured["warmup"] is kansas_city._warmup

    def test_reset_session_drops_key(self, monkeypatch):
        """``reset_session`` drops the cached ``kansas_city`` session."""
        calls = []
        monkeypatch.setattr(kansas_city, "_reset", calls.append)
        kansas_city.reset_session()
        assert calls == ["kansas_city"]


class TestFetch:
    """Tests for ``fetch_kansas_city`` and its 403 re-warm."""

    def test_returns_content_on_200(self, monkeypatch):
        """A 200 returns the body bytes and sends the default referer."""
        session = MagicMock()
        session.get = MagicMock(return_value=_response(200, content=b"xlsx"))
        monkeypatch.setattr(kansas_city, "_get_session", lambda: session)
        assert kansas_city.fetch_kansas_city("https://x/f.xlsx") == b"xlsx"
        _, kwargs = session.get.call_args
        assert kwargs["headers"] == {"Referer": f"{kansas_city.SITE_HOST}/"}

    def test_rewarms_on_403(self, monkeypatch):
        """A 403 drops the session and retries once with the given referer."""
        responses = iter([_response(403), _response(200, content=b"xlsx")])
        session = MagicMock()
        session.get = MagicMock(side_effect=lambda *a, **k: next(responses))
        monkeypatch.setattr(kansas_city, "_get_session", lambda: session)
        reset_calls = []
        monkeypatch.setattr(kansas_city, "reset_session", lambda: reset_calls.append(1))
        out = kansas_city.fetch_kansas_city("https://x/f.xlsx", referer="https://x/")
        assert out == b"xlsx"
        assert reset_calls == [1]
        _, kwargs = session.get.call_args
        assert kwargs["headers"] == {"Referer": "https://x/"}
