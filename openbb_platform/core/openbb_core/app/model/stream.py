"""Lazy, non-blocking, signal-safe handle for streaming responses."""

import asyncio
import atexit
import contextlib
import inspect
import json
import os
import signal
import sys
import threading
import time
from collections.abc import Callable
from functools import cache
from typing import TYPE_CHECKING, Any, cast

from uuid_extensions import uuid7str

if TYPE_CHECKING:
    from openbb_core.app.query import Query

_ACTIVE: "set[OBBStream]" = set()
_ACTIVE_LOCK = threading.Lock()


def stop_all(timeout: float = 2.0) -> None:
    """Stop every active stream.

    Parameters
    ----------
    timeout : float
        Maximum seconds to wait for each stream to wind down.
    """
    with _ACTIVE_LOCK:
        streams = list(_ACTIVE)
    for stream in streams:
        with contextlib.suppress(Exception):
            stream.stop(timeout=timeout)


@cache
def _install_shutdown_handlers() -> None:
    """Install atexit and signal handlers once, chaining to existing handlers."""
    atexit.register(stop_all)

    if threading.current_thread() is not threading.main_thread():
        return

    for sig in (signal.SIGINT, getattr(signal, "SIGTERM", None)):
        if sig is None:
            continue
        try:
            previous = signal.getsignal(sig)
        except (ValueError, OSError):
            continue

        prev_handler = cast(
            "Callable[[int, Any], Any] | None",
            previous if callable(previous) else None,
        )
        prev_is_default = previous == signal.SIG_DFL

        def _handler(signum, frame, _prev=prev_handler, _default=prev_is_default):
            stop_all()
            if _prev is not None:
                _prev(signum, frame)
            elif _default:
                signal.signal(signum, signal.SIG_DFL)
                os.kill(os.getpid(), signum)

        with contextlib.suppress(ValueError, OSError):
            signal.signal(sig, _handler)


class OBBStream:
    """Non-blocking, signal-safe handle to a streaming endpoint response.

    Iterate it directly with ``async for row in stream`` or drive it on a
    background thread with ``start()`` / ``stop()``.

    Attributes
    ----------
    id : str
        Unique identifier of the stream.
    provider : str or None
        Provider name.
    warnings : list or None
        Warnings raised while opening the stream.
    extra : dict
        Extra info, e.g. execution and results metadata.
    media_type : str
        Stream content type, e.g. ``text/event-stream``.

    Methods
    -------
    start(output=None, handler=None)
        Stream on a background thread; output defaults to STDOUT and may be a
        file path, file object, or socket; handler transforms or filters items.
    stop(timeout=5.0)
        Stop the stream and wait for it to wind down.
    wait(timeout=None)
        Block until the stream finishes.

    Examples
    --------
    >>> stream = obb.binance_stream.book_ticker(provider="binance", symbol="BTCUSDT")
    >>> stream.start()
    >>> stream.stop()
    >>> async for row in obb.binance_stream.book_ticker(provider="binance"):
    ...     ...
    """

    def __init__(self, source: Any) -> None:
        """Wrap a streaming response or async iterable.

        Parameters
        ----------
        source : Any
            A streaming response exposing ``body_iterator`` or an async iterable.
        """
        self._response = source
        body_iterator = getattr(source, "body_iterator", None)
        if body_iterator is None and hasattr(source, "__aiter__"):
            body_iterator = source
        if body_iterator is None:
            raise TypeError(
                "OBBStream requires a streaming response or an async iterable; "
                f"got {type(source).__name__}"
            )
        self._body_iterator = body_iterator
        self.media_type = getattr(source, "media_type", None) or "text/event-stream"
        self.id: str = uuid7str()
        self.provider: str | None = None
        self.warnings: list | None = None
        self.extra: dict[str, Any] = {}
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._task: asyncio.Task | None = None
        self._handler: Callable[[Any], Any] | None = None
        self._stop_event = threading.Event()
        self._started = False

    @property
    def started(self) -> bool:
        """Whether the stream has been started."""
        return self._started

    @property
    def running(self) -> bool:
        """Whether the background stream is currently running."""
        return bool(self._thread and self._thread.is_alive())

    @classmethod
    async def from_query(cls, query: "Query") -> "OBBStream":
        """Build an OBBStream from a provider query.

        Parameters
        ----------
        query : Query
            Initialized query whose provider fetcher yields a stream.

        Returns
        -------
        OBBStream
            Handle over the provider's stream, carrying the query's provider and
            any results metadata under ``extra``.
        """
        from openbb_core.provider.abstract.annotated_result import AnnotatedResult

        result = await query.execute()
        metadata = None
        if isinstance(result, AnnotatedResult):
            metadata = result.metadata
            result = result.result
        stream = cls(result)
        stream.provider = getattr(query, "provider", None)
        if metadata is not None:
            stream.extra["results_metadata"] = metadata
        return stream

    def start(
        self,
        output: str | os.PathLike | Any | None = None,
        handler: Callable[[Any], Any] | None = None,
    ) -> "OBBStream":
        """Begin streaming on a background thread.

        Parameters
        ----------
        output : str or os.PathLike or file or socket, optional
            Destination for stream chunks. Defaults to STDOUT.
        handler : Callable, optional
            Function each chunk is passed through before writing. A return value
            is written; ``None`` consumes the chunk. May be sync or async.

        Returns
        -------
        OBBStream
            This handle.
        """
        if self._started:
            raise RuntimeError(
                "stream already started; the underlying iterator is single-use"
                " and cannot be restarted — create a new stream."
            )

        _install_shutdown_handlers()
        self._handler = handler
        self._stop_event = threading.Event()
        sink, close_sink = self._resolve_sink(output)
        self._started = True
        self._thread = threading.Thread(
            target=self._run, args=(sink, close_sink), daemon=True
        )
        with _ACTIVE_LOCK:
            _ACTIVE.add(self)
        self._thread.start()
        return self

    def wait(self, timeout: float | None = None) -> None:
        """Block until the stream finishes, processing signals in short slices.

        Parameters
        ----------
        timeout : float, optional
            Maximum seconds to wait.
        """
        thread = self._thread
        if thread is None:
            return
        deadline = None if timeout is None else time.monotonic() + timeout
        while thread.is_alive():
            thread.join(0.2)
            if deadline is not None and time.monotonic() >= deadline:
                break

    def stop(self, timeout: float = 5.0) -> None:
        """Stop the background stream and wait briefly for it to wind down.

        Parameters
        ----------
        timeout : float
            Maximum seconds to wait for the worker thread to exit.
        """
        self._stop_event.set()
        loop, task = self._loop, self._task
        if loop is not None and task is not None and not loop.is_closed():
            with contextlib.suppress(RuntimeError):
                loop.call_soon_threadsafe(self._cancel)
        if (
            self._thread is not None
            and self._thread.is_alive()
            and self._thread is not threading.current_thread()
        ):
            self._thread.join(timeout=timeout)
        with _ACTIVE_LOCK:
            _ACTIVE.discard(self)

    def _cancel(self) -> None:
        """Cancel the consume task; cancellation unwinds and closes the iterator."""
        if self._task is not None and not self._task.done():
            self._task.cancel()

    def __aiter__(self) -> Any:
        """Return the typed async iterator of stream items."""
        self._started = True
        return self._body_iterator.__aiter__()

    def aiter(self) -> Any:
        """Return the underlying typed async iterator."""
        self._started = True
        return self._body_iterator

    async def aiter_bytes(self) -> Any:
        """Yield serialized chunks as bytes for a server StreamingResponse.

        Yields
        ------
        bytes
            Serialized stream chunk.
        """
        self._started = True
        async for chunk in self._body_iterator:
            serialized = self._serialize_chunk(chunk)
            yield (
                serialized
                if isinstance(serialized, (bytes, bytearray))
                else serialized.encode("utf-8")
            )

    @staticmethod
    def _serialize_chunk(chunk: Any) -> Any:
        """Serialize a stream item to text or bytes.

        Parameters
        ----------
        chunk : Any
            A raw chunk, a pydantic model, or a mapping.

        Returns
        -------
        str or bytes
            The serialized chunk.
        """
        if isinstance(chunk, (str, bytes, bytearray)):
            return chunk
        model_dump_json = getattr(chunk, "model_dump_json", None)
        if callable(model_dump_json):
            return model_dump_json() + "\n"
        return json.dumps(chunk, default=str) + "\n"

    @staticmethod
    def _resolve_sink(output: Any) -> tuple[Any, bool]:
        """Resolve ``output`` to a writable sink and whether to close it.

        Parameters
        ----------
        output : Any
            A path, a writable file or pipe, a socket, or None.

        Returns
        -------
        tuple
            The sink object and whether this handle owns closing it.
        """
        if output is None:
            return sys.stdout, False
        if isinstance(output, (str, os.PathLike)):
            return open(output, "w", encoding="utf-8"), True  # noqa: SIM115
        if hasattr(output, "write") or hasattr(output, "sendall"):
            return output, False
        raise TypeError(
            "output must be a path, a writable file/pipe, or a socket; "
            f"got {type(output).__name__}"
        )

    @classmethod
    def _write(cls, sink: Any, chunk: Any) -> None:
        """Write a serialized chunk to a file, STDOUT, or socket.

        Parameters
        ----------
        sink : Any
            The destination sink.
        chunk : Any
            The stream item to write.
        """
        serialized = cls._serialize_chunk(chunk)
        if hasattr(sink, "sendall"):
            sink.sendall(
                serialized.encode("utf-8")
                if isinstance(serialized, str)
                else serialized
            )
            return
        if isinstance(serialized, (bytes, bytearray)):
            serialized = bytes(serialized).decode("utf-8", errors="replace")
        sink.write(serialized)
        if hasattr(sink, "flush"):
            sink.flush()

    def _run(self, sink: Any, close_sink: bool) -> None:
        """Drive the stream on a dedicated event loop in the worker thread.

        Parameters
        ----------
        sink : Any
            The destination sink.
        close_sink : bool
            Whether to close the sink when the stream ends.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        self._task = loop.create_task(self._consume(sink))
        if self._stop_event.is_set():
            self._task.cancel()
        try:
            with contextlib.suppress(asyncio.CancelledError, Exception):
                loop.run_until_complete(self._task)
        finally:
            with contextlib.suppress(Exception):
                self._drain_pending_tasks(loop)
            with contextlib.suppress(Exception):
                loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
            if close_sink:
                with contextlib.suppress(Exception):
                    sink.close()
            with _ACTIVE_LOCK:
                _ACTIVE.discard(self)

    @staticmethod
    def _drain_pending_tasks(loop: asyncio.AbstractEventLoop) -> None:
        """Cancel and await tasks left on the loop, e.g. a websocket keepalive.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            The worker loop being torn down.
        """
        pending = [task for task in asyncio.all_tasks(loop) if not task.done()]
        if not pending:
            return
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

    async def _consume(self, sink: Any) -> None:
        """Iterate the stream, passing each chunk through the handler to the sink.

        Parameters
        ----------
        sink : Any
            The destination sink.
        """
        handler = self._handler
        iterator = self._body_iterator
        try:
            async for chunk in iterator:
                payload = chunk
                if handler is not None:
                    result = handler(chunk)
                    if inspect.isawaitable(result):
                        result = await result
                    if result is None:
                        continue
                    payload = result
                self._write(sink, payload)
        finally:
            aclose = getattr(iterator, "aclose", None)
            if aclose is not None:
                with contextlib.suppress(Exception):
                    await aclose()

    def __repr__(self) -> str:
        """Return the handle's repr."""
        return f"OBBStream(media_type={self.media_type!r}, running={self.running})"
