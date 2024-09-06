import json
from pathlib import Path

import pytest
from openbb_platform_api.widgets_utils import build_json, modify_query_schema

# pylint: disable=redefined-outer-name


# Load the mock OpenAPI JSON
@pytest.fixture(scope="module")
def mock_openapi_json():
    mock_openapi_path = Path(__file__).parent / "mock_openapi.json"
    with open(mock_openapi_path) as file:
        return json.load(file)


# Load the mock widgets JSON
@pytest.fixture(scope="module")
def mock_widgets_json():
    mock_widgets_path = Path(__file__).parent / "mock_widgets.json"
    with open(mock_widgets_path) as file:
        return json.load(file)


@pytest.mark.parametrize(
    "query_schema, provider_value, expected_result",
    [
        (
            [
                {"paramName": "provider", "description": "Provider parameter"},
                {"paramName": "symbol", "description": "Symbol parameter"},
                {
                    "paramName": "chart",
                    "description": "Chart parameter (provider:fred)",
                },
                {
                    "paramName": "sort",
                    "description": "Sort parameter. Multiple comma separated items allowed for provider(s):"
                    + " fred, yfinance.",
                },
            ],
            "fred",
            [
                {"paramName": "symbol", "description": "Symbol parameter"},
                {"paramName": "chart", "description": "Chart parameter"},
                {
                    "paramName": "sort",
                    "description": "Sort parameter. Multiple comma separated items allowed.",
                },
                {"paramName": "provider", "value": "fred", "show": False},
            ],
        ),
        (
            [
                {"paramName": "provider", "description": "Provider parameter"},
                {"paramName": "symbol", "description": "Symbol parameter"},
                {
                    "paramName": "chart",
                    "description": "Chart parameter (provider:yfinance)",
                },
                {
                    "paramName": "sort",
                    "description": "Sort parameter. Multiple comma separated items allowed for provider(s): "
                    + "fred, yfinance.",
                },
            ],
            "yfinance",
            [
                {"paramName": "symbol", "description": "Symbol parameter"},
                {"paramName": "chart", "description": "Chart parameter"},
                {
                    "paramName": "sort",
                    "description": "Sort parameter. Multiple comma separated items allowed.",
                },
                {"paramName": "provider", "value": "yfinance", "show": False},
            ],
        ),
    ],
)
def test_modify_query_schema(query_schema, provider_value, expected_result):
    result = modify_query_schema(query_schema, provider_value)
    assert result == expected_result


def test_build_json(mock_openapi_json, mock_widgets_json):
    result = build_json(mock_openapi_json)
    assert result.keys() == mock_widgets_json.keys()
    for key, value in result.items():
        assert value.keys() == mock_widgets_json[key].keys()
        assert value["endpoint"] == mock_widgets_json[key]["endpoint"]
        assert value["gridData"] == mock_widgets_json[key]["gridData"]
        assert value["data"]["dataKey"] == mock_widgets_json[key]["data"]["dataKey"]
        assert (
            value["data"]["table"]["showAll"]
            == mock_widgets_json[key]["data"]["table"]["showAll"]
        )


if __name__ == "__main__":
    pytest.main()
