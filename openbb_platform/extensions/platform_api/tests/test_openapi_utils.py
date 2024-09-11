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
    "path, params_number,expected_has_chart",
    [
        ("/api/v1/economy/balance_of_payments", 4, False),
        ("/api/v1/economy/fred_series", 8, True),
    ],
)
def test_get_query_schema_for_widget(
    mock_openapi_json, path, params_number, expected_has_chart
):
    route_params, has_chart = get_query_schema_for_widget(mock_openapi_json, path)
    assert len(route_params) == params_number
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
    "openapi_schema_ref",
    [
        "FredBalanceOfPaymentsData",
        "FredUofMichiganData",
        "FredSurveyOfEconomicConditionsChicagoData",
    ],
)
def test_data_schema_to_columns_defs(mock_openapi_json, openapi_schema_ref):
    result_schema_ref = {
        "anyOf": [
            {
                "items": {
                    "oneOf": [{"$ref": f"#/components/schemas/{openapi_schema_ref}"}]
                }
            }
        ]
    }
    column_defs = data_schema_to_columns_defs(mock_openapi_json, result_schema_ref)
    assert len(column_defs) > 1  # There should be at least two columns


if __name__ == "__main__":
    pytest.main()
