"""Tests for the Deribit ticker subscription."""

import asyncio
import json

import pytest
from websockets import ConnectionClosed

from openbb_deribit.utils import websocket


class _Socket:
    """A stand-in for one websocket connection."""

    def __init__(self, frames):
        self.frames = list(frames)
        self.sent: list = []

    async def send(self, frame):
        """Record what the subscription asked for."""
        self.sent.append(json.loads(frame))

    async def recv(self):
        """Return the next frame, or stall when there are none left."""
        if not self.frames:
            await asyncio.sleep(10)

        frame = self.frames.pop(0)

        if isinstance(frame, Exception):
            raise frame

        return json.dumps(frame)

    async def __aenter__(self):
        """Enter the connection context."""
        return self

    async def __aexit__(self, *args):
        """Leave the connection context."""
        return False


def _tick(symbol):
    """Return one ticker frame for a symbol."""
    return {"params": {"data": {"instrument_name": symbol, "mark_price": 1.0}}}


@pytest.fixture
def connect(monkeypatch):
    """Install a canned connection and return what it recorded."""

    def install(frames):
        socket = _Socket(frames)
        monkeypatch.setattr("websockets.asyncio.client.connect", lambda url: socket)

        return socket

    return install


class TestSubscribeTickers:
    """The subscription returns one ticker per symbol it was asked for."""

    @pytest.mark.asyncio
    async def test_collects_every_symbol(self, connect):
        """The read stops as soon as every symbol has arrived."""
        socket = connect([_tick("A"), _tick("B")])
        messages: set = set()
        received = await websocket.subscribe_tickers(["A", "B"], messages)

        assert set(received) == {"A", "B"}
        assert messages == set()
        assert socket.sent[0]["params"]["channels"] == [
            "ticker.A.100ms",
            "ticker.B.100ms",
        ]

    @pytest.mark.asyncio
    async def test_ignores_duplicates_and_noise(self, connect):
        """Repeats and frames carrying no ticker are skipped."""
        connect([{"id": 1}, _tick("A"), _tick("A"), _tick("B")])
        messages: set = set()
        received = await websocket.subscribe_tickers(["A", "B"], messages)

        assert set(received) == {"A", "B"}

    @pytest.mark.asyncio
    async def test_reports_an_exchange_error(self, connect):
        """An error frame stops the read and is reported."""
        connect([{"error": {"message": "no"}}])
        messages: set = set()
        received = await websocket.subscribe_tickers(["A"], messages)

        assert received == {}
        assert any("returned an error" in message for message in messages)

    @pytest.mark.asyncio
    async def test_a_closed_connection_returns_what_arrived(self, connect):
        """A connection that closed early keeps the tickers it did deliver."""
        connect([_tick("A"), ConnectionClosed(None, None)])
        messages: set = set()
        received = await websocket.subscribe_tickers(["A", "B"], messages)

        assert set(received) == {"A"}

    @pytest.mark.asyncio
    async def test_timeout_says_how_many_are_missing(self, connect, monkeypatch):
        """A subscription that stalls names how much did not arrive."""
        monkeypatch.setattr(websocket, "SUBSCRIBE_TIMEOUT", 0.05)
        connect([_tick("A")])
        messages: set = set()
        received = await websocket.subscribe_tickers(["A", "B"], messages)

        assert set(received) == {"A"}
        assert any("1 of 2 contracts" in message for message in messages)

    @pytest.mark.asyncio
    async def test_a_failed_connection_is_reported(self, monkeypatch):
        """A connection that could not be opened is reported, not raised."""

        def _connect(url):
            raise OSError("no route to host")

        monkeypatch.setattr("websockets.asyncio.client.connect", _connect)
        messages: set = set()
        received = await websocket.subscribe_tickers(["A"], messages)

        assert received == {}
        assert any("subscription failed" in message for message in messages)
