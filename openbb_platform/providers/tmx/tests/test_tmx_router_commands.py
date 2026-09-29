"""Tests that every model-backed router command delegates to the query engine."""

import inspect

import pytest

from openbb_tmx.routers import (
    calendar,
    currency,
    derivatives,
    equity,
    estimates,
    etf,
    fixedincome,
    fundamentals,
    futures,
    index,
    markets,
    news,
    options,
    ownership,
)

MODULES = [
    calendar,
    currency,
    derivatives,
    equity,
    estimates,
    etf,
    fixedincome,
    fundamentals,
    futures,
    index,
    markets,
    news,
    options,
    ownership,
]


def _commands(module):
    """Yield every coroutine command defined on a sub-router module."""
    for name, obj in vars(module).items():
        if name.startswith("_") or not inspect.iscoroutinefunction(obj):
            continue

        if set(inspect.signature(obj).parameters) == {
            "cc",
            "provider_choices",
            "standard_params",
            "extra_params",
        }:
            yield name, obj


ALL_COMMANDS = [
    pytest.param(module, name, command, id=f"{module.__name__.split('.')[-1]}.{name}")
    for module in MODULES
    for name, command in _commands(module)
]


class TestCommandDelegation:
    """Every command hands off to ``OBBject.from_query``."""

    def test_every_module_exposes_commands(self):
        assert len(ALL_COMMANDS) >= 30

    @pytest.mark.parametrize(("module", "name", "command"), ALL_COMMANDS)
    async def test_command_delegates(self, monkeypatch, module, name, command):
        seen: dict = {}

        async def from_query(query):
            seen["called"] = True
            return "obbject"

        monkeypatch.setattr(
            "openbb_core.app.model.obbject.OBBject.from_query", from_query
        )
        monkeypatch.setattr(module, "OBBQuery", lambda **kwargs: kwargs)

        result = await command(
            cc=None, provider_choices=None, standard_params=None, extra_params=None
        )

        assert result == "obbject"
        assert seen["called"]
