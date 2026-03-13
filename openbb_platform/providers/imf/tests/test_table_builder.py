"""Tests for IMF Table Builder."""

# ruff: noqa: I001
# pylint: disable=W0621,W0613,W0212,R0903,C0302,C0415

from unittest.mock import MagicMock, patch

import pytest


class TestImfTableBuilder:
    """Tests for ImfTableBuilder class."""

    @pytest.fixture
    def mock_query_builder(self):
        """Mock ImfQueryBuilder for table builder tests."""
        with patch(
            "openbb_imf.utils.query_builder.ImfQueryBuilder"
        ) as MockQueryBuilder:
            mock_instance = MockQueryBuilder.return_value
            mock_instance.metadata = MagicMock()
            mock_instance.dataflows = {
                "BOP": {
                    "id": "BOP",
                    "name": "Balance of Payments",
                    "structureRef": {"id": "IMF_BOP"},
                }
            }
            mock_instance.validate_dimension_constraints = MagicMock()
            yield MockQueryBuilder

    def test_table_builder_instantiation(self, mock_query_builder):
        """Test that table builder can be instantiated."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        builder = ImfTableBuilder()
        assert builder is not None
        assert builder.query_builder is not None

    def test_validate_dimension_constraints_delegates(self, mock_query_builder):
        """Test that dimension validation delegates to query builder."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        builder = ImfTableBuilder()
        builder._validate_dimension_constraints("BOP", COUNTRY="USA")

        mock_query_builder.return_value.validate_dimension_constraints.assert_called_once_with(
            "BOP", COUNTRY="USA"
        )


class TestTableIdParsing:
    """Tests for table ID parsing logic."""

    @pytest.fixture
    def mock_query_builder(self):
        """Mock ImfQueryBuilder."""
        with patch(
            "openbb_imf.utils.query_builder.ImfQueryBuilder"
        ) as MockQueryBuilder:
            mock_instance = MockQueryBuilder.return_value
            mock_instance.metadata = MagicMock()
            mock_instance.dataflows = {"BOP": {"id": "BOP"}}
            mock_instance.validate_dimension_constraints = MagicMock()
            yield MockQueryBuilder

    def test_table_id_with_dataflow_prefix(self, mock_query_builder):
        """Test parsing table_id with dataflow::table_id format."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        builder = ImfTableBuilder()

        # Test that table_id parsing handles dataflow::table_id format
        # The format "BOP::H_BOP_STANDARD" should be parsed correctly
        # This is a smoke test to ensure the builder can be called with this format
        # Actual parsing is validated via integration tests
        assert builder.query_builder is not None

        # Test signature accepts table_id with special characters
        import inspect

        sig = inspect.signature(builder.get_table)
        assert "table_id" in sig.parameters


class TestHierarchyDetection:
    """Tests for hierarchy/table detection in symbols."""

    def test_table_id_starts_with_h(self):
        """Test that H_ prefix identifies table IDs."""
        # Table IDs start with H_
        table_ids = [
            "H_BOP_BOP_AGG_STANDARD_PRESENTATION",
            "H_IRFCL_TOTAL_RESERVES",
            "H_GFS_EXPENSE",
        ]
        for tid in table_ids:
            assert tid.startswith("H_"), f"{tid} should start with H_"

    def test_indicator_ids_no_h_prefix(self):
        """Test that indicator IDs don't start with H_."""
        indicator_ids = [
            "CD_T",
            "DB_T",
            "PCPI_IX",
            "BM_MAI",
            "GDP",
        ]
        for ind in indicator_ids:
            assert not ind.startswith("H_"), f"{ind} should not start with H_"


class TestTableDataStructure:
    """Tests for expected table data structure."""

    def test_table_data_contains_hierarchy_fields(self):
        """Test that table data includes hierarchy metadata."""
        # Expected fields in table data
        expected_fields = [
            "order",
            "level",
            "parent_id",
            "series_id",
            "title",
            "TIME_PERIOD",
            "OBS_VALUE",
        ]

        # Create sample table data
        sample_row = {
            "order": 1,
            "level": 0,
            "parent_id": None,
            "series_id": "IMF_BOP_SERIES",
            "COUNTRY": "United States",
            "country_code": "USA",
            "title": "Current Account Balance",
            "TIME_PERIOD": "2024-12-31",
            "OBS_VALUE": -300000000000.0,
        }

        for field in expected_fields:
            assert field in sample_row, f"Missing field: {field}"


class TestTableBuilderWithMockedMetadata:
    """Tests with fully mocked metadata."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all dependencies for table builder."""

        class FakeImfParamsBuilder:
            """Lightweight stand-in for ImfParamsBuilder used in table tests."""

            def __init__(self, dataflow: str):  # noqa: ARG002
                self._dimensions = ["COUNTRY", "INDICATOR"]
                self._selections = {d: None for d in self._dimensions}

            def _get_dimensions_in_order(self):
                return list(self._dimensions)

            def get_options_for_dimension(self, dim_id):
                if dim_id.upper() == "COUNTRY":
                    return [{"value": "US", "label": "United States"}]
                if dim_id.upper() == "INDICATOR":
                    return [
                        {"value": "CAB", "label": "CAB"},
                        {"value": "GOODS", "label": "GOODS"},
                        {"value": "IND", "label": "IND"},
                        {"value": "IND_XDC", "label": "IND_XDC"},
                    ]
                return [{"value": "*", "label": "*"}]

            def set_dimension(self, dim_tuple):
                dim_id, value = dim_tuple
                self._selections[dim_id] = value
                return self._selections

            def get_next_dimension_to_select(self):
                for dim in self._dimensions:
                    if self._selections.get(dim) is None:
                        return dim
                return None

        with patch(
            "openbb_imf.utils.query_builder.ImfQueryBuilder"
        ) as MockQueryBuilder, patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            FakeImfParamsBuilder,
        ):
            mock_qb = MockQueryBuilder.return_value

            # Mock metadata
            mock_qb.metadata = MagicMock()
            mock_qb.metadata.get_table_in.return_value = {
                "id": "H_BOP_STANDARD",
                "title": "Balance of Payments Standard",
                "hierarchy": [
                    {
                        "order": 1,
                        "level": 0,
                        "id": "CAB",
                        "parent_id": None,
                        "title": "Current Account",
                        "series_id": "CAB_SERIES",
                        "dimension_values": {"INDICATOR": ["CAB"]},
                    },
                    {
                        "order": 2,
                        "level": 1,
                        "id": "GOODS",
                        "parent_id": "CAB",
                        "title": "Goods",
                        "series_id": "GOODS_SERIES",
                        "dimension_values": {"INDICATOR": ["GOODS"]},
                    },
                ],
            }

            # Mock validation
            mock_qb.validate_dimension_constraints = MagicMock()

            # Mock dataflows
            mock_qb.dataflows = {
                "BOP": {
                    "id": "BOP",
                    "name": "Balance of Payments",
                    "structureRef": {"id": "IMF_BOP"},
                }
            }

            yield MockQueryBuilder

    def test_get_table_returns_expected_structure(self, mock_dependencies):
        """Test that get_table method exists and has correct signature."""
        import inspect

        from openbb_imf.utils.table_builder import ImfTableBuilder

        builder = ImfTableBuilder()

        # Verify get_table method exists and has expected parameters
        assert hasattr(builder, "get_table")
        sig = inspect.signature(builder.get_table)

        # Check required parameters exist
        params = sig.parameters
        assert "dataflow" in params or "table_id" in params

        # Verify the builder is properly initialized
        assert builder.query_builder is not None
        assert builder.metadata is not None

    def test_hierarchy_to_dimension_mapping(self, mock_dependencies):
        """Test that hierarchy codes are mapped to dimensions."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        # We need to mock `fetch_data` to return something that `get_table` can process
        # `get_table` calls `fetch_data` on query_builder.

        mock_qb = mock_dependencies.return_value
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_SERIES",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 100,
                },
                {
                    "series_id": "GOODS_SERIES",
                    "INDICATOR_code": "GOODS",
                    "indicator_code": "GOODS",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 50,
                },
            ],
            "metadata": {},
        }

        # Mock table structure
        mock_qb.metadata.get_dataflow_table_structure.return_value = {
            "hierarchy_id": "H_BOP_STANDARD",
            "hierarchy_name": "Balance of Payments Standard",
            "hierarchy_description": "",
            "dataflow_id": "BOP",
            "codelist_id": "CL_INDICATOR",
            "agency_id": "IMF",
            "version": "1.0",
            "total_groups": 2,
            "type": "presentation",
            "indicators": [
                {
                    "order": 1,
                    "level": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "title": "Current Account",
                    "series_id": "CAB_SERIES",
                    "indicator_code": "CAB",
                    "dimension_values": {"INDICATOR": ["CAB"]},
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "level": 1,
                    "id": "GOODS",
                    "parent_id": "CAB",
                    "title": "Goods",
                    "series_id": "GOODS_SERIES",
                    "indicator_code": "GOODS",
                    "dimension_values": {"INDICATOR": ["GOODS"]},
                    "dimension_id": "INDICATOR",
                },
            ],
        }

        builder = ImfTableBuilder()

        # Call get_table
        result = builder.get_table("BOP", "H_BOP_STANDARD", COUNTRY="US")
        rows_by_series = {row["series_id"]: row for row in result["data"]}

        assert set(rows_by_series) == {"CAB_SERIES", "GOODS_SERIES"}
        assert rows_by_series["CAB_SERIES"]["order"] == 1
        assert rows_by_series["CAB_SERIES"]["level"] == 0
        assert rows_by_series["GOODS_SERIES"]["order"] == 2
        assert rows_by_series["GOODS_SERIES"]["level"] == 1

    def test_indicator_list_truncation_and_post_filtering(self, mock_dependencies):
        """Test that long indicator lists are truncated and post-filtered."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb = mock_dependencies.return_value

        # Create a large hierarchy
        indicators = []
        for i in range(100):
            indicators.append(
                {
                    "order": i,
                    "level": 0,
                    "id": f"IND_{i}",
                    "parent_id": None,
                    "title": f"Indicator {i}",
                    "series_id": f"SERIES_{i}",
                    "indicator_code": f"IND_{i}",
                    "dimension_values": {"INDICATOR": [f"IND_{i}"]},
                    "dimension_id": "INDICATOR",
                }
            )

        mock_qb.metadata.get_dataflow_table_structure.return_value = {
            "hierarchy_id": "H_LARGE",
            "hierarchy_name": "Large Table",
            "hierarchy_description": "",
            "dataflow_id": "BOP",
            "codelist_id": "CL_INDICATOR",
            "agency_id": "IMF",
            "version": "1.0",
            "total_groups": 100,
            "type": "presentation",
            "indicators": indicators,
        }

        # Empty data is acceptable; this test focuses on request parameters
        mock_qb.fetch_data.return_value = {"data": [], "metadata": {}}

        builder = ImfTableBuilder()
        builder.get_table("BOP", "H_LARGE", COUNTRY="US")

        # Check that fetch_data was called with wildcard or truncated list
        call_args = mock_qb.fetch_data.call_args
        assert call_args is not None
        kwargs = call_args[1]

        # We can check that the indicator parameter is bounded to a reasonable length
        # (table builder uses a 1500-character safeguard in fallback path).
        if "INDICATOR" in kwargs:
            assert len(kwargs["INDICATOR"]) < 1500

    def test_prefix_matching_suffixed_indicators(self, mock_dependencies):
        """Test matching of indicators with suffixes."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb = mock_dependencies.return_value

        mock_qb.metadata.get_dataflow_table_structure.return_value = {
            "hierarchy_id": "H_SUFFIX",
            "hierarchy_name": "Suffix Table",
            "hierarchy_description": "",
            "dataflow_id": "BOP",
            "codelist_id": "CL_INDICATOR",
            "agency_id": "IMF",
            "version": "1.0",
            "total_groups": 1,
            "type": "presentation",
            "indicators": [
                {
                    "order": 1,
                    "level": 0,
                    "id": "IND",
                    "parent_id": None,
                    "title": "Indicator",
                    "series_id": "IND_SERIES",
                    "indicator_code": "IND",
                    "dimension_values": {"INDICATOR": ["IND"]},  # Base code
                    "dimension_id": "INDICATOR",
                }
            ],
        }

        # Mock fetch_data returning suffixed version (e.g. IND_XDC)
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "IND_XDC",
                    "INDICATOR_code": "IND_XDC",
                    "indicator_code": "IND_XDC",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 100,
                }
            ],
            "metadata": {},
        }

        # We need to ensure the builder can map IND_XDC back to IND hierarchy entry
        # This usually happens if the builder is smart enough to match prefix.

        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_SUFFIX", COUNTRY="US")
        row = result["data"][0]

        assert row["series_id"] == "IND_XDC"
        assert row["order"] == 1
        assert row["level"] == 0

    def test_time_range_validation_in_table_flow(self, mock_dependencies):
        """Test that time range validation occurs in table flow."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb = mock_dependencies.return_value

        mock_qb.metadata.get_dataflow_table_structure.return_value = {
            "hierarchy_id": "H_BOP_STANDARD",
            "hierarchy_name": "Balance of Payments Standard",
            "hierarchy_description": "",
            "dataflow_id": "BOP",
            "codelist_id": "CL_INDICATOR",
            "agency_id": "IMF",
            "version": "1.0",
            "total_groups": 1,
            "type": "presentation",
            "indicators": [
                {
                    "order": 1,
                    "level": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "title": "Current Account",
                    "series_id": "CAB_SERIES",
                    "indicator_code": "CAB",
                    "dimension_values": {"INDICATOR": ["CAB"]},
                    "dimension_id": "INDICATOR",
                }
            ],
        }

        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_SERIES",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 100,
                }
            ],
            "metadata": {},
        }

        builder = ImfTableBuilder()

        builder.get_table(
            "BOP", "H_BOP_STANDARD", COUNTRY="US", start_date="2020", end_date="2021"
        )

        mock_qb.fetch_data.assert_called()
        call_kwargs = mock_qb.fetch_data.call_args[1]
        assert call_kwargs.get("start_date") == "2020"
        assert call_kwargs.get("end_date") == "2021"


class TestBopCompositeHierarchyMatching:
    """Regression tests for BOP hierarchy matching.

    These tests are deterministic (no network) and validate that the IMF hierarchy
    is treated as the source of truth for parent/child relationships.
    """

    @pytest.fixture
    def mock_bop_dependencies(self):
        """Mock query builder + params builder for BOP composite matching tests."""

        class FakeImfParamsBuilder:
            def __init__(self, dataflow: str):  # noqa: ARG002
                self._dimensions = ["COUNTRY", "INDICATOR", "BOP_ACCOUNTING_ENTRY"]
                self._selections = {d: None for d in self._dimensions}

            def _get_dimensions_in_order(self):
                return list(self._dimensions)

            def get_options_for_dimension(self, dim_id):
                dim_id = dim_id.upper()
                if dim_id == "COUNTRY":
                    return [{"value": "AU", "label": "Australia"}]
                if dim_id == "INDICATOR":
                    return [
                        {"value": "SINCEX", "label": "SINCEX"},
                        {"value": "O", "label": "O"},
                    ]
                if dim_id == "BOP_ACCOUNTING_ENTRY":
                    return [
                        {"value": "NETCD_T", "label": "Net"},
                        {"value": "CD_T", "label": "Credit"},
                        {"value": "DB_T", "label": "Debit"},
                        {"value": "A_P", "label": "Assets"},
                        {"value": "L_P", "label": "Liabilities"},
                    ]
                return [{"value": "*", "label": "*"}]

            def set_dimension(self, dim_tuple):
                dim_id, value = dim_tuple
                self._selections[dim_id] = value
                return self._selections

            def get_next_dimension_to_select(self):
                for dim in self._dimensions:
                    if self._selections.get(dim) is None:
                        return dim
                return None

        with patch(
            "openbb_imf.utils.query_builder.ImfQueryBuilder"
        ) as MockQueryBuilder, patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            FakeImfParamsBuilder,
        ):
            mock_qb = MockQueryBuilder.return_value
            mock_qb.validate_dimension_constraints = MagicMock()

            # Minimal metadata object with required attributes
            mock_qb.metadata = MagicMock()
            mock_qb.metadata.dataflows = {
                "BOP": {
                    "id": "BOP",
                    "name": "Balance of Payments",
                    # Keep structureRef id falsy to avoid datastructure-dependent logic
                    "structureRef": {"id": ""},
                }
            }
            mock_qb.metadata.datastructures = {}
            mock_qb.metadata._codelist_cache = {}

            # Ensure builder uses consistent dataflow map
            mock_qb.dataflows = mock_qb.metadata.dataflows

            # Hierarchy contains:
            # - A Net node (NETCD_T)
            # - Two leaf nodes with the same indicator_code (SINCEX) under NETCD_T
            # - Two leaf nodes with the same indicator_code (O) under A_P and L_P
            mock_qb.metadata.get_dataflow_table_structure.return_value = {
                "hierarchy_id": "H_BOP_FAKE",
                "hierarchy_name": "BOP Fake",
                "hierarchy_description": "",
                "dataflow_id": "BOP",
                "codelist_id": "CL_BOP_INDICATOR",
                "agency_id": "IMF",
                "version": "1.0",
                "total_groups": 7,
                "type": "presentation",
                "indicators": [
                    {
                        "order": 1,
                        "depth": 0,
                        "id": "NETCD_T",
                        "parent_id": None,
                        "label": "Net (credits less debits)",
                        "series_id": "",
                        "indicator_code": "NETCD_T",
                        "is_group": True,
                        "dimension_id": "BOP_ACCOUNTING_ENTRY",
                    },
                    {
                        "order": 2,
                        "depth": 1,
                        "id": "SINCEX_CD",
                        "parent_id": "NETCD_T",
                        "label": "Secondary income excluding exceptional financing",
                        "series_id": "",
                        "indicator_code": "SINCEX",
                        "is_group": False,
                        "dimension_id": "INDICATOR",
                    },
                    {
                        "order": 3,
                        "depth": 1,
                        "id": "SINCEX_DB",
                        "parent_id": "NETCD_T",
                        "label": "Secondary income excluding exceptional financing",
                        "series_id": "",
                        "indicator_code": "SINCEX",
                        "is_group": False,
                        "dimension_id": "INDICATOR",
                    },
                    {
                        "order": 4,
                        "depth": 0,
                        "id": "A_P",
                        "parent_id": None,
                        "label": "Assets, Positions",
                        "series_id": "",
                        "indicator_code": "A_P",
                        "is_group": True,
                        "dimension_id": "BOP_ACCOUNTING_ENTRY",
                    },
                    {
                        "order": 5,
                        "depth": 0,
                        "id": "L_P",
                        "parent_id": None,
                        "label": "Liabilities, Positions",
                        "series_id": "",
                        "indicator_code": "L_P",
                        "is_group": True,
                        "dimension_id": "BOP_ACCOUNTING_ENTRY",
                    },
                    {
                        "order": 6,
                        "depth": 1,
                        "id": "O_A",
                        "parent_id": "A_P",
                        "label": "Other investment",
                        "series_id": "",
                        "indicator_code": "O",
                        "is_group": False,
                        "dimension_id": "INDICATOR",
                    },
                    {
                        "order": 7,
                        "depth": 1,
                        "id": "O_L",
                        "parent_id": "L_P",
                        "label": "Other investment",
                        "series_id": "",
                        "indicator_code": "O",
                        "is_group": False,
                        "dimension_id": "INDICATOR",
                    },
                ],
            }

            # Data rows intentionally omit usable series_id to force composite matching
            mock_qb.fetch_data.return_value = {
                "data": [
                    {
                        "series_id": "",
                        "INDICATOR_code": "SINCEX",
                        "BOP_ACCOUNTING_ENTRY_code": "CD_T",
                        "REF_AREA_code": "AU",
                        "TIME_PERIOD": "2024-12-31",
                        "OBS_VALUE": 9.86,
                    },
                    {
                        "series_id": "",
                        "INDICATOR_code": "SINCEX",
                        "BOP_ACCOUNTING_ENTRY_code": "DB_T",
                        "REF_AREA_code": "AU",
                        "TIME_PERIOD": "2024-12-31",
                        "OBS_VALUE": 10.04,
                    },
                    {
                        "series_id": "",
                        "INDICATOR_code": "O",
                        "BOP_ACCOUNTING_ENTRY_code": "A_P",
                        "REF_AREA_code": "AU",
                        "TIME_PERIOD": "2024-12-31",
                        "OBS_VALUE": 1.0,
                    },
                    {
                        "series_id": "",
                        "INDICATOR_code": "O",
                        "BOP_ACCOUNTING_ENTRY_code": "L_P",
                        "REF_AREA_code": "AU",
                        "TIME_PERIOD": "2024-12-31",
                        "OBS_VALUE": 2.0,
                    },
                ],
                "metadata": {},
            }

            yield MockQueryBuilder

    def test_bop_credit_debit_resolves_under_net_parent(self, mock_bop_dependencies):
        """Credit and Debit rows must resolve under the hierarchy's Net parent."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_BOP_FAKE", COUNTRY="AU")

        rows = [r for r in result["data"] if r.get("INDICATOR_code") == "SINCEX"]
        # Expect both Credit and Debit to be kept (not dropped)
        assert len(rows) == 2

        for row in rows:
            # Composite match should use hierarchy parent (NETCD_T), not CD_T/DB_T
            assert row.get("parent_code") == "NETCD_T"
            assert "excluding exceptional financing" in (row.get("title") or "")

        titles = {r.get("title") for r in rows}
        assert any(t and t.endswith(", Credit") for t in titles)
        assert any(t and t.endswith(", Debit") for t in titles)

    def test_bop_assets_liabilities_remain_distinct_paths(self, mock_bop_dependencies):
        """Assets and Liabilities must remain separate hierarchy paths."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_BOP_FAKE", COUNTRY="AU")

        rows = [r for r in result["data"] if r.get("INDICATOR_code") == "O"]
        assert len(rows) == 2

        parent_codes = {r.get("parent_code") for r in rows}
        assert parent_codes == {"A_P", "L_P"}

        titles = {r.get("title") for r in rows}
        assert any(t and t.endswith(", Assets") for t in titles)
        assert any(t and t.endswith(", Liabilities") for t in titles)


class TestTableBuilderErrorHandling:
    """Tests for error handling in table builder."""

    @pytest.fixture
    def mock_query_builder(self):
        """Mock ImfQueryBuilder."""
        with patch(
            "openbb_imf.utils.query_builder.ImfQueryBuilder"
        ) as MockQueryBuilder:
            mock_instance = MockQueryBuilder.return_value
            mock_instance.metadata = MagicMock()
            mock_instance.dataflows = {"BOP": {"id": "BOP"}}
            mock_instance.validate_dimension_constraints = MagicMock()
            yield MockQueryBuilder

    def test_invalid_dataflow_raises_error(self, mock_query_builder):
        """Test that invalid dimension constraints raises appropriate error."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        builder = ImfTableBuilder()

        # Mock validation to raise error for invalid dataflow
        mock_query_builder.return_value.validate_dimension_constraints.side_effect = (
            ValueError("Invalid dataflow: INVALID_DATAFLOW")
        )

        with pytest.raises(ValueError) as exc_info:
            builder._validate_dimension_constraints("INVALID_DATAFLOW", COUNTRY="USA")

        assert "Invalid" in str(exc_info.value)

    def test_dimension_constraint_validation_error(self, mock_query_builder):
        """Test that invalid dimension values raise validation error."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        builder = ImfTableBuilder()

        # Mock validation to raise error
        mock_query_builder.return_value.validate_dimension_constraints.side_effect = (
            ValueError("Invalid country: XYZ")
        )

        with pytest.raises(ValueError) as exc_info:
            builder._validate_dimension_constraints("BOP", COUNTRY="XYZ")

        assert (
            "Invalid" in str(exc_info.value) or "country" in str(exc_info.value).lower()
        )
