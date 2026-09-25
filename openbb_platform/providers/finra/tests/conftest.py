"""Shared fixtures for the openbb_finra test suite."""

import json
from pathlib import Path

import pytest

from openbb_finra.utils import client

DATA_DIR = Path(__file__).parent / "data"
REAL_OPEN_SESSION = client.open_session


class FakeResponse:
    """A recorded or scripted HTTP response."""

    def __init__(self, status: int = 200, text: str = "", headers: dict | None = None):
        """Hold the status, body, and headers."""
        self.status = status
        self._text = text
        self.headers = headers or {}
        self.released = False

    async def text(self) -> str:
        """Return the body."""
        return self._text

    def release(self) -> None:
        """Mark the response as released."""
        self.released = True


class FakeCookie:
    """A cookie held by the fake session."""

    def __init__(self, key: str, value: str):
        """Hold the cookie name and value."""
        self.key = key
        self.value = value


class FakeSession:
    """A session that answers from recorded interactions or a responder."""

    def __init__(self, interactions=None, responder=None, cookies=None):
        """Hold the answers and the cookie jar."""
        self.interactions = list(interactions or [])
        self.responder = responder
        self.cookie_jar = [
            FakeCookie(key, value) for key, value in (cookies or {}).items()
        ]
        self.calls: list[dict] = []
        self.closed = False

    def _answer(self, method: str, url: str, params=None, body=None) -> FakeResponse:
        call = {"method": method, "url": url, "params": params, "json": body}
        self.calls.append(call)

        if self.responder is not None:
            return self.responder(call)

        for interaction in self.interactions:
            if (
                interaction["method"] == method
                and interaction["url"] == url
                and interaction["params"] == params
                and interaction["json"] == body
            ):
                return FakeResponse(
                    interaction["status"], interaction["text"], interaction["headers"]
                )

        raise AssertionError(f"No recorded answer for {method} {url} {params} {body}")

    async def get(self, url, params=None, **kwargs):
        """Answer a GET request."""
        return self._answer("GET", url, params=params)

    async def post(self, url, json=None, **kwargs):
        """Answer a POST request."""
        return self._answer("POST", url, body=json)

    async def close(self):
        """Mark the session as closed."""
        self.closed = True


def cassette(name: str) -> list[dict]:
    """Return the recorded interactions of one scenario."""
    return json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))


@pytest.fixture
def response():
    """Return the fake response class."""
    return FakeResponse


@pytest.fixture
def trace_answer():
    """Return a builder of TRACE envelopes carrying rows."""

    def build(rows: list, total: int | None = None) -> FakeResponse:
        return FakeResponse(
            200,
            json.dumps(
                {
                    "status": "success",
                    "returnBody": {
                        "headers": {
                            "Record-Total": [str(len(rows) if total is None else total)]
                        },
                        "data": json.dumps(rows),
                    },
                }
            ),
        )

    return build


@pytest.fixture
def real_open_session():
    """Return the session factory the provider uses outside of tests."""
    return REAL_OPEN_SESSION


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Fail loudly rather than reaching FINRA from a unit test."""

    async def _forbidden():
        raise AssertionError("A unit test opened a session. Install a fake session.")

    monkeypatch.setattr("openbb_finra.utils.client.open_session", _forbidden)


@pytest.fixture
def fake_session(monkeypatch):
    """Install a fake session built from a cassette or a responder."""

    def install(name=None, responder=None, cookies=None) -> FakeSession:
        session = FakeSession(
            cassette(name) if name else None,
            responder,
            {"XSRF-TOKEN": "token"} if cookies is None else cookies,
        )

        async def _open():
            return session

        monkeypatch.setattr("openbb_finra.utils.client.open_session", _open)

        return session

    return install
