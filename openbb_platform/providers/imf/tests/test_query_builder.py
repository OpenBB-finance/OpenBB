"""Comprehensive tests for IMF query parsing, search, and fetch helpers."""

# ruff: noqa: I001, SLF001
# pylint: disable=W0621,W0613,W0212,R0903

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
    # Central bank phrase should match at least the explicit central bank flow.
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
    with patch("openbb_imf.utils.query_builder.ImfMetadata") as MockMetadata, patch(
        "openbb_core.provider.utils.helpers.make_request"
    ) as mock_make_request:
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
    # Returned SDMX time periods include end-of-year date strings.
    assert set(df["TIME_PERIOD"]) == {"2020-12-31", "2021-12-31"}


def test_strict_error_missing_dataflow(mock_imf_query_builder):
    builder = mock_imf_query_builder
    with pytest.raises(ValueError, match="Dataflow 'MISSING' not found"):
        builder.build_url("MISSING")
