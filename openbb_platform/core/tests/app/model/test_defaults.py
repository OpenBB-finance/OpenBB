"""Test the Defaults class."""

from openbb_core.app.model.defaults import Defaults


def test_defaults():
    """Test the Defaults class."""
    cc = Defaults(commands={"/equity/price": {"provider": "test"}})
    assert isinstance(cc, Defaults)
    assert cc.commands == {"equity.price": {"provider": ["test"]}}


def test_fields():
    """Test the Defaults fields."""
    assert "commands" in Defaults.model_fields


"""Additional tests for openbb_core.app.model.defaults.Defaults."""

import pytest

from openbb_core.app.model.abstract.warning import OpenBBWarning


def test_defaults_normalizes_route_keys_and_provider_string():
    d = Defaults(commands={"/equity/profile": {"provider": "fmp"}})
    assert "equity.profile" in d.commands
    assert d.commands["equity.profile"]["provider"] == ["fmp"]


def test_defaults_routes_alias_warns():
    with pytest.warns(OpenBBWarning, match="deprecated"):
        d = Defaults(
            routes={"/x/y": {"provider": "p"}},
            preferences={"show_warnings": False},
        )
    assert "x.y" in d.commands


def test_defaults_empty_routes_treated_as_missing():
    d = Defaults(routes={}, preferences={"show_warnings": True})
    assert d.commands == {}


def test_defaults_update_merges_commands():
    d = Defaults(commands={"a.b": {"provider": ["p1"]}})
    d.update(Defaults(commands={"a.c": {"provider": ["p2"]}}))
    assert "a.b" in d.commands
    assert "a.c" in d.commands


def test_defaults_repr_contains_classname():
    d = Defaults(commands={"a.b": {"provider": ["p"]}})
    r = repr(d)
    assert "Defaults" in r
    assert "commands" in r
