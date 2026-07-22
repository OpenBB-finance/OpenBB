"""Tests for the USAspending HTTP client."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.treasury.utils import usaspending


def _capture(monkeypatch, response=None, error: Exception | None = None) -> dict:
    """Patch amake_request and record the call it receives.

    Parameters
    ----------
    response : Any
        Body the patched request returns.
    error : Exception | None
        Exception the patched request raises instead of returning.

    Returns
    -------
    dict
        The recorded url, method and keyword arguments.
    """
    captured: dict = {}

    async def _fake_request(url, method="GET", **kwargs):
        captured["url"] = url
        captured["method"] = method
        captured["kwargs"] = kwargs
        if error is not None:
            raise error
        return response

    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.amake_request", _fake_request
    )
    return captured


class TestRequest:
    """Tests for the low-level request wrapper."""

    def test_get_sends_no_body_and_no_json_headers(self, monkeypatch):
        """A GET carries neither a JSON body nor a content-type header."""
        captured = _capture(monkeypatch, {"ok": True})
        result = asyncio.run(usaspending._request("https://x/y/", method="GET"))
        assert result == {"ok": True}
        assert captured["method"] == "GET"
        assert "json" not in captured["kwargs"]
        assert "headers" not in captured["kwargs"]

    def test_post_sends_the_payload_as_json(self, monkeypatch):
        """A payload is sent as the JSON body with a JSON content type."""
        captured = _capture(monkeypatch, {"ok": True})
        asyncio.run(
            usaspending._request(
                "https://x/y/", method="POST", payload={"type": "agency"}
            )
        )
        assert captured["method"] == "POST"
        assert captured["kwargs"]["json"] == {"type": "agency"}
        assert captured["kwargs"]["headers"] == {"Content-Type": "application/json"}

    def test_post_keeps_caller_supplied_headers(self, monkeypatch):
        """Caller headers survive and the content type is added alongside them."""
        captured = _capture(monkeypatch, {"ok": True})
        asyncio.run(
            usaspending._request(
                "https://x/y/",
                method="POST",
                payload={"a": 1},
                headers={"X-Trace": "abc"},
            )
        )
        assert captured["kwargs"]["headers"] == {
            "X-Trace": "abc",
            "Content-Type": "application/json",
        }

    def test_post_does_not_override_an_explicit_content_type(self, monkeypatch):
        """An explicit content type is left as the caller set it."""
        captured = _capture(monkeypatch, {"ok": True})
        asyncio.run(
            usaspending._request(
                "https://x/y/",
                method="POST",
                payload={"a": 1},
                headers={"Content-Type": "application/vnd.api+json"},
            )
        )
        assert (
            captured["kwargs"]["headers"]["Content-Type"] == "application/vnd.api+json"
        )

    def test_post_does_not_mutate_the_callers_header_dict(self, monkeypatch):
        """The caller's header dict is copied, not edited in place."""
        _capture(monkeypatch, {"ok": True})
        headers = {"X-Trace": "abc"}
        asyncio.run(
            usaspending._request(
                "https://x/y/", method="POST", payload={"a": 1}, headers=headers
            )
        )
        assert headers == {"X-Trace": "abc"}

    def test_extra_kwargs_pass_straight_through(self, monkeypatch):
        """Transport options such as timeout reach amake_request untouched."""
        captured = _capture(monkeypatch, {"ok": True})
        asyncio.run(usaspending._request("https://x/y/", timeout=90))
        assert captured["kwargs"]["timeout"] == 90


class TestCheckResponse:
    """Tests for response-body validation."""

    def test_a_bare_array_is_returned_as_is(self):
        """Endpoints that answer with a bare array are passed through."""
        body = [{"recipient_id": "abc"}, {"recipient_id": "def"}]
        assert usaspending._check_response(body, "https://x/y/") == body

    def test_an_empty_array_is_returned_as_is(self):
        """An empty array is a valid body, not an error."""
        assert usaspending._check_response([], "https://x/y/") == []

    def test_an_object_is_returned_as_is(self):
        """A plain JSON object is passed through."""
        body = {"results": [], "page_metadata": {}}
        assert usaspending._check_response(body, "https://x/y/") == body

    def test_a_non_json_body_raises_with_the_url(self):
        """A body that is neither object nor array names the url that produced it."""
        with pytest.raises(OpenBBError, match="Unexpected USAspending response") as exc:
            usaspending._check_response("<html>502</html>", "https://x/y/")
        assert "https://x/y/" in str(exc.value)
        assert "<html>502</html>" in str(exc.value)

    def test_a_none_body_raises(self):
        """A missing body is reported rather than returned as None."""
        with pytest.raises(OpenBBError, match="Unexpected USAspending response"):
            usaspending._check_response(None, "https://x/y/")

    def test_an_api_detail_message_raises(self):
        """An API error object surfaces the source's own message."""
        with pytest.raises(
            OpenBBError, match="USAspending API error -> Field 'fy' is required"
        ):
            usaspending._check_response(
                {"detail": "Field 'fy' is required"}, "https://x/y/"
            )


class TestGetUsaspending:
    """Tests for the GET helper."""

    def test_the_path_is_joined_to_the_v2_base(self, monkeypatch):
        """The endpoint path is resolved under the v2 base url."""
        captured = _capture(monkeypatch, {"results": []})
        asyncio.run(usaspending.get_usaspending("awards/CONT_IDV_X_1549/"))
        assert (
            captured["url"]
            == "https://api.usaspending.gov/api/v2/awards/CONT_IDV_X_1549/"
        )
        assert captured["method"] == "GET"

    def test_it_returns_the_decoded_object(self, monkeypatch):
        """A successful call returns the decoded body."""
        _capture(monkeypatch, {"results": [{"id": 1}]})
        assert asyncio.run(usaspending.get_usaspending("references/")) == {
            "results": [{"id": 1}]
        }

    def test_it_returns_a_bare_array(self, monkeypatch):
        """An endpoint answering with an array returns that array."""
        _capture(monkeypatch, [{"name": "child"}])
        assert asyncio.run(usaspending.get_usaspending("recipient/children/x/")) == [
            {"name": "child"}
        ]

    def test_a_transport_failure_is_wrapped_with_url_and_type(self, monkeypatch):
        """A request failure names the url and the underlying exception class."""
        _capture(monkeypatch, error=TimeoutError("timed out"))
        with pytest.raises(OpenBBError) as exc:
            asyncio.run(usaspending.get_usaspending("subawards/"))
        message = str(exc.value)
        assert "USAspending request failed" in message
        assert "https://api.usaspending.gov/api/v2/subawards/" in message
        assert "TimeoutError: timed out" in message

    def test_a_transport_failure_keeps_the_original_cause(self, monkeypatch):
        """The original exception is chained so the traceback stays useful."""
        original = ValueError("bad json")
        _capture(monkeypatch, error=original)
        with pytest.raises(OpenBBError) as exc:
            asyncio.run(usaspending.get_usaspending("subawards/"))
        assert exc.value.__cause__ is original

    def test_an_api_error_body_raises(self, monkeypatch):
        """An error object in a 200 body still raises."""
        _capture(monkeypatch, {"detail": "Unknown award id"})
        with pytest.raises(OpenBBError, match="Unknown award id"):
            asyncio.run(usaspending.get_usaspending("awards/nope/"))

    def test_kwargs_reach_the_transport(self, monkeypatch):
        """Timeout and params given to the helper reach the request."""
        captured = _capture(monkeypatch, {"results": []})
        asyncio.run(
            usaspending.get_usaspending("references/", timeout=90, params={"fy": 2026})
        )
        assert captured["kwargs"]["timeout"] == 90
        assert captured["kwargs"]["params"] == {"fy": 2026}


class TestPostUsaspending:
    """Tests for the POST helper."""

    def test_it_posts_the_payload_to_the_v2_base(self, monkeypatch):
        """The payload is posted as JSON to the resolved endpoint."""
        captured = _capture(monkeypatch, {"results": []})
        asyncio.run(
            usaspending.post_usaspending("spending/", {"type": "agency"}, timeout=90)
        )
        assert captured["url"] == "https://api.usaspending.gov/api/v2/spending/"
        assert captured["method"] == "POST"
        assert captured["kwargs"]["json"] == {"type": "agency"}
        assert captured["kwargs"]["timeout"] == 90

    def test_it_returns_the_decoded_object(self, monkeypatch):
        """A successful call returns the decoded body."""
        _capture(monkeypatch, {"total": 5, "results": []})
        assert asyncio.run(usaspending.post_usaspending("spending/", {})) == {
            "total": 5,
            "results": [],
        }

    def test_an_empty_payload_is_still_sent_as_a_body(self, monkeypatch):
        """An empty dict is a body, so the JSON headers are still set."""
        captured = _capture(monkeypatch, {"results": []})
        asyncio.run(usaspending.post_usaspending("spending/", {}))
        assert captured["kwargs"]["json"] == {}
        assert captured["kwargs"]["headers"] == {"Content-Type": "application/json"}

    def test_a_transport_failure_is_wrapped_with_url_and_type(self, monkeypatch):
        """A request failure names the url and the underlying exception class."""
        _capture(monkeypatch, error=ConnectionResetError("peer closed"))
        with pytest.raises(OpenBBError) as exc:
            asyncio.run(usaspending.post_usaspending("spending/", {"type": "agency"}))
        message = str(exc.value)
        assert "USAspending request failed" in message
        assert "https://api.usaspending.gov/api/v2/spending/" in message
        assert "ConnectionResetError: peer closed" in message

    def test_an_api_error_body_raises(self, monkeypatch):
        """An error object in a 200 body still raises."""
        _capture(monkeypatch, {"detail": "Invalid type"})
        with pytest.raises(OpenBBError, match="USAspending API error -> Invalid type"):
            asyncio.run(usaspending.post_usaspending("spending/", {"type": "nope"}))

    def test_a_non_json_body_raises(self, monkeypatch):
        """A gateway error page raises rather than being returned."""
        _capture(monkeypatch, "Service Unavailable")
        with pytest.raises(OpenBBError, match="Unexpected USAspending response"):
            asyncio.run(usaspending.post_usaspending("spending/", {}))
