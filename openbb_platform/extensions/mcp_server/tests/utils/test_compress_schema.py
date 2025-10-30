"""Test schema compression in fastmcp."""

from fastmcp.utilities.json_schema import compress_schema


def test_prune_params():
    """Test the prune_params functionality of compress_schema."""
    schema = {
        "properties": {"a": {"type": "string"}, "b": {"type": "integer"}},
        "required": ["a", "b"],
    }
    compressed = compress_schema(schema, prune_params=["a"])
    assert "a" not in compressed["properties"]
    assert "a" not in compressed["required"]
    assert "b" in compressed["properties"]


def test_prune_defs():
    """Test the prune_defs functionality of compress_schema."""
    schema = {
        "properties": {"a": {"$ref": "#/$defs/Used"}},
        "$defs": {"Used": {"type": "string"}, "Unused": {"type": "integer"}},
    }
    compressed = compress_schema(schema, prune_defs=True)
    assert "Used" in compressed["$defs"]
    assert "Unused" not in compressed["$defs"]


def test_prune_additional_properties():
    """Test the prune_additional_properties functionality of compress_schema."""
    schema = {"properties": {"a": {"type": "string"}}, "additionalProperties": False}
    compressed = compress_schema(schema, prune_additional_properties=True)
    assert "additionalProperties" not in compressed


def test_prune_titles():
    """Test the prune_titles functionality of compress_schema."""
    schema = {"title": "Test", "properties": {"a": {"title": "A", "type": "string"}}}
    compressed = compress_schema(schema, prune_titles=True)
    assert "title" not in compressed
    assert "title" not in compressed["properties"]["a"]


def test_combined_compression():
    """Test a combination of all compression functionalities."""
    schema = {
        "title": "Test",
        "properties": {
            "a": {"$ref": "#/$defs/Used"},
            "b": {"type": "integer"},
            "c": {"type": "string"},
        },
        "required": ["a", "b", "c"],
        "additionalProperties": False,
        "$defs": {"Used": {"type": "string"}, "Unused": {"type": "integer"}},
    }
    compressed = compress_schema(
        schema,
        prune_params=["c"],
        prune_defs=True,
        prune_additional_properties=True,
        prune_titles=True,
    )
    assert "title" not in compressed
    assert "c" not in compressed["properties"]
    assert "c" not in compressed["required"]
    assert "additionalProperties" not in compressed
    assert "Used" in compressed["$defs"]
    assert "Unused" not in compressed["$defs"]
