"""Test the obbject registry."""

from openbb_cli.argparse_translator.obbject_registry import Registry
from openbb_core.app.model.obbject import OBBject

# pylint: disable=unused-variable
# ruff: noqa: disable=F841


def test_registry_operations():
    """Test the registry operations."""
    registry = Registry()
    obbject1 = OBBject(
        id="1", results=True, extra={"register_key": "key1", "command": "cmd1"}
    )
    obbject2 = OBBject(
        id="2", results=True, extra={"register_key": "key2", "command": "cmd2"}
    )
    obbject3 = OBBject(  # noqa: F841
        id="3", results=True, extra={"register_key": "key3", "command": "cmd3"}
    )

    # Add obbjects to the registry
    assert registry.register(obbject1) is True
    assert registry.register(obbject2) is True
    # Attempt to add the same object again
    assert registry.register(obbject1) is False
    # Ensure the registry size is correct
    assert len(registry.obbjects) == 2

    # Get by index
    assert registry.get(0) == obbject2
    assert registry.get(1) == obbject1
    # Get by key
    assert registry.get("key1") == obbject1
    assert registry.get("key2") == obbject2
    # Invalid index/key
    assert registry.get(2) is None
    assert registry.get("invalid_key") is None

    # Remove an object
    registry.remove(0)
    assert len(registry.obbjects) == 1
    assert registry.get("key2") is None

    # Validate the 'all' property
    all_obbjects = registry.all
    assert "command" in all_obbjects[0]
    assert all_obbjects[0]["command"] == "cmd1"

    # Clean up by removing all objects
    registry.remove()
    assert len(registry.obbjects) == 0
    assert registry.get("key1") is None
