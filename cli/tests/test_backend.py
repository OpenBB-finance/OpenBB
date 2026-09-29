"""Tests for the pluggable controller backend.

Drives ``LocalBackend`` against a fake ``openbb`` module injected into
``sys.modules`` (so the tests don't depend on the real provider stack), and
``SpecBackend`` / ``SpecTranslator`` against synthetic spec docs.
"""

from __future__ import annotations

import argparse
import sys
import types
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from openbb_cli.backend import (
    LocalBackend,
    SpecBackend,
    SpecTranslator,
    _CommandStub,
    _NamedStub,
)


class _FakeBaseModel(BaseModel):
    """Pydantic model used to mark a router as a "command" rather than a menu."""

    pass


def _install_fake_obb(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Install a stand-in ``openbb`` module exposing the surface ``LocalBackend`` reads."""
    obb = types.SimpleNamespace()
    obb.equity = types.SimpleNamespace(_marker="menu-equity")
    obb.coverage = _FakeBaseModel()
    obb.user = types.SimpleNamespace()
    obb.system = types.SimpleNamespace()
    obb.account = types.SimpleNamespace()
    obb.reference = {
        "paths": {"/equity/quote": {"description": "Get a quote."}},
        "routers": {"/equity/": {"description": "Equity menu."}},
    }
    fake_mod = types.ModuleType("openbb")
    fake_mod.obb = obb
    monkeypatch.setitem(sys.modules, "openbb", fake_mod)
    return obb


def test_local_backend_lazy_import(monkeypatch):
    """``_obb`` is None until something reads from the backend."""
    _install_fake_obb(monkeypatch)
    backend = LocalBackend()
    assert backend._obb is None
    assert "equity" in backend.routers
    assert backend._obb is not None


def test_local_backend_routers_classifies_menu_vs_command(monkeypatch):
    _install_fake_obb(monkeypatch)
    backend = LocalBackend()
    routers = backend.routers
    assert routers["equity"] == "menu"
    assert routers["coverage"] == "command"
    for excluded in ("user", "system", "account"):
        assert excluded not in routers


def test_local_backend_routers_cached_after_first_call(monkeypatch):
    _install_fake_obb(monkeypatch)
    backend = LocalBackend()
    first = backend.routers
    second = backend.routers
    assert first is second


def test_local_backend_reference_paths_and_routers(monkeypatch):
    _install_fake_obb(monkeypatch)
    backend = LocalBackend()
    assert backend.reference_paths == {"/equity/quote": {"description": "Get a quote."}}
    assert backend.reference_routers == {"/equity/": {"description": "Equity menu."}}


def test_local_backend_get_command_target(monkeypatch):
    obb = _install_fake_obb(monkeypatch)
    backend = LocalBackend()
    assert backend.get_command_target("equity") is obb.equity


def test_local_backend_get_translators_for_path_calls_processor(monkeypatch):
    """``get_translators_for_path`` instantiates ``ArgparseClassProcessor``
    against the obb-side router target and returns its ``translators`` /
    ``paths`` outputs."""
    _install_fake_obb(monkeypatch)
    backend = LocalBackend()
    fake_processor = MagicMock()
    fake_processor.translators = {"equity_quote": MagicMock()}
    fake_processor.paths = {"price": "subpath"}
    monkeypatch.setattr(
        "openbb_cli.argparse_translator.argparse_class_processor.ArgparseClassProcessor",
        MagicMock(return_value=fake_processor),
    )
    translators, paths = backend.get_translators_for_path("equity")
    assert translators == {"equity_quote": fake_processor.translators["equity_quote"]}
    assert paths == {"price": "subpath"}


def _spec_with(commands=None, routers=None, reference=None):
    return {
        "version": 1,
        "base_url": "http://h",
        "api_prefix": "/api",
        "commands": commands or {},
        "routers": routers or {},
        "reference": reference or {"paths": {}, "routers": {}},
    }


def test_spec_backend_routers_filters_top_level_only():
    """Only entries without dots are top-level routers."""
    backend = SpecBackend(
        _spec_with(
            routers={
                "fxs": "menu",
                "fxs.list": "menu",
                "fxs.list.counterparties": "command",
                "rates": "menu",
            }
        ),
        dispatcher=MagicMock(),
    )
    assert backend.routers == {"fxs": "menu", "rates": "menu"}


def test_spec_backend_reference_paths_and_routers():
    backend = SpecBackend(
        _spec_with(
            reference={
                "paths": {"/x": {"description": "x"}},
                "routers": {"/x/": {"description": "X menu"}},
            }
        ),
        dispatcher=MagicMock(),
    )
    assert backend.reference_paths == {"/x": {"description": "x"}}
    assert backend.reference_routers == {"/x/": {"description": "X menu"}}


def test_spec_backend_reference_handles_missing_keys():
    """An empty spec doc should still yield empty dicts, not raise."""
    backend = SpecBackend(
        {"version": 1, "base_url": "http://h"}, dispatcher=MagicMock()
    )
    assert backend.reference_paths == {}
    assert backend.reference_routers == {}


def test_spec_backend_get_command_target_unknown_returns_stub():
    backend = SpecBackend(_spec_with(), dispatcher=MagicMock())
    stub = backend.get_command_target("not.a.command")
    assert isinstance(stub, _CommandStub)
    assert stub.model_dump()["command"] == "not.a.command"


def test_spec_backend_get_command_target_known_includes_meta():
    backend = SpecBackend(
        _spec_with(commands={"x": {"method": "get", "url_path": "/api/x"}}),
        dispatcher=MagicMock(),
    )
    stub = backend.get_command_target("x")
    dump = stub.model_dump()
    assert dump["command"] == "x"
    assert dump["method"] == "get"
    assert dump["url_path"] == "/api/x"


def test_spec_backend_get_translators_for_path_collects_commands():
    """Commands under ``router.`` show up; other prefixes are skipped."""
    cmd_spec = {"method": "get", "url_path": "/api/x", "parameters": []}
    backend = SpecBackend(
        _spec_with(
            commands={
                "fxs.latest": cmd_spec,
                "fxs.list.counterparties": cmd_spec,
                "fxs.search": cmd_spec,
                "rates.all.latest": cmd_spec,
            }
        ),
        dispatcher=MagicMock(),
    )
    translators, paths = backend.get_translators_for_path("fxs")
    assert set(translators) == {"fxs_latest", "fxs_list_counterparties", "fxs_search"}
    assert paths == {"list": "subpath"}


def test_spec_backend_get_translators_for_path_lists_only_direct_children():
    """Grandchildren (``pd.get.all.timeseries.csv`` -> ``all``, ``timeseries``)
    must not surface as direct sub-paths — they're embedded in flattened
    translator names under their direct-parent sub-controller instead.
    """
    cmd_spec = {"method": "get", "url_path": "/api/x", "parameters": []}
    backend = SpecBackend(
        _spec_with(
            commands={
                "pd.list.timeseries": cmd_spec,
                "pd.get.all.timeseries.csv": cmd_spec,
            }
        ),
        dispatcher=MagicMock(),
    )
    translators, paths = backend.get_translators_for_path("pd")
    assert paths == {"list": "subpath", "get": "subpath"}
    assert "all" not in paths
    assert "timeseries" not in paths
    # Translator names keep the full flattened path so the direct-child
    # sub-controller can still route to nested commands.
    assert "pd_get_all_timeseries_csv" in translators
    assert "pd_list_timeseries" in translators


def test_spec_backend_empty_router_returns_no_translators():
    backend = SpecBackend(
        _spec_with(commands={"other.x": {"method": "get", "parameters": []}}),
        dispatcher=MagicMock(),
    )
    translators, paths = backend.get_translators_for_path("missing")
    assert translators == {}
    assert paths == {}


def test_command_stub_model_dump_carries_meta():
    stub = _CommandStub("x.y", {"method": "get", "url_path": "/api/x/y"})
    dump = stub.model_dump()
    assert dump == {"command": "x.y", "method": "get", "url_path": "/api/x/y"}


def test_command_stub_model_dump_with_empty_meta():
    stub = _CommandStub("solo", {})
    assert stub.model_dump() == {"command": "solo"}


def _trl(command: str, dispatcher: Any) -> SpecTranslator:
    return SpecTranslator(
        command,
        {
            "method": "get",
            "url_path": f"/api/{command.replace('.', '/')}",
            "description": "synth",
            "parameters": [
                {
                    "name": "x",
                    "in": "query",
                    "type": "string",
                    "is_list": False,
                    "required": False,
                    "default": None,
                    "choices": [],
                    "help": None,
                }
            ],
        },
        dispatcher,
    )


def test_spec_translator_parser_returns_fresh_copy():
    """``parser`` returns a deep copy each access — controllers mutate it."""
    trl = _trl("foo.bar", dispatcher=MagicMock())
    p1 = trl.parser
    p2 = trl.parser
    assert p1 is not p2
    p1.add_argument("--injected")
    p3 = trl.parser
    assert "--injected" not in {
        opt for action in p3._actions for opt in action.option_strings
    }


def test_spec_translator_func_is_named_stub():
    """``translator.func.__name__`` is used by export-filename generation."""
    trl = _trl("equity.price.historical", dispatcher=MagicMock())
    assert trl.func.__name__ == "equity_price_historical"


def test_spec_translator_execute_func_dispatches_and_returns_result():
    response = MagicMock(ok=True, result={"hello": "world"}, error=None)
    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock(return_value=response)
    trl = _trl("foo.bar", dispatcher)
    out = trl.execute_func(argparse.Namespace(x="v"))
    assert out == {"hello": "world"}
    dispatched_request = dispatcher.dispatch.call_args.args[0]
    assert dispatched_request.command == "foo.bar"
    assert dispatched_request.params == {"x": "v"}


def test_spec_translator_execute_func_drops_none_and_unknown_params():
    """``None`` values are dropped, AND params not declared in the spec are
    stripped — ``parse_known_args_and_warn`` injects CLI-internal flags
    (``export``, ``help``, ``register_obbject``, …) onto the namespace and
    those would otherwise leak onto the upstream URL as query params.
    """
    response = MagicMock(ok=True, result=[], error=None)
    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock(return_value=response)
    trl = _trl("foo.bar", dispatcher)
    trl.execute_func(
        argparse.Namespace(
            x="kept",
            y=None,
            export="",
            help=False,
            register_obbject=True,
        )
    )
    params = dispatcher.dispatch.call_args.args[0].params
    assert params == {"x": "kept"}


def test_spec_translator_execute_func_raises_on_dispatch_failure():
    err = MagicMock(message="server said no")
    response = MagicMock(ok=False, result=None, error=err)
    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock(return_value=response)
    trl = _trl("x", dispatcher)
    with pytest.raises(RuntimeError, match="server said no"):
        trl.execute_func(argparse.Namespace())


def test_spec_translator_execute_func_raises_with_default_message_when_no_error():
    """An ``ok=False`` response without an explicit error still raises."""
    response = MagicMock(ok=False, result=None, error=None)
    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock(return_value=response)
    trl = _trl("x", dispatcher)
    with pytest.raises(RuntimeError, match="dispatch failed"):
        trl.execute_func(argparse.Namespace())


def test_named_stub_records_name():
    stub = _NamedStub("my_cmd")
    assert stub.__name__ == "my_cmd"


def test_named_stub_call_raises():
    """Calling the stub directly is a programming error — controllers must use execute_func."""
    stub = _NamedStub("x")
    with pytest.raises(RuntimeError, match="execute_func"):
        stub()


# --- SpecTranslator multi-provider rejection ---


def _multi_provider_translator(dispatcher: Any) -> SpecTranslator:
    """Translator for a multi-provider command: ``cboe`` accepts ``use_cache``,
    ``intrinio`` accepts ``source``, both share ``symbol``."""
    return SpecTranslator(
        "equity.price.quote",
        {
            "method": "get",
            "url_path": "/api/equity/price/quote",
            "description": "Q",
            "providers": ["cboe", "intrinio"],
            "parameters": [
                {
                    "name": "provider",
                    "in": "query",
                    "type": "string",
                    "is_list": False,
                    "required": True,
                    "choices": ["cboe", "intrinio"],
                    "default": None,
                    "help": None,
                    "providers": [],
                },
                {
                    "name": "symbol",
                    "in": "query",
                    "type": "string",
                    "is_list": False,
                    "required": True,
                    "default": None,
                    "choices": [],
                    "help": None,
                    "providers": [],
                },
                {
                    "name": "use_cache",
                    "in": "query",
                    "type": "boolean",
                    "is_list": False,
                    "required": False,
                    "default": True,
                    "choices": [],
                    "help": None,
                    "providers": ["cboe"],
                },
                {
                    "name": "source",
                    "in": "query",
                    "type": "string",
                    "is_list": False,
                    "required": False,
                    "default": None,
                    "choices": [],
                    "help": None,
                    "providers": ["intrinio"],
                },
            ],
        },
        dispatcher,
    )


def test_spec_translator_dispatches_when_provider_flags_match():
    response = MagicMock(ok=True, result={}, error=None)
    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock(return_value=response)
    trl = _multi_provider_translator(dispatcher)
    trl.execute_func(
        argparse.Namespace(provider="cboe", symbol="AAPL", use_cache=False)
    )
    params = dispatcher.dispatch.call_args.args[0].params
    assert params == {"provider": "cboe", "symbol": "AAPL", "use_cache": False}


def test_spec_translator_rejects_flag_not_valid_for_chosen_provider():
    """``--source`` is intrinio-only; passing it with ``--provider cboe`` raises."""
    import pytest

    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock()
    trl = _multi_provider_translator(dispatcher)
    with pytest.raises(
        RuntimeError, match=r"flags not valid for provider='cboe'.*--source"
    ):
        trl.execute_func(
            argparse.Namespace(provider="cboe", symbol="AAPL", source="iex")
        )
    dispatcher.dispatch.assert_not_called()


def test_spec_translator_no_validation_when_provider_unset():
    """If the user didn't supply ``--provider``, validation is skipped (server reports)."""
    response = MagicMock(ok=True, result={}, error=None)
    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock(return_value=response)
    trl = _multi_provider_translator(dispatcher)
    # No provider in namespace → validation skipped
    trl.execute_func(argparse.Namespace(symbol="AAPL", use_cache=True))
    dispatcher.dispatch.assert_called_once()


def test_spec_translator_no_validation_for_non_multi_provider_command():
    """Single-provider commands: no validation, even if a stray flag is passed."""
    response = MagicMock(ok=True, result={}, error=None)
    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock(return_value=response)
    trl = _trl("foo.bar", dispatcher)  # no providers list
    # Only declared param ``x`` is forwarded; no provider validation kicks in
    trl.execute_func(argparse.Namespace(x="v"))
    dispatcher.dispatch.assert_called_once()
