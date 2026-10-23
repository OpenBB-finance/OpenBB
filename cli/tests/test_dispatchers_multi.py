"""Tests for openbb_cli.dispatchers.multi — namespace routing and aggregation."""

from __future__ import annotations

import pytest

from openbb_cli.dispatchers.multi import MultiSpecDispatcher
from openbb_cli.dispatchers.protocol import Request, Response, ResponseError


class _StubDispatcher:
    """Minimal HttpDispatcher stand-in for routing tests.

    Records every call so assertions can verify which backend received a
    request and with what command/params after the namespace strip.
    """

    def __init__(self, name: str, commands: list[str]) -> None:
        self.name = name
        self._spec_doc = {
            "commands": {cmd: {"description": f"{name} {cmd}"} for cmd in commands}
        }
        self.calls: list[tuple[str, dict | None]] = []
        self.closed = False

    async def dispatch(self, request: Request, method: str | None = None) -> Response:
        self.calls.append((request.command, request.params))
        if request.command == "__commands__":
            return Response(
                id=request.id,
                ok=True,
                result=[
                    {"name": c, "description": ""} for c in self._spec_doc["commands"]
                ],
                error=None,
            )
        if request.command == "__schema__":
            name = (request.params or {}).get("name")
            return Response(
                id=request.id,
                ok=True,
                result={"name": name, "from": self.name},
                error=None,
            )
        return Response(
            id=request.id,
            ok=True,
            result={"backend": self.name, "command": request.command},
            error=None,
        )

    async def aclose(self) -> None:
        self.closed = True


def _make_multi() -> tuple[MultiSpecDispatcher, _StubDispatcher, _StubDispatcher]:
    a = _StubDispatcher("a", ["bill", "law"])
    b = _StubDispatcher("b", ["markets.ambs", "rates"])
    return MultiSpecDispatcher({"a": a, "b": b}), a, b


def test_init_rejects_empty_dispatchers():
    with pytest.raises(ValueError, match="at least one namespace"):
        MultiSpecDispatcher({})


def test_merged_spec_doc_prefixes_command_names():
    multi, _, _ = _make_multi()
    cmds = multi._spec_doc["commands"]
    assert set(cmds) == {"a.bill", "a.law", "b.markets.ambs", "b.rates"}


def test_merged_spec_doc_publishes_each_namespace_as_top_level_menu():
    """The REPL Home reads ``routers`` to populate menus — without per-namespace
    entries here, the multi-spec REPL would render an empty Home."""
    multi, _, _ = _make_multi()
    routers = multi._spec_doc["routers"]
    assert routers == {"a": "menu", "b": "menu"}


def test_merged_spec_doc_namespaces_reference_paths_and_routers():
    """``reference.paths`` and ``reference.routers`` come along too, with each
    entry namespaced so describe / help text resolves under the right backend."""
    a = _StubDispatcher("a", ["bill"])
    a._spec_doc["reference"] = {
        "paths": {"/bill": {"description": "A bill."}},
        "routers": {"": {"description": "Top-level a."}},
    }
    b = _StubDispatcher("b", ["rates"])
    b._spec_doc["reference"] = {
        "paths": {"/rates": {"description": "A rate."}},
        "routers": {"markets": {"description": "Markets sub."}},
    }
    multi = MultiSpecDispatcher({"a": a, "b": b})
    ref = multi._spec_doc["reference"]
    assert ref["paths"] == {
        "/a/bill": {"description": "A bill."},
        "/b/rates": {"description": "A rate."},
    }
    assert ref["routers"] == {
        "a": {"description": "Top-level a."},
        "b/markets": {"description": "Markets sub."},
    }


@pytest.mark.asyncio
async def test_dispatch_routes_to_namespace_and_strips_prefix():
    multi, a, b = _make_multi()
    resp = await multi.dispatch(Request(command="b.markets.ambs", params={"x": 1}))
    assert resp.ok
    assert resp.result == {"backend": "b", "command": "markets.ambs"}
    assert b.calls == [("markets.ambs", {"x": 1})]
    assert a.calls == []


@pytest.mark.asyncio
async def test_dispatch_unknown_namespace_returns_error():
    multi, _, _ = _make_multi()
    resp = await multi.dispatch(Request(command="c.foo"))
    assert not resp.ok
    assert resp.error.type == "UnknownNamespace"
    assert "Available: a, b" in resp.error.message


@pytest.mark.asyncio
async def test_dispatch_command_without_dot_errors():
    """A bare ``foo`` (no namespace prefix) must not silently match a backend."""
    multi, _, _ = _make_multi()
    resp = await multi.dispatch(Request(command="bill"))
    assert not resp.ok
    assert resp.error.type == "UnknownNamespace"


@pytest.mark.asyncio
async def test_list_commands_aggregates_with_prefixed_names():
    multi, _, _ = _make_multi()
    resp = await multi.dispatch(Request(command="__commands__"))
    assert resp.ok
    names = [r["name"] for r in resp.result]
    assert names == sorted(["a.bill", "a.law", "b.markets.ambs", "b.rates"])


@pytest.mark.asyncio
async def test_list_commands_skips_failing_backends():
    """A backend that errors on ``__commands__`` doesn't poison the aggregate."""

    class _Broken(_StubDispatcher):
        async def dispatch(self, request, method=None):
            if request.command == "__commands__":
                return Response(
                    id=request.id,
                    ok=False,
                    result=None,
                    error=ResponseError(type="X", message="broke"),
                )
            return await super().dispatch(request, method)

    a = _StubDispatcher("a", ["bill"])
    b = _Broken("b", ["rates"])
    multi = MultiSpecDispatcher({"a": a, "b": b})
    resp = await multi.dispatch(Request(command="__commands__"))
    assert resp.ok
    assert [r["name"] for r in resp.result] == ["a.bill"]


@pytest.mark.asyncio
async def test_schema_strips_namespace_and_forwards():
    multi, a, b = _make_multi()
    resp = await multi.dispatch(
        Request(command="__schema__", params={"name": "a.bill"})
    )
    assert resp.ok
    assert resp.result == {"name": "bill", "from": "a"}
    assert a.calls == [("__schema__", {"name": "bill"})]
    assert b.calls == []


@pytest.mark.asyncio
async def test_schema_unknown_namespace_returns_error():
    multi, _, _ = _make_multi()
    resp = await multi.dispatch(Request(command="__schema__", params={"name": "c.foo"}))
    assert not resp.ok
    assert resp.error.type == "UnknownNamespace"


@pytest.mark.asyncio
async def test_schema_missing_namespace_in_name_errors():
    multi, _, _ = _make_multi()
    resp = await multi.dispatch(
        Request(command="__schema__", params={"name": "bareword"})
    )
    assert not resp.ok
    assert resp.error.type == "UnknownNamespace"


@pytest.mark.asyncio
async def test_list_commands_skips_malformed_entries():
    """Entries that aren't dicts (or lack a ``name``) are dropped from the aggregate."""

    class _Misbehaving(_StubDispatcher):
        async def dispatch(self, request, method=None):
            if request.command == "__commands__":
                return Response(
                    id=request.id,
                    ok=True,
                    result=[
                        "not-a-dict",  # skipped
                        {"description": "no name key"},  # skipped (no `name`)
                        {"name": "valid"},  # kept
                    ],
                    error=None,
                )
            return await super().dispatch(request, method)

    multi = MultiSpecDispatcher({"x": _Misbehaving("x", [])})
    resp = await multi.dispatch(Request(command="__commands__"))
    assert resp.ok
    assert [r["name"] for r in resp.result] == ["x.valid"]


@pytest.mark.asyncio
async def test_aclose_closes_every_backend():
    multi, a, b = _make_multi()
    await multi.aclose()
    assert a.closed and b.closed
