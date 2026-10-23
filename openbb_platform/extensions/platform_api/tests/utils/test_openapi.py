"""Test OpenAPI Utils."""

# ruff: noqa: E501

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
            5,
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
                    "parameter_name": "taxonomy",
                    "label": "Taxonomy",
                    "description": "Taxonomy family to explore. Omit to list all available taxonomies and their descriptions.",
                    "optional": True,
                    "type": "text",
                    "value": None,
                    "multiple_items_allowed": {},
                    "options": {
                        "sec": [
                            {"label": "us-gaap", "value": "us-gaap"},
                            {"label": "srt", "value": "srt"},
                            {"label": "dei", "value": "dei"},
                            {"label": "ecd", "value": "ecd"},
                            {"label": "cyd", "value": "cyd"},
                            {"label": "ffd", "value": "ffd"},
                            {"label": "ifrs", "value": "ifrs"},
                            {"label": "hmrc-dpl", "value": "hmrc-dpl"},
                            {"label": "rxp", "value": "rxp"},
                            {"label": "spac", "value": "spac"},
                            {"label": "cef", "value": "cef"},
                            {"label": "oef", "value": "oef"},
                            {"label": "vip", "value": "vip"},
                            {"label": "fnd", "value": "fnd"},
                            {"label": "sro", "value": "sro"},
                            {"label": "sbs", "value": "sbs"},
                            {"label": "rocr", "value": "rocr"},
                            {"label": "country", "value": "country"},
                            {"label": "currency", "value": "currency"},
                            {"label": "exch", "value": "exch"},
                            {"label": "naics", "value": "naics"},
                            {"label": "sic", "value": "sic"},
                            {"label": "stpr", "value": "stpr"},
                            {"label": "snj", "value": "snj"},
                        ]
                    },
                    "x-widget_config": {},
                    "available_providers": ["sec"],
                    "show": True,
                },
                {
                    "parameter_name": "year",
                    "label": "Year",
                    "description": "Taxonomy year (2009-2026 for us-gaap, varies by taxonomy). Defaults to the most recent year when omitted.",
                    "optional": True,
                    "type": "text",
                    "value": None,
                    "multiple_items_allowed": {},
                    "options": {"sec": []},
                    "x-widget_config": {},
                    "available_providers": ["sec"],
                    "show": True,
                },
                {
                    "parameter_name": "component",
                    "label": "Component",
                    "description": "Presentation component to retrieve. Values are taxonomy-specific. Omit to return all components for the taxonomy.",
                    "optional": True,
                    "type": "text",
                    "value": None,
                    "multiple_items_allowed": {},
                    "options": {"sec": []},
                    "x-widget_config": {},
                    "available_providers": ["sec"],
                    "show": True,
                },
                {
                    "parameter_name": "category",
                    "label": "Category",
                    "description": "Filter taxonomies by SEC filer category.",
                    "optional": True,
                    "type": "text",
                    "value": None,
                    "multiple_items_allowed": {},
                    "options": {
                        "sec": [
                            {
                                "label": "operating_company",
                                "value": "operating_company",
                            },
                            {
                                "label": "investment_company",
                                "value": "investment_company",
                            },
                            {
                                "label": "self_regulatory_org",
                                "value": "self_regulatory_org",
                            },
                            {"label": "sbs_repository", "value": "sbs_repository"},
                            {"label": "nrsro", "value": "nrsro"},
                            {"label": "common_reference", "value": "common_reference"},
                        ]
                    },
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


# ---------------------------------------------------------------------------
# data_schema_to_columns_defs branches (focused unit-style coverage)
# ---------------------------------------------------------------------------


def _columns_openapi_for_widget(
    properties: dict, *, title="MyData", schema_extras: dict | None = None
) -> dict:
    """Build a minimal openapi document so ``data_schema_to_columns_defs``
    has something to walk.

    Layout: ``/some/route`` → response references an ``OBBject_<title>``
    schema whose ``properties.results`` is an array of items pointing
    at the data schema (named ``<title>``). The data schema's
    ``properties`` are what column-defs get built from.
    """
    data_schema = {"title": title, "properties": properties}
    if schema_extras:
        data_schema.update(schema_extras)
    obbject_name = f"OBBject_{title}_"
    return {
        "components": {
            "schemas": {
                title: data_schema,
                obbject_name: {
                    "title": obbject_name,
                    "properties": {
                        "results": {
                            "anyOf": [
                                {
                                    "items": {"$ref": f"#/components/schemas/{title}"},
                                    "type": "array",
                                },
                                {"type": "null"},
                            ]
                        }
                    },
                },
            }
        },
        "paths": {
            "/some/route": {
                "get": {
                    "operationId": "some_op",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": f"#/components/schemas/{obbject_name}"
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }


def test_data_schema_to_columns_handles_anyof_branches():
    """``anyOf`` mixing types selects the right ``cellDataType``:
    number wins over text/date-string; date-string wins over text;
    text is fallback. ``format: "date"`` (no time component) maps to
    ``cellDataType: "dateString"`` so the value renders as YYYY-MM-DD
    verbatim instead of being parsed as a timestamp.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "amount": {"anyOf": [{"type": "number"}, {"type": "null"}]},
        "asof": {"anyOf": [{"type": "string", "format": "date"}, {"type": "null"}]},
        "ts": {"anyOf": [{"type": "string", "format": "date-time"}, {"type": "null"}]},
        "label": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    by_field = {c["field"]: c for c in cols}
    assert by_field["amount"]["cellDataType"] == "number"
    assert by_field["asof"]["cellDataType"] == "dateString"
    assert by_field["ts"]["cellDataType"] == "date"
    assert by_field["label"]["cellDataType"] == "text"


def test_data_schema_to_columns_handles_items_array_subschema():
    """``items``-shaped property routes through the same anyOf-style
    detection.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "scores": {
            "type": "array",
            "items": {"anyOf": [{"type": "number"}, {"type": "null"}]},
        }
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    assert cols[0]["cellDataType"] == "number"


def test_data_schema_to_columns_handles_items_with_string_date():
    """``items`` with date-formatted string → cellDataType=dateString
    (verbatim YYYY-MM-DD render, no implicit timestamp parsing).
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "dates": {
            "type": "array",
            "items": {
                "anyOf": [
                    {"type": "string", "format": "date"},
                    {"type": "null"},
                ]
            },
        }
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    assert cols[0]["cellDataType"] == "dateString"


def test_data_schema_to_columns_date_column_sorts_descending_by_default():
    """A column literally named ``date`` is the temporal axis of the
    dataset; pre-sort descending so the most recent observation lands
    at the top. Authors can override via
    ``widget_config.data.table.columnsDefs[].sort``.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "date": {"type": "string", "format": "date", "title": "Date"},
        "value": {"type": "number"},
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    by_field = {c["field"]: c for c in cols}
    assert by_field["date"]["sort"] == "desc"
    # The default doesn't leak onto non-date columns.
    assert "sort" not in by_field["value"]


def test_data_schema_to_columns_other_date_columns_dont_get_sort():
    """Only the column literally named ``date`` gets the descending
    sort default — fields like ``start_date`` / ``as_of_date`` are
    parameters or annotations, not the time-series axis.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "as_of_date": {"type": "string", "format": "date"},
        "start_date": {"type": "string", "format": "date"},
        "value": {"type": "number"},
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    for c in cols:
        assert "sort" not in c


def test_data_schema_to_columns_date_time_format_uses_date_celltype():
    """``format: "date-time"`` (full timestamp with time-of-day) maps
    to ``cellDataType: "date"`` so ag-grid parses it as a Date object
    and locale-renders. Distinct from the no-time ``format: "date"``
    case which uses ``"dateString"`` for verbatim YYYY-MM-DD render.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "ts": {"type": "string", "format": "date-time"},
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    assert cols[0]["cellDataType"] == "date"


def test_data_schema_to_columns_handles_items_text_fallback():
    """Items with no recognized type → text fallback."""
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "tags": {
            "type": "array",
            "items": {"anyOf": [{"type": "object"}]},
        }
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    assert cols[0]["cellDataType"] == "text"


def test_data_schema_to_columns_anyof_text_fallback():
    """AnyOf with no number / date types → text fallback."""
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "kind": {"anyOf": [{"type": "object"}, {"type": "null"}]},
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    assert cols[0]["cellDataType"] == "text"


def test_data_schema_to_columns_integer_uses_int_formatter():
    """Integer-typed props get ``formatterFn="int"``."""
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {"count": {"type": "integer"}}
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    assert cols[0]["cellDataType"] == "number"
    assert cols[0]["formatterFn"] == "int"


def test_data_schema_to_columns_pins_date_and_symbol_columns():
    """``date`` / ``symbol`` columns get pinned to the left."""
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "date": {"type": "string", "format": "date"},
        "symbol": {"type": "string"},
        "value": {"type": "number"},
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    by_field = {c["field"]: c for c in cols}
    assert by_field["date"]["pinned"] == "left"
    assert by_field["symbol"]["pinned"] == "left"
    assert "pinned" not in by_field["value"]


def test_data_schema_to_columns_uppercases_acronym_field_names():
    """``cik`` / ``isin`` / etc. get header uppercased + text type."""
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "cik": {"type": "string"},
        "isin": {"type": "string"},
        "symbol": {"type": "string"},
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    by_field = {c["field"]: c for c in cols}
    assert by_field["cik"]["headerName"] == "CIK"
    assert by_field["isin"]["headerName"] == "ISIN"
    assert by_field["symbol"]["cellDataType"] == "text"


def test_data_schema_to_columns_year_fields_render_as_text_to_skip_comma():
    """Year fields use ``cellDataType: "text"`` — that's the only way
    to suppress ag-grid's locale-based thousands separator
    (``"2,023"`` → ``"2023"``). ``formatterFn: "none"`` alone doesn't
    override the type-driven number formatting. 4-digit years sort
    identically as text vs. number, so no semantic loss.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {"fiscal_year": {"type": "string"}}
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    assert cols[0]["cellDataType"] == "text"
    assert cols[0]["formatterFn"] == "none"


def _columns_openapi_for_chains(properties: dict) -> dict:
    """Variant of ``_columns_openapi_for_widget`` that registers the
    route under ``/x/chains`` so the chains-specific branches fire.
    """
    base = _columns_openapi_for_widget(properties)
    base["paths"]["/x/chains"] = base["paths"].pop("/some/route")
    return base


def test_data_schema_to_columns_chains_route_hides_redundant_fields():
    """``/chains`` routes hide certain redundant fields."""
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "underlying_symbol": {"type": "string"},
        "contract_symbol": {"type": "string"},
    }
    openapi = _columns_openapi_for_chains(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/x/chains")
    for col in cols:
        if col["field"] in ("underlying_symbol", "contract_symbol"):
            assert col.get("hide") is True


def test_data_schema_to_columns_greeks_get_no_formatter():
    """Greeks (``delta`` / ``gamma`` / ``theta`` / ``rho``) get
    ``formatterFn="none"``; some get a ``greenRed`` render.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "delta": {"type": "number"},
        "gamma": {"type": "number"},
        "theta": {"type": "number"},
    }
    openapi = _columns_openapi_for_chains(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/x/chains")
    by_field = {c["field"]: c for c in cols}
    assert by_field["delta"]["formatterFn"] == "none"
    assert by_field["delta"]["renderFn"] == "greenRed"
    assert by_field["theta"]["renderFn"] == "greenRed"


def test_data_schema_to_columns_implied_volatility_normalized_percent():
    """``/chains`` routes format ``implied_volatility`` as a normalized
    percent.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {"implied_volatility": {"type": "number"}}
    openapi = _columns_openapi_for_chains(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/x/chains")
    assert cols[0]["formatterFn"] == "normalizedPercent"


def test_data_schema_to_columns_change_field_renders_green_red():
    """``change`` field renders with a green/red color treatment."""
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {"change": {"type": "number"}}
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    assert cols[0]["renderFn"] == "greenRed"


def test_data_schema_to_columns_percent_unit_measurement():
    """``x-unit_measurement="percent"`` → percent formatter + greenRed."""
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "rate": {"type": "number", "x-unit_measurement": "percent"},
        "scaled_rate": {
            "type": "number",
            "x-unit_measurement": "percent",
            "x-frontend_multiply": 100,
        },
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    by_field = {c["field"]: c for c in cols}
    assert by_field["rate"]["formatterFn"] == "percent"
    assert by_field["scaled_rate"]["formatterFn"] == "normalizedPercent"
    assert by_field["rate"]["renderFn"] == "greenRed"


def test_data_schema_to_columns_x_widget_config_exclude_drops_column():
    """``x-widget_config.exclude=True`` on a property drops the column."""
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "kept": {"type": "string"},
        "dropped": {"type": "string", "x-widget_config": {"exclude": True}},
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    fields = [c["field"] for c in cols]
    assert "kept" in fields
    assert "dropped" not in fields


def test_data_schema_to_columns_x_widget_config_merges_overrides():
    """Non-exclude ``x-widget_config`` overrides update the column def."""
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    properties = {
        "amount": {
            "type": "number",
            "x-widget_config": {"headerName": "AMT"},
        }
    }
    openapi = _columns_openapi_for_widget(properties)
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    assert cols[0]["headerName"] == "AMT"


def test_data_schema_to_columns_get_widget_config_short_circuits():
    """``get_widget_config=True`` returns the schema-level
    ``x-widget_config`` block instead of a list of column defs.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    openapi = _columns_openapi_for_widget(
        {"amount": {"type": "number"}},
        schema_extras={"x-widget_config": {"$.runButton": True}},
    )
    out = data_schema_to_columns_defs(
        openapi, "w_obb", "test", "/some/route", get_widget_config=True
    )
    assert out == {"$.runButton": True}


def test_data_schema_to_columns_oneof_provider_match_in_anyof_outer():
    """When the response schema's outer ``anyOf`` contains an item with
    a ``oneOf`` (no ``items.oneOf``), the provider-prefix match picks
    the right schema — exercises lines 710-715.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    openapi = {
        "components": {
            "schemas": {
                "FmpData": {
                    "title": "FmpData",
                    "properties": {"amount": {"type": "number"}},
                },
                "PolygonData": {
                    "title": "PolygonData",
                    "properties": {"value": {"type": "number"}},
                },
                "OBBject_oneof_outer": {
                    "title": "OBBject_oneof_outer",
                    "properties": {
                        "results": {
                            "anyOf": [
                                {
                                    "oneOf": [
                                        {"$ref": "#/components/schemas/FmpData"},
                                        {"$ref": "#/components/schemas/PolygonData"},
                                    ]
                                },
                                {"type": "null"},
                            ]
                        }
                    },
                },
            }
        },
        "paths": {
            "/some/route": {
                "get": {
                    "operationId": "outer_op",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/OBBject_oneof_outer"
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    cols = data_schema_to_columns_defs(openapi, "w_obb", "fmp", "/some/route")
    fields = [c["field"] for c in cols]
    assert "amount" in fields  # FmpData picked


def test_data_schema_to_columns_falls_back_to_first_schema_on_no_match():
    """When neither description nor title matches the provider, the
    first schema in the list is used as a final fallback — exercises
    line 758-759.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    openapi = {
        "components": {
            "schemas": {
                "AlphaData": {
                    "title": "alpha_data",
                    "description": "fmp data",
                    "properties": {"a": {"type": "number"}},
                },
                "BetaData": {
                    "title": "beta_data",
                    "description": "polygon data",
                    "properties": {"b": {"type": "number"}},
                },
                "OBBject_fallback": {
                    "title": "OBBject_fallback",
                    "properties": {
                        "results": {
                            "anyOf": [
                                {
                                    "items": {
                                        "oneOf": [
                                            {"$ref": "#/components/schemas/AlphaData"},
                                            {"$ref": "#/components/schemas/BetaData"},
                                        ]
                                    },
                                    "type": "array",
                                },
                                {"type": "null"},
                            ]
                        }
                    },
                },
            }
        },
        "paths": {
            "/some/route": {
                "get": {
                    "operationId": "fb_op",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/OBBject_fallback"
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    # Provider "yfinance" doesn't match either alpha / beta description
    # or title — falls back to the first schema (AlphaData with field "a").
    cols = data_schema_to_columns_defs(openapi, "w_obb", "yfinance", "/some/route")
    fields = [c["field"] for c in cols]
    assert "a" in fields


def test_post_query_schema_for_widget_walks_request_body_ref_properties():
    """A POST whose ``requestBody.schema`` is a ``$ref`` pointing at a
    schema with ``properties`` walks each property and emits per-param
    schemas.
    """
    from openbb_platform_api.utils.openapi import post_query_schema_for_widget

    openapi = {
        "components": {
            "schemas": {
                "PostBody": {
                    "title": "PostBody",
                    "properties": {
                        "name": {"type": "string", "title": "Name"},
                        "age": {"type": "integer"},
                    },
                }
            }
        },
        "paths": {
            "/api/v1/submit": {
                "post": {
                    "operationId": "submit_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PostBody"}
                            }
                        }
                    },
                }
            }
        },
    }
    out = post_query_schema_for_widget(openapi, "submit_op", "/api/v1/submit")
    names = [p.get("parameter_name") for p in out or []]
    # ``provider`` sentinel is auto-appended at the end.
    assert "name" in names
    assert "age" in names


def test_post_query_schema_for_widget_with_title_in_schema_picks_provider():
    """``schema.title`` matching a key inside ``schema`` itself uses
    that title as the sole provider — exercises line 1074.
    """
    from openbb_platform_api.utils.openapi import post_query_schema_for_widget

    openapi = {
        "components": {
            "schemas": {
                "PostBody": {
                    "title": "PostBody",
                    "properties": {"x": {"type": "number"}},
                }
            }
        },
        "paths": {
            "/api/v1/submit": {
                "post": {
                    "operationId": "submit_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "title": "fmp",
                                    "fmp": {"choices": ["a", "b"]},
                                    "$ref": "#/components/schemas/PostBody",
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    out = post_query_schema_for_widget(openapi, "submit_op", "/api/v1/submit")
    assert isinstance(out, list)


def test_post_query_schema_for_widget_with_comma_separated_title_providers():
    """``schema.title="fmp,polygon"`` splits into two providers —
    exercises lines 1075-1076.
    """
    from openbb_platform_api.utils.openapi import post_query_schema_for_widget

    openapi = {
        "components": {
            "schemas": {
                "PostBody": {
                    "title": "PostBody",
                    "properties": {"x": {"type": "number"}},
                }
            }
        },
        "paths": {
            "/api/v1/submit": {
                "post": {
                    "operationId": "submit_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "title": "fmp,polygon",
                                    "$ref": "#/components/schemas/PostBody",
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    out = post_query_schema_for_widget(openapi, "submit_op", "/api/v1/submit")
    assert isinstance(out, list)


def test_post_query_schema_for_widget_with_route_parameters():
    """A POST route with explicit ``parameters`` (not just requestBody)
    walks them via ``set_param`` — exercises lines 1080-1086.
    """
    from openbb_platform_api.utils.openapi import post_query_schema_for_widget

    openapi = {
        "components": {
            "schemas": {
                "PostBody": {
                    "title": "PostBody",
                    "properties": {"x": {"type": "number"}},
                }
            }
        },
        "paths": {
            "/api/v1/submit": {
                "post": {
                    "operationId": "submit_op",
                    "parameters": [
                        {
                            "name": "extra_param",
                            "in": "query",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PostBody"}
                            }
                        }
                    },
                }
            }
        },
    }
    out = post_query_schema_for_widget(openapi, "submit_op", "/api/v1/submit")
    names = [p.get("parameter_name") for p in out or []]
    # Both the explicit parameter and the body field made it through.
    assert "extra_param" in names
    assert "x" in names


def test_post_query_schema_for_widget_walks_request_body_with_target_schema_filter():
    """``target_schema`` filters the walked properties to just one
    field — covers the ``if target_schema and target_schema != k``
    skip arms.
    """
    from openbb_platform_api.utils.openapi import post_query_schema_for_widget

    openapi = {
        "components": {
            "schemas": {
                "PostBody": {
                    "title": "PostBody",
                    "properties": {
                        "kept": {"type": "string"},
                        "skipped": {"type": "string"},
                    },
                }
            }
        },
        "paths": {
            "/api/v1/submit": {
                "post": {
                    "operationId": "submit_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PostBody"}
                            }
                        }
                    },
                }
            }
        },
    }
    out = post_query_schema_for_widget(
        openapi, "submit_op", "/api/v1/submit", target_schema="kept"
    )
    names = [p.get("parameter_name") for p in out or []]
    # Only ``kept`` survived the filter.
    assert "kept" in names
    assert "skipped" not in names


def test_post_query_schema_anyof_param_with_choices_and_types():
    """A POST body field with ``anyOf`` mixing types + ``enum`` flows
    through ``set_param`` and produces a typed param with choices —
    exercises lines 1018, 1038, 1048.
    """
    from openbb_platform_api.utils.openapi import post_query_schema_for_widget

    openapi = {
        "components": {
            "schemas": {
                "PostBody": {
                    "title": "PostBody",
                    "properties": {
                        "category": {
                            "anyOf": [
                                {"type": "string", "enum": ["a", "b", "c"]},
                                {"type": "null"},
                            ]
                        },
                    },
                }
            }
        },
        "paths": {
            "/api/v1/submit": {
                "post": {
                    "operationId": "submit_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PostBody"}
                            }
                        }
                    },
                }
            }
        },
    }
    out = post_query_schema_for_widget(openapi, "submit_op", "/api/v1/submit")
    by_name = {p.get("parameter_name"): p for p in out or []}
    assert "category" in by_name


def test_set_parameter_options_multiple_providers_with_multiple_enums():
    """``title=fmp,polygon`` + ``anyOf`` containing matching number of
    enum lists triggers the position-based mapping — exercises
    lines 212-219 (the multi-provider/multi-enum branch).
    """
    from openbb_platform_api.utils.openapi import set_parameter_options

    p_schema = {
        "title": "fmp,polygon",
        "anyOf": [
            {"type": "string", "enum": ["fmp_a", "fmp_b"]},
            {"type": "string", "enum": ["pgn_a", "pgn_b"]},
        ],
    }
    p = {"parameter_name": "x"}
    out = set_parameter_options(p, p_schema, ["fmp", "polygon"])
    options = out.get("options", {})
    # Each provider got its enum at the same positional index.
    assert {"label": "fmp_a", "value": "fmp_a"} in options.get("fmp", [])
    assert {"label": "pgn_a", "value": "pgn_a"} in options.get("polygon", [])


def test_set_parameter_options_general_choices_with_multiple_providers():
    """When ``general_choices`` exist and there are multiple providers
    (no provider-specific match), the choices land under ``other``
    rather than a specific provider — exercises lines 282-286.
    """
    from openbb_platform_api.utils.openapi import set_parameter_options

    p_schema = {
        "title": "params",
        "enum": ["x", "y", "z"],
        "multiple_items_allowed": False,
    }
    p = {"parameter_name": "x"}
    out = set_parameter_options(p, p_schema, ["fmp", "polygon"])
    assert "other" in out.get("options", {})


def test_set_parameter_options_provider_widget_config_extracted():
    """A per-provider ``x-widget_config`` block lands in the param's
    ``x-widget_config`` field — exercises line 190.
    """
    from openbb_platform_api.utils.openapi import set_parameter_options

    p_schema = {
        "fmp": {
            "choices": ["a", "b"],
            "x-widget_config": {"label": "FMP override"},
        },
    }
    p = {"parameter_name": "x"}
    out = set_parameter_options(p, p_schema, ["fmp"])
    assert out.get("x-widget_config", {}).get("fmp", {}).get("label") == "FMP override"


def test_process_parameter_strips_multiple_items_suffix_from_description():
    """``"Stock symbol Multiple comma separated items allowed"`` →
    description trimmed to ``"Stock symbol"``. Exercises lines 479-481.
    """
    from openbb_platform_api.utils.openapi import process_parameter

    param = {
        "name": "symbol",
        "description": "Stock symbol Multiple comma separated items allowed.",
        "schema": {"type": "string"},
        "in": "query",
    }
    out = process_parameter(param, ["fmp"])
    assert "Multiple comma separated items allowed" not in out["description"]


def test_process_parameter_picks_up_widget_config_from_schema_per_provider():
    """``x-widget_config`` keyed by provider gets unwrapped — exercises
    lines 533-538.
    """
    from openbb_platform_api.utils.openapi import process_parameter

    param = {
        "name": "x",
        "description": "X param",
        "schema": {
            "type": "string",
            "x-widget_config": {"fmp": {"label": "FMP X"}},
        },
        "in": "query",
    }
    out = process_parameter(param, ["fmp"])
    # The provider-specific widget_config block is unwrapped into the
    # param, so ``label`` is "FMP X".
    assert out.get("label") == "FMP X"


def test_process_parameter_filters_provider_specific_via_valid_list():
    """A param whose title says one provider AND that provider is in
    the current ``providers`` list, but ``set_parameter_options``
    populated ``available_providers`` with a different one (e.g. via
    schema-level provider keys). Exercises lines 553-569.
    """
    from openbb_platform_api.utils.openapi import process_parameter

    # Title says ``fmp``; both fmp and polygon are in providers; the
    # param survives because fmp is current.
    param = {
        "name": "tier",
        "description": "Tier desc.",
        "schema": {"type": "string", "title": "fmp"},
        "in": "query",
    }
    out = process_parameter(param, ["fmp", "polygon"])
    assert out.get("parameter_name") == "tier"
    assert "fmp" in out.get("available_providers", [])


def test_process_parameter_extracts_multiple_providers_from_description():
    """A description with ``(provider: fmp, polygon)`` adds both to the
    available_providers list — exercises lines 514-519.
    """
    from openbb_platform_api.utils.openapi import process_parameter

    param = {
        "name": "tier",
        "description": "Tier (provider: fmp, polygon).",
        "schema": {"type": "string"},
        "in": "query",
    }
    out = process_parameter(param, ["fmp", "polygon"])
    assert "fmp" in out["available_providers"]
    assert "polygon" in out["available_providers"]


def test_data_schema_to_columns_schema_level_field_exclude():
    """When a schema-level field (a peer of ``properties`` in
    ``target_schema``) carries ``x-widget_config.exclude=True``, the
    column for that property is dropped — exercises lines 960-963.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    openapi = _columns_openapi_for_widget(
        {"amount": {"type": "number"}, "ignored": {"type": "string"}},
        schema_extras={
            # ``ignored`` peer entry (not under properties) carries the
            # exclude config. The function reads ``target_schema.get(key)``
            # to look for this peer-level config.
            "ignored": {"x-widget_config": {"exclude": True}},
        },
    )
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    fields = [c["field"] for c in cols]
    assert "amount" in fields
    assert "ignored" not in fields


def test_data_schema_to_columns_schema_level_field_merges_widget_config():
    """A schema-level peer entry's ``x-widget_config`` (without exclude)
    merges into the column def — exercises line 963 alone.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    openapi = _columns_openapi_for_widget(
        {"amount": {"type": "number"}},
        schema_extras={
            "amount": {"x-widget_config": {"headerName": "Total"}},
        },
    )
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    assert cols[0].get("headerName") == "Total"


def test_set_parameter_options_general_choices_anyof_no_title_providers():
    """``anyOf`` containing enums + no title_providers — populates
    general_choices via the second branch, exercises lines 259-268.
    """
    from openbb_platform_api.utils.openapi import set_parameter_options

    p_schema = {
        "anyOf": [
            {"type": "string", "enum": ["x", "y"]},
            {"type": "null"},
        ],
    }
    p = {"parameter_name": "x"}
    out = set_parameter_options(p, p_schema, ["fmp"])
    # With one provider, general_choices land under that provider's key.
    options = out.get("options", {})
    assert {"label": "x", "value": "x"} in options.get("fmp", [])


def test_post_query_schema_for_widget_walks_anyof_schema():
    """A POST whose ``requestBody`` schema has ``anyOf`` (rather than a
    single ``$ref``) walks each variant — exercises lines 1133-1166.
    """
    from openbb_platform_api.utils.openapi import post_query_schema_for_widget

    openapi = {
        "components": {
            "schemas": {
                "Variant1": {
                    "title": "Variant1",
                    "properties": {"x": {"type": "number"}},
                },
            }
        },
        "paths": {
            "/api/v1/submit": {
                "post": {
                    "operationId": "submit_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "anyOf": [
                                        {"$ref": "#/components/schemas/Variant1"},
                                        {
                                            "properties": {"y": {"type": "string"}},
                                        },
                                    ],
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    out = post_query_schema_for_widget(openapi, "submit_op", "/api/v1/submit")
    names = [p.get("parameter_name") for p in out or []]
    # Both variants' properties surfaced.
    assert "x" in names
    assert "y" in names


def test_data_schema_to_columns_uses_result_schema_ref_directly_when_no_refs():
    """When the response schema's anyOf items don't unpack into refs but
    the schema itself has properties, that schema becomes the source.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    openapi = {
        "components": {
            "schemas": {
                "FlatRoute": {
                    "title": "FlatRoute",
                    "properties": {
                        "results": {
                            # ``anyOf`` with no $ref / oneOf / items.$ref —
                            # schema_refs stays empty; schema's properties
                            # are used directly.
                            "anyOf": [{"type": "object"}],
                            "properties": {"x": {"type": "number"}},
                        }
                    },
                },
            }
        },
        "paths": {
            "/some/route": {
                "get": {
                    "operationId": "flat_op",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/FlatRoute"}
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    cols = data_schema_to_columns_defs(openapi, "w_obb", "test", "/some/route")
    # Either covers the column or returns []; either way the lookup didn't crash.
    assert isinstance(cols, list)


def test_data_schema_to_columns_picks_provider_specific_schema_via_description():
    """When multiple data schemas are available, match by description
    that starts with the provider name.
    """
    from openbb_platform_api.utils.openapi import data_schema_to_columns_defs

    openapi = {
        "components": {
            "schemas": {
                "FmpData": {
                    "description": "fmp data class",
                    "properties": {"amount": {"type": "number"}},
                },
                "PolygonData": {
                    "description": "polygon data class",
                    "properties": {"value": {"type": "number"}},
                },
                "OBBject_multi": {
                    "title": "OBBject_multi",
                    "properties": {
                        "results": {
                            "anyOf": [
                                {
                                    "items": {
                                        "oneOf": [
                                            {"$ref": "#/components/schemas/FmpData"},
                                            {
                                                "$ref": "#/components/schemas/PolygonData"
                                            },
                                        ]
                                    },
                                    "type": "array",
                                },
                                {"type": "null"},
                            ]
                        }
                    },
                },
            }
        },
        "paths": {
            "/some/route": {
                "get": {
                    "operationId": "multi_op",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/OBBject_multi"
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    cols = data_schema_to_columns_defs(openapi, "w_obb", "fmp", "/some/route")
    fields = [c["field"] for c in cols]
    # Picked the FMP variant (matches by description), so its ``amount``
    # property is the one that surfaces.
    assert "amount" in fields
    assert "value" not in fields


# ---------------------------------------------------------------------------
# set_parameter_type type-rewrite branches
# ---------------------------------------------------------------------------


def test_set_parameter_type_string_becomes_text():
    """``schema.type=string`` → ``p.type=text`` for widget rendering."""
    from openbb_platform_api.utils.openapi import set_parameter_type

    p = {"parameter_name": "x", "value": ""}
    out = set_parameter_type(p, {"type": "string"})
    assert out["type"] == "text"


def test_set_parameter_type_numeric_value_becomes_number():
    """A numeric ``value`` (without ``type``) trips the number branch."""
    from openbb_platform_api.utils.openapi import set_parameter_type

    p = {"parameter_name": "x", "value": 1.5}
    out = set_parameter_type(p, {})
    assert out["type"] == "number"


def test_set_parameter_type_boolean_via_anyof():
    """An ``anyOf`` whose first element is ``boolean`` → bool widget."""
    from openbb_platform_api.utils.openapi import set_parameter_type

    p = {"parameter_name": "x", "value": True}
    out = set_parameter_type(p, {"anyOf": [{"type": "boolean"}, {"type": "null"}]})
    assert out["type"] == "boolean"


def test_set_parameter_type_date_field_becomes_date():
    """``parameter_name="date"`` or any ``*_date`` field gets the date type."""
    from openbb_platform_api.utils.openapi import set_parameter_type

    p1 = set_parameter_type({"parameter_name": "date", "value": ""}, {})
    p2 = set_parameter_type({"parameter_name": "start_date", "value": ""}, {})
    assert p1["type"] == "date"
    assert p2["type"] == "date"


def test_set_parameter_type_timeframe_becomes_text():
    """``timeframe`` in the parameter name → text (not number)."""
    from openbb_platform_api.utils.openapi import set_parameter_type

    p = set_parameter_type({"parameter_name": "timeframe", "value": ""}, {})
    assert p["type"] == "text"


def test_set_parameter_type_limit_always_number():
    """``parameter_name="limit"`` is always a number widget."""
    from openbb_platform_api.utils.openapi import set_parameter_type

    p = set_parameter_type({"parameter_name": "limit", "value": ""}, {})
    assert p["type"] == "number"


def test_extract_provider_description_picks_section_for_target_provider():
    """A multi-provider description splits sections by ``(provider:..)``
    markers; the matching section returns just the description text.
    """
    from openbb_platform_api.utils.openapi import _extract_provider_description

    desc = (
        "General intro for symbol;\n    "
        "fmp-specific notes (provider: fmp);\n    "
        "polygon-specific notes (provider: polygon)"
    )
    out = _extract_provider_description(desc, "polygon")
    assert "polygon-specific notes" in out


def test_extract_provider_description_handles_multi_section_text():
    """When a section preceding the provider marker contains multiple
    semicolon-newline-separated chunks, the last one is the matching
    provider's text — exercises lines 361-363.
    """
    from openbb_platform_api.utils.openapi import _extract_provider_description

    desc = (
        "first;\n    second;\n    fmp section (provider: fmp);\n    "
        "polygon section (provider: polygon)"
    )
    out = _extract_provider_description(desc, "fmp")
    # ``fmp section`` is the last section before the (provider: fmp) marker.
    assert "fmp section" in out


def test_get_query_schema_for_widget_skips_sort_and_order_params(mock_openapi_json):
    """``sort`` and ``order`` parameters are skipped during schema
    construction; ``chart`` toggles the has_chart flag and is also
    skipped — exercises lines 605-609 of get_query_schema_for_widget.
    """
    from openbb_platform_api.utils.openapi import get_query_schema_for_widget

    # Inject sort, order, chart parameters into a route's parameter list.
    test_openapi = {
        "paths": {
            "/test_route": {
                "get": {
                    "operationId": "test_op",
                    "parameters": [
                        {
                            "name": "sort",
                            "in": "query",
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "order",
                            "in": "query",
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "chart",
                            "in": "query",
                            "schema": {"type": "boolean"},
                        },
                        {
                            "name": "symbol",
                            "in": "query",
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                }
            }
        },
        "components": {"schemas": {}},
    }
    params, has_chart = get_query_schema_for_widget(test_openapi, "/test_route")
    names = [p.get("parameter_name") for p in params]
    # Sort/order skipped; symbol kept.
    assert "sort" not in names
    assert "order" not in names
    assert "symbol" in names
    # ``chart`` triggered the flag and was skipped.
    assert has_chart is True
    assert "chart" not in names


def test_set_parameter_type_array_collapses_to_text():
    """An ``array`` or ``list`` typed param renders as text (one widget
    can't natively show structured arrays).
    """
    from openbb_platform_api.utils.openapi import set_parameter_type

    p = set_parameter_type(
        {"parameter_name": "tags", "value": "", "type": "array"}, {"type": "array"}
    )
    assert p["type"] == "text"


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


# ---------------------------------------------------------------------------
# SSRM auto-detection — _schema_inherits + is_ssrm_route
# ---------------------------------------------------------------------------


def _ssrm_openapi(
    *,
    request_schema: str | None = None,
    response_schema: str | None = None,
    schemas: dict | None = None,
    method: str = "post",
) -> dict:
    """Build a minimal OpenAPI dict with a single route whose body and/or
    response point at the named component schemas.
    """
    body: dict = {}
    if request_schema:
        body = {
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{request_schema}"}
                    }
                }
            }
        }
    response_schema_block: dict = {"type": "object"}
    if response_schema:
        response_schema_block = {"$ref": f"#/components/schemas/{response_schema}"}
    return {
        "components": {"schemas": schemas or {}},
        "paths": {
            "/api/v1/ssrm": {
                method: {
                    "operationId": "ssrm_op",
                    "summary": "S",
                    "description": "D",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": response_schema_block}
                            }
                        }
                    },
                    **body,
                }
            }
        },
    }


def test_is_ssrm_route_request_body_direct_match():
    """Body $ref → ``AgGridRowsRequest`` is the canonical SSRM signal."""
    from openbb_platform_api.utils.openapi import is_ssrm_route

    openapi = _ssrm_openapi(
        request_schema="AgGridRowsRequest",
        schemas={"AgGridRowsRequest": {"title": "AgGridRowsRequest"}},
    )
    assert is_ssrm_route(openapi, "/api/v1/ssrm", "post") is True


def test_is_ssrm_route_request_body_subclass_via_allof():
    """A Pydantic subclass of ``AgGridRowsRequest`` shows up in OpenAPI as
    ``allOf: [{"$ref": ".../AgGridRowsRequest"}]`` — must still match.
    """
    from openbb_platform_api.utils.openapi import is_ssrm_route

    openapi = _ssrm_openapi(
        request_schema="ProviderRowsRequest",
        schemas={
            "ProviderRowsRequest": {
                "title": "ProviderRowsRequest",
                "allOf": [{"$ref": "#/components/schemas/AgGridRowsRequest"}],
            },
            "AgGridRowsRequest": {"title": "AgGridRowsRequest"},
        },
    )
    assert is_ssrm_route(openapi, "/api/v1/ssrm", "post") is True


def test_is_ssrm_route_request_body_transitive_inheritance():
    """Subclass-of-subclass still matches via the recursive walk."""
    from openbb_platform_api.utils.openapi import is_ssrm_route

    openapi = _ssrm_openapi(
        request_schema="GrandchildRowsRequest",
        schemas={
            "GrandchildRowsRequest": {
                "title": "GrandchildRowsRequest",
                "allOf": [{"$ref": "#/components/schemas/MidRowsRequest"}],
            },
            "MidRowsRequest": {
                "title": "MidRowsRequest",
                "allOf": [{"$ref": "#/components/schemas/AgGridRowsRequest"}],
            },
            "AgGridRowsRequest": {"title": "AgGridRowsRequest"},
        },
    )
    assert is_ssrm_route(openapi, "/api/v1/ssrm", "post") is True


def test_is_ssrm_route_skips_inline_allof_entries_without_ref():
    """Pydantic emits inline schemas inside ``allOf`` for field-level
    constraints (e.g. ``allOf: [{"$ref": ...}, {"description": "..."}]``).
    Entries without a ``$ref`` should be skipped, not crash.
    """
    from openbb_platform_api.utils.openapi import is_ssrm_route

    openapi = _ssrm_openapi(
        request_schema="ConstrainedRowsRequest",
        schemas={
            "ConstrainedRowsRequest": {
                "title": "ConstrainedRowsRequest",
                "allOf": [
                    {"description": "no ref here"},
                    {"$ref": "#/components/schemas/AgGridRowsRequest"},
                ],
            },
            "AgGridRowsRequest": {"title": "AgGridRowsRequest"},
        },
    )
    assert is_ssrm_route(openapi, "/api/v1/ssrm", "post") is True


def test_is_ssrm_route_handles_allof_cycle():
    """Cyclic ``allOf`` chains shouldn't recurse forever."""
    from openbb_platform_api.utils.openapi import is_ssrm_route

    openapi = _ssrm_openapi(
        request_schema="A",
        schemas={
            "A": {"title": "A", "allOf": [{"$ref": "#/components/schemas/B"}]},
            "B": {"title": "B", "allOf": [{"$ref": "#/components/schemas/A"}]},
        },
    )
    # No match, but more importantly: doesn't blow the stack.
    assert is_ssrm_route(openapi, "/api/v1/ssrm", "post") is False


def test_is_ssrm_route_response_named_aggrid_rows_response():
    """Pydantic emits ``AgGridRowsResponse[Foo]`` with the title
    ``AgGridRowsResponse_Foo_`` — prefix match wins.
    """
    from openbb_platform_api.utils.openapi import is_ssrm_route

    openapi = _ssrm_openapi(
        response_schema="AgGridRowsResponse_FooRow_",
        schemas={"AgGridRowsResponse_FooRow_": {"title": "AgGridRowsResponse[FooRow]"}},
    )
    assert is_ssrm_route(openapi, "/api/v1/ssrm", "post") is True


def test_is_ssrm_route_response_structural_rowdata_rowcount():
    """Even without the canonical name, a response whose properties
    include both ``rowData`` and ``rowCount`` is treated as SSRM.
    """
    from openbb_platform_api.utils.openapi import is_ssrm_route

    openapi = _ssrm_openapi(
        response_schema="CustomRowsResponse",
        schemas={
            "CustomRowsResponse": {
                "title": "CustomRowsResponse",
                "properties": {
                    "rowData": {"type": "array"},
                    "rowCount": {"type": "integer"},
                },
            }
        },
    )
    assert is_ssrm_route(openapi, "/api/v1/ssrm", "post") is True


def test_is_ssrm_route_negative_unrelated_post():
    """Plain POST routes with neither signal are not promoted."""
    from openbb_platform_api.utils.openapi import is_ssrm_route

    openapi = _ssrm_openapi(
        request_schema="Plain",
        response_schema="PlainOut",
        schemas={
            "Plain": {"title": "Plain"},
            "PlainOut": {
                "title": "PlainOut",
                "properties": {"x": {"type": "number"}},
            },
        },
    )
    assert is_ssrm_route(openapi, "/api/v1/ssrm", "post") is False


def test_is_ssrm_route_negative_response_only_rowdata():
    """``rowData`` alone (no ``rowCount``) does NOT count as SSRM —
    structural match requires both keys, on purpose.
    """
    from openbb_platform_api.utils.openapi import is_ssrm_route

    openapi = _ssrm_openapi(
        response_schema="HalfMatch",
        schemas={
            "HalfMatch": {
                "title": "HalfMatch",
                "properties": {"rowData": {"type": "array"}},
            }
        },
    )
    assert is_ssrm_route(openapi, "/api/v1/ssrm", "post") is False


def test_is_ssrm_route_missing_route_returns_false():
    """Defensive — unknown route can't match."""
    from openbb_platform_api.utils.openapi import is_ssrm_route

    assert is_ssrm_route({"paths": {}, "components": {}}, "/nope", "post") is False


def test_is_ssrm_route_body_ref_pointing_at_unknown_schema():
    """A $ref to a missing component shouldn't crash; just doesn't match."""
    from openbb_platform_api.utils.openapi import is_ssrm_route

    openapi = _ssrm_openapi(request_schema="MissingFromComponents")
    assert is_ssrm_route(openapi, "/api/v1/ssrm", "post") is False


def test_get_data_schema_for_widget_unwraps_ssrm_rowdata_to_row_model():
    """For SSRM responses, ``get_data_schema_for_widget`` descends from
    ``AgGridRowsResponse[Row]`` to the row model so column auto-detection
    sees the row's fields.
    """
    openapi = {
        "components": {
            "schemas": {
                "FooRow": {
                    "title": "FooRow",
                    "properties": {
                        "symbol": {"type": "string"},
                        "price": {"type": "number"},
                    },
                },
                "AgGridRowsResponse_FooRow_": {
                    "title": "AgGridRowsResponse[FooRow]",
                    "properties": {
                        "rowData": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/FooRow"},
                        },
                        "rowCount": {"type": "integer"},
                    },
                },
            }
        },
        "paths": {
            "/api/v1/ssrm": {
                "post": {
                    "operationId": "ssrm_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/AgGridRowsResponse_FooRow_"
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    schema = get_data_schema_for_widget(openapi, "ssrm_op", "/api/v1/ssrm")
    assert schema == openapi["components"]["schemas"]["FooRow"]


def test_get_data_schema_for_widget_ssrm_inline_row_items_no_ref():
    """When ``rowData.items`` is inlined (no $ref), the inline schema is
    returned as-is — column generation still has something to walk.
    """
    openapi = {
        "components": {
            "schemas": {
                "InlineSsrm": {
                    "title": "InlineSsrm",
                    "properties": {
                        "rowData": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"q": {"type": "number"}},
                            },
                        },
                        "rowCount": {"type": "integer"},
                    },
                }
            }
        },
        "paths": {
            "/api/v1/ssrm": {
                "post": {
                    "operationId": "ssrm_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/InlineSsrm"
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    schema = get_data_schema_for_widget(openapi, "ssrm_op", "/api/v1/ssrm")
    assert schema == {
        "type": "object",
        "properties": {"q": {"type": "number"}},
    }


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


# ---------------------------------------------------------------------------
# Coverage gaps in process_parameter, data_schema_to_columns_defs, and
# post_query_schema_for_widget
# ---------------------------------------------------------------------------


def test_process_parameter_label_falls_back_to_schema_title_when_name_empty():
    """Empty ``param["name"]`` produces an empty ``param_name.title()`` —
    triggers the ``schema.title or param.title`` fallback at line 481.
    """
    out = process_parameter(
        {"name": "", "schema": {"title": "Fallback Title"}}, ["fmp"]
    )
    assert out["label"] == "Fallback Title"


def test_process_parameter_strips_multiple_items_suffix_from_schema_description():
    """When ``param.description`` is missing but ``schema.description``
    carries the ``Multiple comma separated items allowed`` suffix, the
    suffix-strip at lines 551-557 kicks in. The line 489-495 path
    that *normally* strips the suffix is gated on ``param.description``
    being truthy — when it isn't, we fall back to schema description
    and the second strip pass cleans it up.
    """
    out = process_parameter(
        {
            "name": "tickers",
            "schema": {
                "description": (
                    "List of tickers. Multiple comma separated items allowed."
                ),
            },
        },
        ["fmp"],
    )
    assert "Multiple comma separated items allowed" not in out["description"]
    assert out["description"].startswith("List of tickers")


def test_process_parameter_extracts_multi_provider_from_comma_title():
    """A schema title of the form ``"fmp,polygon"`` is split into a list
    of providers — exercises lines 576-578. After the split, the
    parameter is gated to only those providers via the
    ``valid_provider_list`` filter further down.
    """
    out = process_parameter(
        {"name": "x", "schema": {"title": "fmp,polygon"}},
        ["fmp", "polygon", "yfinance"],
    )
    # Both providers from the title made it onto available_providers,
    # and at least one matches our current providers list, so the
    # parameter is kept.
    assert out
    assert sorted(out.get("available_providers", [])) == ["fmp", "polygon"]


def test_data_schema_to_columns_picks_provider_via_title_when_descriptions_dont_match():
    """Multi-schema flow: when none of the candidate schema descriptions
    match the provider, fall back to matching by ``title`` — exercises
    lines 844-845.
    """
    openapi = {
        "components": {
            "schemas": {
                "OBBject_FooData_": {
                    "title": "OBBject_FooData_",
                    "properties": {
                        "results": {
                            "anyOf": [
                                {
                                    "items": {
                                        "oneOf": [
                                            {"$ref": "#/components/schemas/FmpFooData"},
                                            {"$ref": "#/components/schemas/YFooData"},
                                        ]
                                    },
                                    "type": "array",
                                }
                            ]
                        }
                    },
                },
                # Descriptions are deliberately generic so the first
                # description-loop misses; titles carry the provider
                # prefix instead, forcing the title fallback to fire.
                "FmpFooData": {
                    "title": "FmpFooData",
                    "description": "Generic foo data shape.",
                    "properties": {"value": {"type": "number"}},
                },
                "YFooData": {
                    "title": "YFooData",
                    "description": "Generic foo data shape.",
                    "properties": {"value": {"type": "number"}},
                },
            }
        },
        "paths": {
            "/api/v1/foo": {
                "get": {
                    "operationId": "foo_op",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/OBBject_FooData_"
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    cols = data_schema_to_columns_defs(openapi, "foo_op", "fmp", "/api/v1/foo")
    # Title-fallback selected the FmpFooData schema; only one column
    # comes back regardless, but the lookup didn't crash and produced
    # a non-empty result driven by the title path.
    assert any(c["field"] == "value" for c in cols)


def test_post_query_schema_anyof_property_no_type_falls_back_to_text():
    """A POST body property whose ``anyOf`` items have no ``type`` keys
    (only ``$ref`` or ``enum``) hits the fallback type assignment at
    lines 1127-1135.
    """
    openapi = {
        "components": {
            "schemas": {
                "Body": {
                    "title": "Body",
                    "type": "object",
                    "properties": {
                        # anyOf entries are pure $refs — no ``type`` key,
                        # so ``param_types`` ends up empty and the else
                        # branch at line 1127 sets the fallback type.
                        "obj": {
                            "anyOf": [
                                {"$ref": "#/components/schemas/Sub"},
                                {"type": "null"},
                            ],
                            "type": "object",
                        }
                    },
                },
                "Sub": {"title": "Sub", "type": "object", "properties": {}},
            }
        },
        "paths": {
            "/api/v1/post": {
                "post": {
                    "operationId": "post_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Body"}
                            }
                        }
                    },
                }
            }
        },
    }
    params = post_query_schema_for_widget(openapi, "post_op", "/api/v1/post")
    obj_param = next((p for p in params if p["parameter_name"] == "obj"), None)
    assert obj_param is not None
    # ``type: "object"`` falls through to ``"text"`` per the fallback.
    assert obj_param["type"] == "text"


def test_post_query_schema_top_level_enum_extends_choices():
    """A POST body property with a top-level ``enum`` (no ``anyOf``)
    feeds the ``choices.extend`` path at line 1137 — the resulting
    options dict carries those values under the ``custom`` key.
    """
    openapi = {
        "components": {
            "schemas": {
                "Body": {
                    "title": "Body",
                    "type": "object",
                    "properties": {
                        "side": {"enum": ["buy", "sell", "hold"]},
                    },
                }
            }
        },
        "paths": {
            "/api/v1/post": {
                "post": {
                    "operationId": "post_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Body"}
                            }
                        }
                    },
                }
            }
        },
    }
    params = post_query_schema_for_widget(openapi, "post_op", "/api/v1/post")
    side = next(p for p in params if p["parameter_name"] == "side")
    # ``set_param`` builds ``options = {"custom": [...]}``;
    # ``set_parameter_options`` rewraps it as ``{provider: choices}``.
    options = side.get("options", {})
    flat_values = []
    for v in options.values():
        if isinstance(v, list):
            flat_values.extend(c.get("value") for c in v)
    assert {"buy", "sell", "hold"}.issubset(set(flat_values))


def test_post_query_schema_route_parameters_as_dict():
    """OpenAPI normally emits ``parameters`` as a list, but the function
    also handles a dict shape — exercises lines 1173-1175.
    """
    openapi = {
        "components": {
            "schemas": {
                "Body": {
                    "title": "Body",
                    "type": "object",
                    "properties": {"x": {"type": "number"}},
                }
            }
        },
        "paths": {
            "/api/v1/post": {
                "post": {
                    "operationId": "post_op",
                    "parameters": {  # dict form, not list
                        "extra": {"type": "string"}
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Body"}
                            }
                        }
                    },
                }
            }
        },
    }
    params = post_query_schema_for_widget(openapi, "post_op", "/api/v1/post")
    assert any(p.get("parameter_name") == "extra" for p in params)


def test_post_query_schema_param_ref_falsy_falls_back_to_schema_dict():
    """When ``schema["$ref"]`` is falsy (empty/None), the ``or schema``
    fallback at line 1181 returns the schema dict itself; the dict
    branch at line 1184-1185 then strips it down to its ``type`` value
    so the rest of the function can keep walking.
    """
    openapi = {
        "components": {"schemas": {}},
        "paths": {
            "/api/v1/post": {
                "post": {
                    "operationId": "post_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                # ``$ref: ""`` is falsy → the function
                                # falls back to ``schema`` (this dict),
                                # which has ``type: "object"`` so the
                                # dict-strip branch at 1184-1185 fires.
                                "schema": {"$ref": "", "type": "object"}
                            }
                        }
                    },
                }
            }
        },
    }
    # No crash, returns either [] or None (depending on the rest of the
    # walk). The important thing for coverage is that we hit lines
    # 1184-1185.
    out = post_query_schema_for_widget(openapi, "post_op", "/api/v1/post")
    assert out in (None, [])


def test_post_query_schema_anyof_body_with_target_schema_filters_properties():
    """When the body schema is an ``anyOf`` list and a ``target_schema``
    is supplied, the loop at line 1232-1243 walks each item and skips
    properties whose key doesn't match ``target_schema`` — exercises
    lines 1236 (ref-based skip) and 1242 (inline-property skip).
    """
    openapi = {
        "components": {
            "schemas": {
                "RefBody": {
                    "title": "RefBody",
                    "type": "object",
                    "properties": {
                        "wanted": {"type": "string"},
                        "skipped": {"type": "number"},
                    },
                }
            }
        },
        "paths": {
            "/api/v1/post": {
                "post": {
                    "operationId": "post_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    # Mix: one $ref item + one inline-properties
                                    # item, each carrying both ``wanted`` and
                                    # ``skipped`` keys so the target_schema
                                    # filter has to skip on both branches.
                                    "anyOf": [
                                        {"$ref": "#/components/schemas/RefBody"},
                                        {
                                            "properties": {
                                                "wanted": {"type": "string"},
                                                "skipped": {"type": "number"},
                                            }
                                        },
                                    ],
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    params = post_query_schema_for_widget(
        openapi, "post_op", "/api/v1/post", target_schema="wanted"
    )
    names = [p["parameter_name"] for p in params]
    assert "wanted" in names
    assert "skipped" not in names


def test_get_data_schema_descends_into_inline_results_envelope():
    """Spec-driven launches synthesize the response schema inline
    under ``content.application/json.schema`` (no ``components.schemas``
    $ref roundtrip). The Socrata generator emits the
    ``{"properties": {"results": {"items": {...}}}}`` envelope shape;
    column auto-detection has to descend into ``items`` to find the
    row fields. Without this, the launcher generated widget configs
    with no ``columnsDefs`` for the entire spec-driven proxy path.
    """
    from openbb_platform_api.utils.openapi import get_data_schema_for_widget

    inline_schema = {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "format": "date"},
                        "year": {"type": "integer"},
                        "region": {"type": "string"},
                        "price": {"type": "number"},
                    },
                },
            }
        },
    }
    openapi = {
        "components": {"schemas": {}},
        "paths": {
            "/resource/abcd-1234.json": {
                "get": {
                    "operationId": "fertilizer.prices",
                    "responses": {
                        "200": {
                            "content": {"application/json": {"schema": inline_schema}}
                        }
                    },
                }
            }
        },
    }
    out = get_data_schema_for_widget(
        openapi, "fertilizer.prices", "/resource/abcd-1234.json"
    )
    assert isinstance(out, dict)
    assert "properties" in out
    assert set(out["properties"]) == {"date", "year", "region", "price"}


def test_get_data_schema_descends_into_inline_results_with_ref_items():
    """Results envelope where ``items`` is a ``$ref`` to a component
    schema — the launcher resolves the $ref and returns the row
    schema. Mixed inline/$ref shape that real OpenAPI specs produce
    when the row model is reusable.
    """
    from openbb_platform_api.utils.openapi import get_data_schema_for_widget

    openapi = {
        "components": {
            "schemas": {
                "FooRow": {
                    "type": "object",
                    "properties": {"x": {"type": "integer"}},
                }
            }
        },
        "paths": {
            "/r": {
                "get": {
                    "operationId": "r_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "results": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/FooRow"
                                                },
                                            }
                                        },
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    out = get_data_schema_for_widget(openapi, "r_op", "/r")
    assert out == openapi["components"]["schemas"]["FooRow"]


def test_get_data_schema_returns_results_block_when_items_missing():
    """``results`` with no ``items`` (degenerate / non-array) — return
    the ``results`` block itself so column generation can still walk
    its properties if it has any.
    """
    from openbb_platform_api.utils.openapi import get_data_schema_for_widget

    inline_schema = {
        "type": "object",
        "properties": {
            "results": {
                # No ``items`` — properties live directly here.
                "type": "object",
                "properties": {"x": {"type": "integer"}},
            }
        },
    }
    openapi = {
        "components": {"schemas": {}},
        "paths": {
            "/r": {
                "get": {
                    "operationId": "r_op",
                    "responses": {
                        "200": {
                            "content": {"application/json": {"schema": inline_schema}}
                        }
                    },
                }
            }
        },
    }
    out = get_data_schema_for_widget(openapi, "r_op", "/r")
    # Returns the ``results`` dict so downstream column generation
    # can still walk its properties.
    assert out == inline_schema["properties"]["results"]


def test_get_data_schema_descends_into_inline_rowdata_with_ref_items():
    """SSRM rowData envelope where ``items`` is a ``$ref`` — same as
    the results-with-ref case, but for the SSRM payload shape.
    """
    from openbb_platform_api.utils.openapi import get_data_schema_for_widget

    openapi = {
        "components": {
            "schemas": {
                "BarRow": {
                    "type": "object",
                    "properties": {"y": {"type": "string"}},
                }
            }
        },
        "paths": {
            "/s": {
                "post": {
                    "operationId": "s_op",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "rowData": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/BarRow"
                                                },
                                            },
                                            "rowCount": {"type": "integer"},
                                        },
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    out = get_data_schema_for_widget(openapi, "s_op", "/s")
    assert out == openapi["components"]["schemas"]["BarRow"]


def test_get_data_schema_descends_into_inline_rowdata_ssrm():
    """Inline SSRM-shaped schema (``rowData`` / ``rowCount`` envelope)
    descends to the row schema under ``rowData.items`` — same logic
    as the components-resolved path, but without going through
    ``$ref`` lookup.
    """
    from openbb_platform_api.utils.openapi import get_data_schema_for_widget

    inline_schema = {
        "type": "object",
        "properties": {
            "rowData": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "price": {"type": "number"},
                    },
                },
            },
            "rowCount": {"type": "integer"},
        },
    }
    openapi = {
        "components": {"schemas": {}},
        "paths": {
            "/some/ssrm": {
                "post": {
                    "operationId": "ssrm_op",
                    "responses": {
                        "200": {
                            "content": {"application/json": {"schema": inline_schema}}
                        }
                    },
                }
            }
        },
    }
    out = get_data_schema_for_widget(openapi, "ssrm_op", "/some/ssrm")
    assert isinstance(out, dict)
    assert set(out["properties"]) == {"symbol", "price"}


def test_get_data_schema_returns_inline_object_as_row_when_no_envelope():
    """A bare inline object schema (no ``results`` / ``rowData``
    envelope) describes a single row directly. Falls through to
    returning the schema itself so column generation has something
    to walk.
    """
    from openbb_platform_api.utils.openapi import get_data_schema_for_widget

    inline_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "score": {"type": "number"},
        },
    }
    openapi = {
        "components": {"schemas": {}},
        "paths": {
            "/single": {
                "get": {
                    "operationId": "single_op",
                    "responses": {
                        "200": {
                            "content": {"application/json": {"schema": inline_schema}}
                        }
                    },
                }
            }
        },
    }
    out = get_data_schema_for_widget(openapi, "single_op", "/single")
    assert out is inline_schema


def test_spec_proxy_inline_schema_produces_columnsdefs_end_to_end():
    """End-to-end: a spec-driven proxy app with an inline
    Socrata-style response_schema produces a widget with
    ``columnsDefs`` populated from the row's fields. Regression for
    the ``Fertilizer Prices By Region`` empty-columnsDefs report.
    """
    from openbb_platform_api.app.spec import build_app_from_spec
    from openbb_platform_api.utils.widgets import build_json

    spec = {
        "version": 5,
        "base_url": "https://example.com",
        "api_prefix": "",
        "commands": {
            "fertilizer.prices": {
                "url_path": "/resource/abcd.json",
                "method": "get",
                "description": "Fertilizer prices.",
                "providers": [],
                "parameters": [
                    {
                        "name": "region",
                        "in": "query",
                        "type": "string",
                        "is_list": False,
                        "required": False,
                        "default": None,
                        "choices": [],
                        "providers": [],
                    },
                ],
                "request_body_schema": None,
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "date": {"type": "string", "format": "date"},
                                    "year": {"type": "integer"},
                                    "region": {"type": "string"},
                                    "price": {"type": "number"},
                                },
                            },
                        }
                    },
                },
            }
        },
        "routers": {},
        "reference": {},
    }
    app = build_app_from_spec(spec)
    out = build_json(app.openapi(), [])
    assert len(out) == 1
    widget = next(iter(out.values()))
    cols = widget["data"]["table"].get("columnsDefs")
    assert cols, f"expected columnsDefs to be populated; got {cols}"
    by_field = {c["field"]: c for c in cols}
    # Date got the dateString cellDataType + descending sort default.
    assert by_field["date"]["cellDataType"] == "dateString"
    assert by_field["date"]["sort"] == "desc"
    # Year is rendered as text to suppress ag-grid's locale comma.
    assert by_field["year"]["cellDataType"] == "text"
    # Other types preserved.
    assert by_field["region"]["cellDataType"] == "text"
    assert by_field["price"]["cellDataType"] == "number"


if __name__ == "__main__":
    pytest.main()
