"""Tests for openbb_imf.utils.dot_helpers."""

# ruff: noqa: I001

from unittest.mock import MagicMock, patch

import pytest


COUNTRY_FIXTURE = [
    {"value": "USA", "label": "United States"},
    {"value": "GBR", "label": "United Kingdom"},
    {"value": "DEU", "label": "Germany"},
    {"value": "G001", "label": "World"},
    {"value": "G163", "label": "Euro Area"},
    {"value": "GX170", "label": "Europe"},
    {"value": "G7", "label": "Group of Seven"},
    {"value": "TX1", "label": "Total Exports"},
    {"value": "TX2", "label": "Other TX"},
]


@pytest.fixture
def _patch_metadata(monkeypatch):
    """Patch ``ImfMetadata().get_dataflow_parameters`` for IMTS country data."""

    class FakeMeta:
        def get_dataflow_parameters(self, _dataflow):
            return {"COUNTRY": list(COUNTRY_FIXTURE)}

    monkeypatch.setattr("openbb_imf.utils.metadata.ImfMetadata", FakeMeta)


class TestLoadCountryChoices:
    """Tests for load_country_choices."""

    def test_groups_split_and_sorted(self, _patch_metadata):
        """Plain countries, G-regions, and TX groups appear in that order."""
        from openbb_imf.utils.dot_helpers import load_country_choices

        result = load_country_choices()
        values = [item["value"] for item in result]

        # plain country block first
        plain_values = {"USA", "GBR", "DEU"}
        plain_block_idx = [i for i, v in enumerate(values) if v in plain_values]
        # G regions next
        g_block_idx = [
            i for i, v in enumerate(values) if v in {"G001", "G163", "GX170", "G7"}
        ]
        # TX groups last
        tx_block_idx = [i for i, v in enumerate(values) if v in {"TX1", "TX2"}]

        assert max(plain_block_idx) < min(g_block_idx)
        assert max(g_block_idx) < min(tx_block_idx)


class TestListCountryChoices:
    """Tests for list_country_choices."""

    def test_returns_codes(self, _patch_metadata):
        """Returns just the value codes."""
        from openbb_imf.utils.dot_helpers import list_country_choices

        result = list_country_choices()
        assert "USA" in result
        assert "G001" in result
        assert all(isinstance(c, str) for c in result)


class TestLabelToCodeMap:
    """Tests for get_label_to_code_map."""

    def test_normalized_labels(self, _patch_metadata):
        """Normalized label maps to its code."""
        from openbb_imf.utils.dot_helpers import get_label_to_code_map

        result = get_label_to_code_map()
        assert result["united_states"] == "USA"
        assert result["united_kingdom"] == "GBR"
        assert result["world"] == "G001"


class TestCodeToLabelMap:
    """Tests for get_code_to_label_map."""

    def test_codes_map_to_labels(self, _patch_metadata):
        """Codes map to normalized labels."""
        from openbb_imf.utils.dot_helpers import get_code_to_label_map

        result = get_code_to_label_map()
        assert result["USA"] == "united_states"
        assert result["G001"] == "world"


class TestResolveCountryInput:
    """Tests for resolve_country_input."""

    def test_empty_raises(self):
        """Empty input raises ValueError."""
        from openbb_imf.utils.dot_helpers import resolve_country_input

        with pytest.raises(ValueError, match="cannot be empty"):
            resolve_country_input("")

    def test_all_alias(self):
        """'all' / '*' return '*'."""
        from openbb_imf.utils.dot_helpers import resolve_country_input

        assert resolve_country_input("all") == "*"
        assert resolve_country_input("*") == "*"

    def test_common_aliases(self):
        """Common aliases resolve to fixed codes."""
        from openbb_imf.utils.dot_helpers import resolve_country_input

        assert resolve_country_input("world") == "G001"
        assert resolve_country_input("eurozone") == "G163"
        assert resolve_country_input("euro_area") == "G163"
        assert resolve_country_input("Euro Area") == "G163"
        assert resolve_country_input("EU") == "G998"
        assert resolve_country_input("european_union") == "G998"
        assert resolve_country_input("europe") == "GX170"

    def test_iso_code(self, _patch_metadata):
        """Valid ISO-like code passes through."""
        from openbb_imf.utils.dot_helpers import resolve_country_input

        assert resolve_country_input("USA") == "USA"
        assert resolve_country_input("usa") == "USA"

    def test_resolve_by_label(self, _patch_metadata):
        """Country label resolves to code."""
        from openbb_imf.utils.dot_helpers import resolve_country_input

        assert resolve_country_input("united_states") == "USA"
        assert resolve_country_input("United States") == "USA"

    def test_unknown_raises(self, _patch_metadata):
        """Unknown country raises ValueError with hint."""
        from openbb_imf.utils.dot_helpers import resolve_country_input

        with pytest.raises(ValueError, match="not a valid IMF country code"):
            resolve_country_input("Atlantis")


class TestImtsQuery:
    """Tests for imts_query."""

    def _make_qb(self, **overrides):
        """Build a mocked ImfQueryBuilder context manager."""
        qb = MagicMock()
        qb.metadata.get_dataflow_parameters.return_value = {
            "COUNTRY": [
                {"value": "USA"},
                {"value": "G001"},
                {"value": "GBR"},
            ],
            "COUNTERPART_COUNTRY": [
                {"value": "G001"},
                {"value": "USA"},
            ],
        }
        qb.fetch_data.return_value = {"data": [], "metadata": {}}
        for k, v in overrides.items():
            setattr(qb, k, v)
        return qb

    def test_empty_country_raises(self):
        """Empty country/counterpart raises ValueError."""
        from openbb_imf.utils.dot_helpers import imts_query

        with pytest.raises(ValueError, match="cannot be empty"):
            imts_query(country="", counterpart="G001", indicator="*")

    def test_invalid_frequency_raises(self):
        """Frequency not in A/Q/M raises."""
        from openbb_imf.utils.dot_helpers import imts_query

        with pytest.raises(ValueError, match="Frequency must be one of"):
            imts_query(country="USA", counterpart="G001", indicator="*", freq="X")

    def test_simple_query_dispatches(self):
        """Valid inputs dispatch to query_builder.fetch_data."""
        from openbb_imf.utils import dot_helpers

        qb = self._make_qb()
        with patch("openbb_imf.utils.query_builder.ImfQueryBuilder", return_value=qb):
            out = dot_helpers.imts_query(
                country="USA",
                counterpart="G001",
                indicator="X",
                freq="annual",
            )
        assert out == {"data": [], "metadata": {}}
        kwargs = qb.fetch_data.call_args.kwargs
        assert kwargs["dataflow"] == "IMTS"
        assert kwargs["FREQUENCY"] == "A"
        assert kwargs["COUNTRY"] == "USA"
        assert kwargs["COUNTERPART_COUNTRY"] == "G001"
        assert kwargs["INDICATOR"] == "X"

    def test_comma_separated_country(self):
        """Comma-separated country string becomes a list."""
        from openbb_imf.utils import dot_helpers

        qb = self._make_qb()
        with patch("openbb_imf.utils.query_builder.ImfQueryBuilder", return_value=qb):
            dot_helpers.imts_query(
                country="USA,GBR",
                counterpart="G001",
                indicator="*",
                freq="A",
            )
        kwargs = qb.fetch_data.call_args.kwargs
        assert kwargs["COUNTRY"] == ["USA", "GBR"]

    def test_wildcard_counterpart(self):
        """'*' counterpart passes through."""
        from openbb_imf.utils import dot_helpers

        qb = self._make_qb()
        with patch("openbb_imf.utils.query_builder.ImfQueryBuilder", return_value=qb):
            dot_helpers.imts_query(
                country="USA",
                counterpart="*",
                indicator="*",
                freq="A",
            )
        kwargs = qb.fetch_data.call_args.kwargs
        assert kwargs["COUNTERPART_COUNTRY"] == "*"

    def test_invalid_country_raises(self):
        """Invalid country code raises ValueError listing offending codes."""
        from openbb_imf.utils import dot_helpers

        qb = self._make_qb()
        with patch("openbb_imf.utils.query_builder.ImfQueryBuilder", return_value=qb):
            with pytest.raises(ValueError, match="Invalid country"):
                dot_helpers.imts_query(
                    country="ZZZ",
                    counterpart="G001",
                    indicator="*",
                )

    def test_invalid_counterpart_raises(self):
        """Invalid counterpart code raises ValueError."""
        from openbb_imf.utils import dot_helpers

        qb = self._make_qb()
        with patch("openbb_imf.utils.query_builder.ImfQueryBuilder", return_value=qb):
            with pytest.raises(ValueError, match="Invalid counterpart"):
                dot_helpers.imts_query(
                    country="USA",
                    counterpart="ZZZ",
                    indicator="*",
                )

    def test_wildcard_in_country_list(self):
        """A '*' inside a list collapses to wildcard."""
        from openbb_imf.utils import dot_helpers

        qb = self._make_qb()
        with patch("openbb_imf.utils.query_builder.ImfQueryBuilder", return_value=qb):
            dot_helpers.imts_query(
                country=["USA", "*"],
                counterpart=["G001"],
                indicator="*",
            )
        kwargs = qb.fetch_data.call_args.kwargs
        assert kwargs["COUNTRY"] == "*"

    def test_no_valid_values_passthrough(self):
        """When params lack the dimension, selection passes through unchanged."""
        from openbb_imf.utils import dot_helpers

        qb = self._make_qb()
        qb.metadata.get_dataflow_parameters.return_value = {}
        with patch("openbb_imf.utils.query_builder.ImfQueryBuilder", return_value=qb):
            dot_helpers.imts_query(country="ZZZ", counterpart="QQQ", indicator="*")
        kwargs = qb.fetch_data.call_args.kwargs
        assert kwargs["COUNTRY"] == "ZZZ"
        assert kwargs["COUNTERPART_COUNTRY"] == "QQQ"

    def test_indicator_comma_list(self):
        """Comma-separated indicator splits to list."""
        from openbb_imf.utils import dot_helpers

        qb = self._make_qb()
        with patch("openbb_imf.utils.query_builder.ImfQueryBuilder", return_value=qb):
            dot_helpers.imts_query(
                country="USA",
                counterpart="G001",
                indicator="X, M",
            )
        kwargs = qb.fetch_data.call_args.kwargs
        assert kwargs["INDICATOR"] == ["X", "M"]

    def test_single_country_list(self):
        """Single-item list with one country returns just the string."""
        from openbb_imf.utils import dot_helpers

        qb = self._make_qb()
        with patch("openbb_imf.utils.query_builder.ImfQueryBuilder", return_value=qb):
            dot_helpers.imts_query(
                country=["USA"],
                counterpart=["G001"],
                indicator="*",
            )
        kwargs = qb.fetch_data.call_args.kwargs
        assert kwargs["COUNTRY"] == "USA"
        assert kwargs["COUNTERPART_COUNTRY"] == "G001"

    def test_counterpart_country_fallback(self):
        """Missing COUNTERPART_COUNTRY falls back to COUNTRY param values."""
        from openbb_imf.utils import dot_helpers

        qb = self._make_qb()
        qb.metadata.get_dataflow_parameters.return_value = {
            "COUNTRY": [{"value": "USA"}, {"value": "G001"}],
        }
        with patch("openbb_imf.utils.query_builder.ImfQueryBuilder", return_value=qb):
            dot_helpers.imts_query(country="USA", counterpart="G001", indicator="*")
        kwargs = qb.fetch_data.call_args.kwargs
        assert kwargs["COUNTERPART_COUNTRY"] == "G001"
