"""Test the Defaults class."""

from openbb_core.app.model.defaults import Defaults


def test_defaults():
    """Test the Defaults class."""
    cc = Defaults(routes={"test": {"test": "test"}})
    assert isinstance(cc, Defaults)
    assert cc.routes == {"test": {"test": "test"}}


def test_fields():
    """Test the Defaults fields."""
    fields = Defaults.model_fields
    fields_keys = fields.keys()

    assert "routes" in fields_keys
