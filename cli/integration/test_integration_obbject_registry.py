"""Test the obbject registry."""

from openbb_core.app.model.obbject import OBBject

from openbb_cli.argparse_translator.obbject_registry import Registry

# ruff: noqa: F841


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

    assert registry.register(obbject1) is True
    assert registry.register(obbject2) is True
    assert registry.register(obbject1) is False
    assert len(registry.obbjects) == 2

    assert registry.get(0) == obbject2
    assert registry.get(1) == obbject1
    assert registry.get("key1") == obbject1
    assert registry.get("key2") == obbject2
    assert registry.get(2) is None
    assert registry.get("invalid_key") is None

    registry.remove(0)
    assert len(registry.obbjects) == 1
    assert registry.get("key2") is None

    all_obbjects = registry.all
    # ``command`` lives under ``extra`` — that's where the OBBject keeps
    # it and where the registry surfaces it (no synthetic top-level
    # mirror that would duplicate ``extra.metadata.route`` etc.).
    assert "command" in all_obbjects[0]["extra"]
    assert all_obbjects[0]["extra"]["command"] == "cmd1"

    registry.remove()
    assert len(registry.obbjects) == 0
    assert registry.get("key1") is None
