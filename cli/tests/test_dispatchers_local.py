"""Tests for openbb_cli.dispatchers.local.LocalDispatcher.

Every test resolves commands through the **real** generated static ``obb``
namespace produced by the session-scoped synthetic-extension fixture. Each
``run_in_obb`` call is a fresh subprocess so entry-point caching can't
masquerade as a working dispatcher.
"""

from openbb_cli.dispatchers.local import CommandNotFound, LocalDispatcher


def test_dispatch_resolves_real_command(run_in_obb):
    """The dispatcher walks ``obb.cli_test.echo`` and returns its OBBject."""
    result = run_in_obb("""
        import asyncio
        from openbb_cli.dispatchers.local import LocalDispatcher
        from openbb_cli.dispatchers.protocol import Request
        d = LocalDispatcher()
        resp = asyncio.run(
            d.dispatch(Request(id="r1", command="cli_test.echo", params={"value": "hi"}))
        )
        RESULT = resp.model_dump()
    """)
    assert result["ok"] is True
    assert result["id"] == "r1"
    assert result["result"]["results"] == {"echo": "hi"}


def test_dispatch_async_command(run_in_obb):
    """Async commands are awaited; results round-trip through OBBject."""
    result = run_in_obb("""
        import asyncio
        from openbb_cli.dispatchers.local import LocalDispatcher
        from openbb_cli.dispatchers.protocol import Request
        d = LocalDispatcher()
        resp = asyncio.run(
            d.dispatch(Request(command="cli_test.quote", params={"symbol": "TSLA"}))
        )
        RESULT = resp.model_dump()
    """)
    assert result["ok"] is True
    assert result["result"]["results"] == {"symbol": "TSLA", "async": True}


def test_dispatch_missing_command(run_in_obb):
    """Unknown command paths surface as CommandNotFound, not raised."""
    result = run_in_obb("""
        import asyncio
        from openbb_cli.dispatchers.local import LocalDispatcher
        from openbb_cli.dispatchers.protocol import Request
        d = LocalDispatcher()
        resp = asyncio.run(d.dispatch(Request(command="not.a.real.thing")))
        RESULT = resp.model_dump()
    """)
    assert result["ok"] is False
    assert result["error"]["type"] == "CommandNotFound"


def test_dispatch_missing_required_param(run_in_obb):
    """Missing required param surfaces as a structured error.

    ``cli_test.quote`` declares ``symbol: str`` as required. openbb-core's
    router wrapping rejects the call when it isn't supplied; the dispatcher
    reports the failure as ``ok=False`` with a populated ``error`` field.
    """
    result = run_in_obb("""
        import asyncio
        from openbb_cli.dispatchers.local import LocalDispatcher
        from openbb_cli.dispatchers.protocol import Request
        d = LocalDispatcher()
        resp = asyncio.run(
            d.dispatch(Request(command="cli_test.quote", params={}))
        )
        RESULT = resp.model_dump()
    """)
    assert result["ok"] is False
    assert result["error"] is not None
    assert result["error"]["type"]


def test_dispatch_runtime_error_isolated(run_in_obb):
    """A command that raises produces an error Response, not propagation.

    openbb-core wraps user-raised exceptions in ``OpenBBError`` at the
    command-runner boundary, so that's the type the dispatcher reports.
    """
    result = run_in_obb("""
        import asyncio
        from openbb_cli.dispatchers.local import LocalDispatcher
        from openbb_cli.dispatchers.protocol import Request
        d = LocalDispatcher()
        resp = asyncio.run(d.dispatch(Request(command="cli_test.bomb")))
        RESULT = resp.model_dump()
    """)
    assert result["ok"] is False
    assert result["error"]["type"] == "OpenBBError"
    assert "boom" in result["error"]["message"]


def test_dispatch_empty_segment_rejected(run_in_obb):
    result = run_in_obb("""
        import asyncio
        from openbb_cli.dispatchers.local import LocalDispatcher
        from openbb_cli.dispatchers.protocol import Request
        d = LocalDispatcher()
        resp = asyncio.run(d.dispatch(Request(command="cli_test..echo")))
        RESULT = resp.model_dump()
    """)
    assert result["ok"] is False
    assert result["error"]["type"] == "CommandNotFound"


def test_dispatch_list_results_round_trip(run_in_obb):
    """List-typed OBBject results survive serialization to dict."""
    result = run_in_obb("""
        import asyncio
        from openbb_cli.dispatchers.local import LocalDispatcher
        from openbb_cli.dispatchers.protocol import Request
        d = LocalDispatcher()
        resp = asyncio.run(
            d.dispatch(Request(command="cli_test.rows", params={"n": 3}))
        )
        RESULT = resp.model_dump()
    """)
    assert result["ok"] is True
    assert result["result"]["results"] == [
        {"i": 0, "v": 0},
        {"i": 1, "v": 2},
        {"i": 2, "v": 4},
    ]


def test_aclose_is_noop(run_in_obb):
    result = run_in_obb("""
        import asyncio
        from openbb_cli.dispatchers.local import LocalDispatcher
        d = LocalDispatcher()
        asyncio.run(d.aclose())
        RESULT = {"closed": True}
    """)
    assert result == {"closed": True}


def test_serialize_passes_through_primitives():
    assert LocalDispatcher._serialize(None) is None
    assert LocalDispatcher._serialize(42) == 42
    assert LocalDispatcher._serialize("x") == "x"
    assert LocalDispatcher._serialize([1, 2, 3]) == [1, 2, 3]


def test_serialize_uses_model_dump():
    class M:
        def model_dump(
            self, *, exclude_unset: bool = False, exclude_none: bool = False
        ) -> dict:
            return {
                "v": 1,
                "exclude_unset": exclude_unset,
                "exclude_none": exclude_none,
            }

    assert LocalDispatcher._serialize(M()) == {
        "v": 1,
        "exclude_unset": True,
        "exclude_none": True,
    }


def test_serialize_uses_to_dict_for_dataframe_like():
    """Hits the ``to_dict(orient='records')`` branch in ``_serialize``."""

    class D:
        def to_dict(self, orient: str):
            assert orient == "records"
            return [{"a": 1}, {"a": 2}]

    assert LocalDispatcher._serialize(D()) == [{"a": 1}, {"a": 2}]


def test_resolve_walks_attribute_path():
    from types import SimpleNamespace

    root = SimpleNamespace(a=SimpleNamespace(b=SimpleNamespace(c="leaf")))
    assert LocalDispatcher._resolve(root, "a.b.c") == "leaf"


def test_resolve_empty_segment_raises():
    import pytest

    with pytest.raises(CommandNotFound):
        LocalDispatcher._resolve(object(), "a..b")


def test_resolve_unknown_attribute_raises():
    import pytest

    with pytest.raises(CommandNotFound):
        LocalDispatcher._resolve(object(), "missing")


def test_command_not_found_subclasses_keyerror():
    assert issubclass(CommandNotFound, KeyError)


def test_dispatch_runs_sync_command_in_thread_pool():
    """Sync (non-async) callables go through ``asyncio.to_thread``."""
    import asyncio
    import sys
    from types import SimpleNamespace
    from unittest.mock import patch as _patch

    from openbb_cli.dispatchers.protocol import Request

    def sync_echo(value: str) -> dict:
        return {"echo": value, "ran_in": "main_or_thread"}

    fake = SimpleNamespace(cli_test=SimpleNamespace(echo=sync_echo))
    fake_module = SimpleNamespace(obb=fake)
    with _patch.dict(sys.modules, {"openbb": fake_module}):
        d = LocalDispatcher()
    resp = asyncio.run(
        d.dispatch(Request(command="cli_test.echo", params={"value": "x"}))
    )
    assert resp.ok is True
    assert resp.result == {"echo": "x", "ran_in": "main_or_thread"}


def test_dispatch_runs_async_command_in_loop():
    """Async (coroutine) callables are awaited directly."""
    import asyncio
    import sys
    from types import SimpleNamespace
    from unittest.mock import patch as _patch

    from openbb_cli.dispatchers.protocol import Request

    async def async_echo(value: str) -> dict:
        await asyncio.sleep(0)
        return {"echo": value, "ran_in": "loop"}

    fake = SimpleNamespace(cli_test=SimpleNamespace(echo=async_echo))
    fake_module = SimpleNamespace(obb=fake)
    with _patch.dict(sys.modules, {"openbb": fake_module}):
        d = LocalDispatcher()
    resp = asyncio.run(
        d.dispatch(Request(command="cli_test.echo", params={"value": "y"}))
    )
    assert resp.ok is True
    assert resp.result == {"echo": "y", "ran_in": "loop"}


def test_run_in_obb_propagates_subprocess_failure(run_in_obb):
    """The helper raises AssertionError if the subprocess exits non-zero."""
    import pytest

    with pytest.raises(AssertionError) as exc_info:
        run_in_obb("RESULT = 1/0")
    assert "ZeroDivisionError" in str(exc_info.value) or "rc=" in str(exc_info.value)
