"""Native batch execution must write a response even when a backend raises."""

import asyncio
import json
from io import StringIO

import pytest

from openbb_cli.dispatchers.protocol import Response
from openbb_cli.dispatchers.runtime import run_batch


class Backend:
    def __init__(self):
        self.closed = False

    async def dispatch(self, request):
        await asyncio.sleep(0)
        if request.command == "fail":
            raise ValueError("backend unavailable")
        return Response(id=request.id, ok=True, result=request.command)

    async def aclose(self):
        self.closed = True


def test_exception_is_written_and_following_requests_complete():
    backend = Backend()
    reader = StringIO(' {"id":"1","command":"fail"}\n{"id":"2","command":"ok"}\n')
    writer = StringIO()
    assert run_batch(backend, reader, writer, concurrency=1) == 1
    rows = {row["id"]: row for row in map(json.loads, writer.getvalue().splitlines())}
    assert rows["1"]["ok"] is False
    assert rows["1"]["error"]["type"] == "ValueError"
    assert rows["2"]["result"] == "ok"
    assert backend.closed


def test_all_concurrent_responses_are_written_before_return():
    backend = Backend()
    reader = StringIO(
        "".join(json.dumps({"id": str(n), "command": "ok"}) + "\n" for n in range(100))
    )
    writer = StringIO()
    assert run_batch(backend, reader, writer, concurrency=8) == 0
    assert len(writer.getvalue().splitlines()) == 100
    assert backend.closed


class BrokenOutput(StringIO):
    def __init__(self):
        super().__init__()
        self.calls = 0

    def write(self, value):
        self.calls += 1
        if self.calls == 1:
            raise BrokenPipeError("fixture output closed")
        return len(value)

    def flush(self):
        pass


def test_early_output_failure_is_observed_and_backend_closes():
    backend = Backend()
    reader = StringIO(
        "".join(json.dumps({"id": str(n), "command": "ok"}) + "\n" for n in range(20))
    )
    with pytest.raises(BrokenPipeError, match="fixture output closed"):
        run_batch(backend, reader, BrokenOutput(), concurrency=1)
    assert backend.closed
