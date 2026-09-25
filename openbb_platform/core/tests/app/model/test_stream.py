"""Tests for the OBBStream model."""

import asyncio
import io
import socket
import time

import pytest

from openbb_core.app.model import stream as stream_module
from openbb_core.app.model.stream import (
    OBBStream,
    _install_shutdown_handlers,
    stop_all,
)
from openbb_core.provider.abstract.annotated_result import AnnotatedResult


class _Source:
    """A streaming response stub exposing ``body_iterator``."""

    media_type = "text/event-stream"

    def __init__(self, count: int = 3, sleep: float = 0.0):
        self._count = count
        self._sleep = sleep
        self.body_iterator = self._gen()

    async def _gen(self):
        for index in range(self._count):
            if self._sleep:
                await asyncio.sleep(self._sleep)
            yield f"data: {index}\n\n"


class _Model:
    """A row stub exposing ``model_dump_json``."""

    def model_dump_json(self) -> str:
        return '{"tick": 1}'


def test_init_with_body_iterator():
    handle = OBBStream(_Source())
    assert handle.media_type == "text/event-stream"
    assert handle.started is False
    assert handle.running is False
    assert "OBBStream(" in repr(handle)


def test_init_with_async_iterable():
    async def _agen():
        yield "x"

    handle = OBBStream(_agen())
    assert handle.media_type == "text/event-stream"


def test_init_rejects_non_iterable():
    with pytest.raises(TypeError):
        OBBStream(object())


def test_resolve_sink_rejects_invalid():
    with pytest.raises(TypeError):
        OBBStream._resolve_sink(123)


def test_serialize_chunk_variants():
    assert OBBStream._serialize_chunk("a") == "a"
    assert OBBStream._serialize_chunk(b"b") == b"b"
    assert OBBStream._serialize_chunk(_Model()) == '{"tick": 1}\n'
    assert OBBStream._serialize_chunk({"x": 1}) == '{"x": 1}\n'


def test_start_to_file(tmp_path):
    path = tmp_path / "out.txt"
    handle = OBBStream(_Source(3))
    handle.start(output=str(path))
    handle.wait(timeout=2)
    handle.stop()
    assert "data: 0" in path.read_text()
    assert handle.running is False


def test_start_to_stringio_default_repr():
    buf = io.StringIO()
    handle = OBBStream(_Source(3))
    handle.start(output=buf)
    handle.wait(timeout=2)
    handle.stop()
    assert handle.started is True
    lines = [line for line in buf.getvalue().splitlines() if line.strip()]
    assert lines == ["data: 0", "data: 1", "data: 2"]


def test_start_to_socket():
    recv, send = socket.socketpair()
    recv.settimeout(2)
    handle = OBBStream(_Source(2))
    handle.start(output=send)
    handle.wait(timeout=2)
    handle.stop()
    data = recv.recv(4096)
    recv.close()
    send.close()
    assert b"data: 0" in data


def test_start_serializes_model_rows():
    buf = io.StringIO()

    class _ModelSource:
        media_type = "text/event-stream"

        def __init__(self):
            self.body_iterator = self._gen()

        async def _gen(self):
            yield _Model()

    handle = OBBStream(_ModelSource())
    handle.start(output=buf)
    handle.wait(timeout=2)
    handle.stop()
    assert buf.getvalue() == '{"tick": 1}\n'


def test_start_twice_raises():
    handle = OBBStream(_Source(1000, sleep=0.05))
    handle.start(output=io.StringIO())
    try:
        with pytest.raises(RuntimeError):
            handle.start()
    finally:
        handle.stop()


def test_start_after_stop_raises():
    handle = OBBStream(_Source(3))
    handle.start(output=io.StringIO())
    handle.wait(timeout=2)
    handle.stop()
    with pytest.raises(RuntimeError, match="single-use"):
        handle.start()


def test_start_after_iteration_raises():
    async def _run():
        handle = OBBStream(_Source(2))
        _ = [chunk async for chunk in handle]
        return handle

    handle = asyncio.run(_run())
    with pytest.raises(RuntimeError, match="single-use"):
        handle.start()


def test_handler_filters_chunks():
    buf = io.StringIO()
    seen: list = []

    def _handler(chunk):
        seen.append(chunk)

    handle = OBBStream(_Source(3))
    handle.start(output=buf, handler=_handler)
    handle.wait(timeout=2)
    handle.stop()
    assert len(seen) == 3
    assert buf.getvalue() == ""


def test_handler_async_transform():
    buf = io.StringIO()

    async def _handler(chunk):
        return chunk.upper()

    handle = OBBStream(_Source(2))
    handle.start(output=buf, handler=_handler)
    handle.wait(timeout=2)
    handle.stop()
    assert "DATA: 0" in buf.getvalue()


def test_async_iteration():
    async def _run():
        return [chunk async for chunk in OBBStream(_Source(3))]

    assert asyncio.run(_run()) == ["data: 0\n\n", "data: 1\n\n", "data: 2\n\n"]


def test_aiter_bytes():
    async def _run():
        return [chunk async for chunk in OBBStream(_Source(2)).aiter_bytes()]

    assert asyncio.run(_run()) == [b"data: 0\n\n", b"data: 1\n\n"]


def test_aiter_returns_iterator():
    handle = OBBStream(_Source(1))
    assert handle.aiter() is handle._body_iterator
    assert handle.started is True


def test_from_query_plain_result():
    class _Query:
        async def execute(self):
            async def _gen():
                yield "a"

            return _gen()

    async def _run():
        handle = await OBBStream.from_query(_Query())
        return [chunk async for chunk in handle]

    assert asyncio.run(_run()) == ["a"]


def test_from_query_annotated_result():
    class _Query:
        async def execute(self):
            async def _gen():
                yield "b"

            return AnnotatedResult(result=_gen(), metadata={})

    async def _run():
        handle = await OBBStream.from_query(_Query())
        return [chunk async for chunk in handle]

    assert asyncio.run(_run()) == ["b"]


def test_wait_returns_immediately_when_not_started():
    handle = OBBStream(_Source(1))
    handle.wait(timeout=1)
    assert handle.running is False


def test_stop_interrupts_stalled_stream():
    class _Stalled:
        media_type = "text/event-stream"

        def __init__(self):
            self.body_iterator = self._gen()

        async def _gen(self):
            await asyncio.sleep(100)
            yield "never"

    handle = OBBStream(_Stalled())
    handle.start(output=io.StringIO())
    time.sleep(0.1)
    started = time.monotonic()
    handle.stop(timeout=5)
    assert time.monotonic() - started < 3
    assert handle.running is False


def test_run_cancels_when_stop_requested_before_loop_starts():
    handle = OBBStream(_Source(3))
    handle._stop_event.set()
    buf = io.StringIO()
    try:
        handle._run(buf, False)
    finally:
        asyncio.set_event_loop(None)
    assert handle.running is False
    assert buf.getvalue() == ""


def test_drain_pending_tasks_cancels_leftover_loop_tasks():
    class _LeakySource:
        media_type = "text/event-stream"

        def __init__(self):
            self.body_iterator = self._gen()

        async def _gen(self):
            asyncio.ensure_future(asyncio.sleep(1000))
            yield "data: 0\n\n"

    handle = OBBStream(_LeakySource())
    handle.start(output=io.StringIO())
    handle.wait(timeout=2)
    handle.stop()
    assert handle.running is False


def test_stop_when_never_started_is_noop():
    handle = OBBStream(_Source(1))
    handle.stop()
    assert handle.running is False


def test_wait_with_timeout_on_long_stream():
    handle = OBBStream(_Source(1000, sleep=0.05))
    handle.start(output=io.StringIO())
    handle.wait(timeout=0.2)
    handle.stop()
    assert handle.running is False


def test_stop_all_stops_active_streams():
    handle = OBBStream(_Source(1000, sleep=0.05))
    handle.start(output=io.StringIO())
    assert handle.running is True
    stop_all()
    assert handle.running is False


def test_install_shutdown_handlers_idempotent_and_signal_chain(monkeypatch):
    import signal

    _install_shutdown_handlers.cache_clear()

    registered: dict = {}

    def _fake_signal(sig, handler):
        registered[sig] = handler

    monkeypatch.setattr(signal, "signal", _fake_signal)
    monkeypatch.setattr(signal, "getsignal", lambda _sig: signal.SIG_DFL)
    monkeypatch.setattr(stream_module, "stop_all", lambda *a, **k: None)

    _install_shutdown_handlers()
    _install_shutdown_handlers()

    handler = registered.get(signal.SIGINT)
    assert callable(handler)

    killed: list = []
    monkeypatch.setattr(stream_module.os, "kill", lambda pid, sig: killed.append(sig))
    handler(signal.SIGINT, None)
    assert killed == [signal.SIGINT]

    _install_shutdown_handlers.cache_clear()


def test_resolve_sink_defaults_to_stdout():
    import sys

    sink, close = OBBStream._resolve_sink(None)
    assert sink is sys.stdout
    assert close is False


def test_write_decodes_bytes_for_text_sink():
    buf = io.StringIO()
    OBBStream._write(buf, b"hello\n")
    assert buf.getvalue() == "hello\n"


def test_install_handlers_non_main_thread():
    import threading

    _install_shutdown_handlers.cache_clear()
    errors: list = []

    def _run():
        try:
            _install_shutdown_handlers()
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    worker = threading.Thread(target=_run)
    worker.start()
    worker.join()
    assert not errors
    _install_shutdown_handlers.cache_clear()


def test_install_handlers_getsignal_raises(monkeypatch):
    import signal

    _install_shutdown_handlers.cache_clear()

    def _raise(_sig):
        raise ValueError("no handler")

    monkeypatch.setattr(signal, "signal", lambda *a: None)
    monkeypatch.setattr(signal, "getsignal", _raise)
    monkeypatch.setattr(stream_module, "stop_all", lambda *a, **k: None)
    _install_shutdown_handlers()
    _install_shutdown_handlers.cache_clear()


def test_install_handlers_sigterm_absent(monkeypatch):
    import signal

    _install_shutdown_handlers.cache_clear()
    monkeypatch.delattr(signal, "SIGTERM", raising=False)
    monkeypatch.setattr(signal, "signal", lambda *a: None)
    monkeypatch.setattr(signal, "getsignal", lambda _sig: signal.SIG_DFL)
    monkeypatch.setattr(stream_module, "stop_all", lambda *a, **k: None)
    _install_shutdown_handlers()
    _install_shutdown_handlers.cache_clear()


def test_install_shutdown_handlers_chains_previous(monkeypatch):
    import signal

    _install_shutdown_handlers.cache_clear()

    registered: dict = {}
    prev_calls: list = []

    def _prev(signum, frame):
        prev_calls.append(signum)

    def _record_signal(sig, handler):
        registered[sig] = handler

    monkeypatch.setattr(signal, "signal", _record_signal)
    monkeypatch.setattr(signal, "getsignal", lambda _sig: _prev)
    monkeypatch.setattr(stream_module, "stop_all", lambda *a, **k: None)

    _install_shutdown_handlers()
    registered[signal.SIGINT](signal.SIGINT, None)
    assert prev_calls == [signal.SIGINT]

    _install_shutdown_handlers.cache_clear()
