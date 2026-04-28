"""Behavioral tests for ``openbb_core.api.router.coverage``.

The original tests mocked ``CommandMap``/``ProviderInterface``, populated
``return_value.<attr>`` with toy dicts, then asserted ``response`` was
truthy — a tautology. These rewrites build a real ``CommandMap`` whose
internal coverage state is seeded with known values, run the actual
handler, and assert the handler forwards (not transforms) those values.
"""

import asyncio
from unittest.mock import MagicMock

from openbb_core.api.router.coverage import (
    get_command_coverage,
    get_commands_model_map,
    get_provider_coverage,
)
from openbb_core.app.router import CommandMap


def _seeded_command_map(provider_cov, command_cov, commands_model) -> CommandMap:
    """Return a ``CommandMap`` whose internal coverage fields are pre-populated."""
    cmap = CommandMap()
    cmap._provider_coverage = provider_cov
    cmap._command_coverage = command_cov
    cmap._commands_model = commands_model
    return cmap


def test_get_provider_coverage_returns_command_map_provider_coverage():
    """Handler returns ``CommandMap.provider_coverage`` verbatim."""
    seed = {"polygon": ["/equity/price/historical"], "fmp": ["/equity/price/quote"]}
    cmap = _seeded_command_map(seed, {}, {})

    result = asyncio.run(get_provider_coverage(cmap))

    assert result == seed
    # And it must be the exact dict instance (no copy/transform).
    assert result is cmap.provider_coverage


def test_get_command_coverage_returns_command_map_command_coverage():
    """Handler returns ``CommandMap.command_coverage`` verbatim."""
    seed = {
        "/equity/price/historical": ["polygon", "fmp"],
        "/equity/price/quote": ["fmp"],
    }
    cmap = _seeded_command_map({}, seed, {})

    result = asyncio.run(get_command_coverage(cmap))

    assert result == seed
    assert result is cmap.command_coverage


def test_get_commands_model_map_serializes_provider_command_metadata():
    """``/coverage/command_model`` walks ``commands_model`` and emits a JSON-serializable map.

    The handler is non-trivial: it iterates ``CommandMap.commands_model``,
    looks up each model's provider info via ``ProviderInterface.map``, copies
    over ``QueryParams``/``Data`` field metadata, and merges any ``openbb``
    pseudo-provider fields into every real provider's field set.
    """
    cmap = _seeded_command_map({}, {}, {"/equity/price/historical": "EquityPriceHist"})

    # Build a minimal but realistic ProviderInterface stand-in. We only
    # need the attributes the handler reads: ``map`` and
    # ``return_annotations``.
    field_attrs = {"annotation": str, "description": "Stock symbol"}
    fake_field = MagicMock(_attributes_set=field_attrs)
    pi = MagicMock()
    pi.map = {
        "EquityPriceHist": {
            "polygon": {
                "QueryParams": {
                    "docstring": "polygon query",
                    "fields": {"symbol": fake_field},
                },
                "Data": {"docstring": "polygon data", "fields": {}},
            },
            "openbb": {
                "QueryParams": {
                    "docstring": "shared",
                    "fields": {"shared_field": fake_field},
                },
                "Data": {"docstring": "shared data", "fields": {}},
            },
        }
    }

    class _Schema:
        pass

    _Schema.__name__ = "OBBject_EquityPriceHist"

    pi.return_annotations = {"EquityPriceHist": _Schema}

    result = asyncio.run(get_commands_model_map(cmap, pi))

    # Top-level: one entry per command in commands_model
    assert "/equity/price/historical" in result
    entry = result["/equity/price/historical"]

    # Schema name forwarded
    assert entry["response_schema_name"] == "OBBject_EquityPriceHist"

    # ``openbb`` is folded into providers and removed from the output
    assert "openbb" not in entry
    assert "polygon" in entry

    # Provider's QueryParams now includes both its own ``symbol`` and the
    # merged-in ``shared_field`` from ``openbb``.
    poly_q_fields = entry["polygon"]["QueryParams"]["fields"]
    assert "symbol" in poly_q_fields
    assert "shared_field" in poly_q_fields

    # ``annotation`` was stringified by the handler so the result is JSON safe.
    assert poly_q_fields["symbol"]["annotation"] == str(str)


def test_get_commands_model_map_handles_missing_response_schema():
    """When a model has no ``return_annotations`` entry, schema name is ``None``."""
    cmap = _seeded_command_map({}, {}, {"/eco/cpi": "CPI"})
    pi = MagicMock()
    pi.map = {
        "CPI": {
            "fred": {
                "QueryParams": {"docstring": "", "fields": {}},
                "Data": {"docstring": "", "fields": {}},
            },
            "openbb": {
                "QueryParams": {"docstring": "", "fields": {}},
                "Data": {"docstring": "", "fields": {}},
            },
        }
    }
    pi.return_annotations = {"CPI": None}

    result = asyncio.run(get_commands_model_map(cmap, pi))

    assert result["/eco/cpi"]["response_schema_name"] is None
