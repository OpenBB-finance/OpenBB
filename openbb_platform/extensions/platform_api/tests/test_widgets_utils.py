import json
from pathlib import Path

import pytest
from openbb_platform_api.utils.widgets import build_json, modify_query_schema

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
                {
                    "parameter_name": "provider",
                    "label": "Provider",
                    "description": "Source of the data.",
                    "optional": True,
                    "type": "text",
                    "available_providers": ["sec"],
                    "show": True,
                },
                {
                    "parameter_name": "query",
                    "label": "Query",
                    "description": "Search query.",
                    "optional": True,
                    "value": "",
                    "options": {"sec": []},
                    "multiple_items_allowed": {},
                    "available_providers": ["sec"],
                    "type": "text",
                    "show": True,
                },
                {
                    "parameter_name": "use_cache",
                    "label": "Use Cache",
                    "description": "Whether or not to use cache.",
                    "optional": True,
                    "value": True,
                    "options": {"sec": []},
                    "multiple_items_allowed": {},
                    "available_providers": ["sec"],
                    "type": "boolean",
                    "show": True,
                },
                {
                    "parameter_name": "url",
                    "label": "Url",
                    "description": "Enter an optional URL path to fetch the next level.",
                    "optional": True,
                    "value": None,
                    "options": {"sec": []},
                    "multiple_items_allowed": {},
                    "available_providers": ["sec"],
                    "show": True,
                },
            ],
            "sec",
            [
                {
                    "label": "Query",
                    "description": "Search query.",
                    "optional": True,
                    "value": "",
                    "type": "text",
                    "show": True,
                    "paramName": "query",
                },
                {
                    "label": "Use Cache",
                    "description": "Whether or not to use cache.",
                    "optional": True,
                    "value": True,
                    "type": "boolean",
                    "show": True,
                    "paramName": "use_cache",
                },
                {
                    "label": "Url",
                    "description": "Enter an optional URL path to fetch the next level.",
                    "optional": True,
                    "value": None,
                    "show": True,
                    "paramName": "url",
                },
                {"paramName": "provider", "value": "sec", "show": False},
            ],
        ),
        (
            [
                {
                    "parameter_name": "provider",
                    "label": "Provider",
                    "description": "Source of the data.",
                    "optional": True,
                    "type": "text",
                    "available_providers": ["fred"],
                    "show": True,
                },
                {
                    "parameter_name": "symbol",
                    "label": "Symbol",
                    "description": "Symbol to get data for.",
                    "optional": False,
                    "type": "text",
                    "multiple_items_allowed": {"fred": True},
                    "show": True,
                },
                {
                    "parameter_name": "start_date",
                    "label": "Start Date",
                    "description": "Start date of the data, in YYYY-MM-DD format.",
                    "optional": True,
                    "value": None,
                    "options": {"fred": []},
                    "multiple_items_allowed": {},
                    "available_providers": ["fred"],
                    "type": "date",
                    "show": True,
                },
                {
                    "parameter_name": "end_date",
                    "label": "End Date",
                    "description": "End date of the data, in YYYY-MM-DD format.",
                    "optional": True,
                    "value": None,
                    "options": {"fred": []},
                    "multiple_items_allowed": {},
                    "available_providers": ["fred"],
                    "type": "date",
                    "show": True,
                },
                {
                    "parameter_name": "limit",
                    "label": "Limit",
                    "description": "The number of data entries to return.",
                    "optional": True,
                    "value": 100000,
                    "options": {"fred": []},
                    "multiple_items_allowed": {},
                    "available_providers": ["fred"],
                    "type": "number",
                    "show": True,
                },
                {
                    "parameter_name": "frequency",
                    "label": "Frequency",
                    "description": "Frequency aggregation to convert high frequency data to lower frequency."
                    + "\n        "
                    + "\n    None = No change"
                    + "\n        "
                    + "\n    a = Annual"
                    + "\n        "
                    + "\n    q = Quarterly"
                    + "\n        "
                    + "\n    m = Monthly"
                    + "\n        "
                    + "\n    w = Weekly"
                    + "\n        "
                    + "\n    d = Daily"
                    + "\n        "
                    + "\n    wef = Weekly, Ending Friday"
                    + "\n        "
                    + "\n    weth = Weekly, Ending Thursday"
                    + "\n        "
                    + "\n    wew = Weekly, Ending Wednesday"
                    + "\n        "
                    + "\n    wetu = Weekly, Ending Tuesday"
                    + "\n        "
                    + "\n    wem = Weekly, Ending Monday"
                    + "\n        "
                    + "\n    wesu = Weekly, Ending Sunday"
                    + "\n        "
                    + "\n    wesa = Weekly, Ending Saturday"
                    + "\n        "
                    + "\n    bwew = Biweekly, Ending Wednesday"
                    + "\n        "
                    + "\n    bwem = Biweekly, Ending Monday",
                    "optional": True,
                    "value": None,
                    "options": {
                        "fred": [
                            {"label": "a", "value": "a"},
                            {"label": "q", "value": "q"},
                            {"label": "m", "value": "m"},
                            {"label": "w", "value": "w"},
                            {"label": "d", "value": "d"},
                            {"label": "wef", "value": "wef"},
                            {"label": "weth", "value": "weth"},
                            {"label": "wew", "value": "wew"},
                            {"label": "wetu", "value": "wetu"},
                            {"label": "wem", "value": "wem"},
                            {"label": "wesu", "value": "wesu"},
                            {"label": "wesa", "value": "wesa"},
                            {"label": "bwew", "value": "bwew"},
                            {"label": "bwem", "value": "bwem"},
                        ]
                    },
                    "multiple_items_allowed": {},
                    "available_providers": ["fred"],
                    "show": True,
                },
                {
                    "parameter_name": "aggregation_method",
                    "label": "Aggregation Method",
                    "description": "A key that indicates the aggregation method used for frequency aggregation."
                    + "\n        This parameter has no affect if the frequency parameter is not set."
                    + "\n        "
                    + "\n    avg = Average"
                    + "\n        "
                    + "\n    sum = Sum"
                    + "\n        "
                    + "\n    eop = End of Period",
                    "optional": True,
                    "value": "eop",
                    "options": {
                        "fred": [
                            {"label": "avg", "value": "avg"},
                            {"label": "sum", "value": "sum"},
                            {"label": "eop", "value": "eop"},
                        ]
                    },
                    "multiple_items_allowed": {},
                    "available_providers": ["fred"],
                    "show": True,
                },
                {
                    "parameter_name": "transform",
                    "label": "Transform",
                    "description": "Transformation type"
                    + "\n        "
                    + "\n    None = No transformation"
                    + "\n        "
                    + "\n    chg = Change"
                    + "\n        "
                    + "\n    ch1 = Change from Year Ago"
                    + "\n        "
                    + "\n    pch = Percent Change"
                    + "\n        "
                    + "\n    pc1 = Percent Change from Year Ago"
                    + "\n        "
                    + "\n    pca = Compounded Annual Rate of Change"
                    + "\n        "
                    + "\n    cch = Continuously Compounded Rate of Change"
                    + "\n        "
                    + "\n    cca = Continuously Compounded Annual Rate of Change"
                    + "\n        "
                    + "\n    log = Natural Log",
                    "optional": True,
                    "value": None,
                    "options": {
                        "fred": [
                            {"label": "chg", "value": "chg"},
                            {"label": "ch1", "value": "ch1"},
                            {"label": "pch", "value": "pch"},
                            {"label": "pc1", "value": "pc1"},
                            {"label": "pca", "value": "pca"},
                            {"label": "cch", "value": "cch"},
                            {"label": "cca", "value": "cca"},
                            {"label": "log", "value": "log"},
                        ]
                    },
                    "multiple_items_allowed": {},
                    "available_providers": ["fred"],
                    "show": True,
                },
            ],
            "fred",
            [
                {
                    "label": "Symbol",
                    "description": "Symbol to get data for. Multiple comma separated items allowed.",
                    "optional": False,
                    "type": "text",
                    "show": True,
                    "multiSelect": True,
                    "paramName": "symbol",
                },
                {
                    "label": "Start Date",
                    "description": "Start date of the data, in YYYY-MM-DD format.",
                    "optional": True,
                    "value": None,
                    "type": "date",
                    "show": True,
                    "paramName": "start_date",
                },
                {
                    "label": "End Date",
                    "description": "End date of the data, in YYYY-MM-DD format.",
                    "optional": True,
                    "value": None,
                    "type": "date",
                    "show": True,
                    "paramName": "end_date",
                },
                {
                    "label": "Limit",
                    "description": "The number of data entries to return.",
                    "optional": True,
                    "value": 100000,
                    "type": "number",
                    "show": True,
                    "paramName": "limit",
                },
                {
                    "label": "Frequency",
                    "description": "Frequency aggregation to convert high frequency data to lower frequency."
                    + "\n        "
                    + "\n    None = No change"
                    + "\n        "
                    + "\n    a = Annual"
                    + "\n        "
                    + "\n    q = Quarterly"
                    + "\n        "
                    + "\n    m = Monthly"
                    + "\n        "
                    + "\n    w = Weekly"
                    + "\n        "
                    + "\n    d = Daily"
                    + "\n        "
                    + "\n    wef = Weekly, Ending Friday"
                    + "\n        "
                    + "\n    weth = Weekly, Ending Thursday"
                    + "\n        "
                    + "\n    wew = Weekly, Ending Wednesday"
                    + "\n        "
                    + "\n    wetu = Weekly, Ending Tuesday"
                    + "\n        "
                    + "\n    wem = Weekly, Ending Monday"
                    + "\n        "
                    + "\n    wesu = Weekly, Ending Sunday"
                    + "\n        "
                    + "\n    wesa = Weekly, Ending Saturday"
                    + "\n        "
                    + "\n    bwew = Biweekly, Ending Wednesday"
                    + "\n        "
                    + "\n    bwem = Biweekly, Ending Monday",
                    "optional": True,
                    "value": None,
                    "show": True,
                    "options": [
                        {"label": "a", "value": "a"},
                        {"label": "q", "value": "q"},
                        {"label": "m", "value": "m"},
                        {"label": "w", "value": "w"},
                        {"label": "d", "value": "d"},
                        {"label": "wef", "value": "wef"},
                        {"label": "weth", "value": "weth"},
                        {"label": "wew", "value": "wew"},
                        {"label": "wetu", "value": "wetu"},
                        {"label": "wem", "value": "wem"},
                        {"label": "wesu", "value": "wesu"},
                        {"label": "wesa", "value": "wesa"},
                        {"label": "bwew", "value": "bwew"},
                        {"label": "bwem", "value": "bwem"},
                    ],
                    "type": "text",
                    "paramName": "frequency",
                },
                {
                    "label": "Aggregation Method",
                    "description": "A key that indicates the aggregation method used for frequency aggregation."
                    + "\n        This parameter has no affect if the frequency parameter is not set."
                    + "\n        "
                    + "\n    avg = Average"
                    + "\n        "
                    + "\n    sum = Sum"
                    + "\n        "
                    + "\n    eop = End of Period",
                    "optional": True,
                    "value": "eop",
                    "show": True,
                    "options": [
                        {"label": "avg", "value": "avg"},
                        {"label": "sum", "value": "sum"},
                        {"label": "eop", "value": "eop"},
                    ],
                    "type": "text",
                    "paramName": "aggregation_method",
                },
                {
                    "label": "Transform",
                    "description": "Transformation type"
                    + "\n        "
                    + "\n    None = No transformation"
                    + "\n        "
                    + "\n    chg = Change"
                    + "\n        "
                    + "\n    ch1 = Change from Year Ago"
                    + "\n        "
                    + "\n    pch = Percent Change"
                    + "\n        "
                    + "\n    pc1 = Percent Change from Year Ago"
                    + "\n        "
                    + "\n    pca = Compounded Annual Rate of Change"
                    + "\n        "
                    + "\n    cch = Continuously Compounded Rate of Change"
                    + "\n        "
                    + "\n    cca = Continuously Compounded Annual Rate of Change"
                    + "\n        "
                    + "\n    log = Natural Log",
                    "optional": True,
                    "value": None,
                    "show": True,
                    "options": [
                        {"label": "chg", "value": "chg"},
                        {"label": "ch1", "value": "ch1"},
                        {"label": "pch", "value": "pch"},
                        {"label": "pc1", "value": "pc1"},
                        {"label": "pca", "value": "pca"},
                        {"label": "cch", "value": "cch"},
                        {"label": "cca", "value": "cca"},
                        {"label": "log", "value": "log"},
                    ],
                    "type": "text",
                    "paramName": "transform",
                },
                {"paramName": "provider", "value": "fred", "show": False},
            ],
        ),
    ],
)
def test_modify_query_schema(query_schema, provider_value, expected_result):
    result = modify_query_schema(query_schema, provider_value)
    assert result == expected_result


def test_build_json(mock_openapi_json, mock_widgets_json):
    result = build_json(openapi=mock_openapi_json, widget_exclude_filter=[])
    assert (
        len(result) == len(mock_openapi_json["paths"]) + 1
    )  # +1 for the duplicate path with a chart.
    assert result == mock_widgets_json


if __name__ == "__main__":
    pytest.main()
