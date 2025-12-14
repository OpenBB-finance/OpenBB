"""Test OpenAPI Utils."""

# pylint: disable=redefined-outer-name,line-too-long
# flake8: noqa: E501

import json
from pathlib import Path

import pytest
from openbb_platform_api.utils.openapi import (
    _extract_provider_description,
    data_schema_to_columns_defs,
    get_data_schema_for_widget,
    get_query_schema_for_widget,
    post_query_schema_for_widget,
    process_parameter,
)


# Load the mock OpenAPI JSON
@pytest.fixture(scope="module")
def mock_openapi_json():
    mock_openapi_path = Path(__file__).parent / "mock_openapi.json"
    with open(mock_openapi_path, encoding="utf-8") as file:
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
                    "value": None,
                    "show": False,
                    "available_providers": ["fred"],
                },
                {
                    "parameter_name": "country",
                    "label": "Country",
                    "description": "The country to get data. Enter as a 3-letter ISO country code, default is USA.",
                    "optional": True,
                    "type": "text",
                    "value": "united_states",
                    "multiple_items_allowed": {},
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
                    "x-widget_config": {},
                    "available_providers": ["fred"],
                    "show": True,
                },
                {
                    "parameter_name": "start_date",
                    "label": "Start Date",
                    "description": "Start date of the data, in YYYY-MM-DD format.",
                    "optional": True,
                    "type": "date",
                    "value": None,
                    "multiple_items_allowed": {},
                    "options": {"fred": []},
                    "x-widget_config": {},
                    "available_providers": ["fred"],
                    "show": True,
                },
                {
                    "parameter_name": "end_date",
                    "label": "End Date",
                    "description": "End date of the data, in YYYY-MM-DD format.",
                    "optional": True,
                    "type": "date",
                    "value": None,
                    "multiple_items_allowed": {},
                    "options": {"fred": []},
                    "x-widget_config": {},
                    "available_providers": ["fred"],
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
                    "value": None,
                    "show": False,
                    "available_providers": ["fred"],
                },
                {
                    "parameter_name": "symbol",
                    "label": "Symbol",
                    "description": "Symbol to get data for.",
                    "optional": False,
                    "type": "text",
                    "value": None,
                    "multiple_items_allowed": {"fred": True},
                    "options": {"fred": []},
                    "x-widget_config": {},
                    "show": True,
                },
                {
                    "parameter_name": "start_date",
                    "label": "Start Date",
                    "description": "Start date of the data, in YYYY-MM-DD format.",
                    "optional": True,
                    "type": "date",
                    "value": None,
                    "multiple_items_allowed": {},
                    "options": {"fred": []},
                    "x-widget_config": {},
                    "show": True,
                },
                {
                    "parameter_name": "end_date",
                    "label": "End Date",
                    "description": "End date of the data, in YYYY-MM-DD format.",
                    "optional": True,
                    "type": "date",
                    "value": None,
                    "multiple_items_allowed": {},
                    "options": {"fred": []},
                    "x-widget_config": {},
                    "show": True,
                },
                {
                    "parameter_name": "limit",
                    "label": "Limit",
                    "description": "The number of data entries to return.",
                    "optional": True,
                    "type": "number",
                    "value": 100000,
                    "multiple_items_allowed": {},
                    "options": {"fred": []},
                    "x-widget_config": {},
                    "show": True,
                },
                {
                    "parameter_name": "frequency",
                    "label": "Frequency",
                    "description": "Frequency aggregation to convert high frequency data to lower frequency.\n        \n    None = No change\n        \n    a = Annual\n        \n    q = Quarterly\n        \n    m = Monthly\n        \n    w = Weekly\n        \n    d = Daily\n        \n    wef = Weekly, Ending Friday\n        \n    weth = Weekly, Ending Thursday\n        \n    wew = Weekly, Ending Wednesday\n        \n    wetu = Weekly, Ending Tuesday\n        \n    wem = Weekly, Ending Monday\n        \n    wesu = Weekly, Ending Sunday\n        \n    wesa = Weekly, Ending Saturday\n        \n    bwew = Biweekly, Ending Wednesday\n        \n    bwem = Biweekly, Ending Monday",
                    "optional": True,
                    "type": "text",
                    "value": None,
                    "multiple_items_allowed": {},
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
                    "x-widget_config": {},
                    "available_providers": ["fred"],
                    "show": True,
                },
                {
                    "parameter_name": "aggregation_method",
                    "label": "Aggregation Method",
                    "description": "A key that indicates the aggregation method used for frequency aggregation.\n"
                    + "        This parameter has no affect if the frequency parameter is not set.\n"
                    + "        \n    avg = Average\n        \n    sum = Sum\n        \n    eop = End of Period",
                    "optional": True,
                    "type": "text",
                    "value": "eop",
                    "multiple_items_allowed": {},
                    "options": {
                        "fred": [
                            {"label": "avg", "value": "avg"},
                            {"label": "sum", "value": "sum"},
                            {"label": "eop", "value": "eop"},
                        ]
                    },
                    "x-widget_config": {},
                    "available_providers": ["fred"],
                    "show": True,
                },
                {
                    "parameter_name": "transform",
                    "label": "Transform",
                    "description": "Transformation type\n        \n    None = No transformation\n        \n    chg = Change\n        \n    ch1 = Change from Year Ago\n        \n    pch = Percent Change\n        \n    pc1 = Percent Change from Year Ago\n        \n    pca = Compounded Annual Rate of Change\n        \n    cch = Continuously Compounded Rate of Change\n        \n    cca = Continuously Compounded Annual Rate of Change\n        \n    log = Natural Log",
                    "optional": True,
                    "type": "text",
                    "value": None,
                    "multiple_items_allowed": {},
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
                    "x-widget_config": {},
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
                    "value": None,
                    "show": False,
                    "available_providers": ["sec"],
                },
                {
                    "parameter_name": "query",
                    "label": "Query",
                    "description": "Search query.",
                    "optional": True,
                    "type": "text",
                    "value": "",
                    "multiple_items_allowed": {},
                    "options": {"sec": []},
                    "x-widget_config": {},
                    "show": True,
                },
                {
                    "parameter_name": "use_cache",
                    "label": "Use Cache",
                    "description": "Whether or not to use cache.",
                    "optional": True,
                    "type": "boolean",
                    "value": True,
                    "multiple_items_allowed": {},
                    "options": {"sec": []},
                    "x-widget_config": {},
                    "show": True,
                },
                {
                    "parameter_name": "url",
                    "label": "Url",
                    "description": "Enter an optional URL path to fetch the next level.",
                    "optional": True,
                    "type": "text",
                    "value": None,
                    "multiple_items_allowed": {},
                    "options": {"sec": []},
                    "x-widget_config": {},
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
        "form_submit_form_submit_post",
    ],
)
def test_post_query_schema_for_widget(mock_openapi_json, openapi_operation_id):
    """Test post_query_schema_for_widget function."""
    schema = post_query_schema_for_widget(mock_openapi_json, openapi_operation_id)
    assert schema


@pytest.mark.parametrize(
    "openapi_operation_id",
    [
        "economy_survey_sloos",
        "economy_survey_university_of_michigan",
        "economy_balance_of_payments",
    ],
)
def test_data_schema_to_columns_defs(mock_openapi_json, openapi_operation_id):
    """Test data_schema_to_columns_defs function."""
    column_defs = data_schema_to_columns_defs(
        mock_openapi_json, openapi_operation_id, provider="fred"
    )
    assert len(column_defs) > 1  # There should be at least two columns


class TestExtractProviderDescription:
    """Tests for _extract_provider_description function."""

    def test_simple_description_no_provider(self):
        """Test extraction from simple description without provider markers."""
        desc = "This is a simple description."
        result = _extract_provider_description(desc, "fred")
        assert result == "This is a simple description."

    def test_description_with_multiple_items_suffix(self):
        """Test that 'Multiple comma separated items allowed' is stripped."""
        desc = "Description text. Multiple comma separated items allowed."
        result = _extract_provider_description(desc, "fred")
        assert result == "Description text."

    def test_provider_specific_description_extraction(self):
        """Test extraction of provider-specific description."""
        desc = "Fred specific description (provider: fred);\n    Other description (provider: other)"
        result = _extract_provider_description(desc, "fred")
        assert result == "Fred specific description"

    def test_embedded_semicolon_preserved(self):
        """Test that semicolons in description text are preserved."""
        desc = "A semicolon delimited list of tags; Example: 'japan;imports' (provider: fred)"
        result = _extract_provider_description(desc, "fred")
        assert "Example: 'japan;imports'" in result

    def test_multiple_providers_in_marker(self):
        """Test handling of multiple providers in one marker."""
        desc = "Shared description (provider: fred, yfinance)"
        result = _extract_provider_description(desc, "fred")
        assert result == "Shared description"

    def test_provider_at_end_of_marker(self):
        """Test provider listed last in comma-separated list."""
        desc = "Description text (provider: other, fred)"
        result = _extract_provider_description(desc, "fred")
        assert result == "Description text"

    def test_empty_description(self):
        """Test handling of empty description."""
        result = _extract_provider_description("", "fred")
        assert result == ""

    def test_fallback_to_general_description(self):
        """Test fallback when provider not found in markers."""
        desc = "General description (provider: other_provider)"
        result = _extract_provider_description(desc, "fred")
        assert result == "General description"


class TestProcessParameterWithSingleProvider:
    """Tests for process_parameter function with single_provider parameter."""

    def test_provider_specific_default_extracted(self):
        """Test that provider-specific default is extracted when single_provider is set."""
        param = {
            "name": "country",
            "description": "Country for fred (provider: fred); Country for other (provider: other)",
            "schema": {
                "fred": {"default": "united_states"},
                "other": {"default": "germany"},
            },
        }
        result = process_parameter(param, ["fred", "other"], single_provider="fred")
        assert result["value"] == "united_states"
        assert (
            "fred" in result["description"].lower()
            or "country" in result["description"].lower()
        )

    def test_global_default_used_when_no_provider_specific(self):
        """Test that global default is used when provider has no specific default."""
        param = {
            "name": "limit",
            "description": "Limit results",
            "default": 100,
            "schema": {},
        }
        result = process_parameter(param, ["fred", "other"], single_provider="fred")
        assert result["value"] == 100

    def test_global_default_skipped_when_other_providers_have_defaults(self):
        """Test that global default is skipped when other providers have specific defaults."""
        param = {
            "name": "topic",
            "description": "Topic param",
            "default": "general_default",
            "schema": {
                "other_provider": {"default": "specific_default"},
            },
        }
        result = process_parameter(
            param, ["fred", "other_provider"], single_provider="fred"
        )
        # fred should not inherit global default because other_provider has a specific one
        assert result["value"] is None

    def test_provider_specific_description_extracted(self):
        """Test that provider-specific description is extracted."""
        param = {
            "name": "indicator",
            "description": "Fred indicator description (provider: fred); Other indicator (provider: other)",
            "schema": {},
        }
        result = process_parameter(param, ["fred", "other"], single_provider="fred")
        assert "Fred indicator" in result["description"]
        assert "Other" not in result["description"]

    def test_no_single_provider_uses_general_description(self):
        """Test that without single_provider, general description is used."""
        param = {
            "name": "symbol",
            "description": "General symbol description (provider: fred); Other desc (provider: other)",
            "schema": {},
        }
        result = process_parameter(param, ["fred", "other"], single_provider=None)
        assert result["description"] == "General symbol description"


class TestGetQuerySchemaWithSingleProvider:
    """Tests for get_query_schema_for_widget with single_provider parameter."""

    def test_single_provider_passed_to_process_parameter(self, mock_openapi_json):
        """Test that single_provider is passed through to process_parameter."""
        # Use a route that has provider-specific params
        route = "/api/v1/economy/cpi"
        query_schema, _ = get_query_schema_for_widget(
            mock_openapi_json, route, single_provider="fred"
        )
        country_param = next(
            (p for p in query_schema if p["parameter_name"] == "country"), None
        )
        if country_param:
            # Should have the default value for fred provider
            assert country_param.get("value") is not None or country_param.get(
                "optional"
            )


if __name__ == "__main__":
    pytest.main()
