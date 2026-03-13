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
