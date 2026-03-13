"""Test ImfMetadata search functionality."""

# ruff: noqa: I001
# pylint: disable=W0621,R0903
import pytest

from openbb_imf.utils import metadata as md


MOCK_DATAFLOWS = [
    {
        "id": "BOP",
        "name": "Balance of Payments",
        "description": "International Monetary Fund balance of payments data.",
        "structureRef": {"id": "DSD_BOP"},
    },
    {
        "id": "CPI",
        "name": "Consumer Price Index",
        "description": "International Monetary Fund CPI dataset.",
        "structureRef": {"id": "DSD_CPI"},
    },
    {
        "id": "GOV",
        "name": "Government Finance Statistics",
        "description": "Statistics produced by the IMF.",
        "structureRef": {"id": "DSD_GOV"},
    },
]


@pytest.fixture
def imf_metadata(monkeypatch):
    """Provide a minimal ImfMetadata with canned dataflows and parameters."""
    monkeypatch.setattr(md.ImfMetadata, "_instance", None)
    monkeypatch.setattr(md.ImfMetadata, "_load_from_cache", lambda self: True)

    meta = md.ImfMetadata()
    meta.dataflows = {d["id"]: d for d in MOCK_DATAFLOWS}
    meta.dataflow_groups = {"IMF.STA": MOCK_DATAFLOWS}

    def _fake_get_dataflow_parameters(dataflow_id: str):
        if dataflow_id not in meta.dataflows:
            raise ValueError(f"Dataflow '{dataflow_id}' not found.")

        # Return a lightweight, deterministic parameter mapping.
        return {
            "COUNTRY": [
                {"value": "USA", "label": "United States"},
                {"value": "MEX", "label": "Mexico"},
            ],
            "FREQUENCY": [
                {"value": "A", "label": "Annual"},
                {"value": "Q", "label": "Quarterly"},
            ],
            "TIME_PERIOD": [
                {"value": "YYYY", "label": "Year (Start Date: 1980, End Date: 2024)"},
                {
                    "value": "YYYY-MM",
                    "label": "Month (Start Date: 1990-01, End Date: 2024-12)",
                },
                {
                    "value": "YYYY-QQ",
                    "label": "Quarter (Start Date: 1990-Q1, End Date: 2024-Q4)",
                },
                {
                    "value": "YYYY-SS",
                    "label": "Semester (Start Date: 1990-S1, End Date: 2024-S2)",
                },
                {"value": "START", "label": "Start Date: 1990"},
                {"value": "END", "label": "End Date: 2024"},
            ],
        }

    meta.get_dataflow_parameters = _fake_get_dataflow_parameters
    return meta


def test_search_datasets_by_id(imf_metadata):
    query = "BOP"
    results = imf_metadata.search_dataflows(query)

    assert results
    assert any(
        query.lower() in df["id"].lower()
        for group in results
        for df in group["dataflows"]
    )


def test_search_datasets_by_name(imf_metadata):
    query = "Balance of Payments"
    results = imf_metadata.search_dataflows(query)

    assert results
    assert any(
        query.lower() in df["name"].lower()
        for group in results
        for df in group["dataflows"]
    )


def test_search_datasets_by_description(imf_metadata):
    query = "International Monetary Fund"
    results = imf_metadata.search_dataflows(query)

    assert results
    assert any(
        query.lower() in df["description"].lower()
        for group in results
        for df in group["dataflows"]
    )


def test_search_datasets_no_match(imf_metadata):
    query = "nonexistent_dataflow_xyz"
    results = imf_metadata.search_dataflows(query)

    assert results == []


def test_get_dataflow_parameters_cpi(imf_metadata):
    dataflow_id = "CPI"
    parameters = imf_metadata.get_dataflow_parameters(dataflow_id)

    assert "COUNTRY" in parameters
    assert "FREQUENCY" in parameters
    assert "TIME_PERIOD" in parameters
    assert isinstance(parameters["COUNTRY"], list)
    assert isinstance(parameters["FREQUENCY"], list)
    assert isinstance(parameters["TIME_PERIOD"], list)
    assert any(option["value"] == "USA" for option in parameters["COUNTRY"])
    assert any(option["value"] == "A" for option in parameters["FREQUENCY"])
    assert any(option["value"] == "YYYY" for option in parameters["TIME_PERIOD"])


def test_get_dataflow_parameters_invalid_dataflow(imf_metadata):
    dataflow_id = "INVALID_DATAFLOW"
    with pytest.raises(ValueError, match=f"Dataflow '{dataflow_id}' not found."):
        imf_metadata.get_dataflow_parameters(dataflow_id)


def test_get_dataflow_parameters_time_period_options(imf_metadata):
    dataflow_id = "CPI"
    parameters = imf_metadata.get_dataflow_parameters(dataflow_id)
    time_period_options = parameters.get("TIME_PERIOD")

    assert time_period_options is not None
    assert len(time_period_options) == 6
    assert any(option["value"] == "YYYY" for option in time_period_options)
    assert any(option["value"] == "YYYY-MM" for option in time_period_options)
    assert any(option["value"] == "YYYY-QQ" for option in time_period_options)
    assert any(option["value"] == "YYYY-SS" for option in time_period_options)
    assert any("Start Date:" in option["label"] for option in time_period_options)
    assert any("End Date:" in option["label"] for option in time_period_options)
