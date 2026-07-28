"""Comprehensive tests for IMF query parsing, search, and fetch helpers."""

# ruff: noqa: I001, SLF001

from textwrap import dedent
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from openbb_imf.utils import metadata as md
from openbb_imf.utils.query_builder import ImfQueryBuilder


MOCK_SDMX_CHUNKS_DATAFLOWS = [
    {
        "id": "DATAFLOW_A",
        "name": "Dataflow A Name",
        "description": "Description for dataflow A with keyword gold.",
        "structureRef": {"id": "DSD_A"},
    },
    {
        "id": "DATAFLOW_B",
        "name": "Dataflow B Name with reserves",
        "description": "Another description.",
        "structureRef": {"id": "DSD_B"},
    },
    {
        "id": "DATAFLOW_GOLD_STATISTICS",
        "name": "Gold Statistics",
        "description": "Comprehensive data on gold holdings and reserves.",
        "structureRef": {"id": "DSD_GOLD"},
    },
    {
        "id": "DATAFLOW_CENTRAL_BANK",
        "name": "Central Bank Operations",
        "description": "Data on central bank activities.",
        "structureRef": {"id": "DSD_CENTRAL"},
    },
]

MOCK_DATAFLOW_GROUPS = {
    "IMF.STA": [
        {
            "id": "DATAFLOW_C",
            "name": "Central Bank Data",
            "description": "Data related to central banks.",
            "structureRef": {"id": "DSD_CENTRAL"},
        },
        {
            "id": "DATAFLOW_D",
            "name": "Gold Reserves Statistics",
            "description": "Statistics on gold reserves.",
            "structureRef": {"id": "DSD_GOLD"},
        },
        {
            "id": "DATAFLOW_E",
            "name": "Economic Indicators",
            "description": "Various economic indicators.",
            "structureRef": {"id": "DSD_ECON"},
        },
    ]
}

MOCK_DATASTRUCTURES = [
    {
        "id": "DSD_TEST",
        "dimensions": [
            {"id": "COUNTRY", "position": 0, "conceptRef": {"id": "COUNTRY"}},
            {"id": "INDICATOR", "position": 1, "conceptRef": {"id": "INDICATOR"}},
            {"id": "TIME_PERIOD", "position": 2, "conceptRef": {"id": "TIME_PERIOD"}},
        ],
    }
]

MOCK_DATAFLOWS_FOR_PIVOT_TEST = {
    "TEST_DATAFLOW": {
        "id": "TEST_DATAFLOW",
        "name": "Test Dataflow",
        "description": "A dataflow for testing pivoting.",
        "structureRef": {"id": "DSD_TEST"},
        "agencyID": "IMF.STA",
        "presentations": [
            {
                "presentation_title": "Indicators by Country",
                "presentation_description": "Data pivoted by indicator for each country.",
            }
        ],
    }
}

MOCK_CONCEPTSCHEMES = {}
MOCK_DATASET_ID_MAPPING = {}
MOCK_IMF_COUNTRY_MAP = {}


@pytest.fixture
def imf_metadata(monkeypatch):
    """Provide an isolated ImfMetadata instance with canned data."""
    monkeypatch.setattr(md.ImfMetadata, "_instance", None)
    monkeypatch.setattr(md.ImfMetadata, "_load_from_cache", lambda self: True)

    meta = md.ImfMetadata()
    meta.dataflows = {d["id"]: d for d in MOCK_SDMX_CHUNKS_DATAFLOWS}
    meta.dataflow_groups = MOCK_DATAFLOW_GROUPS
    return meta


def test_parse_query_variants(imf_metadata):
    assert imf_metadata._parse_query("gold") == [["gold"]]
    assert imf_metadata._parse_query('"central bank"') == [["central bank"]]
    assert imf_metadata._parse_query("gold + reserves") == [["gold", "reserves"]]
    assert imf_metadata._parse_query("gold | reserves") == [["gold"], ["reserves"]]
    assert imf_metadata._parse_query('gold + reserves | "central bank"') == [
        ["gold", "reserves"],
        ["central bank"],
    ]
    assert imf_metadata._parse_query("") == []
    assert imf_metadata._parse_query("   ") == []


def test_search_dataflows_by_keywords(imf_metadata):
    results = imf_metadata.search_dataflows("gold")
    ids = {df["id"] for group in results for df in group.get("dataflows", [])}
    assert "DATAFLOW_A" in ids
    assert "DATAFLOW_GOLD_STATISTICS" in ids


def test_search_dataflows_or_operator(imf_metadata):
    results = imf_metadata.search_dataflows("DATAFLOW_A | DATAFLOW_B")
    ids = {df["id"] for group in results for df in group.get("dataflows", [])}
    assert ids == {"DATAFLOW_A", "DATAFLOW_B"}


def test_search_dataflows_phrase(imf_metadata):
    results = imf_metadata.search_dataflows('"central bank"')
    ids = {df["id"] for group in results for df in group.get("dataflows", [])}
    assert "DATAFLOW_CENTRAL_BANK" in ids


@pytest.fixture
def mock_imf_query_builder():
    """Return an ImfQueryBuilder wired with canned metadata."""
    with patch("openbb_imf.utils.query_builder.ImfMetadata") as MockMetadata:
        mock_metadata_instance = MockMetadata.return_value

        dataflows_dict = {d["id"]: d for d in MOCK_SDMX_CHUNKS_DATAFLOWS}
        dataflows_dict.update(MOCK_DATAFLOWS_FOR_PIVOT_TEST)
        mock_metadata_instance.dataflows = dataflows_dict

        datastructures_dict = {d["id"]: d for d in MOCK_DATASTRUCTURES}
        mock_metadata_instance.datastructures = datastructures_dict

        mock_metadata_instance.conceptschemes = MOCK_CONCEPTSCHEMES
        mock_metadata_instance.dataflow_groups = MOCK_DATAFLOW_GROUPS
        mock_metadata_instance.dataset_id_mapping = MOCK_DATASET_ID_MAPPING
        mock_metadata_instance.imf_country_map = MOCK_IMF_COUNTRY_MAP

        yield ImfQueryBuilder()


MOCK_XML_RESPONSE = dedent(
    """
    <message:StructureSpecificData
        xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message"
        xmlns:common="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/common"
        xmlns:ss="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/data/structurespecific">
        <message:DataSet>
            <Series COUNTRY="US" INDICATOR="GDP">
                <Obs TIME_PERIOD="2020" OBS_VALUE="10" />
                <Obs TIME_PERIOD="2021" OBS_VALUE="12" />
            </Series>
            <Series COUNTRY="US" INDICATOR="CPI">
                <Obs TIME_PERIOD="2020" OBS_VALUE="100" />
                <Obs TIME_PERIOD="2021" OBS_VALUE="120" />
            </Series>
        </message:DataSet>
    </message:StructureSpecificData>
    """
)


@pytest.fixture
def mock_imf_query_builder_with_pivot_data():
    """Return an ImfQueryBuilder with request mocked to return canned XML."""
    with (
        patch("openbb_imf.utils.query_builder.ImfMetadata") as MockMetadata,
        patch("openbb_core.provider.utils.helpers.make_request") as mock_make_request,
    ):
        mock_metadata_instance = MockMetadata.return_value

        dataflows_dict = {d["id"]: d for d in MOCK_SDMX_CHUNKS_DATAFLOWS}
        dataflows_dict.update(MOCK_DATAFLOWS_FOR_PIVOT_TEST)
        mock_metadata_instance.dataflows = dataflows_dict

        datastructures_dict = {d["id"]: d for d in MOCK_DATASTRUCTURES}
        mock_metadata_instance.datastructures = datastructures_dict

        mock_metadata_instance.conceptschemes = MOCK_CONCEPTSCHEMES
        mock_metadata_instance.dataflow_groups = MOCK_DATAFLOW_GROUPS

        mock_metadata_instance.get_dataflow_parameters.return_value = {
            "COUNTRY": [{"value": "US", "label": "United States"}],
            "INDICATOR": [
                {"value": "GDP", "label": "Gross Domestic Product"},
                {"value": "CPI", "label": "Consumer Price Index"},
            ],
            "TIME_PERIOD": [
                {"value": "2020", "label": "2020"},
                {"value": "2021", "label": "2021"},
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = MOCK_XML_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_make_request.return_value = mock_response

        builder = ImfQueryBuilder()
        yield builder


def test_fetch_data_structure(mock_imf_query_builder_with_pivot_data):
    builder = mock_imf_query_builder_with_pivot_data
    result = builder.fetch_data(
        "TEST_DATAFLOW", COUNTRY="US", INDICATOR="GDP+CPI", _skip_validation=True
    )

    assert "data" in result and "metadata" in result
    df = pd.DataFrame(result["data"])

    expected_cols = {
        "COUNTRY",
        "country_code",
        "INDICATOR",
        "INDICATOR_code",
        "series_id",
        "TIME_PERIOD",
        "OBS_VALUE",
    }
    assert expected_cols.issubset(set(df.columns))
    assert set(df["INDICATOR_code"]) == {"GDP", "CPI"}


def test_fetch_data_time_periods(mock_imf_query_builder_with_pivot_data):
    builder = mock_imf_query_builder_with_pivot_data
    result = builder.fetch_data(
        "TEST_DATAFLOW", COUNTRY="US", INDICATOR="GDP+CPI", _skip_validation=True
    )

    df = pd.DataFrame(result["data"])
    assert set(df["TIME_PERIOD"]) == {"2020-12-31", "2021-12-31"}


def test_strict_error_missing_dataflow(mock_imf_query_builder):
    builder = mock_imf_query_builder
    with pytest.raises(ValueError, match="Dataflow 'MISSING' not found"):
        builder.build_url("MISSING")


@pytest.fixture
def base_metadata(monkeypatch):
    """Build an isolated ``ImfMetadata`` with a flexible default catalog."""
    monkeypatch.setattr(md.ImfMetadata, "_instance", None)
    monkeypatch.setattr(md.ImfMetadata, "_load_from_cache", lambda self: True)
    meta = md.ImfMetadata()
    meta.dataflows = {
        "FLOW": {
            "id": "FLOW",
            "agencyID": "IMF.STA",
            "name": "Flow",
            "description": "desc",
            "structureRef": {"id": "DSD_FLOW"},
        },
        "NO_AGENCY": {
            "id": "NO_AGENCY",
            "name": "No Agency",
            "structureRef": {"id": "DSD_FLOW"},
        },
        "BAD_DSD": {
            "id": "BAD_DSD",
            "agencyID": "IMF.STA",
            "name": "Bad",
            "structureRef": {"id": "DSD_MISSING"},
        },
    }
    meta.datastructures = {
        "DSD_FLOW": {
            "id": "DSD_FLOW",
            "agencyID": "IMF.STA",
            "dimensions": [
                {"id": "COUNTRY", "position": 0, "conceptRef": {"id": "COUNTRY"}},
                {"id": "FREQUENCY", "position": 1, "conceptRef": {"id": "FREQ"}},
                {"id": "INDICATOR", "position": 2, "conceptRef": {"id": "INDICATOR"}},
            ],
            "attributes": [],
        }
    }
    meta._codelist_cache = {
        "CL_UNIT_MULT": {"3": "Thousands", "6": "Millions"},
        "CL_UNIT": {"USD": "US dollar", "EUR": "Euro"},
    }
    return meta


@pytest.fixture
def builder(base_metadata):  # noqa: ARG001
    """Construct an ``ImfQueryBuilder`` against the canned metadata."""
    return ImfQueryBuilder()


class TestBuildUrl:
    """Tests covering ``ImfQueryBuilder.build_url``."""

    def test_unknown_dataflow_raises(self, builder):
        """Unknown dataflow surfaces as ``ValueError``."""
        with pytest.raises(ValueError, match="Dataflow 'MISSING' not found"):
            builder.build_url("MISSING")

    def test_missing_dsd_raises(self, builder):
        """Missing data-structure reference raises a clear error."""
        with pytest.raises(ValueError, match="Data structure not found"):
            builder.build_url("BAD_DSD")

    def test_missing_agency_raises(self, builder, monkeypatch):
        """Missing agency id raises a clear error."""
        monkeypatch.setitem(builder.metadata.dataflows["FLOW"], "agencyID", None)
        with pytest.raises(ValueError, match="Agency ID not found"):
            builder.build_url("FLOW", INDICATOR="GDP")

    def test_lower_case_dimension_keys_matched(self, builder):
        """Lower-case kwargs match against upper-case dimension IDs."""
        url = builder.build_url("FLOW", country="USA", frequency="A", indicator="GDP")
        assert "/USA.A.GDP" in url

    def test_list_value_uses_plus_join(self, builder):
        """A ``list`` dimension value joins with ``+``."""
        url = builder.build_url("FLOW", INDICATOR=["GDP", "CPI"], COUNTRY="USA")
        assert "USA.*.GDP+CPI" in url

    def test_long_value_collapses_to_wildcard(self, builder):
        """Values longer than 1500 chars become ``*`` in the key segment."""
        big = "X" * 1600
        url = builder.build_url("FLOW", INDICATOR=big, COUNTRY="USA")
        assert "/USA.*.*" in url

    def test_wildcard_value_kept_as_star(self, builder):
        """An explicit ``*`` value stays ``*``."""
        url = builder.build_url("FLOW", INDICATOR="*", COUNTRY="USA")
        assert "/USA.*.*" in url

    def test_extra_query_params_appended(self, builder):
        """Unmatched kwargs become query-string parameters."""
        url = builder.build_url("FLOW", INDICATOR="GDP", custom="value")
        assert "custom=value" in url

    def test_annual_frequency_uses_year_format(self, builder):
        """Annual frequency formats time period as ``YYYY-01-01``."""
        url = builder.build_url(
            "FLOW",
            COUNTRY="USA",
            INDICATOR="GDP",
            FREQUENCY="A",
            start_date="2020",
            end_date="2022",
        )
        assert "ge:2020-01-01" in url
        assert "le:2023-01-01" in url

    def test_monthly_frequency_increments_end_month(self, builder):
        """Monthly frequency bumps the end month forward by one."""
        url = builder.build_url(
            "FLOW",
            COUNTRY="USA",
            INDICATOR="GDP",
            FREQUENCY="M",
            start_date="2020-01",
            end_date="2020-12",
        )
        assert "ge:2020-01-01" in url
        assert "le:2021-01-01" in url

    def test_monthly_end_wraps_year(self, builder):
        """When the end month is December, the year is advanced."""
        url = builder.build_url(
            "FLOW",
            COUNTRY="USA",
            INDICATOR="GDP",
            FREQUENCY="Q",
            start_date="2020-06",
            end_date="2020-12",
        )
        assert "le:2021-01-01" in url

    def test_limit_appends_last_n_observations(self, builder):
        """A positive ``limit`` appends ``lastNObservations``."""
        url = builder.build_url("FLOW", COUNTRY="USA", limit=5)
        assert "lastNObservations=5" in url

    def test_no_limit_when_zero(self, builder):
        """A non-positive limit is ignored."""
        url = builder.build_url("FLOW", COUNTRY="USA", limit=0)
        assert "lastNObservations" not in url


class TestValidateDimensionConstraints:
    """Tests for ``ImfQueryBuilder.validate_dimension_constraints``."""

    def _patch_builder(self, builder, dim_order, options_for, last_resp=None):
        """Patch ``ImfParamsBuilder`` to return canned data."""
        from openbb_imf.utils import progressive_helper as ph

        class FakeBuilder:
            def __init__(self, dataflow_id):  # noqa: ARG002
                self._dims = list(dim_order)
                self._selections: dict = {d: None for d in dim_order}
                self._last_constraints_response = last_resp or {}

            def _get_dimensions_in_order(self):
                return list(self._dims)

            def get_options_for_dimension(self, dim_id):
                return options_for.get(dim_id, [])

            def set_dimension(self, tup):
                self._selections[tup[0]] = tup[1]
                return self._selections

        return patch.object(ph, "ImfParamsBuilder", FakeBuilder)

    def test_unknown_value_raises(self, builder):
        """An invalid value raises ``ValueError``."""
        ctx = self._patch_builder(
            builder,
            ["COUNTRY", "INDICATOR"],
            {
                "COUNTRY": [{"value": "USA", "label": "USA"}],
                "INDICATOR": [{"value": "GDP", "label": "GDP"}],
            },
        )
        with ctx:
            with pytest.raises(ValueError, match="Invalid value"):
                builder.validate_dimension_constraints(
                    "FLOW", COUNTRY="USA", INDICATOR="ZZZ"
                )

    def test_comma_separated_values_parsed(self, builder):
        """Comma-separated user values are split before validation."""
        ctx = self._patch_builder(
            builder,
            ["INDICATOR"],
            {
                "INDICATOR": [
                    {"value": "GDP", "label": "G"},
                    {"value": "CPI", "label": "C"},
                ]
            },
        )
        with ctx:
            builder.validate_dimension_constraints("FLOW", INDICATOR="GDP, CPI")

    def test_plus_separated_values_parsed(self, builder):
        """Plus-separated user values are split before validation."""
        ctx = self._patch_builder(
            builder,
            ["INDICATOR"],
            {
                "INDICATOR": [
                    {"value": "GDP", "label": "G"},
                    {"value": "CPI", "label": "C"},
                ]
            },
        )
        with ctx:
            builder.validate_dimension_constraints("FLOW", INDICATOR="GDP+CPI")

    def test_list_value_validated(self, builder):
        """List values are validated unchanged."""
        ctx = self._patch_builder(
            builder,
            ["INDICATOR"],
            {"INDICATOR": [{"value": "GDP", "label": "G"}]},
        )
        with ctx:
            builder.validate_dimension_constraints("FLOW", INDICATOR=["GDP"])

    def test_wildcard_skips_value_check(self, builder):
        """A ``*`` value skips per-value validation."""
        ctx = self._patch_builder(
            builder,
            ["INDICATOR"],
            {"INDICATOR": [{"value": "GDP", "label": "G"}]},
        )
        with ctx:
            builder.validate_dimension_constraints("FLOW", INDICATOR="*")

    def test_oversized_value_skips_check(self, builder):
        """Values whose joined length exceeds 2000 chars skip validation."""
        ctx = self._patch_builder(
            builder,
            ["INDICATOR"],
            {"INDICATOR": [{"value": "A", "label": "A"}]},
        )
        long_value = "+".join("V" * 200 for _ in range(40))
        with ctx:
            builder.validate_dimension_constraints("FLOW", INDICATOR=long_value)

    def test_empty_user_value_skipped(self, builder):
        """Empty / falsy dimension values are silently skipped."""
        ctx = self._patch_builder(
            builder,
            ["INDICATOR"],
            {"INDICATOR": [{"value": "GDP", "label": "G"}]},
        )
        with ctx:
            builder.validate_dimension_constraints("FLOW", INDICATOR="")
            builder.validate_dimension_constraints("FLOW", INDICATOR=None)

    def test_keyerror_emits_openbb_warning(self, builder):
        """A ``KeyError`` while validating emits an ``OpenBBWarning``."""
        from openbb_core.app.model.abstract.warning import OpenBBWarning
        from openbb_imf.utils import progressive_helper as ph

        class Boom:
            def __init__(self, dataflow_id):  # noqa: ARG002
                raise KeyError("nope")

        with patch.object(ph, "ImfParamsBuilder", Boom):
            with pytest.warns(OpenBBWarning, match="Could not validate"):
                builder.validate_dimension_constraints("FLOW", COUNTRY="USA")

    def test_time_period_outside_range_raises(self, builder):
        """A start_date past the available range raises ``ValueError``."""
        last_resp = {
            "full_response": {
                "data": {
                    "contentConstraints": [
                        {
                            "annotations": [
                                {"id": "time_period_start", "title": "2010-01"},
                                {"id": "time_period_end", "title": "2020-12"},
                            ]
                        }
                    ]
                }
            }
        }
        ctx = self._patch_builder(
            builder,
            ["COUNTRY"],
            {"COUNTRY": [{"value": "USA", "label": "USA"}]},
            last_resp=last_resp,
        )
        with ctx:
            with pytest.raises(ValueError, match="after the latest available"):
                builder.validate_dimension_constraints(
                    "FLOW", COUNTRY="USA", start_date="2025-01"
                )
            with pytest.raises(ValueError, match="before the earliest available"):
                builder.validate_dimension_constraints(
                    "FLOW", COUNTRY="USA", end_date="2000-01"
                )

    def test_time_period_from_data_constraints(self, builder):
        """The data-constraints branch is honoured when content-constraints empty."""
        last_resp = {
            "full_response": {
                "data": {
                    "dataConstraints": [
                        {
                            "annotations": [
                                {"id": "time_period_start", "title": "2010-01"},
                                {"id": "time_period_end", "title": "2020-12"},
                            ]
                        }
                    ]
                }
            }
        }
        ctx = self._patch_builder(
            builder,
            ["COUNTRY"],
            {"COUNTRY": [{"value": "USA", "label": "USA"}]},
            last_resp=last_resp,
        )
        with ctx:
            with pytest.raises(ValueError, match="after the latest available"):
                builder.validate_dimension_constraints(
                    "FLOW", COUNTRY="USA", start_date="2025-01"
                )


class TestExtractDatasetAttributes:
    """Tests for ``_extract_dataset_attributes_from_cache``."""

    def test_attributes_propagated(self, builder, monkeypatch):
        """Optional attributes present on the dataflow flow into the result."""
        monkeypatch.setitem(builder.metadata.dataflows["FLOW"], "publisher", "IMF")
        monkeypatch.setitem(builder.metadata.dataflows["FLOW"], "license", "CC")
        attrs = builder._extract_dataset_attributes_from_cache("FLOW")
        assert attrs["publisher"] == "IMF"
        assert attrs["license"] == "CC"
        assert attrs["dataflow_id"] == "FLOW"
        assert attrs["dataflow_name"] == "Flow"
        assert attrs["dataflow_description"] == "desc"


class TestExtractAttributeValue:
    """Tests for ``_extract_attribute_value``."""

    def test_int_lookup_dict(self, builder):
        """An ``int`` value indexes into ``values`` and returns the ``en`` key."""
        attr_def = {"values": [{"en": "Yes", "id": "Y"}]}
        assert builder._extract_attribute_value(0, attr_def) == "Yes"

    def test_int_lookup_no_en(self, builder):
        """Fallback to ``name``, then ``id`` when ``en`` is missing."""
        attr_def = {"values": [{"id": "Y"}]}
        assert builder._extract_attribute_value(0, attr_def) == "Y"

    def test_int_lookup_scalar(self, builder):
        """An ``int`` indexing into a non-dict scalar returns the scalar."""
        attr_def = {"values": ["plain"]}
        assert builder._extract_attribute_value(0, attr_def) == "plain"

    def test_list_int(self, builder):
        """A list of ints uses the first entry as an index."""
        attr_def = {"values": [{"en": "Yes"}]}
        assert builder._extract_attribute_value([0], attr_def) == "Yes"

    def test_list_int_scalar(self, builder):
        """A list of ints pointing at a scalar returns it."""
        attr_def = {"values": ["plain"]}
        assert builder._extract_attribute_value([0], attr_def) == "plain"

    def test_list_dict_first(self, builder):
        """A list of dicts returns the first dict's localized value."""
        assert builder._extract_attribute_value([{"en": "Apple"}], {}) == "Apple"

    def test_list_other_first(self, builder):
        """A list of scalars returns the first scalar."""
        assert builder._extract_attribute_value(["x"], {}) == "x"

    def test_dict_value(self, builder):
        """A bare dict returns its localized value."""
        assert builder._extract_attribute_value({"en": "EN", "name": "N"}, {}) == "EN"

    def test_passthrough(self, builder):
        """Other scalar values are returned unchanged."""
        assert builder._extract_attribute_value("plain", {}) == "plain"


class TestExtractDatasetAttributesFull:
    """Tests for ``_extract_dataset_attributes`` (live structure path)."""

    def test_full_structure_with_topics(self, builder):
        """Structure attributes (TOPIC_DATASET/UPDATE_DATE/etc.) flow through."""
        builder.metadata._codelist_cache["CL_TOPIC"] = {"T1": "Trade", "T2": "Money"}
        structure = {
            "attributes": {
                "dataSet": [
                    {"id": "TOPIC_DATASET", "values": [{"ids": ["T1", "T2"]}]},
                    {"id": "KEYWORDS_DATASET", "values": [{"en": "kw"}]},
                    {"id": "UPDATE_DATE"},
                    {"id": "PUBLICATION_DATE"},
                    {"id": "PUBLISHER", "values": [{"en": "IMF"}]},
                    {"id": "UNRELATED"},
                ]
            }
        }
        json_data = {
            "dataSets": [
                {
                    "attributes": [
                        0,
                        0,
                        "2024-05-01.123456789",
                        "2023-01-01",
                        0,
                        "ignore",
                    ]
                }
            ]
        }
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert attrs["topics"] == ["Trade", "Money"]
        assert attrs["keywords"] == "kw"
        assert "last_updated" in attrs
        assert attrs["publication_date"] == "2023-01-01"
        assert attrs["publisher"] == "IMF"

    def test_topic_dataset_via_int_id(self, builder):
        """A TOPIC_DATASET that points at an ``id`` dict still resolves."""
        builder.metadata._codelist_cache["CL_TOPIC"] = {"T1": "Trade"}
        structure = {
            "attributes": {
                "dataSet": [
                    {"id": "TOPIC_DATASET", "values": [{"id": "T1"}]},
                ]
            }
        }
        json_data = {"dataSets": [{"attributes": [0]}]}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert attrs["topics"] == ["Trade"]

    def test_topic_dataset_via_list_of_ints(self, builder):
        """A TOPIC_DATASET that's a list of ints resolves via index lookup."""
        builder.metadata._codelist_cache["CL_TOPIC"] = {"T1": "Trade"}
        structure = {
            "attributes": {
                "dataSet": [
                    {"id": "TOPIC_DATASET", "values": [{"id": "T1"}]},
                ]
            }
        }
        json_data = {"dataSets": [{"attributes": [[0]]}]}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert attrs["topics"] == ["Trade"]

    def test_topic_dataset_string_list_passes_through(self, builder):
        """A TOPIC_DATASET that arrives as a list of strings is kept as-is."""
        builder.metadata._codelist_cache.pop("CL_TOPIC", None)
        structure = {"attributes": {"dataSet": [{"id": "TOPIC_DATASET"}]}}
        json_data = {"dataSets": [{"attributes": [["XYZ"]]}]}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert attrs["topics"] == ["XYZ"]

    def test_no_dataset_attributes_returns_top_level(self, builder):
        """When ``dataSets`` is empty the function returns just the dataflow-level dict."""
        structure = {"attributes": {"dataSet": [{"id": "PUBLISHER"}]}}
        json_data = {"dataSets": []}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert attrs["dataflow_id"] == "FLOW"
        assert "publisher" not in attrs

    def test_update_date_with_decimal_pads_fractional(self, builder):
        """An UPDATE_DATE with a short fractional second is padded out."""
        structure = {
            "attributes": {
                "dataSet": [
                    {"id": "UPDATE_DATE"},
                ]
            }
        }
        json_data = {"dataSets": [{"attributes": ["2024-01-01T00:00:00.12"]}]}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert "last_updated" in attrs

    def test_unrelated_attr_id_skipped(self, builder):
        """An attr_id not in the recognised list is ignored without raising."""
        structure = {
            "attributes": {
                "dataSet": [{"id": "OTHER"}],
            }
        }
        json_data = {"dataSets": [{"attributes": [1]}]}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert "other" not in attrs

    def test_dataflow_obj_keys_propagated(self, builder, monkeypatch):
        """Top-level dataflow-object keys flow into the result."""
        monkeypatch.setitem(builder.metadata.dataflows["FLOW"], "publisher", "IMF")
        attrs = builder._extract_dataset_attributes({}, {"dataSets": []}, "FLOW")
        assert attrs["publisher"] == "IMF"

    def test_topic_dataset_int_via_scalar_value(self, builder):
        """A TOPIC_DATASET int that maps to a non-dict value in ``values`` is appended."""
        builder.metadata._codelist_cache["CL_TOPIC"] = {"T": "Trade"}
        structure = {
            "attributes": {
                "dataSet": [
                    {"id": "TOPIC_DATASET", "values": ["T"]},
                ]
            }
        }
        json_data = {"dataSets": [{"attributes": [0]}]}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert attrs["topics"] == ["Trade"]

    def test_topic_dataset_list_with_scalar_value(self, builder):
        """A list[int] pointing at a scalar in ``values`` collects the scalar."""
        builder.metadata._codelist_cache["CL_TOPIC"] = {"T": "Trade"}
        structure = {
            "attributes": {
                "dataSet": [
                    {"id": "TOPIC_DATASET", "values": ["T"]},
                ]
            }
        }
        json_data = {"dataSets": [{"attributes": [[0]]}]}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert attrs["topics"] == ["Trade"]

    def test_topic_dataset_no_codelist_returns_raw(self, builder):
        """Without ``CL_TOPIC`` cached, the raw topic codes are returned."""
        builder.metadata._codelist_cache.pop("CL_TOPIC", None)
        structure = {
            "attributes": {
                "dataSet": [
                    {"id": "TOPIC_DATASET", "values": [{"id": "T"}]},
                ]
            }
        }
        json_data = {"dataSets": [{"attributes": [0]}]}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert attrs["topics"] == ["T"]

    def test_topic_dataset_list_with_ids_dict(self, builder):
        """A list of ints can resolve to ``ids`` dict in ``values``."""
        builder.metadata._codelist_cache["CL_TOPIC"] = {"T1": "Trade"}
        structure = {
            "attributes": {
                "dataSet": [
                    {"id": "TOPIC_DATASET", "values": [{"ids": ["T1"]}]},
                ]
            }
        }
        json_data = {"dataSets": [{"attributes": [[0]]}]}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert attrs["topics"] == ["Trade"]

    def test_update_date_no_fractional_passes_through(self, builder):
        """UPDATE_DATE without a fractional component is recorded as-is."""
        structure = {"attributes": {"dataSet": [{"id": "UPDATE_DATE"}]}}
        json_data = {"dataSets": [{"attributes": ["2024-01-01"]}]}
        attrs = builder._extract_dataset_attributes(structure, json_data, "FLOW")
        assert attrs.get("last_updated") == "2024-01-01"


class TestExtractIndicatorMetadata:
    """Tests for ``_extract_indicator_metadata``."""

    def test_indicator_metadata_full_payload(self, builder):
        """A full payload populates trade_flow / valuation / unit / topic / key_indicator."""
        builder.metadata._codelist_cache.update(
            {
                "CL_TRADE_FLOW": {"M": "Imports"},
                "CL_VALUATION": {"FOB": "Free on Board"},
                "CL_UNIT": {"USD": "US dollar"},
                "CL_TOPIC": {"T1": "Trade"},
            }
        )
        structure = {
            "dimensions": {
                "series": [
                    {"id": "INDICATOR", "values": [{"id": "GDP"}]},
                ]
            },
            "attributes": {
                "dimensionGroup": [
                    {"id": "SERIES_NAME"},
                    {"id": "TRADE_FLOW", "values": [{"id": "M"}]},
                    {"id": "VALUATION", "values": [{"id": "FOB"}]},
                    {"id": "UNIT", "values": [{"id": "USD"}]},
                    {"id": "TOPIC", "values": [{"id": "T1"}]},
                    {"id": "KEY_INDICATOR"},
                ]
            },
        }
        dim_group_attrs = {
            ":0:": [["GDP series"], 0, 0, 0, 0, ["true"]],
        }
        meta = builder._extract_indicator_metadata(dim_group_attrs, structure)
        entry = meta["GDP"]
        assert entry["series_name"] == "GDP series"
        assert entry["trade_flow"] == "Imports"
        assert entry["valuation"] == "Free on Board"
        assert entry["unit"] == "US dollar"
        assert entry["topic"] == ["Trade"]
        assert entry["key_indicator"] is True

    def test_unit_special_aggregate(self, builder):
        """Special aggregate unit codes (``ALL``, ``W0``...) are passed through."""
        structure = {
            "dimensions": {"series": [{"id": "INDICATOR", "values": [{"id": "GDP"}]}]},
            "attributes": {
                "dimensionGroup": [
                    {"id": "UNIT", "values": [{"id": "ALL"}]},
                ]
            },
        }
        dim_group_attrs = {":0:": [0]}
        meta = builder._extract_indicator_metadata(dim_group_attrs, structure)
        assert meta["GDP"]["unit"] == "ALL"

    def test_unit_without_codelist(self, builder):
        """Without ``CL_UNIT`` cached, the raw code is used."""
        builder.metadata._codelist_cache.pop("CL_UNIT", None)
        structure = {
            "dimensions": {"series": [{"id": "INDICATOR", "values": [{"id": "GDP"}]}]},
            "attributes": {
                "dimensionGroup": [
                    {"id": "UNIT", "values": [{"id": "XYZ"}]},
                ]
            },
        }
        dim_group_attrs = {":0:": [0]}
        meta = builder._extract_indicator_metadata(dim_group_attrs, structure)
        assert meta["GDP"]["unit"] == "XYZ"

    def test_no_indicator_dim_returns_empty(self, builder):
        """If no indicator dimension exists in the structure, return ``{}``."""
        structure = {
            "dimensions": {"series": [{"id": "COUNTRY"}]},
            "attributes": {"dimensionGroup": []},
        }
        assert builder._extract_indicator_metadata({}, structure) == {}

    def test_indicator_idx_non_integer_skipped(self, builder):
        """A non-integer key part is skipped without raising."""
        structure = {
            "dimensions": {"series": [{"id": "INDICATOR", "values": [{"id": "GDP"}]}]},
            "attributes": {"dimensionGroup": []},
        }
        assert builder._extract_indicator_metadata({":not_int:": []}, structure) == {}

    def test_indicator_idx_out_of_range_skipped(self, builder):
        """A position past the dimension values is skipped silently."""
        structure = {
            "dimensions": {"series": [{"id": "INDICATOR", "values": [{"id": "GDP"}]}]},
            "attributes": {"dimensionGroup": []},
        }
        assert builder._extract_indicator_metadata({":99:": []}, structure) == {}

    def test_topic_via_ids_list(self, builder):
        """A TOPIC dim_group value with ``ids`` collects each topic code."""
        builder.metadata._codelist_cache.update({"CL_TOPIC": {"T1": "Trade"}})
        structure = {
            "dimensions": {"series": [{"id": "INDICATOR", "values": [{"id": "GDP"}]}]},
            "attributes": {
                "dimensionGroup": [
                    {"id": "TOPIC", "values": [{"ids": ["T1"]}]},
                ]
            },
        }
        meta = builder._extract_indicator_metadata({":0:": [0]}, structure)
        assert meta["GDP"]["topic"] == ["Trade"]

    def test_trade_flow_without_codelist(self, builder):
        """A ``TRADE_FLOW`` value without ``CL_TRADE_FLOW`` cached falls back to the code."""
        builder.metadata._codelist_cache.pop("CL_TRADE_FLOW", None)
        structure = {
            "dimensions": {"series": [{"id": "INDICATOR", "values": [{"id": "GDP"}]}]},
            "attributes": {
                "dimensionGroup": [
                    {"id": "TRADE_FLOW", "values": [{"id": "M"}]},
                ]
            },
        }
        meta = builder._extract_indicator_metadata({":0:": [0]}, structure)
        assert meta["GDP"]["trade_flow"] == "M"

    def test_valuation_without_codelist(self, builder):
        """A ``VALUATION`` value without ``CL_VALUATION`` cached falls back to the code."""
        builder.metadata._codelist_cache.pop("CL_VALUATION", None)
        structure = {
            "dimensions": {"series": [{"id": "INDICATOR", "values": [{"id": "GDP"}]}]},
            "attributes": {
                "dimensionGroup": [
                    {"id": "VALUATION", "values": [{"id": "FOB"}]},
                ]
            },
        }
        meta = builder._extract_indicator_metadata({":0:": [0]}, structure)
        assert meta["GDP"]["valuation"] == "FOB"

    def test_topic_without_codelist_returns_raw_codes(self, builder):
        """Without ``CL_TOPIC`` cached, topic codes are returned verbatim."""
        builder.metadata._codelist_cache.pop("CL_TOPIC", None)
        structure = {
            "dimensions": {"series": [{"id": "INDICATOR", "values": [{"id": "GDP"}]}]},
            "attributes": {
                "dimensionGroup": [
                    {"id": "TOPIC", "values": [{"id": "T1"}]},
                ]
            },
        }
        meta = builder._extract_indicator_metadata({":0:": [0]}, structure)
        assert meta["GDP"]["topic"] == ["T1"]

    def test_empty_key_skipped(self, builder):
        """A blank ``group_key`` is skipped via the ``not indicator_idx_str`` guard."""
        structure = {
            "dimensions": {"series": [{"id": "INDICATOR", "values": [{"id": "GDP"}]}]},
            "attributes": {"dimensionGroup": []},
        }
        assert builder._extract_indicator_metadata({"::": []}, structure) == {}

    def test_short_group_key_skipped(self, builder):
        """A group_key shorter than the indicator-dim position is skipped."""
        structure = {
            "dimensions": {
                "series": [
                    {"id": "COUNTRY"},
                    {"id": "INDICATOR", "values": [{"id": "GDP"}]},
                ]
            },
            "attributes": {"dimensionGroup": []},
        }
        # group_key has 1 part, indicator at position 1 -> skipped
        assert builder._extract_indicator_metadata({":0:": []}, structure) == {}

    def test_empty_indicator_idx_string_skipped(self, builder):
        """An empty string at the indicator-dim position is skipped."""
        structure = {
            "dimensions": {
                "series": [
                    {"id": "COUNTRY"},
                    {"id": "INDICATOR", "values": [{"id": "GDP"}]},
                ]
            },
            "attributes": {"dimensionGroup": []},
        }
        # ":0::X".strip(":") -> "0::X", parts=["0", "", "X"]; position 1 -> "" -> skipped
        assert builder._extract_indicator_metadata({":0::X": []}, structure) == {}


class TestParseAttributes:
    """Tests for ``_parse_attributes`` helper."""

    def test_passthrough_string(self, builder):
        """Plain string values are returned as-is."""
        result = builder._parse_attributes(["X"], [{"id": "A"}])
        assert result == {"A": "X"}

    def test_int_index_lookup(self, builder):
        """An integer value is treated as an index into ``values``."""
        result = builder._parse_attributes(
            [1], [{"id": "A", "values": [{"id": "X"}, {"id": "Y"}]}]
        )
        assert result == {"A": "Y"}

    def test_none_skipped(self, builder):
        """``None`` values are skipped without raising."""
        result = builder._parse_attributes([None, "Z"], [{"id": "A"}, {"id": "B"}])
        assert result == {"B": "Z"}

    def test_extra_value_dropped(self, builder):
        """Extra values past the definition list are silently dropped."""
        result = builder._parse_attributes(["X", "Y"], [{"id": "A"}])
        assert result == {"A": "X"}


class TestBuildTranslationMaps:
    """Tests for ``_build_translation_maps``."""

    def test_from_dataflow_parameters(self, builder, monkeypatch):
        """Translation maps prefer ``get_dataflow_parameters`` output."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {"COUNTRY": [{"value": "USA", "label": "United States"}]},
        )
        maps = builder._build_translation_maps({}, "FLOW")
        assert maps["COUNTRY"] == {"USA": "United States"}

    def test_falls_back_to_structure_values(self, builder, monkeypatch):
        """When ``get_dataflow_parameters`` blows up, the structure path is used."""

        def boom(_df):
            raise RuntimeError("nope")

        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", boom)
        structure = {
            "dimensions": {
                "series": [
                    {
                        "id": "COUNTRY",
                        "values": [
                            {"id": "US", "name": "United States"},
                            {"id": "ZZ", "name": "ZZ"},  # name == code -> skipped
                        ],
                    }
                ],
                "observation": [],
            }
        }
        maps = builder._build_translation_maps(structure, "FLOW")
        assert maps["COUNTRY"]["US"] == "United States"
        assert "ZZ" not in maps.get("COUNTRY", {})

    def test_dim_without_id_skipped(self, builder, monkeypatch):
        """Series dims missing ``id`` are skipped."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        structure = {"dimensions": {"series": [{"values": [{"id": "X", "name": "Y"}]}]}}
        maps = builder._build_translation_maps(structure, "FLOW")
        assert maps == {}

    def test_empty_values_skipped(self, builder, monkeypatch):
        """Dims with empty ``values`` are skipped."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        structure = {"dimensions": {"series": [{"id": "COUNTRY", "values": []}]}}
        maps = builder._build_translation_maps(structure, "FLOW")
        assert maps == {}


class TestFetchDataXml:
    """Tests for the XML parsing branch of ``fetch_data``."""

    XML_TEMPLATE = dedent(
        """
        <message:StructureSpecificData
            xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message"
            xmlns:common="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/common"
            xmlns:ss="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/data/structurespecific">
            <message:DataSet>
                <Series COUNTRY="USA" INDICATOR="GDP" SCALE="6" UNIT="USD" TYPE_OF_TRANSFORMATION="Index">
                    <Obs TIME_PERIOD="2020" OBS_VALUE="100" />
                    <Obs TIME_PERIOD="2021" OBS_VALUE="" />
                </Series>
                <Series COUNTRY="USA" INDICATOR="CPI" SCALE="bad">
                    <Obs TIME_PERIOD="2020" OBS_VALUE="42" />
                </Series>
            </message:DataSet>
        </message:StructureSpecificData>
        """
    )

    def _xml_response(self, text=None):
        """Build a fake ``requests.Response`` carrying ``text``."""
        mock_response = MagicMock()
        mock_response.text = text if text is not None else self.XML_TEMPLATE
        mock_response.raise_for_status.return_value = None
        return mock_response

    def test_request_exception_raises_openbb_error(self, builder):
        """A networking ``RequestException`` is wrapped in ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from requests.exceptions import RequestException

        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            side_effect=RequestException("network down"),
        ):
            with pytest.raises(OpenBBError, match="An error occurred"):
                builder.fetch_data(
                    "FLOW", COUNTRY="USA", INDICATOR="GDP", _skip_validation=True
                )

    def test_fetch_data_tolerates_missing_indicator_dim(self, builder, monkeypatch):
        """``KeyError`` from ``get_indicators_in`` collapses to an empty map."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {},
        )

        def _raise(_df):
            """Mimic the production failure for the ``FFS`` dataflow."""
            raise KeyError(
                "Could not find an indicator-like dimension for dataflow 'FLOW'."
            )

        monkeypatch.setattr(builder.metadata, "get_indicators_in", _raise)
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=self._xml_response(),
        ):
            result = builder.fetch_data(
                "FLOW", COUNTRY="USA", INDICATOR="GDP", _skip_validation=True
            )
        assert "data" in result and "metadata" in result

    def test_invalid_xml_raises_openbb_error(self, builder):
        """Garbage XML surfaces as ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=self._xml_response(text="<bad xml"),
        ):
            with pytest.raises(OpenBBError, match="Failed to parse XML"):
                builder.fetch_data(
                    "FLOW", COUNTRY="USA", INDICATOR="GDP", _skip_validation=True
                )

    def test_no_dataset_raises(self, builder):
        """An XML document without a ``DataSet`` element raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        no_dataset = (
            '<root xmlns="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message"/>'
        )
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=self._xml_response(text=no_dataset),
        ):
            with pytest.raises(OpenBBError, match="No data found"):
                builder.fetch_data(
                    "FLOW", COUNTRY="USA", INDICATOR="GDP", _skip_validation=True
                )

    def test_full_xml_extraction(self, builder, monkeypatch):
        """A full XML payload yields rows with translated SCALE / UNIT / unit_multiplier."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {
                "COUNTRY": [{"value": "USA", "label": "United States"}],
                "INDICATOR": [
                    {"value": "GDP", "label": "Gross Domestic Product"},
                    {"value": "CPI", "label": "Consumer Price Index"},
                ],
            },
        )
        monkeypatch.setattr(
            builder.metadata,
            "get_indicators_in",
            lambda _df: [
                {"indicator": "GDP", "description": "Gross Domestic Product"},
                {"indicator": "CPI", "description": "Consumer Price Index"},
            ],
        )
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=self._xml_response(),
        ):
            result = builder.fetch_data(
                "FLOW", COUNTRY="USA", INDICATOR="GDP+CPI", _skip_validation=True
            )

        assert "data" in result and "metadata" in result
        codes = {row["INDICATOR_code"] for row in result["data"]}
        assert codes == {"GDP", "CPI"}
        gdp_rows = [row for row in result["data"] if row["INDICATOR_code"] == "GDP"]
        assert gdp_rows[0]["unit_multiplier"] == 10**6
        assert gdp_rows[0]["scale"] == "Millions"
        assert gdp_rows[0]["unit"] == "US dollar"
        cpi_row = next(row for row in result["data"] if row["INDICATOR_code"] == "CPI")
        assert cpi_row["scale"] == "bad"

    def test_empty_data_rows_raises(self, builder, monkeypatch):
        """A DataSet without any observations raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {},
        )
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        empty_xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="" />
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=self._xml_response(text=empty_xml),
        ):
            with pytest.raises(OpenBBError, match="No data rows found"):
                builder.fetch_data(
                    "FLOW", COUNTRY="USA", INDICATOR="GDP", _skip_validation=True
                )


class TestFetchDataSeriesMeta:
    """Tests for the series-meta enrichment inside ``fetch_data``."""

    def _xml_with_counterpart(self):
        """Series-level XML carrying COUNTERPART_COUNTRY + DERIVATION_TYPE."""
        return dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Group INDICATOR="GDP" type="GroupType">
                        <Comp id="UNIT"><Value>USD</Value></Comp>
                        <Comp id="SCALE"><Value>6</Value></Comp>
                        <Comp id="EXTRA"><Value>Something</Value></Comp>
                    </Group>
                    <Series COUNTRY="USA" INDICATOR="GDP" COUNTERPART_COUNTRY="GBR" IFS_FLAG="X" CUSTOM="MyDim">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="5" DERIVATION_TYPE="YoY" UNIT="EUR" SCALE="3"/>
                        <Obs TIME_PERIOD="2021" OBS_VALUE="7" DERIVATION_TYPE="MoM"/>
                        <Obs TIME_PERIOD="2022" OBS_VALUE="D"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )

    def test_counterpart_country_and_group_attrs(self, builder, monkeypatch):
        """Group-level attributes flow into series meta; counterpart added to titles."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {"COUNTRY": [{"value": "USA", "label": "United States"}]},
        )
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        mock_response = MagicMock()
        mock_response.text = self._xml_with_counterpart()
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        rows = result["data"]
        assert rows[0]["counterpart_country_code"] == "GBR"
        assert rows[0]["CUSTOM"] == "MyDim"
        assert "IFS_FLAG" not in rows[0]
        gdp_meta = next(iter(result["metadata"].values()))
        assert gdp_meta["derivation_type"] in {"MoM; YoY", "YoY; MoM"}

    def test_type_of_transformation_unit_branches(self, builder, monkeypatch):
        """``TYPE_OF_TRANSFORMATION`` infers unit / scale through various heuristics."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])

        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="A" TYPE_OF_TRANSFORMATION="Index">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                    <Series COUNTRY="USA" INDICATOR="B" TYPE_OF_TRANSFORMATION="Percent change, year-over-year">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                    <Series COUNTRY="USA" INDICATOR="C" TYPE_OF_TRANSFORMATION="Percent change, period-over-period">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                    <Series COUNTRY="USA" INDICATOR="D" TYPE_OF_TRANSFORMATION="Something, Index">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                    <Series COUNTRY="USA" INDICATOR="E" TYPE_OF_TRANSFORMATION="Something else, foo">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                    <Series COUNTRY="USA" INDICATOR="F" TYPE_OF_TRANSFORMATION="Plain">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        units = {row["INDICATOR_code"]: row.get("unit") for row in result["data"]}
        scales = {row["INDICATOR_code"]: row.get("scale") for row in result["data"]}
        assert units["A"] == "Index"
        assert units["B"] == "Percent change"
        assert scales["B"] == "Year-over-year"
        assert scales["C"] == "Period-over-period"
        assert units["D"] == "Index"
        assert units["E"] == "Something else, foo"
        assert units["F"] == "Plain"

    def test_indicator_code_suffix_used_for_unit(self, builder, monkeypatch):
        """A trailing ``_USD`` style suffix resolves through ``CL_UNIT``."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])

        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP_USD">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="10"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["unit"] == "US dollar"

    def test_obs_level_unit_and_scale(self, builder, monkeypatch):
        """Per-observation ``UNIT``/``SCALE`` attributes flow into the row."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])

        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1" UNIT="EUR" SCALE="3"/>
                        <Obs TIME_PERIOD="2021" OBS_VALUE="2" SCALE="bad"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        first, second = result["data"]
        assert first["unit"] == "Euro"
        assert first["scale"] == "Thousands"
        assert first["unit_multiplier"] == 1000
        assert second["scale"] == "bad"

    def test_obs_value_via_child_element(self, builder, monkeypatch):
        """Observation values can be carried in an ``ObsValue`` child element."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])

        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020">
                            <ObsValue value="42"/>
                        </Obs>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["OBS_VALUE"] == 42

    def test_derivation_type_translated_via_codelist(self, builder, monkeypatch):
        """``DERIVATION_TYPE`` values translate through ``CL_DERIVATION_TYPE`` codelist."""
        builder.metadata._codelist_cache["CL_DERIVATION_TYPE"] = {
            "YoY": "Year over year"
        }
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1" DERIVATION_TYPE="YoY"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        meta = next(iter(result["metadata"].values()))
        if isinstance(meta, dict):
            assert meta.get("derivation_type") == "Year over year"

    def test_dataset_attrs_propagated(self, builder, monkeypatch):
        """Dataflow-level ``publisher`` shows up under ``metadata.dataset``."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {},
        )
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        monkeypatch.setitem(builder.metadata.dataflows["FLOW"], "publisher", "IMF")
        mock_response = MagicMock()
        mock_response.text = TestFetchDataXml.XML_TEMPLATE
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data(
                "FLOW", COUNTRY="USA", INDICATOR="GDP+CPI", _skip_validation=True
            )
        assert result["metadata"]["dataset"]["publisher"] == "IMF"

    def test_validates_when_skip_validation_false(self, builder, monkeypatch):
        """The validate path is hit when ``_skip_validation`` is False."""
        called: list = []

        def fake_validate(*args, **kwargs):  # noqa: ARG001
            called.append(True)
            raise ValueError("invalid")

        monkeypatch.setattr(builder, "validate_dimension_constraints", fake_validate)
        with pytest.raises(ValueError, match="invalid"):
            builder.fetch_data("FLOW", COUNTRY="USA")
        assert called

    def test_group_with_type_only_attribute_skipped(self, builder, monkeypatch):
        """A Group whose only attribute is ``type=…GROUP…`` is skipped."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Group type="MyGroupType"/>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert len(result["data"]) == 1

    def test_attr_codelist_map_populated(self, builder, monkeypatch):
        """When attributes carry a codelist reference, their cache entries are used."""
        builder.metadata.datastructures["DSD_FLOW"]["attributes"] = [
            {
                "id": "UNIT",
                "localRepresentation": {
                    "enumeration": "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=IMF.STA:CL_UNIT(1.0)"
                },
            }
        ]
        monkeypatch.setattr(
            builder.metadata,
            "_resolve_codelist_id",
            lambda *_args, **_kwargs: "CL_UNIT",
        )
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP" UNIT="USD">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["unit"] == "US dollar"

    def test_group_attribute_seeds_unit_and_scale(self, builder, monkeypatch):
        """A Group's UNIT/SCALE attribute fills series metadata when absent on series."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        builder.metadata._codelist_cache.pop("CL_UNIT", None)
        builder.metadata._codelist_cache.pop("CL_UNIT_MULT", None)
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Group INDICATOR="GDP" type="GroupType">
                        <Comp id="UNIT"><Value>USD</Value></Comp>
                        <Comp id="SCALE"><Value>6</Value></Comp>
                        <Comp id="EXTRA"><Value>Yes</Value></Comp>
                    </Group>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        row = result["data"][0]
        assert row["unit"] == "USD"
        assert row["scale"] == "10^6"
        assert row["EXTRA"] == "Yes"

    def test_dim_translation_for_non_indicator_non_country(self, builder, monkeypatch):
        """Translation maps apply to non-indicator/non-country dims too."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {"CUSTOM": [{"value": "X", "label": "Xtra"}]},
        )
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP" CUSTOM="X">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["CUSTOM"] == "Xtra"
        assert result["data"][0]["CUSTOM_code"] == "X"

    def test_label_source_unit_extraction(self, builder, monkeypatch):
        """Unit / scale can be extracted from PRODUCTION_INDEX label."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" PRODUCTION_INDEX="Industrial Production (Index, 2015=100)">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert "unit" in result["data"][0]

    def test_oversized_indicator_value_falls_to_wildcard(self, builder, monkeypatch):
        """A ``len > 1500`` indicator value collapses to ``*`` in the URL."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        captured = {}

        def fake_make_request(url, headers=None):  # noqa: ARG001
            captured["url"] = url
            mock_response = MagicMock()
            mock_response.text = TestFetchDataXml.XML_TEMPLATE
            mock_response.raise_for_status.return_value = None
            return mock_response

        with patch(
            "openbb_core.provider.utils.helpers.make_request", new=fake_make_request
        ):
            builder.fetch_data(
                "FLOW",
                COUNTRY="USA",
                INDICATOR="A" * 1600,
                _skip_validation=True,
            )
        assert "/USA.*.*" in captured["url"]

    def test_series_scale_via_attr_codelist(self, builder, monkeypatch):
        """A series-level SCALE attribute uses ``attr_codelist_map`` when populated."""
        builder.metadata.datastructures["DSD_FLOW"]["attributes"] = [
            {"id": "SCALE"},
        ]
        monkeypatch.setattr(
            builder.metadata,
            "_resolve_codelist_id",
            lambda *_args, **_kwargs: "CL_UNIT_MULT",
        )
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP" SCALE="6">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["scale"] == "Millions"

    def test_series_scale_without_codelist(self, builder, monkeypatch):
        """A series-level SCALE without any codelist cache uses the ``10^N`` fallback."""
        builder.metadata._codelist_cache.pop("CL_UNIT_MULT", None)
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP" SCALE="6">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["scale"] == "10^6"

    def test_obs_scale_without_codelist(self, builder, monkeypatch):
        """Per-obs SCALE without any codelist cache uses ``10^N`` fallback."""
        builder.metadata._codelist_cache.pop("CL_UNIT_MULT", None)
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1" SCALE="3"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["scale"] == "10^3"

    def test_dim_with_empty_id_skipped(self, builder, monkeypatch):
        """A dimension with an empty ``id`` is skipped during indicator-order build."""
        builder.metadata.datastructures["DSD_FLOW"]["dimensions"].insert(
            0, {"id": "", "position": -1}
        )
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert len(result["data"]) == 1

    def test_indicator_label_yields_unit_and_scale(self, builder, monkeypatch):
        """An INDICATOR label embedding ``X per Y`` extracts unit & scale."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {
                "INDICATOR": [{"value": "GDP", "label": "GDP (US dollar per capita)"}]
            },
        )
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        row = result["data"][0]
        assert row.get("unit") == "US dollar"
        assert "Per Capita" in (row.get("scale") or "")

    def test_label_sources_provide_unit_when_indicator_does_not(
        self, builder, monkeypatch
    ):
        """A PRODUCTION_INDEX label is used to derive unit + scale."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {},
        )
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" PRODUCTION_INDEX="Industrial Output (US dollar per capita)">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        row = result["data"][0]
        assert row.get("unit") == "US dollar"
        assert row.get("scale") and "Per Capita" in row["scale"]

    def test_group_namespaced_value_child(self, builder, monkeypatch):
        """``ss:Value`` namespaced children inside Comp elements resolve correctly."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message"
                xmlns:ss="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/data/structurespecific">
                <message:DataSet>
                    <Group INDICATOR="GDP" type="GroupType">
                        <Comp id="UNIT"><ss:Value>USD</ss:Value></Comp>
                    </Group>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["unit"] == "US dollar"

    def test_obs_value_via_value_child_text(self, builder, monkeypatch):
        """An ``<OBS_VALUE>`` child's text is picked up when no attribute is set."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020">
                            <Value>77</Value>
                        </Obs>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["OBS_VALUE"] == 77

    def test_counterpart_country_translation_used(self, builder, monkeypatch):
        """COUNTERPART_COUNTRY translation flows from the translation map."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {
                "COUNTERPART_COUNTRY": [{"value": "GBR", "label": "United Kingdom"}]
            },
        )
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" COUNTERPART_COUNTRY="GBR" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["COUNTERPART_COUNTRY"] == "United Kingdom"

    def test_group_attr_unit_scale_codelist_path(self, builder, monkeypatch):
        """Group-level UNIT/SCALE attributes use ``attr_codelist_map`` when populated."""
        monkeypatch.setattr(
            builder.metadata,
            "_resolve_codelist_id",
            lambda *_args, **_kwargs: (
                "CL_UNIT" if _args[2] == "UNIT" else "CL_UNIT_MULT"
            ),
        )
        builder.metadata.datastructures["DSD_FLOW"]["attributes"] = [
            {"id": "UNIT"},
            {"id": "SCALE"},
        ]
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Group INDICATOR="GDP" type="GroupType">
                        <Comp id="UNIT"><Value>USD</Value></Comp>
                        <Comp id="SCALE"><Value>6</Value></Comp>
                    </Group>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        row = result["data"][0]
        assert row["unit"] == "US dollar"
        assert row["scale"] == "Millions"

    def test_group_attr_scale_invalid_int(self, builder, monkeypatch):
        """Non-integer group SCALE values fall through to the ``except`` branch."""
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Group INDICATOR="GDP" type="GroupType">
                        <Comp id="SCALE"><Value>not-an-int</Value></Comp>
                    </Group>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["scale"] == "not-an-int"

    def test_group_attr_translated_dim(self, builder, monkeypatch):
        """Group attributes with translation maps populate <id>/<id>_code."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {"CUSTOM": [{"value": "X", "label": "Xtra"}]},
        )
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Group INDICATOR="GDP" type="GroupType">
                        <Comp id="CUSTOM"><Value>X</Value></Comp>
                    </Group>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        assert result["data"][0]["CUSTOM"] == "Xtra"

    def test_obs_unit_scale_codelist_path(self, builder, monkeypatch):
        """Obs-level UNIT/SCALE use the attribute-codelist map when populated."""
        builder.metadata.datastructures["DSD_FLOW"]["attributes"] = [
            {"id": "UNIT"},
            {"id": "SCALE"},
        ]
        monkeypatch.setattr(
            builder.metadata,
            "_resolve_codelist_id",
            lambda *_args, **_kwargs: (
                "CL_UNIT" if _args[2] == "UNIT" else "CL_UNIT_MULT"
            ),
        )
        monkeypatch.setattr(builder.metadata, "get_dataflow_parameters", lambda _df: {})
        monkeypatch.setattr(builder.metadata, "get_indicators_in", lambda _df: [])
        xml = dedent(
            """
            <message:StructureSpecificData
                xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v3_0/message">
                <message:DataSet>
                    <Series COUNTRY="USA" INDICATOR="GDP">
                        <Obs TIME_PERIOD="2020" OBS_VALUE="1" UNIT="EUR" SCALE="6"/>
                    </Series>
                </message:DataSet>
            </message:StructureSpecificData>
            """
        )
        mock_response = MagicMock()
        mock_response.text = xml
        mock_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=mock_response,
        ):
            result = builder.fetch_data("FLOW", _skip_validation=True)
        row = result["data"][0]
        assert row["unit"] == "Euro"
        assert row["scale"] == "Millions"


class TestGetCachedTranslations:
    """Tests for ``_get_cached_translations``."""

    def test_translation_map_built(self, builder, monkeypatch):
        """The translation map mirrors the dataflow parameters."""
        monkeypatch.setattr(
            builder.metadata,
            "get_dataflow_parameters",
            lambda _df: {"INDICATOR": [{"value": "GDP", "label": "G"}]},
        )
        result = builder._get_cached_translations("FLOW")
        assert result == {"INDICATOR": {"GDP": "G"}}
