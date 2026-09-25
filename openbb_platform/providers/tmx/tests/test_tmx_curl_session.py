"""Tests for the transport that rides out a Cloudflare refusal."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_tmx.utils import curl_session


class Response:
    """A stand-in for one curl_cffi response."""

    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self.content = b"{}" if payload is not None else b""
        self._payload = payload

    def json(self):
        """Return the decoded body."""
        return self._payload


@pytest.fixture
def transport(monkeypatch):
    """Answer each attempt from a scripted list of status codes."""
    monkeypatch.setattr(curl_session, "BACKOFF", 0)
    state: dict = {"codes": [], "calls": [], "rebuilds": 0}

    class Session:
        def request(self, method, url, **kwargs):
            state["calls"].append((method, url))

            return Response(state["codes"].pop(0), {"ok": True})

    def get_session(key, warmup=True):
        return Session()

    def cache_clear():
        state["rebuilds"] += 1

    get_session.cache_clear = cache_clear
    monkeypatch.setattr(curl_session, "get_session", get_session)

    return state


class TestRequestWithRetry:
    """A refusal is retried rather than raised."""

    def test_an_accepted_request_is_returned_at_once(self, transport):
        transport["codes"] = [200]
        response = curl_session.request_with_retry("ciro", "GET", "https://x")

        assert response.status_code == 200
        assert len(transport["calls"]) == 1

    def test_a_refusal_is_retried(self, transport):
        """The edge refuses individual requests, not the session."""
        transport["codes"] = [403, 403, 200]
        response = curl_session.request_with_retry("ciro", "POST", "https://x")

        assert response.status_code == 200
        assert len(transport["calls"]) == 3

    def test_every_refusal_is_reported(self, transport):
        transport["codes"] = [403] * curl_session.ATTEMPTS

        with pytest.raises(OpenBBError, match="was refused by the host"):
            curl_session.request_with_retry("ciro", "GET", "https://x")

        assert len(transport["calls"]) == curl_session.ATTEMPTS

    def test_the_session_is_rebuilt_once_along_the_way(self, transport):
        """A clearance that really has lapsed needs a new session."""
        transport["codes"] = [403] * curl_session.ATTEMPTS

        with pytest.raises(OpenBBError):
            curl_session.request_with_retry("ciro", "GET", "https://x")

        assert transport["rebuilds"] == 1

    def test_a_service_outage_is_retried_too(self, transport):
        transport["codes"] = [503, 200]

        assert (
            curl_session.request_with_retry("ciro", "GET", "https://x").status_code
            == 200
        )

    def test_another_status_is_handed_back_unretried(self, transport):
        transport["codes"] = [500]
        response = curl_session.request_with_retry("ciro", "GET", "https://x")

        assert response.status_code == 500
        assert len(transport["calls"]) == 1

    def test_the_method_and_url_are_passed_through(self, transport):
        transport["codes"] = [200]
        curl_session.request_with_retry("ciro", "POST", "https://x/y")

        assert transport["calls"] == [("POST", "https://x/y")]


class TestGetJson:
    """The JSON helper built on the retrying transport."""

    async def test_the_body_is_decoded(self, transport):
        transport["codes"] = [200]

        assert await curl_session.get_json("ciro", "https://x") == {"ok": True}

    async def test_a_refusal_is_ridden_out(self, transport):
        transport["codes"] = [403, 200]

        assert await curl_session.get_json("ciro", "https://x") == {"ok": True}

    async def test_a_hard_failure_is_reported(self, transport):
        transport["codes"] = [500]

        with pytest.raises(OpenBBError, match="failed with status 500"):
            await curl_session.get_json("ciro", "https://x")

    async def test_a_repeated_refusal_is_reported(self, transport):
        transport["codes"] = [403] * curl_session.ATTEMPTS

        with pytest.raises(OpenBBError, match="was refused by the host"):
            await curl_session.get_json("ciro", "https://x")


class TestCiroPost:
    """The CIRO query endpoints post through the same transport."""

    async def test_the_body_is_decoded(self, transport):
        from openbb_tmx.utils import ciro

        transport["codes"] = [200]

        assert await ciro._post_json("/x", {}) == {"ok": True}

    async def test_a_refusal_is_ridden_out(self, transport):
        from openbb_tmx.utils import ciro

        transport["codes"] = [403, 200]

        assert await ciro._post_json("/x", {}) == {"ok": True}

    async def test_a_response_without_content_is_empty(self, transport, monkeypatch):
        from openbb_tmx.utils import ciro

        class Empty:
            def request(self, method, url, **kwargs):
                return Response(200)

        monkeypatch.setattr(
            curl_session, "get_session", lambda key, warmup=True: Empty()
        )

        assert await ciro._post_json("/x", {}) == {}

    async def test_a_hard_failure_is_reported(self, transport):
        from openbb_tmx.utils import ciro

        transport["codes"] = [500]

        with pytest.raises(OpenBBError, match="failed with status 500"):
            await ciro._post_json("/x", {})

    async def test_a_repeated_refusal_is_reported(self, transport):
        """A refusal must not read as an empty answer and lose trades."""
        from openbb_tmx.utils import ciro

        transport["codes"] = [403] * curl_session.ATTEMPTS

        with pytest.raises(OpenBBError, match="was refused by the host"):
            await ciro._post_json("/x", {})
