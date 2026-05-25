"""Tests for IMF Table Builder."""

# ruff: noqa: I001

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

        assert builder.query_builder is not None

        import inspect

        sig = inspect.signature(builder.get_table)
        assert "table_id" in sig.parameters


class TestHierarchyDetection:
    """Tests for hierarchy/table detection in symbols."""

    def test_table_id_starts_with_h(self):
        """Test that H_ prefix identifies table IDs."""
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
        expected_fields = [
            "order",
            "level",
            "parent_id",
            "series_id",
            "title",
            "TIME_PERIOD",
            "OBS_VALUE",
        ]

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

        with (
            patch("openbb_imf.utils.query_builder.ImfQueryBuilder") as MockQueryBuilder,
            patch(
                "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
                FakeImfParamsBuilder,
            ),
        ):
            mock_qb = MockQueryBuilder.return_value

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

            mock_qb.validate_dimension_constraints = MagicMock()

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

        assert hasattr(builder, "get_table")
        sig = inspect.signature(builder.get_table)

        params = sig.parameters
        assert "dataflow" in params or "table_id" in params

        assert builder.query_builder is not None
        assert builder.metadata is not None

    def test_hierarchy_to_dimension_mapping(self, mock_dependencies):
        """Test that hierarchy codes are mapped to dimensions."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

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

        result = builder.get_table("BOP", "H_BOP_STANDARD", COUNTRY="US")
        rows_by_series = {row["series_id"]: row for row in result["data"]}

        assert set(rows_by_series) == {"CAB_SERIES", "GOODS_SERIES"}
        assert rows_by_series["CAB_SERIES"]["order"] == 1
        assert rows_by_series["CAB_SERIES"]["level"] == 0
        assert rows_by_series["GOODS_SERIES"]["order"] == 2
        assert rows_by_series["GOODS_SERIES"]["level"] == 1

    def test_indicator_list_truncation_and_post_filtering(self, mock_dependencies):
        """Test that long indicator lists are truncated and post-filtered."""
        from openbb_core.app.model.abstract.warning import OpenBBWarning

        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb = mock_dependencies.return_value

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

        mock_qb.fetch_data.return_value = {"data": [], "metadata": {}}

        builder = ImfTableBuilder()
        with pytest.warns(OpenBBWarning, match="Progressive constraint filtering"):
            builder.get_table("BOP", "H_LARGE", COUNTRY="US")

        call_args = mock_qb.fetch_data.call_args
        assert call_args is not None
        kwargs = call_args[1]

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
    """Regression tests for BOP hierarchy matching."""

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

        with (
            patch("openbb_imf.utils.query_builder.ImfQueryBuilder") as MockQueryBuilder,
            patch(
                "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
                FakeImfParamsBuilder,
            ),
        ):
            mock_qb = MockQueryBuilder.return_value
            mock_qb.validate_dimension_constraints = MagicMock()

            mock_qb.metadata = MagicMock()
            mock_qb.metadata.dataflows = {
                "BOP": {
                    "id": "BOP",
                    "name": "Balance of Payments",
                    "structureRef": {"id": ""},
                }
            }
            mock_qb.metadata.datastructures = {}
            mock_qb.metadata._codelist_cache = {}

            mock_qb.dataflows = mock_qb.metadata.dataflows

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
        assert len(rows) == 2

        for row in rows:
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

        mock_query_builder.return_value.validate_dimension_constraints.side_effect = (
            ValueError("Invalid country: XYZ")
        )

        with pytest.raises(ValueError) as exc_info:
            builder._validate_dimension_constraints("BOP", COUNTRY="XYZ")

        assert (
            "Invalid" in str(exc_info.value) or "country" in str(exc_info.value).lower()
        )


class FakeImfParamsBuilder:
    """Lightweight stand-in for ``ImfParamsBuilder`` used by table-builder tests."""

    def __init__(
        self,
        dimensions: list[str],
        options: dict[str, list[dict]] | None = None,
        constraints_response: dict | None = None,
    ):
        """Build a fake params builder over a fixed set of dimensions."""
        self._dimensions = list(dimensions)
        self._options = options or {}
        self._selections: dict[str, str | None] = {d: None for d in dimensions}
        self._last_constraints_response = constraints_response or {}

    def _get_dimensions_in_order(self):
        return list(self._dimensions)

    def get_options_for_dimension(self, dim_id):
        return self._options.get(dim_id, [{"value": "*", "label": "*"}])

    def set_dimension(self, tup):
        self._selections[tup[0]] = tup[1]
        return self._selections

    def get_next_dimension_to_select(self):
        for dim in self._dimensions:
            if self._selections.get(dim) is None:
                return dim
        return None


@pytest.fixture
def mock_qb_factory():
    """Return a factory that yields a fully patched table-builder environment."""

    def factory(
        *,
        dimensions=("COUNTRY", "INDICATOR"),
        options=None,
        indicators=None,
        dataflows=None,
        codelist_cache=None,
        fetch_return=None,
        table_structure=None,
        get_dataflow_hierarchies=None,
        constraints_response=None,
    ):
        if dataflows is None:
            dataflows = {
                "BOP": {
                    "id": "BOP",
                    "name": "Balance of Payments",
                    "structureRef": {"id": "DSD"},
                }
            }
        if codelist_cache is None:
            codelist_cache = {}
        if options is None:
            options = {}

        def build_params(dataflow_id):  # noqa: ARG001
            return FakeImfParamsBuilder(
                dimensions=list(dimensions),
                options=options,
                constraints_response=constraints_response,
            )

        ctx_qb = patch("openbb_imf.utils.query_builder.ImfQueryBuilder")
        ctx_ph = patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            new=build_params,
        )
        MockQB = ctx_qb.start()
        ctx_ph.start()

        mock_qb = MockQB.return_value
        mock_qb.metadata = MagicMock()
        mock_qb.metadata.dataflows = dataflows
        mock_qb.metadata.datastructures = {
            "DSD": {
                "id": "DSD",
                "dimensions": [
                    {"id": dim, "position": idx} for idx, dim in enumerate(dimensions)
                ],
            }
        }
        mock_qb.metadata._codelist_cache = codelist_cache
        mock_qb.metadata._resolve_codelist_id = MagicMock(
            return_value="CL_BOP_INDICATOR"
        )
        mock_qb.metadata._get_dimension_for_codelist = MagicMock(return_value=None)
        mock_qb.dataflows = dataflows
        mock_qb.validate_dimension_constraints = MagicMock()

        mock_qb.metadata.get_dataflow_hierarchies = MagicMock(
            return_value=get_dataflow_hierarchies
            if get_dataflow_hierarchies is not None
            else [{"id": "H_TEST"}]
        )
        mock_qb.metadata.get_dataflow_table_structure = MagicMock(
            return_value=table_structure
            or {
                "hierarchy_id": "H_TEST",
                "hierarchy_name": "Test",
                "hierarchy_description": "",
                "dataflow_id": "BOP",
                "codelist_id": "CL_INDICATOR",
                "agency_id": "IMF",
                "version": "1.0",
                "total_groups": 0,
                "type": "presentation",
                "indicators": indicators or [],
            }
        )
        mock_qb.fetch_data = MagicMock(
            return_value=fetch_return or {"data": [], "metadata": {}}
        )

        teardown = [ctx_qb, ctx_ph]
        return mock_qb, MockQB, teardown

    cleanups: list = []
    yielded_factories: list = []

    def wrapped(**kwargs):
        mock_qb, MockQB, teardown = factory(**kwargs)
        cleanups.extend(teardown)
        yielded_factories.append((mock_qb, MockQB))
        return mock_qb, MockQB

    yield wrapped

    for ctx in cleanups:
        ctx.stop()


class TestGetTableValidation:
    """Validation/error-path tests for ``ImfTableBuilder.get_table``."""

    def test_combined_table_id_with_mismatched_dataflow_raises(self, mock_qb_factory):
        """Passing ``dataflow`` that conflicts with the table_id prefix raises."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb_factory()
        builder = ImfTableBuilder()
        with pytest.raises(ValueError, match="Dataflow mismatch"):
            builder.get_table(dataflow="OTHER", table_id="BOP::H_X")

    def test_combined_table_id_parsed(self, mock_qb_factory):
        """Combined ``dataflow::table_id`` is parsed when only ``table_id`` is given."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "Current Account",
                    "series_id": "CAB_SERIES",
                    "indicator_code": "CAB",
                    "is_group": False,
                    "dimension_id": "INDICATOR",
                }
            ],
            options={"INDICATOR": [{"value": "CAB", "label": "CAB"}]},
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_SERIES",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }

        builder = ImfTableBuilder()
        result = builder.get_table(table_id="BOP::H_TEST")
        assert result["table_metadata"]["hierarchy_id"] == "H_TEST"

    def test_missing_dataflow_raises(self, mock_qb_factory):
        """Calling without ``dataflow`` or ``table_id`` raises."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb_factory()
        builder = ImfTableBuilder()
        with pytest.raises(ValueError, match="dataflow is required"):
            builder.get_table()

    def test_no_table_id_single_available(self, mock_qb_factory):
        """A single available table is auto-selected when ``table_id`` is None."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_SERIES",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={"INDICATOR": [{"value": "CAB", "label": "CAB"}]},
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_SERIES",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP")
        assert result["table_metadata"]["hierarchy_id"] == "H_TEST"

    def test_no_available_tables_raises(self, mock_qb_factory):
        """No available tables raises a clear error."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb_factory(get_dataflow_hierarchies=[])
        builder = ImfTableBuilder()
        with pytest.raises(ValueError, match="No tables/hierarchies found"):
            builder.get_table("BOP")

    def test_no_matching_indicators_after_filter_raises(self, mock_qb_factory):
        """Filtering with ``indicators=`` that matches nothing raises."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "A",
                    "parent_id": None,
                    "label": "A",
                    "series_id": "",
                    "indicator_code": "A",
                    "dimension_id": "INDICATOR",
                }
            ],
        )
        builder = ImfTableBuilder()
        with pytest.raises(ValueError, match="No indicators match"):
            builder.get_table("BOP", "H_TEST", indicators="MISSING")


class TestDimensionMapping:
    """Tests for the dimension-mapping branches in ``get_table``."""

    def test_code_urn_codelist_label_skipped(self, mock_qb_factory):
        """Codelists ending in ``_LABELS`` are skipped without raising."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "X",
                    "parent_id": None,
                    "label": "X",
                    "series_id": "",
                    "indicator_code": "X",
                    "code_urn": "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_X_LABELS(1.0).X",
                },
            ],
        )
        builder = ImfTableBuilder()
        with pytest.raises(ValueError, match="No valid indicator codes"):
            builder.get_table("BOP", "H_TEST")

    def test_code_urn_unparsable_warns_and_skips(self, mock_qb_factory):
        """A bad ``code_urn`` emits an ``OpenBBWarning`` and skips the entry."""
        from openbb_core.app.model.abstract.warning import OpenBBWarning

        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "X",
                    "parent_id": None,
                    "label": "X",
                    "series_id": "",
                    "indicator_code": "X",
                    "code_urn": "garbage",
                }
            ],
        )
        builder = ImfTableBuilder()
        with pytest.warns(OpenBBWarning, match="Could not parse codelist"):
            with pytest.raises(ValueError):
                builder.get_table("BOP", "H_TEST")

    def test_dimension_pattern_fallback(self, mock_qb_factory):
        """Pattern fallback resolves ``CL_BOP_INDICATOR`` to ``INDICATOR``."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_SERIES",
                    "indicator_code": "CAB",
                    "code_urn": "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_BOP_INDICATOR(1.0).CAB",
                }
            ],
            options={"INDICATOR": [{"value": "CAB", "label": "CAB"}]},
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_SERIES",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST")
        assert len(result["data"]) >= 1

    def test_unresolvable_codelist_warns_and_skips(self, mock_qb_factory):
        """An unresolvable codelist warns and skips."""
        from openbb_core.app.model.abstract.warning import OpenBBWarning
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "X",
                    "parent_id": None,
                    "label": "X",
                    "series_id": "",
                    "indicator_code": "X",
                    "code_urn": "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_RANDOM_THING(1.0).X",
                }
            ],
        )
        builder = ImfTableBuilder()
        with pytest.warns(OpenBBWarning, match="Could not map codelist"):
            with pytest.raises(ValueError):
                builder.get_table("BOP", "H_TEST")


class TestKwargsNormalization:
    """Tests for the case-insensitive kwargs handling."""

    def test_lowercase_country_normalized(self, mock_qb_factory):
        """Lower-case ``country=`` matches the ``COUNTRY`` dimension."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            dimensions=("REF_AREA", "INDICATOR"),
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_SERIES",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "REF_AREA": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_SERIES",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        builder.get_table("BOP", "H_TEST", country="USA")
        kwargs = mock_qb.fetch_data.call_args[1]
        assert kwargs["REF_AREA"] == "USA"

    def test_invalid_user_value_raises(self, mock_qb_factory):
        """An invalid user-supplied dimension value raises ``ValueError``."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb_factory(
            dimensions=("COUNTRY", "INDICATOR"),
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
        )
        builder = ImfTableBuilder()
        with pytest.raises(ValueError, match="Invalid value"):
            builder.get_table("BOP", "H_TEST", COUNTRY="XYZ")

    def test_unknown_dim_in_dimension_codes(self, mock_qb_factory):
        """A dim outside ``dims_in_order`` populates ``fetch_kwargs`` via fallback."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            dimensions=("COUNTRY",),
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_SERIES",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_SERIES",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        builder.get_table("BOP", "H_TEST", COUNTRY="USA")


class TestPostFiltering:
    """Tests for the post-fetch filtering path."""

    def test_oversized_indicator_list_uses_wildcard_and_post_filters(
        self, mock_qb_factory
    ):
        """Joined-codes longer than 850 chars uses ``*`` then post-filters rows."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        indicators = [
            {
                "order": i,
                "depth": 0,
                "id": f"IND{i}",
                "parent_id": None,
                "label": f"Indicator {i}",
                "series_id": f"S{i}",
                "indicator_code": f"IND_THIS_IS_A_LONG_NAME_{i}",
                "dimension_id": "INDICATOR",
            }
            for i in range(80)
        ]
        options = {
            "INDICATOR": [
                {"value": ind["indicator_code"], "label": ind["indicator_code"]}
                for ind in indicators
            ],
            "COUNTRY": [{"value": "USA", "label": "USA"}],
        }
        mock_qb, _ = mock_qb_factory(
            indicators=indicators,
            options=options,
        )
        # Return rows for only 2 of the 80 indicators -> exercises post-filter
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": f"S{i}",
                    "INDICATOR_code": indicators[i]["indicator_code"],
                    "indicator_code": indicators[i]["indicator_code"],
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": i,
                }
                for i in range(80)
            ]
            + [
                {
                    "series_id": "EXTRA",
                    "INDICATOR_code": "NOT_IN_HIERARCHY",
                    "indicator_code": "NOT_IN_HIERARCHY",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 999,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        # post-filter drops "NOT_IN_HIERARCHY"
        codes = {r.get("INDICATOR_code") for r in result["data"]}
        assert "NOT_IN_HIERARCHY" not in codes
        fetch_kwargs = mock_qb.fetch_data.call_args[1]
        # Because joined codes > 850, the dim is reduced to ``*``
        assert fetch_kwargs["INDICATOR"] == "*"


class TestTitleAndUnitInference:
    """Tests for the title / unit-inference branches."""

    def test_gfs_indicator_with_unit_suffix(self, mock_qb_factory):
        """GFS-flavoured indicators infer ``unit`` from the code suffix."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            dataflows={
                "GFS": {
                    "id": "GFS",
                    "name": "GFS",
                    "structureRef": {"id": "DSD"},
                }
            },
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "REV",
                    "parent_id": None,
                    "label": "Revenue",
                    "series_id": "S1",
                    "indicator_code": "REV_USD",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "INDICATOR": [{"value": "REV_USD", "label": "REV_USD"}],
                "COUNTRY": [{"value": "USA", "label": "USA"}],
            },
            codelist_cache={"CL_UNIT": {"USD": "US dollar"}},
        )
        mock_qb.metadata._resolve_codelist_id = MagicMock(return_value="CL_GFS_REV")
        mock_qb.metadata._codelist_cache["CL_GFS_REV"] = {
            "REV_USD": "Revenue, US dollar"
        }
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "S1",
                    "INDICATOR_code": "REV_USD",
                    "indicator_code": "REV_USD",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("GFS", "H_TEST", COUNTRY="USA")
        row = next(r for r in result["data"] if r.get("INDICATOR_code") == "REV_USD")
        assert row["unit"] == "US dollar"

    def test_path_label_dataflow_uses_label(self, mock_qb_factory):
        """``CL_DIP_INDICATOR`` indicator codelist forces title from ``label``."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "GDP",
                    "parent_id": None,
                    "label": "Gross Domestic Product",
                    "series_id": "S1",
                    "indicator_code": "GDP",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "GDP", "label": "GDP"}],
            },
        )
        mock_qb.metadata._resolve_codelist_id = MagicMock(
            return_value="CL_DIP_INDICATOR"
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "S1",
                    "INDICATOR_code": "GDP",
                    "indicator_code": "GDP",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        row = result["data"][0]
        assert row["title"] == "Gross Domestic Product"

    def test_indicator_label_unit_suffix_trimmed(self, mock_qb_factory):
        """A unit suffix is trimmed from the indicator name."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "GDP",
                    "parent_id": None,
                    "label": "GDP",
                    "series_id": "S1",
                    "indicator_code": "GDP",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "GDP", "label": "GDP"}],
            },
            codelist_cache={
                "CL_BOP_INDICATOR": {"GDP": "Gross Domestic Product, US dollar"},
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "S1",
                    "INDICATOR_code": "GDP",
                    "indicator_code": "GDP",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        row = next(r for r in result["data"] if r.get("INDICATOR_code") == "GDP")
        assert row["title"] == "Gross Domestic Product"

    def test_cpi_index_type_appended(self, mock_qb_factory):
        """CPI dataflow with a non-``CPI`` INDEX_TYPE appends it to the title."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            dataflows={
                "CPI": {
                    "id": "CPI",
                    "name": "CPI",
                    "structureRef": {"id": "DSD"},
                }
            },
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "PCPI",
                    "parent_id": None,
                    "label": "Consumer Prices",
                    "series_id": "S1",
                    "indicator_code": "PCPI",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "PCPI", "label": "PCPI"}],
            },
            codelist_cache={"CL_BOP_INDICATOR": {"PCPI": "Headline CPI"}},
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "S1",
                    "INDICATOR_code": "PCPI",
                    "indicator_code": "PCPI",
                    "INDEX_TYPE_code": "FOOD",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("CPI", "H_TEST", COUNTRY="USA")
        row = next(r for r in result["data"] if r.get("INDICATOR_code") == "PCPI")
        assert row["title"].endswith("(FOOD)")

    def test_currency_label_appended(self, mock_qb_factory):
        """A CURRENCY label distinct from the unit is appended to the title."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "GDP",
                    "parent_id": None,
                    "label": "GDP",
                    "series_id": "S1",
                    "indicator_code": "GDP",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "GDP", "label": "GDP"}],
            },
            codelist_cache={"CL_BOP_INDICATOR": {"GDP": "Gross Domestic Product"}},
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "S1",
                    "INDICATOR_code": "GDP",
                    "indicator_code": "GDP",
                    "CURRENCY_code": "EUR",
                    "CURRENCY": "Euro",
                    "unit_code": "USD",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        row = next(r for r in result["data"] if r.get("INDICATOR_code") == "GDP")
        assert "(Euro)" in row["title"]

    def test_iip_assets_suffix_added(self, mock_qb_factory):
        """IIP-style series IDs get an ``(Assets)`` suffix when missing context."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "O",
                    "parent_id": None,
                    "label": "Other Investment",
                    "series_id": "BOP_IIP_A_P_O",
                    "indicator_code": "O",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "O", "label": "O"}],
            },
            codelist_cache={"CL_BOP_INDICATOR": {"O": "Other Investment"}},
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "BOP_IIP_A_P_O",
                    "INDICATOR_code": "O",
                    "indicator_code": "O",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        row = next(r for r in result["data"] if r.get("INDICATOR_code") == "O")
        assert "(Assets)" in row["title"]

    def test_iip_liabilities_suffix_added(self, mock_qb_factory):
        """IIP-style series IDs get an ``(Liabilities)`` suffix when needed."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "O",
                    "parent_id": None,
                    "label": "Other Investment",
                    "series_id": "BOP_IIP_L_P_O",
                    "indicator_code": "O",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "O", "label": "O"}],
            },
            codelist_cache={"CL_BOP_INDICATOR": {"O": "Other Investment"}},
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "BOP_IIP_L_P_O",
                    "INDICATOR_code": "O",
                    "indicator_code": "O",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        row = next(r for r in result["data"] if r.get("INDICATOR_code") == "O")
        assert "(Liabilities)" in row["title"]


class TestHeaderRows:
    """Tests for the category-header row injection."""

    def test_unmatched_order_creates_header_row(self, mock_qb_factory):
        """A hierarchy order not present in data is added as a category header."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "PARENT",
                    "parent_id": None,
                    "label": "Header Title",
                    "series_id": "",
                    "indicator_code": "PARENT",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "CHILD",
                    "parent_id": "PARENT",
                    "label": "Child",
                    "series_id": "CHILD_SERIES",
                    "indicator_code": "CHILD",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "PARENT", "label": "PARENT"},
                    {"value": "CHILD", "label": "CHILD"},
                ],
            },
            codelist_cache={
                "CL_BOP_INDICATOR": {"CHILD": "Child indicator"},
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CHILD_SERIES",
                    "INDICATOR_code": "CHILD",
                    "indicator_code": "CHILD",
                    "scale": "Units",
                    "unit": "US dollar",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        headers = [r for r in result["data"] if r.get("is_category_header")]
        assert any("Header Title" in (h.get("title") or "") for h in headers)

    def test_header_with_gfs_unit_inference(self, mock_qb_factory):
        """A GFS dataflow infers header units from the child's code suffix."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            dataflows={
                "GFS": {
                    "id": "GFS",
                    "name": "GFS",
                    "structureRef": {"id": "DSD"},
                }
            },
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "REV",
                    "parent_id": None,
                    "label": "Revenue",
                    "series_id": "",
                    "indicator_code": "REV",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "REV_USD",
                    "parent_id": "REV",
                    "label": "Revenue USD",
                    "series_id": "REV_USD_S",
                    "indicator_code": "REV_USD",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "REV", "label": "REV"},
                    {"value": "REV_USD", "label": "REV_USD"},
                ],
            },
            codelist_cache={
                "CL_GFS_REV": {"REV_USD": "Revenue, US dollar"},
                "CL_UNIT": {"USD": "US dollar"},
            },
        )
        mock_qb.metadata._resolve_codelist_id = MagicMock(return_value="CL_GFS_REV")
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "REV_USD_S",
                    "INDICATOR_code": "REV_USD",
                    "indicator_code": "REV_USD",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("GFS", "H_TEST", COUNTRY="USA")
        headers = [r for r in result["data"] if r.get("is_category_header")]
        assert headers
        assert any("US dollar" in (h.get("title") or "") for h in headers)


class TestDatasetMetadataMerge:
    """Tests for dataset-metadata merging into ``table_metadata``."""

    def test_dataset_metadata_merged(self, mock_qb_factory):
        """``dataset`` metadata is popped and merged into ``table_metadata``."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_SERIES",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_SERIES",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {
                "dataset": {
                    "dataflow_name": "Balance of Payments",
                    "dataflow_description": "BOP statistics",
                    "publisher": "IMF",
                    "license": "CC",
                }
            },
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        meta = result["table_metadata"]
        assert meta["dataflow_name"] == "Balance of Payments"
        assert meta["publisher"] == "IMF"
        assert meta["license"] == "CC"


class TestTimeRangeValidation:
    """Tests for the time-range validation in ``get_table``."""

    def test_no_overlap_raises(self, mock_qb_factory):
        """Request whose dates fall outside the available range raises."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        constraints = {
            "full_response": {
                "data": {
                    "dataConstraints": [
                        {
                            "annotations": [
                                {"id": "time_period_start", "title": "2010"},
                                {"id": "time_period_end", "title": "2020"},
                            ]
                        }
                    ]
                }
            }
        }
        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
            constraints_response=constraints,
        )
        builder = ImfTableBuilder()
        with pytest.raises(
            ValueError, match="No data available for the requested time"
        ):
            builder.get_table(
                "BOP", "H_TEST", COUNTRY="USA", start_date="2025", end_date="2026"
            )

    def test_end_date_before_available_raises(self, mock_qb_factory):
        """A request whose end_date is before the available start raises."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        constraints = {
            "full_response": {
                "data": {
                    "dataConstraints": [
                        {
                            "annotations": [
                                {"id": "time_period_start", "title": "2015-01-01"},
                                {"id": "time_period_end", "title": "2020-12-31"},
                            ]
                        }
                    ]
                }
            }
        }
        mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
            constraints_response=constraints,
        )
        builder = ImfTableBuilder()
        with pytest.raises(ValueError, match="No data available for the requested"):
            builder.get_table(
                "BOP", "H_TEST", COUNTRY="USA", start_date="2000-01", end_date="2010-12"
            )

    def test_date_parse_error_breaks_out(self, mock_qb_factory):
        """A malformed time-period annotation breaks out of validation without raising."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        constraints = {
            "full_response": {
                "data": {
                    "dataConstraints": [
                        {
                            "annotations": [
                                {"id": "time_period_start", "title": "not-a-date"},
                                {"id": "time_period_end", "title": "2020-12-31"},
                            ]
                        }
                    ]
                }
            }
        }
        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_S",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
            constraints_response=constraints,
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_S",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        # Should not raise — parse failure breaks the validation loop
        builder.get_table(
            "BOP", "H_TEST", COUNTRY="USA", start_date="2020-01", end_date="2020-12"
        )

    def test_quarterly_range_parses(self, mock_qb_factory):
        """Quarterly date strings (``YYYY-Q1``) parse without raising."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        constraints = {
            "full_response": {
                "data": {
                    "dataConstraints": [
                        {
                            "annotations": [
                                {"id": "time_period_start", "title": "2010-Q1"},
                                {"id": "time_period_end", "title": "2020-Q4"},
                            ]
                        }
                    ]
                }
            }
        }
        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_S",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
            constraints_response=constraints,
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_S",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2015-Q1",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        builder.get_table(
            "BOP", "H_TEST", COUNTRY="USA", start_date="2015-Q1", end_date="2018-Q2"
        )


class TestIndicatorFilters:
    """Tests exercising the ``parent_id`` / ``depth`` / ``indicators`` filters."""

    @pytest.fixture
    def indicators(self):
        """Build a small three-level hierarchy."""
        return [
            {
                "order": 1,
                "depth": 0,
                "id": "P1",
                "parent_id": None,
                "label": "P1",
                "series_id": "P1_S",
                "indicator_code": "P1",
                "dimension_id": "INDICATOR",
            },
            {
                "order": 2,
                "depth": 1,
                "id": "C1",
                "parent_id": "P1",
                "label": "C1",
                "series_id": "C1_S",
                "indicator_code": "C1",
                "dimension_id": "INDICATOR",
            },
            {
                "order": 3,
                "depth": 1,
                "id": "C2",
                "parent_id": "P1",
                "label": "C2",
                "series_id": "C2_S",
                "indicator_code": "C2",
                "dimension_id": "INDICATOR",
            },
        ]

    def test_parent_id_filter(self, mock_qb_factory, indicators):
        """``parent_id`` selects only direct children."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=indicators,
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "C1", "label": "C1"},
                    {"value": "C2", "label": "C2"},
                ],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "C1_S",
                    "INDICATOR_code": "C1",
                    "indicator_code": "C1",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", parent_id="P1", COUNTRY="USA")
        codes = {
            r["INDICATOR_code"]
            for r in result["data"]
            if not r.get("is_category_header")
        }
        assert "C1" in codes

    def test_depth_filter(self, mock_qb_factory, indicators):
        """``depth=0`` selects only top-level indicators."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=indicators,
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "P1", "label": "P1"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "P1_S",
                    "INDICATOR_code": "P1",
                    "indicator_code": "P1",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", depth=0, COUNTRY="USA")
        assert result["data"]

    def test_indicators_list_filter(self, mock_qb_factory, indicators):
        """A list of indicator codes restricts the hierarchy."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=indicators,
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "C1", "label": "C1"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "C1_S",
                    "INDICATOR_code": "C1",
                    "indicator_code": "C1",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", indicators=["C1"], COUNTRY="USA")
        assert result["data"]


class TestWildcardFallback:
    """Tests for the >1500-character indicator-list fallback branch."""

    def test_extra_dim_huge_codes_falls_back_to_wildcard(self, mock_qb_factory):
        """A non-``INDICATOR`` dim with >1500 joined codes collapses to ``*``."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        codes = [f"VERY_LONG_CODE_{i:04d}" for i in range(120)]
        indicators = [
            {
                "order": i,
                "depth": 0,
                "id": code,
                "parent_id": None,
                "label": code,
                "series_id": "",
                "indicator_code": code,
                "dimension_id": "EXTRA",
            }
            for i, code in enumerate(codes)
        ]
        mock_qb, _ = mock_qb_factory(
            dimensions=("COUNTRY",),
            indicators=indicators,
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "EXTRA": [{"value": c, "label": c} for c in codes],
            },
        )
        mock_qb.fetch_data.return_value = {"data": [], "metadata": {}}
        builder = ImfTableBuilder()
        builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        kwargs = mock_qb.fetch_data.call_args[1]
        assert kwargs["EXTRA"] == "*"

    def test_extra_dim_no_match_warns_and_falls_through(self, mock_qb_factory):
        """A non-``INDICATOR`` dim with no matching codes emits a warning and proceeds."""
        from openbb_core.app.model.abstract.warning import OpenBBWarning
        from openbb_imf.utils.table_builder import ImfTableBuilder

        indicators = [
            {
                "order": 1,
                "depth": 0,
                "id": "X",
                "parent_id": None,
                "label": "X",
                "series_id": "",
                "indicator_code": "ZZZ",
                "dimension_id": "EXTRA",
            }
        ]
        mock_qb, _ = mock_qb_factory(
            dimensions=("COUNTRY",),
            indicators=indicators,
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "EXTRA": [{"value": "OTHER", "label": "OTHER"}],
            },
        )
        mock_qb.fetch_data.return_value = {"data": [], "metadata": {}}
        builder = ImfTableBuilder()
        with pytest.warns(OpenBBWarning, match="Progressive constraint"):
            builder.get_table("BOP", "H_TEST", COUNTRY="USA")


class TestProgressiveExceptionFallback:
    """Tests for the warning-fallback when progressive filtering raises."""

    def test_keyerror_warning_fallback(self, mock_qb_factory):
        """A non-validation ``KeyError`` from the builder triggers the unfiltered fallback."""
        from openbb_core.app.model.abstract.warning import OpenBBWarning
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_S",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_S",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }

        class BoomBuilder(FakeImfParamsBuilder):
            def __init__(self):  # noqa: D107
                super().__init__(["COUNTRY", "INDICATOR"])
                self._first_call = True

            def get_options_for_dimension(self, dim_id):
                if self._first_call:
                    self._first_call = False
                    raise KeyError("boom")
                return [{"value": "USA", "label": "USA"}]

        with patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            lambda _df: BoomBuilder(),
        ):
            builder = ImfTableBuilder()
            with pytest.warns(OpenBBWarning, match="Progressive constraint"):
                builder.get_table("BOP", "H_TEST", COUNTRY="USA")


class TestHeaderLabelFromCodelist:
    """Tests for header-label resolution via the indicator codelist."""

    def test_label_matches_code_resolved_from_codelist(self, mock_qb_factory):
        """When the hierarchy label equals the code, the codelist supplies the name."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "PARENT",
                    "parent_id": None,
                    "label": "PARENT",  # Same as indicator_code
                    "series_id": "",
                    "indicator_code": "PARENT",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "CHILD",
                    "parent_id": "PARENT",
                    "label": "Child",
                    "series_id": "CHILD_S",
                    "indicator_code": "CHILD",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "PARENT", "label": "PARENT"},
                    {"value": "CHILD", "label": "CHILD"},
                ],
            },
            codelist_cache={
                "CL_BOP_INDICATOR": {
                    "PARENT": "Parent Group, US dollar, (Core FSI)",
                    "CHILD": "Child indicator",
                }
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CHILD_S",
                    "INDICATOR_code": "CHILD",
                    "indicator_code": "CHILD",
                    "unit": "US dollar",
                    "scale": "Millions",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        headers = [r for r in result["data"] if r.get("is_category_header")]
        assert any("Parent Group" in (h.get("title") or "") for h in headers)

    def test_label_matches_code_resolved_via_suffix_match(self, mock_qb_factory):
        """An exact codelist match falls back to a prefix scan when missing."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "REV",
                    "parent_id": None,
                    "label": "REV",
                    "series_id": "",
                    "indicator_code": "REV",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "REV_USD",
                    "parent_id": "REV",
                    "label": "Rev USD",
                    "series_id": "REV_USD_S",
                    "indicator_code": "REV_USD",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "REV", "label": "REV"},
                    {"value": "REV_USD", "label": "REV_USD"},
                ],
            },
            codelist_cache={
                "CL_BOP_INDICATOR": {"REV_USD": "Revenue series"},  # only suffix exists
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "REV_USD_S",
                    "INDICATOR_code": "REV_USD",
                    "indicator_code": "REV_USD",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        headers = [r for r in result["data"] if r.get("is_category_header")]
        assert any("Revenue series" in (h.get("title") or "") for h in headers)


class TestSeriesIdParsing:
    """Tests for the data-row hierarchy matching via series_id forms."""

    def test_series_id_with_dataflow_marker(self, mock_qb_factory):
        """Series IDs like ``A_BOP_X_Y`` match via the dataflow marker path."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "PREFIX_BOP_CAB",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "BOP::CAB",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        assert result["data"]


class TestGfsHeaderUnitInference:
    """Tests for GFS header unit inference and sector-prefix application."""

    def test_gfs_header_unit_from_child_code(self, mock_qb_factory):
        """A GFS header borrows the unit from its child's code suffix."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            dataflows={
                "GFS": {
                    "id": "GFS",
                    "name": "GFS",
                    "structureRef": {"id": "DSD"},
                }
            },
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "REV",
                    "parent_id": None,
                    "label": "Revenue",
                    "series_id": "",
                    "indicator_code": "REV",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "REV_TAX_USD",
                    "parent_id": "REV",
                    "label": "Tax Revenue",
                    "series_id": "REV_TAX_USD_S",
                    "indicator_code": "REV_TAX_USD",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "REV", "label": "REV"},
                    {"value": "REV_TAX_USD", "label": "REV_TAX_USD"},
                ],
            },
            codelist_cache={
                "CL_GFS_REV": {"REV_TAX_USD": "Tax Revenue, US dollar"},
                "CL_UNIT": {"USD": "US dollar"},
            },
        )
        mock_qb.metadata._resolve_codelist_id = MagicMock(return_value="CL_GFS_REV")
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "REV_TAX_USD_S",
                    "INDICATOR_code": "REV_TAX_USD",
                    "indicator_code": "REV_TAX_USD",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("GFS", "H_TEST", COUNTRY="USA")
        headers = [r for r in result["data"] if r.get("is_category_header")]
        assert any("US dollar" in (h.get("title") or "") for h in headers)


class TestSectorPrefixHeader:
    """Tests for sector-prefix decoration in category headers."""

    def test_sector_prefix_added_to_header(self, mock_qb_factory):
        """A header whose indicator starts with a CL_SECTOR code gets a sector prefix."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "S13_REV",
                    "parent_id": None,
                    "label": "Revenue header",
                    "series_id": "",
                    "indicator_code": "S13_REV",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "S13_REV_TAX",
                    "parent_id": "S13_REV",
                    "label": "Tax",
                    "series_id": "S13_REV_TAX_S",
                    "indicator_code": "S13_REV_TAX",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "S13_REV", "label": "S13_REV"},
                    {"value": "S13_REV_TAX", "label": "S13_REV_TAX"},
                ],
            },
            codelist_cache={
                "CL_SECTOR": {"S13": "General Government"},
                "CL_BOP_INDICATOR": {"S13_REV_TAX": "Tax Revenue"},
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "S13_REV_TAX_S",
                    "INDICATOR_code": "S13_REV_TAX",
                    "indicator_code": "S13_REV_TAX",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        headers = [r for r in result["data"] if r.get("is_category_header")]
        assert any("General Government" in (h.get("title") or "") for h in headers)


class TestEmptyDimensionRaises:
    """Tests for the ``no data available`` warning path in the indicator-dim handling."""

    def test_indicator_codes_dont_match_available(self, mock_qb_factory):
        """Indicator codes that don't match available options trigger a warning fallback."""
        from openbb_core.app.model.abstract.warning import OpenBBWarning
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "X",
                    "parent_id": None,
                    "label": "X",
                    "series_id": "",
                    "indicator_code": "Z_NOT_IN_OPTIONS",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "REAL_INDICATOR", "label": "Real"}],
            },
        )
        mock_qb.fetch_data.return_value = {"data": [], "metadata": {}}
        builder = ImfTableBuilder()
        with pytest.warns(OpenBBWarning, match="Progressive constraint"):
            builder.get_table("BOP", "H_TEST", COUNTRY="USA")


class TestOrderSubIndex:
    """Tests for sub-indexing when multiple series share the same hierarchy order."""

    def test_duplicate_orders_get_sub_indexed(self, mock_qb_factory):
        """Multiple series at the same order get offset by 0.001 increments."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "A",
                    "parent_id": None,
                    "label": "A",
                    "series_id": "A_S",
                    "indicator_code": "A",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "A", "label": "A"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "A_S",
                    "INDICATOR_code": "A",
                    "indicator_code": "A",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                },
                {
                    "series_id": "A_S_v2",  # Different series_id, same hierarchy order via prefix
                    "INDICATOR_code": "A",
                    "indicator_code": "A",
                    "TIME_PERIOD": "2021",
                    "OBS_VALUE": 2,
                },
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        orders = sorted(r["order"] for r in result["data"])
        # At least two distinct orders (1 and 1.001) when more than one series sub-indexed
        assert any(isinstance(o, float) and o != int(o) for o in orders)


class TestRowMatchingViaCompositeKey:
    """Tests for row hierarchy matching when ``series_id`` is empty."""

    def test_row_with_series_id_carrying_double_colon(self, mock_qb_factory):
        """A row with ``series_id`` containing ``::`` matches via sorted codes."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "X",
                    "parent_id": None,
                    "label": "X",
                    "series_id": "BOP::X",
                    "indicator_code": "X",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "X", "label": "X"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "BOP::X",
                    "INDICATOR_code": "X",
                    "indicator_code": "X",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        assert result["data"]

    def test_row_without_indicator_code_skipped(self, mock_qb_factory):
        """Rows missing every indicator-code field are skipped."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_S",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_S",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                },
                {
                    "series_id": "ORPHAN",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                },
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        assert all(r.get("INDICATOR_code") in {"CAB", None, ""} for r in result["data"])


class TestCachedCodelistDimensionLookup:
    """Tests for the cached codelist→dimension resolution."""

    def test_repeated_codelist_uses_cache(self, mock_qb_factory):
        """A second indicator with the same codelist hits the in-method cache."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "A",
                    "parent_id": None,
                    "label": "A",
                    "series_id": "A_S",
                    "indicator_code": "A",
                    "code_urn": "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_BOP_INDICATOR(1.0).A",
                },
                {
                    "order": 2,
                    "depth": 0,
                    "id": "B",
                    "parent_id": None,
                    "label": "B",
                    "series_id": "B_S",
                    "indicator_code": "B",
                    "code_urn": "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_BOP_INDICATOR(1.0).B",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "A", "label": "A"},
                    {"value": "B", "label": "B"},
                ],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "A_S",
                    "INDICATOR_code": "A",
                    "indicator_code": "A",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                },
                {
                    "series_id": "B_S",
                    "INDICATOR_code": "B",
                    "indicator_code": "B",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                },
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        codes = {r.get("INDICATOR_code") for r in result["data"]}
        assert {"A", "B"}.issubset(codes)


class TestGfsRowSectorPrefix:
    """Tests for GFS-row sector handling."""

    def test_gfs_row_sector_prefix_from_sector_code(self, mock_qb_factory):
        """GFS rows pick up the sector via the ``SECTOR_code`` field."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            dataflows={
                "GFS": {
                    "id": "GFS",
                    "name": "GFS",
                    "structureRef": {"id": "DSD"},
                }
            },
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "REV",
                    "parent_id": None,
                    "label": "Revenue",
                    "series_id": "REV_S",
                    "indicator_code": "REV",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "REV", "label": "REV"}],
            },
            codelist_cache={
                "CL_SECTOR": {"S13": "General Government"},
                "CL_GFS_REV": {"REV": "Revenue"},
            },
        )
        mock_qb.metadata._resolve_codelist_id = MagicMock(return_value="CL_GFS_REV")
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "REV_S",
                    "INDICATOR_code": "REV",
                    "indicator_code": "REV",
                    "SECTOR_code": "S13",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("GFS", "H_TEST", COUNTRY="USA")
        row = next(r for r in result["data"] if r.get("INDICATOR_code") == "REV")
        assert "General Government" in (row.get("title") or "")


class TestExistingNetBaseLabels:
    """Tests for the ``, Net`` base-label skip logic in header creation."""

    def test_existing_net_title_prevents_duplicate_header(self, mock_qb_factory):
        """A header sharing the same prefix as an existing ``, Net`` row is suppressed."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "OVERVIEW",
                    "parent_id": None,
                    "label": "Account Overview",
                    "series_id": "",
                    "indicator_code": "OVERVIEW",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "OVERVIEW_NET",
                    "parent_id": "OVERVIEW",
                    "label": "Account Overview, Net",
                    "series_id": "OV_NET_S",
                    "indicator_code": "OVERVIEW_NET",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "OVERVIEW", "label": "OVERVIEW"},
                    {"value": "OVERVIEW_NET", "label": "OVERVIEW_NET"},
                ],
            },
            codelist_cache={
                "CL_BOP_INDICATOR": {
                    "OVERVIEW_NET": "Account Overview, Net",
                    "OVERVIEW": "Account Overview",
                }
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "OV_NET_S",
                    "INDICATOR_code": "OVERVIEW_NET",
                    "indicator_code": "OVERVIEW_NET",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        # The "OVERVIEW" header should be skipped because "Account Overview" matches
        # a base of an existing ", Net" title.
        header_titles = [
            r.get("title")
            for r in result["data"]
            if r.get("is_category_header") and r.get("indicator_code") == "OVERVIEW"
        ]
        assert header_titles == []


class TestNameWithGfsSuffix:
    """Tests for indicator-name suffix stripping."""

    def test_gfs_suffix_stripped_from_indicator_name(self, mock_qb_factory):
        """A ``Stock positions`` suffix on the codelist name is trimmed."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "X",
                    "parent_id": None,
                    "label": "X",
                    "series_id": "X_S",
                    "indicator_code": "X",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "X", "label": "X"}],
            },
            codelist_cache={
                "CL_BOP_INDICATOR": {"X": "Asset, Sub-category, Stock positions"}
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "X_S",
                    "INDICATOR_code": "X",
                    "indicator_code": "X",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        row = next(r for r in result["data"] if r.get("INDICATOR_code") == "X")
        # ``Stock positions`` is trimmed by the GFS-suffix loop
        assert "Stock positions" not in (row.get("title") or "")


class TestGfsHeaderUnitFromParent:
    """Tests for GFS header unit inference via parent_id suffix."""

    def test_header_unit_from_parent_id_suffix(self, mock_qb_factory):
        """When children carry no unit, header inherits unit from parent_id suffix."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            dataflows={
                "GFS": {
                    "id": "GFS",
                    "name": "GFS",
                    "structureRef": {"id": "DSD"},
                }
            },
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "REV_USD",
                    "parent_id": None,
                    "label": "Revenue Group",
                    "series_id": "",
                    "indicator_code": "REV_USD",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "REV_TAX_X",
                    "parent_id": "REV_USD",
                    "label": "Tax",
                    "series_id": "TX_S",
                    "indicator_code": "REV_TAX_X",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "REV_USD", "label": "REV_USD"},
                    {"value": "REV_TAX_X", "label": "REV_TAX_X"},
                ],
            },
            codelist_cache={
                "CL_GFS_REV": {"REV_TAX_X": "Tax"},
                "CL_UNIT": {"USD": "US dollar"},
            },
        )
        mock_qb.metadata._resolve_codelist_id = MagicMock(return_value="CL_GFS_REV")
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "TX_S",
                    "INDICATOR_code": "REV_TAX_X",
                    "indicator_code": "REV_TAX_X",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("GFS", "H_TEST", COUNTRY="USA")
        headers = [r for r in result["data"] if r.get("is_category_header")]
        assert any("US dollar" in (h.get("title") or "") for h in headers)


class TestHierarchyEdgeEntries:
    """Edge-case hierarchy entries."""

    def test_entry_without_indicator_code_in_full_indicators(self, mock_qb_factory):
        """An entry without ``indicator_code`` in the full list is skipped."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "A",
                    "parent_id": None,
                    "label": "A",
                    "series_id": "A_S",
                    "indicator_code": "A",
                    "dimension_id": "INDICATOR",
                },
                {  # No indicator_code -> skipped by line 351
                    "order": 99,
                    "depth": 0,
                    "id": "NOCODE",
                    "parent_id": None,
                    "label": "",
                    "series_id": "",
                    "indicator_code": "",
                    "dimension_id": "INDICATOR",
                },
                {  # order=None -> skipped by line 356
                    "order": None,
                    "depth": 0,
                    "id": "NOORDER",
                    "parent_id": None,
                    "label": "X",
                    "series_id": "",
                    "indicator_code": "NOORDER",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "A", "label": "A"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "A_S",
                    "INDICATOR_code": "A",
                    "indicator_code": "A",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        assert result["data"]

    def test_dim_with_empty_id_skipped(self, mock_qb_factory):
        """A DSD dimension with an empty ID is skipped during indicator-order build."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, MockQB = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "A",
                    "parent_id": None,
                    "label": "A",
                    "series_id": "A_S",
                    "indicator_code": "A",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "A", "label": "A"}],
            },
        )
        # Add a DSD dimension with empty ID
        mock_qb.metadata.datastructures["DSD"]["dimensions"].append(
            {"id": "", "position": 99}
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "A_S",
                    "INDICATOR_code": "A",
                    "indicator_code": "A",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        assert result["data"]


class TestCalculateDepth:
    """Tests for the module-level ``_calculate_depth`` helper."""

    def test_depth_traces_parent_chain(self):
        """The depth equals the number of ancestors in the chain."""
        from openbb_imf.utils.table_builder import _calculate_depth

        indicators = {
            "A": {"indicator_code": "A", "parent_id": None},
            "B": {"indicator_code": "B", "parent_id": "A"},
            "C": {"indicator_code": "C", "parent_id": "B"},
        }
        assert _calculate_depth(indicators["A"], indicators) == 0
        assert _calculate_depth(indicators["B"], indicators) == 1
        assert _calculate_depth(indicators["C"], indicators) == 2

    def test_depth_short_circuits_on_cycle(self):
        """A cycle in parent links returns 0 instead of looping forever."""
        from openbb_imf.utils.table_builder import _calculate_depth

        indicators = {
            "A": {"indicator_code": "A", "parent_id": "B"},
            "B": {"indicator_code": "B", "parent_id": "A"},
        }
        assert _calculate_depth(indicators["A"], indicators) <= 2

    def test_depth_without_code_returns_zero(self):
        """An indicator without a code returns depth 0."""
        from openbb_imf.utils.table_builder import _calculate_depth

        assert _calculate_depth({}, {}) == 0


class TestUnmappedKwarg:
    """Tests for kwargs whose lowercase key matches no dimension."""

    def test_unknown_kwarg_passed_through(self, mock_qb_factory):
        """A kwarg whose lower-case key is not a dimension is forwarded as-is."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_S",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_S",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        builder.get_table("BOP", "H_TEST", COUNTRY="USA", EXTRA_KWARG="passthrough")
        kwargs = mock_qb.fetch_data.call_args[1]
        assert kwargs["EXTRA_KWARG"] == "passthrough"


class TestUnmappedIndicatorDim:
    """Tests for the unmapped-indicator-dim error path."""

    def test_indicator_dim_not_in_hierarchy_raises(self, mock_qb_factory):
        """An indicator dimension absent from both hierarchy and kwargs raises."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb_factory(
            dimensions=("COUNTRY", "INDICATOR"),
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "USA",
                    "parent_id": None,
                    "label": "USA",
                    "series_id": "USA_S",
                    "indicator_code": "USA",
                    "dimension_id": "COUNTRY",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
        )
        builder = ImfTableBuilder()
        with pytest.raises(ValueError, match="could not be mapped"):
            builder.get_table("BOP", "H_TEST")


class TestShallowAvailableEmptyTruncation:
    """Tests for the truncation branch when shallow_codes is empty."""

    def test_deep_only_long_codes_truncated(self, mock_qb_factory):
        """All indicators at depth>1 with joined length>850 triggers truncation."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        long_codes = [f"INDICATOR_VERY_VERY_LONG_NAME_{i:04d}" for i in range(60)]
        indicators = [
            {
                "order": 1,
                "depth": 0,
                "id": "ROOT",
                "parent_id": None,
                "label": "ROOT",
                "series_id": "ROOT_S",
                "indicator_code": "ROOT",
                "dimension_id": "INDICATOR",
            }
        ]
        for i, code in enumerate(long_codes, start=2):
            indicators.append(
                {
                    "order": i,
                    "depth": 3,
                    "id": code,
                    "parent_id": "ROOT",
                    "label": code,
                    "series_id": f"{code}_S",
                    "indicator_code": code,
                    "dimension_id": "INDICATOR",
                }
            )
        options = {
            "COUNTRY": [{"value": "USA", "label": "USA"}],
            "INDICATOR": [{"value": c, "label": c} for c in ["ROOT"] + long_codes],
        }
        mock_qb, _ = mock_qb_factory(indicators=indicators, options=options)
        mock_qb.fetch_data.return_value = {"data": [], "metadata": {}}
        builder = ImfTableBuilder()
        builder.get_table("BOP", "H_TEST", parent_id="ROOT", COUNTRY="USA")
        kwargs = mock_qb.fetch_data.call_args[1]
        assert kwargs["INDICATOR"] == "*"


class TestProgressiveFallbackLargeCodes:
    """Tests for the unfiltered-fallback wildcard when joined codes>1500."""

    def test_progressive_failure_long_codes_uses_wildcard(self, mock_qb_factory):
        """When the progressive builder errors and joined codes>1500, falls back to ``*``."""
        from openbb_core.app.model.abstract.warning import OpenBBWarning
        from openbb_imf.utils.table_builder import ImfTableBuilder

        long_codes = [f"REALLY_LONG_INDICATOR_NAME_{i:05d}" for i in range(120)]
        indicators = [
            {
                "order": i,
                "depth": 0,
                "id": code,
                "parent_id": None,
                "label": code,
                "series_id": f"{code}_S",
                "indicator_code": code,
                "dimension_id": "INDICATOR",
            }
            for i, code in enumerate(long_codes)
        ]
        mock_qb, _ = mock_qb_factory(
            indicators=indicators,
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": c, "label": c} for c in long_codes],
            },
        )
        mock_qb.fetch_data.return_value = {"data": [], "metadata": {}}

        class BoomBuilder(FakeImfParamsBuilder):
            def __init__(self):
                super().__init__(["COUNTRY", "INDICATOR"])
                self._first_call = True

            def get_options_for_dimension(self, dim_id):
                if self._first_call:
                    self._first_call = False
                    raise KeyError("boom")
                return [{"value": c, "label": c} for c in long_codes]

        with patch(
            "openbb_imf.utils.progressive_helper.ImfParamsBuilder",
            lambda _df: BoomBuilder(),
        ):
            builder = ImfTableBuilder()
            with pytest.warns(OpenBBWarning, match="Progressive constraint"):
                builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        kwargs = mock_qb.fetch_data.call_args[1]
        assert kwargs["INDICATOR"] == "*"


class TestSeriesIdDoubleColonFallback:
    """Tests for row matching via sorted-codes when series_id has ``::``."""

    def test_row_series_id_double_colon_falls_through_to_sorted_codes(
        self, mock_qb_factory
    ):
        """A row series_id containing ``::`` not in hierarchy_by_series_id falls through."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "X",
                    "parent_id": None,
                    "label": "X",
                    "series_id": "PREFIX_BOP_X",
                    "indicator_code": "X",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "X", "label": "X"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "OTHERPREFIX::X",
                    "INDICATOR_code": "X",
                    "indicator_code": "X",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        assert result["data"]


class TestBopCompositeMarkerHandling:
    """Tests for the BOP A_P / L_P composite marker selection."""

    @pytest.fixture
    def bop_options(self):
        """Return the BOP options used by the composite tests."""
        return {
            "COUNTRY": [{"value": "USA", "label": "USA"}],
            "INDICATOR": [{"value": "X", "label": "X"}],
            "BOP_ACCOUNTING_ENTRY": [
                {"value": "A_P", "label": "Assets"},
                {"value": "L_P", "label": "Liabilities"},
            ],
        }

    def test_a_p_marker_chooses_asset_candidate(self, mock_qb_factory, bop_options):
        """A_P marker picks the candidate whose haystack mentions ASSET."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        indicators = [
            {
                "order": 1,
                "depth": 0,
                "id": "A_P",
                "parent_id": None,
                "label": "Assets",
                "series_id": "AP_S",
                "indicator_code": "A_P",
                "is_group": True,
                "dimension_id": "BOP_ACCOUNTING_ENTRY",
            },
            {
                "order": 2,
                "depth": 1,
                "id": "X_GENERIC_ONE",
                "parent_id": "A_P",
                "label": "X variant 1",
                "series_id": "",
                "indicator_code": "X",
                "dimension_id": "INDICATOR",
            },
            {
                "order": 3,
                "depth": 1,
                "id": "X_ASSETS_VARIANT",
                "parent_id": "A_P",
                "label": "X assets variant",
                "series_id": "",
                "indicator_code": "X",
                "dimension_id": "INDICATOR",
            },
        ]
        mock_qb, _ = mock_qb_factory(
            dimensions=("COUNTRY", "INDICATOR", "BOP_ACCOUNTING_ENTRY"),
            indicators=indicators,
            options=bop_options,
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "",
                    "INDICATOR_code": "X",
                    "BOP_ACCOUNTING_ENTRY_code": "A_P",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        rows = [r for r in result["data"] if r.get("INDICATOR_code") == "X"]
        assert any(r.get("hierarchy_node_id") == "X_ASSETS_VARIANT" for r in rows)

    def test_l_p_marker_chooses_liability_candidate(self, mock_qb_factory, bop_options):
        """L_P marker picks the candidate whose haystack mentions LIAB."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        indicators = [
            {
                "order": 1,
                "depth": 0,
                "id": "L_P",
                "parent_id": None,
                "label": "Liabilities",
                "series_id": "LP_S",
                "indicator_code": "L_P",
                "is_group": True,
                "dimension_id": "BOP_ACCOUNTING_ENTRY",
            },
            {
                "order": 2,
                "depth": 1,
                "id": "X_GENERIC_VARIANT",
                "parent_id": "L_P",
                "label": "X generic variant",
                "series_id": "",
                "indicator_code": "X",
                "dimension_id": "INDICATOR",
            },
            {
                "order": 3,
                "depth": 1,
                "id": "X_LIABILITIES_NODE",
                "parent_id": "L_P",
                "label": "X liability variant",
                "series_id": "",
                "indicator_code": "X",
                "dimension_id": "INDICATOR",
            },
        ]
        mock_qb, _ = mock_qb_factory(
            dimensions=("COUNTRY", "INDICATOR", "BOP_ACCOUNTING_ENTRY"),
            indicators=indicators,
            options=bop_options,
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "",
                    "INDICATOR_code": "X",
                    "BOP_ACCOUNTING_ENTRY_code": "L_P",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        rows = [r for r in result["data"] if r.get("INDICATOR_code") == "X"]
        assert any(r.get("hierarchy_node_id") == "X_LIABILITIES_NODE" for r in rows)

    def test_no_marker_match_falls_back_to_first_candidate(self, mock_qb_factory):
        """When no candidate carries the marker, the first candidate is returned."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        options = {
            "COUNTRY": [{"value": "USA", "label": "USA"}],
            "INDICATOR": [{"value": "X", "label": "X"}],
            "BOP_ACCOUNTING_ENTRY": [
                {"value": "A_T", "label": "A_T"},
            ],
        }
        indicators = [
            {
                "order": 1,
                "depth": 0,
                "id": "A_T",
                "parent_id": None,
                "label": "Combined",
                "series_id": "",
                "indicator_code": "A_T",
                "is_group": True,
                "dimension_id": "BOP_ACCOUNTING_ENTRY",
            },
            {
                "order": 2,
                "depth": 1,
                "id": "PLAIN_NODE_ONE",
                "parent_id": "A_T",
                "label": "X variant 1",
                "series_id": "PLAIN_SERIES_1",
                "indicator_code": "X",
                "dimension_id": "INDICATOR",
            },
            {
                "order": 3,
                "depth": 1,
                "id": "PLAIN_NODE_TWO",
                "parent_id": "A_T",
                "label": "X variant 2",
                "series_id": "PLAIN_SERIES_2",
                "indicator_code": "X",
                "dimension_id": "INDICATOR",
            },
        ]
        mock_qb, _ = mock_qb_factory(
            dimensions=("COUNTRY", "INDICATOR", "BOP_ACCOUNTING_ENTRY"),
            indicators=indicators,
            options=options,
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "",
                    "INDICATOR_code": "X",
                    "BOP_ACCOUNTING_ENTRY_code": "A_T",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        rows = [r for r in result["data"] if r.get("INDICATOR_code") == "X"]
        assert rows


class TestNetLikeParentFallback:
    """Tests for the NET-like parent fallback when NETCD_T is absent."""

    def test_net_like_parent_used_when_netcd_t_missing(self, mock_qb_factory):
        """A parent whose name starts with NET resolves CD_T/DB_T rows when NETCD_T missing."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        options = {
            "COUNTRY": [{"value": "USA", "label": "USA"}],
            "INDICATOR": [{"value": "Y", "label": "Y"}],
            "BOP_ACCOUNTING_ENTRY": [
                {"value": "NETPLUS", "label": "Net Plus"},
                {"value": "CD_T", "label": "Credit"},
                {"value": "DB_T", "label": "Debit"},
            ],
        }
        indicators = [
            {
                "order": 1,
                "depth": 0,
                "id": "NETPLUS",
                "parent_id": None,
                "label": "Net Plus",
                "series_id": "",
                "indicator_code": "NETPLUS",
                "is_group": True,
                "dimension_id": "BOP_ACCOUNTING_ENTRY",
            },
            {
                "order": 2,
                "depth": 1,
                "id": "Y_UNDER_NETPLUS",
                "parent_id": "NETPLUS",
                "label": "Y composite",
                "series_id": "",
                "indicator_code": "Y",
                "dimension_id": "INDICATOR",
            },
        ]
        mock_qb, _ = mock_qb_factory(
            dimensions=("COUNTRY", "INDICATOR", "BOP_ACCOUNTING_ENTRY"),
            indicators=indicators,
            options=options,
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "",
                    "INDICATOR_code": "Y",
                    "BOP_ACCOUNTING_ENTRY_code": "CD_T",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        rows = [r for r in result["data"] if r.get("INDICATOR_code") == "Y"]
        assert any(r.get("parent_code") == "NETPLUS" for r in rows)


class TestRowWithoutHierMatch:
    """Tests for rows that fail every hierarchy-matching strategy."""

    def test_unmatched_row_dropped(self, mock_qb_factory):
        """A row whose indicator_code doesn't appear in the hierarchy is dropped."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "CAB",
                    "parent_id": None,
                    "label": "CAB",
                    "series_id": "CAB_S",
                    "indicator_code": "CAB",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "CAB", "label": "CAB"}],
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CAB_S",
                    "INDICATOR_code": "CAB",
                    "indicator_code": "CAB",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                },
                {
                    "series_id": "OTHER_SERIES",
                    "INDICATOR_code": "TOTALLY_UNRELATED",
                    "indicator_code": "TOTALLY_UNRELATED",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 99,
                },
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        codes = {r.get("INDICATOR_code") for r in result["data"]}
        assert "TOTALLY_UNRELATED" not in codes


class TestSectorPrefixEmptyName:
    """Tests for the sector_prefix present but sector name empty branch."""

    def test_sector_prefix_with_empty_name_falls_through(self, mock_qb_factory):
        """A sector_prefix mapped to an empty name skips the sector decoration."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "S99_X",
                    "parent_id": None,
                    "label": "S99_X",
                    "series_id": "S99_X_S",
                    "indicator_code": "S99_X",
                    "dimension_id": "INDICATOR",
                }
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "S99_X", "label": "S99_X"}],
            },
            codelist_cache={
                "CL_SECTOR": {"S99": ""},
                "CL_BOP_INDICATOR": {"S99_X": "Indicator Name"},
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "S99_X_S",
                    "INDICATOR_code": "S99_X",
                    "indicator_code": "S99_X",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        row = next(r for r in result["data"] if r.get("INDICATOR_code") == "S99_X")
        assert row["title"] == "Indicator Name"


class TestHeaderLabelUnitSuffixTrim:
    """Tests for header-row codelist-name unit-suffix trimming."""

    def test_header_codelist_unit_suffix_trimmed(self, mock_qb_factory):
        """A unit-pattern suffix on the codelist name is trimmed for headers."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "PARENT",
                    "parent_id": None,
                    "label": "PARENT",
                    "series_id": "",
                    "indicator_code": "PARENT",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "CHILD",
                    "parent_id": "PARENT",
                    "label": "Child",
                    "series_id": "CHILD_S",
                    "indicator_code": "CHILD",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "PARENT", "label": "PARENT"},
                    {"value": "CHILD", "label": "CHILD"},
                ],
            },
            codelist_cache={
                "CL_BOP_INDICATOR": {
                    "PARENT": "Parent Group Name, US dollar",
                    "CHILD": "Child indicator",
                }
            },
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CHILD_S",
                    "INDICATOR_code": "CHILD",
                    "indicator_code": "CHILD",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        headers = [
            r
            for r in result["data"]
            if r.get("is_category_header") and r.get("indicator_code") == "PARENT"
        ]
        assert headers
        title = headers[0]["title"]
        assert "US dollar" not in title
        assert "Parent Group Name" in title


class TestHeaderGfsSuffixTrim:
    """Tests for the GFS-suffix trim in the header-label loop."""

    def test_header_gfs_suffix_trimmed(self, mock_qb_factory):
        """GFS suffixes on the base_label are trimmed."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "PARENT",
                    "parent_id": None,
                    "label": "Revenue Items, Stock positions",
                    "series_id": "",
                    "indicator_code": "PARENT",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "CHILD",
                    "parent_id": "PARENT",
                    "label": "Child",
                    "series_id": "CHILD_S",
                    "indicator_code": "CHILD",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "PARENT", "label": "PARENT"},
                    {"value": "CHILD", "label": "CHILD"},
                ],
            },
            codelist_cache={"CL_BOP_INDICATOR": {"CHILD": "Child indicator"}},
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CHILD_S",
                    "INDICATOR_code": "CHILD",
                    "indicator_code": "CHILD",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        headers = [
            r
            for r in result["data"]
            if r.get("is_category_header") and r.get("indicator_code") == "PARENT"
        ]
        assert headers
        assert "Stock positions" not in headers[0]["title"]
        assert "Revenue Items" in headers[0]["title"]


class TestHeaderScaleOnly:
    """Tests for the header title with valid scale only."""

    def test_header_with_only_scale_renders_scale(self, mock_qb_factory):
        """A header with a scale but no unit renders ``Label (Scale)``."""
        from openbb_imf.utils.table_builder import ImfTableBuilder

        mock_qb, _ = mock_qb_factory(
            indicators=[
                {
                    "order": 1,
                    "depth": 0,
                    "id": "PARENT",
                    "parent_id": None,
                    "label": "Parent Header",
                    "series_id": "",
                    "indicator_code": "PARENT",
                    "is_group": True,
                    "dimension_id": "INDICATOR",
                },
                {
                    "order": 2,
                    "depth": 1,
                    "id": "CHILD",
                    "parent_id": "PARENT",
                    "label": "Child",
                    "series_id": "CHILD_S",
                    "indicator_code": "CHILD",
                    "dimension_id": "INDICATOR",
                },
            ],
            options={
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [
                    {"value": "PARENT", "label": "PARENT"},
                    {"value": "CHILD", "label": "CHILD"},
                ],
            },
            codelist_cache={"CL_BOP_INDICATOR": {"CHILD": "Child indicator"}},
        )
        mock_qb.fetch_data.return_value = {
            "data": [
                {
                    "series_id": "CHILD_S",
                    "INDICATOR_code": "CHILD",
                    "indicator_code": "CHILD",
                    "scale": "Millions",
                    "TIME_PERIOD": "2020",
                    "OBS_VALUE": 1,
                }
            ],
            "metadata": {},
        }
        builder = ImfTableBuilder()
        result = builder.get_table("BOP", "H_TEST", COUNTRY="USA")
        headers = [
            r
            for r in result["data"]
            if r.get("is_category_header") and r.get("indicator_code") == "PARENT"
        ]
        assert headers
        assert headers[0]["title"] == "Parent Header (Millions)"
