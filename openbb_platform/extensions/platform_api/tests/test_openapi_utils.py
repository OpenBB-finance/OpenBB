import json
from pathlib import Path

import pytest
from openbb_platform_api.utils.openapi import (
    data_schema_to_columns_defs,
    get_data_schema_for_widget,
    get_query_schema_for_widget,
)

# pylint: disable=redefined-outer-name


# Load the mock OpenAPI JSON
@pytest.fixture(scope="module")
def mock_openapi_json():
    mock_openapi_path = Path(__file__).parent / "mock_openapi.json"
    with open(mock_openapi_path) as file:
        return json.load(file)


@pytest.mark.parametrize(
    "path, params_number, query_schema, expected_has_chart",
    [
        (
            "/api/v1/economy/balance_of_payments",
            4,
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
                    "parameter_name": "country",
                    "label": "Country",
                    "description": "The country to get data. Enter as a 3-letter ISO country code, default is USA.",
                    "optional": True,
                    "value": "united_states",
                    "options": {
                        "fred": [
                            {"label": "argentina", "value": "argentina"},
                            {"label": "australia", "value": "australia"},
                            {"label": "austria", "value": "austria"},
                            {"label": "belgium", "value": "belgium"},
                            {"label": "brazil", "value": "brazil"},
                            {"label": "canada", "value": "canada"},
                            {"label": "chile", "value": "chile"},
                            {"label": "china", "value": "china"},
                            {"label": "colombia", "value": "colombia"},
                            {"label": "costa_rica", "value": "costa_rica"},
                            {"label": "czechia", "value": "czechia"},
                            {"label": "denmark", "value": "denmark"},
                            {"label": "estonia", "value": "estonia"},
                            {"label": "finland", "value": "finland"},
                            {"label": "france", "value": "france"},
                            {"label": "germany", "value": "germany"},
                            {"label": "greece", "value": "greece"},
                            {"label": "hungary", "value": "hungary"},
                            {"label": "iceland", "value": "iceland"},
                            {"label": "india", "value": "india"},
                            {"label": "indonesia", "value": "indonesia"},
                            {"label": "ireland", "value": "ireland"},
                            {"label": "israel", "value": "israel"},
                            {"label": "italy", "value": "italy"},
                            {"label": "japan", "value": "japan"},
                            {"label": "korea", "value": "korea"},
                            {"label": "latvia", "value": "latvia"},
                            {"label": "lithuania", "value": "lithuania"},
                            {"label": "luxembourg", "value": "luxembourg"},
                            {"label": "mexico", "value": "mexico"},
                            {"label": "netherlands", "value": "netherlands"},
                            {"label": "new_zealand", "value": "new_zealand"},
                            {"label": "norway", "value": "norway"},
                            {"label": "poland", "value": "poland"},
                            {"label": "portugal", "value": "portugal"},
                            {"label": "russia", "value": "russia"},
                            {"label": "saudi_arabia", "value": "saudi_arabia"},
                            {"label": "slovak_republic", "value": "slovak_republic"},
                            {"label": "slovenia", "value": "slovenia"},
                            {"label": "south_africa", "value": "south_africa"},
                            {"label": "spain", "value": "spain"},
                            {"label": "sweden", "value": "sweden"},
                            {"label": "switzerland", "value": "switzerland"},
                            {"label": "turkey", "value": "turkey"},
                            {"label": "united_kingdom", "value": "united_kingdom"},
                            {"label": "united_states", "value": "united_states"},
                            {"label": "g7", "value": "g7"},
                            {"label": "g20", "value": "g20"},
                        ]
                    },
                    "multiple_items_allowed": {},
                    "available_providers": ["fred"],
                    "type": "text",
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
            ],
            False,
        ),
        (
            "/api/v1/economy/fred_series",
            8,
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
                    + "\n    a = Annual\n        "
                    + "\n    q = Quarterly\n        "
                    + "\n    m = Monthly\n        "
                    + "\n    w = Weekly\n        "
                    + "\n    d = Daily\n        "
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
            True,
        ),
        (
            "/api/v1/regulators/sec/schema_files",
            4,
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
            False,
        ),
    ],
)
def test_get_query_schema_for_widget(
    mock_openapi_json, path, params_number, query_schema, expected_has_chart
):
    route_params, has_chart = get_query_schema_for_widget(mock_openapi_json, path)
    assert len(route_params) == params_number
    assert route_params == query_schema
    assert has_chart == expected_has_chart


@pytest.mark.parametrize(
    "openapi_operation_id",
    [
        "economy_survey_sloos",
        "economy_survey_university_of_michigan",
        "economy_balance_of_payments",
    ],
)
def test_get_data_schema_for_widget(mock_openapi_json, openapi_operation_id):
    schema = get_data_schema_for_widget(mock_openapi_json, openapi_operation_id)
    assert schema is not None


@pytest.mark.parametrize(
    "openapi_operation_id",
    [
        "economy_survey_sloos",
        "economy_survey_university_of_michigan",
        "economy_balance_of_payments",
    ],
)
def test_data_schema_to_columns_defs(mock_openapi_json, openapi_operation_id):
    column_defs = data_schema_to_columns_defs(
        mock_openapi_json, openapi_operation_id, provider="fred"
    )
    assert len(column_defs) > 1  # There should be at least two columns


if __name__ == "__main__":
    pytest.main()
