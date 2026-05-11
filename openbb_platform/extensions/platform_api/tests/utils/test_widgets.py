import json
from pathlib import Path

import pytest

from openbb_platform_api.response_models import OmniWidgetResponseModel
from openbb_platform_api.utils.widgets import build_json, modify_query_schema


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


def test_omni_widget_response_model():
    # Create a sample OmniWidgetResponseModel instance

    test_table = [
        {"symbol": "AAPL", "price": 150.0, "volume": 1000000},
        {"symbol": "GOOGL", "price": 2800.0, "volume": 500000},
    ]
    widget = OmniWidgetResponseModel(
        content=test_table,
    )
    # Assert the content and data_format fields
    assert widget.content == test_table
    assert widget.data_format == {
        "data_type": "object",
        "parse_as": "table",
    }
    assert not hasattr(widget, "parse_as")

    widget = OmniWidgetResponseModel(
        content=test_table,
        parse_as="text",
    )
    # Assert the parse_as field takes precedence
    assert widget.content == test_table
    assert widget.data_format == {
        "data_type": "object",
        "parse_as": "text",
    }
    # Assert that the parse_as field is not sent at the root of the object.
    assert not hasattr(widget, "parse_as")

    # Test with JSON string content
    widget = OmniWidgetResponseModel(
        content=json.dumps(test_table),
    )

    # Assert the content and data_format fields
    assert isinstance(widget.content, list)
    assert widget.data_format == {
        "data_type": "object",
        "parse_as": "table",
    }
    assert not hasattr(widget, "parse_as")

    assert "x-widget_config" in widget.schema_json()


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
                    "label": "URL",
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
                    "multiple": True,
                    "style": {
                        "popupWidth": 400,
                    },
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
    assert len(result) == len(
        mock_openapi_json["paths"]
    )  # +1 for the duplicate path with a chart. -1 for the form widget over 2 paths.
    assert result == mock_widgets_json


# ---------------------------------------------------------------------------
# deep_merge_configs (covers the inner merge_values + merge_lists helpers)
# ---------------------------------------------------------------------------


def test_deep_merge_configs_adds_new_keys_to_base():
    """Keys present only in ``update`` get added to ``base`` verbatim."""
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"a": 1}
    out = deep_merge_configs(base, {"b": 2})
    assert out == {"a": 1, "b": 2}


def test_deep_merge_configs_overwrites_with_explicit_empty_values():
    """Update value of ``[]`` / ``{}`` / ``None`` overwrites the base —
    explicit "clear this" semantic.
    """
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"a": [1, 2, 3], "b": {"x": 1}, "c": "value"}
    out = deep_merge_configs(base, {"a": [], "b": {}, "c": None})
    assert out == {"a": [], "b": {}, "c": None}


def test_deep_merge_configs_recurses_into_nested_dicts():
    """Nested dicts get merged, not replaced."""
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"outer": {"keep": 1, "shared": 2}}
    out = deep_merge_configs(base, {"outer": {"shared": 99, "new": 3}})
    assert out == {"outer": {"keep": 1, "shared": 99, "new": 3}}


def test_deep_merge_configs_replaces_scalar_when_types_differ():
    """When types don't match, update wins."""
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"x": "scalar"}
    out = deep_merge_configs(base, {"x": [1, 2]})
    assert out == {"x": [1, 2]}


def test_deep_merge_configs_string_match_keys_normalized_to_tuple():
    """``match_keys="paramName"`` is normalized to a one-tuple."""
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"items": [{"paramName": "a", "value": 1}]}
    update = {"items": [{"paramName": "a", "value": 99}]}
    out = deep_merge_configs(base, update, match_keys="paramName")
    assert out["items"] == [{"paramName": "a", "value": 99}]


def test_deep_merge_configs_merges_lists_by_match_key():
    """Lists of dicts merge by ``paramName`` / ``field`` match key."""
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"items": [{"paramName": "a", "v": 1}, {"paramName": "b", "v": 2}]}
    update = {
        "items": [
            {"paramName": "a", "v": 99},
            {"paramName": "c", "v": 3},
        ]
    }
    out = deep_merge_configs(base, update)
    items = out["items"]
    paramnames = [i["paramName"] for i in items]
    assert paramnames == ["a", "b", "c"]
    assert items[0]["v"] == 99


def test_deep_merge_configs_preserves_unmatched_list_dicts():
    """Base-list dicts whose match-key isn't in update list are preserved."""
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"items": [{"paramName": "kept", "v": 1}]}
    update = {"items": [{"paramName": "new", "v": 2}]}
    out = deep_merge_configs(base, update)
    paramnames = [i["paramName"] for i in out["items"]]
    assert "kept" in paramnames
    assert "new" in paramnames


def test_deep_merge_configs_preserves_base_list_with_no_match_key():
    """Base-list dict with no recognized match key → preserved unchanged."""
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"items": [{"unrelated_key": "x"}]}
    update = {"items": [{"paramName": "new"}]}
    out = deep_merge_configs(base, update)
    items = out["items"]
    assert {"unrelated_key": "x"} in items
    assert {"paramName": "new"} in items


def test_deep_merge_configs_recurses_into_nested_lists():
    """Nested list-of-list merges recursively via ``merge_lists``.

    ``deep_merge_configs`` doesn't deduplicate at the outer level — the
    inner nested list gets recursively merged with the matching update,
    and the unmatched outer-list items from the update are appended.
    """
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"items": [[{"paramName": "a", "v": 1}]]}
    update = {"items": [[{"paramName": "a", "v": 99}]]}
    out = deep_merge_configs(base, update)
    # Inner list gets the merge applied (v: 99 wins).
    assert out["items"][0] == [{"paramName": "a", "v": 99}]


def test_deep_merge_configs_keeps_nested_list_when_no_update_list():
    """Base list-of-list with no matching update list survives."""
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"items": [[1, 2, 3]]}
    update = {"items": [{"paramName": "added"}]}
    out = deep_merge_configs(base, update)
    assert [1, 2, 3] in out["items"]


def test_deep_merge_configs_keeps_non_dict_non_list_base_items():
    """Scalars in the base list pass through unchanged."""
    from openbb_platform_api.utils.widgets import deep_merge_configs

    base = {"items": ["string-item", 42, None]}
    update = {"items": [{"paramName": "added"}]}
    out = deep_merge_configs(base, update)
    for item in ("string-item", 42, None):
        assert item in out["items"]
    assert {"paramName": "added"} in out["items"]


# ---------------------------------------------------------------------------
# get_form_input_paths
# ---------------------------------------------------------------------------


def test_get_form_input_paths_extracts_form_endpoints():
    """``widget_config.form_endpoint`` → mapped from route to endpoint."""
    from openbb_platform_api.utils.widgets import get_form_input_paths

    openapi = {
        "paths": {
            "/with_form": {"get": {"widget_config": {"form_endpoint": "/submit"}}},
            "/no_form": {"get": {"widget_config": {}}},
            "/no_widget_config": {"get": {}},
        }
    }
    out = get_form_input_paths(openapi)
    assert out == {"/with_form": "/submit"}


# ---------------------------------------------------------------------------
# modify_query_schema branches
# ---------------------------------------------------------------------------


def test_modify_query_schema_returns_empty_for_empty_input():
    """Empty input → empty list."""
    out = modify_query_schema([], "fmp")
    assert out == []


def test_modify_query_schema_skips_provider_param():
    """Items with ``parameter_name="provider"`` are dropped."""
    out = modify_query_schema(
        [
            {"parameter_name": "provider", "options": ["fmp", "polygon"]},
            {"parameter_name": "symbol", "type": "text"},
        ],
        "fmp",
    )
    param_names = [i.get("paramName") for i in out]
    # Original ``provider`` skipped; sentinel appended at the end.
    assert "provider" in param_names
    assert "symbol" in param_names


def test_modify_query_schema_skips_unavailable_providers():
    """A param tagged for a different provider is dropped."""
    out = modify_query_schema(
        [
            {
                "parameter_name": "tier",
                "available_providers": ["polygon"],
                "type": "text",
            },
            {"parameter_name": "symbol", "type": "text"},
        ],
        "fmp",
    )
    names = [i.get("paramName") for i in out]
    assert "tier" not in names
    assert "symbol" in names


def test_modify_query_schema_appends_multi_items_hint_to_description():
    """Multi-items provider → appended description, multiSelect=True."""
    out = modify_query_schema(
        [
            {
                "parameter_name": "symbol",
                "description": "Stock symbol.",
                "type": "text",
                "multiple_items_allowed": {"fmp": True},
            }
        ],
        "fmp",
    )
    item = out[0]
    assert "Multiple comma separated items allowed" in item["description"]
    assert item["multiSelect"] is True


def test_modify_query_schema_picks_provider_specific_options():
    """Provider-keyed options → use that provider's list."""
    out = modify_query_schema(
        [
            {
                "parameter_name": "tier",
                "type": "text",
                "options": {"fmp": ["a", "b"], "polygon": ["x", "y"]},
            }
        ],
        "fmp",
    )
    assert out[0]["options"] == ["a", "b"]


def test_modify_query_schema_falls_back_to_other_options():
    """Single ``other`` key → that's the option set used."""
    out = modify_query_schema(
        [
            {
                "parameter_name": "tier",
                "type": "text",
                "options": {"other": ["x", "y"]},
            }
        ],
        "polygon",
    )
    assert out[0]["options"] == ["x", "y"]


def test_modify_query_schema_options_as_list_keyed_by_provider():
    """Bare-list ``options`` value → wrapped under provider key."""
    out = modify_query_schema(
        [
            {
                "parameter_name": "tier",
                "type": "text",
                "options": ["a", "b"],
            }
        ],
        "fmp",
    )
    assert out[0]["options"] == ["a", "b"]


def test_modify_query_schema_uppercase_label_for_known_acronyms():
    """``url`` / ``cik`` / etc. get auto-uppercased labels."""
    out = modify_query_schema(
        [{"parameter_name": "cik", "type": "text"}],
        "fmp",
    )
    assert out[0]["label"] == "CIK"


def test_modify_query_schema_x_widget_config_exclude_drops_param():
    """``exclude=True`` in ``x-widget_config`` → param dropped."""
    out = modify_query_schema(
        [
            {
                "parameter_name": "symbol",
                "type": "text",
                "x-widget_config": {"fmp": {"exclude": True}},
            }
        ],
        "fmp",
    )
    names = [i.get("paramName") for i in out]
    assert "symbol" not in names


def test_modify_query_schema_x_widget_config_merges_into_param():
    """Provider-specific ``x-widget_config`` is deep-merged."""
    out = modify_query_schema(
        [
            {
                "parameter_name": "symbol",
                "type": "text",
                "x-widget_config": {
                    "fmp": {"label": "Custom Symbol", "description": "FMP override"}
                },
            }
        ],
        "fmp",
    )
    item = out[0]
    assert item["label"] == "Custom Symbol"
    assert item["description"] == "FMP override"


def test_modify_query_schema_multi_select_text_no_options_gets_popup_style():
    """MultiSelect + text + no options + no semicolon → popup style."""
    out = modify_query_schema(
        [
            {
                "parameter_name": "tags",
                "type": "text",
                "multiSelect": True,
                "description": "Choose tags.",
            }
        ],
        "fmp",
    )
    item = out[0]
    assert item["multiple"] is True
    assert "popupWidth" in item.get("style", {})


def test_modify_query_schema_custom_provider_skips_provider_sentinel():
    """``provider="custom"`` → no synthetic provider entry appended."""
    out = modify_query_schema([{"parameter_name": "symbol", "type": "text"}], "custom")
    names = [i.get("paramName") for i in out]
    assert "provider" not in names
    assert "symbol" in names


# ---------------------------------------------------------------------------
# build_json edge-case branches
# ---------------------------------------------------------------------------


def _minimal_openapi(
    paths: dict,
    schemas: dict | None = None,
) -> dict:
    """Wrap ``paths`` (and optional ``components.schemas``) in a minimum
    openapi document the launcher's ``build_json`` accepts.
    """
    return {
        "paths": paths,
        "components": {"schemas": schemas or {}},
    }


def _basic_get_route(
    widget_config: dict | None = None, response_schema: dict | None = None
) -> dict:
    """Build a single GET route definition shaped the way ``build_json``
    walks: parameters, response schema, optional widget_config.
    """
    route = {
        "operationId": "test_op",
        "parameters": [],
        "summary": "Summary",
        "description": "Description",
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "schema": response_schema or {"type": "object"}
                    }
                }
            }
        },
    }
    if widget_config:
        route["widget_config"] = widget_config
    return {"get": route}


def test_build_json_empty_openapi_returns_empty_dict():
    """No openapi → no widgets, fast path."""
    assert build_json({}, []) == {}


def test_build_json_skips_widget_with_widget_id_in_exclude_filter():
    """When the derived widget id appears in ``widget_exclude_filter``,
    the widget is dropped before any further processing.
    """
    openapi = _minimal_openapi({"/api/v1/equity_quote": _basic_get_route()})
    out = build_json(openapi, ["equity_quote"])
    assert out == {}


def test_build_json_skips_widget_marked_excluded_in_widget_config():
    """A widget whose own ``widget_config.exclude`` is ``True`` is
    dropped — exercises line 312.
    """
    openapi = _minimal_openapi(
        {"/api/v1/foo_bar": _basic_get_route(widget_config={"exclude": True})}
    )
    out = build_json(openapi, [])
    assert out == {}


def test_build_json_skips_widget_when_starred_filter_matches_route():
    """A wildcard exclude (e.g. ``"/api/v1/equity/*"``) drops every
    matching route — exercises lines 254-256 (split-out starred list)
    and 285-293 (the per-route skip loop).
    """
    openapi = _minimal_openapi({"/api/v1/equity/quote": _basic_get_route()})
    out = build_json(openapi, ["/api/v1/equity/*"])
    assert out == {}


def test_build_json_post_route_appends_widget_id_to_exclude_filter():
    """POST routes whose widget type isn't ssrm/omni/multi-file get
    auto-excluded from later rebuilds — exercises line 704.
    """
    openapi = _minimal_openapi(
        {
            "/api/v1/something": {
                "post": {
                    "operationId": "post_op",
                    "summary": "S",
                    "description": "D",
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
                                "schema": {"type": "object", "properties": {}}
                            }
                        }
                    },
                }
            }
        }
    )
    exclude_filter: list = []
    out = build_json(openapi, exclude_filter)
    # POST builder adds the widget id to the exclude filter, so it
    # doesn't appear in the result.
    assert out == {}
    assert any("something" in item for item in exclude_filter)


def test_build_json_chart_widget_emitted_when_chart_param_present():
    """A GET route whose parameters include ``chart`` gets two widgets:
    one regular table widget and one chart variant.
    """
    openapi = _minimal_openapi(
        {
            "/api/v1/equity_chart": {
                "get": {
                    "operationId": "equity_chart_op",
                    "summary": "S",
                    "description": "D",
                    "parameters": [
                        {
                            "name": "chart",
                            "in": "query",
                            "schema": {"type": "boolean"},
                        }
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
        }
    )
    out = build_json(openapi, [])
    # Both base + chart variant present (widget id ends with ``_chart``).
    assert any(k.endswith("_chart") for k in out)


def test_build_json_metric_widget_uses_compact_grid():
    """``widget_config.type="metric"`` rewrites ``gridData`` from the
    default 40×15 to 4×5 — exercises lines 670-676.
    """
    openapi = _minimal_openapi(
        {"/api/v1/some_metric": _basic_get_route(widget_config={"type": "metric"})}
    )
    out = build_json(openapi, [])
    metric_widget = next(iter(out.values()))
    assert metric_widget["gridData"]["w"] == 4
    assert metric_widget["gridData"]["h"] == 5


def test_build_json_pdf_widget_uses_pdf_grid_defaults():
    """``widget_config.type="pdf"`` rewrites ``gridData`` to 20×25 —
    exercises lines 683-689.
    """
    openapi = _minimal_openapi(
        {"/api/v1/some_pdf": _basic_get_route(widget_config={"type": "pdf"})}
    )
    out = build_json(openapi, [])
    pdf_widget = next(iter(out.values()))
    assert pdf_widget["gridData"]["w"] == 20
    assert pdf_widget["gridData"]["h"] == 25


def test_build_json_widget_config_source_override():
    """``widget_config.source = [...]`` overrides the auto-derived
    provider list — exercises line 697.
    """
    openapi = _minimal_openapi(
        {
            "/api/v1/something": _basic_get_route(
                widget_config={"source": ["custom-source"]}
            )
        }
    )
    out = build_json(openapi, [])
    widget = next(iter(out.values()))
    assert widget["source"] == ["custom-source"]


def test_build_json_post_with_request_body_ref_params():
    """A POST whose ``requestBody`` references a schema with ``$ref``
    properties drives the ``param_names`` extraction path — each ref
    becomes a separate ``post_query_schema_for_widget`` call.
    """
    openapi = {
        "components": {
            "schemas": {
                "PostInput": {
                    "title": "PostInput",
                    "properties": {
                        "data": {"$ref": "#/components/schemas/InputData"},
                    },
                },
                "InputData": {
                    "title": "InputData",
                    "type": "object",
                    "properties": {"x": {"type": "number"}},
                },
            }
        },
        "paths": {
            "/api/v1/something": {
                "post": {
                    "operationId": "post_op",
                    "summary": "S",
                    "description": "D",
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
                                "schema": {"$ref": "#/components/schemas/PostInput"}
                            }
                        }
                    },
                }
            }
        },
    }
    # POST routes get added to the exclude filter automatically; we just
    # need the call not to crash and to handle the ref-following branch.
    exclude_filter: list = []
    build_json(openapi, exclude_filter)
    assert any("something" in item for item in exclude_filter)


def test_build_json_form_endpoint_emits_form_widget():
    """A GET route whose ``widget_config.form_endpoint`` points at a
    POST route emits a ``form`` widget with a ``submit`` button auto-
    appended.
    """
    openapi = {
        "components": {
            "schemas": {
                "FormInput": {
                    "title": "FormInput",
                    "type": "object",
                    "properties": {
                        "field_a": {"$ref": "#/components/schemas/FieldA"},
                    },
                },
                "FieldA": {
                    "title": "FieldA",
                    "type": "object",
                    "properties": {"value": {"type": "number"}},
                },
            }
        },
        "paths": {
            "/api/v1/data_widget": {
                "get": {
                    "operationId": "data_widget_op",
                    "parameters": [],
                    "summary": "S",
                    "description": "D",
                    "widget_config": {"form_endpoint": "/api/v1/data_widget_submit"},
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                }
            },
            "/api/v1/data_widget_submit": {
                "post": {
                    "operationId": "data_widget_submit_op",
                    "summary": "Submit",
                    "description": "Submit data",
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
                                "schema": {"$ref": "#/components/schemas/FormInput"}
                            }
                        }
                    },
                }
            },
        },
    }
    out = build_json(openapi, [])
    # The data_widget gets a 'form' param added with the submit button.
    widget = next(iter(out.values()))
    form_param = next(
        (p for p in widget.get("params", []) if p.get("type") == "form"), None
    )
    assert form_param is not None


def test_build_json_form_endpoint_no_params_with_var_schema_widget_config():
    """A form endpoint whose ``requestBody`` schema has NO ``$ref``
    properties (just a plain object) takes the no-params branch.
    The model-level ``x-widget_config`` gets merged into the form_params
    and ``$.``-prefixed keys are lifted to the widget root.
    """
    openapi = {
        "components": {
            "schemas": {
                "FormSchema": {
                    "title": "Form Schema",
                    "description": "Form description",
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                    },
                    "x-widget_config": {
                        "$.runButton": True,
                        "label": "Custom Form Label",
                    },
                }
            }
        },
        "paths": {
            "/api/v1/data_widget": {
                "get": {
                    "operationId": "data_widget_op",
                    "parameters": [],
                    "summary": "S",
                    "description": "D",
                    "widget_config": {"form_endpoint": "/api/v1/data_widget_submit"},
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                }
            },
            "/api/v1/data_widget_submit": {
                "post": {
                    "operationId": "data_widget_submit_op",
                    "summary": "Submit",
                    "description": "Submit data",
                    "widget_config": {
                        "$.refetchInterval": 30,
                        "type": "form",
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
                                "schema": {"$ref": "#/components/schemas/FormSchema"}
                            }
                        }
                    },
                }
            },
        },
    }
    out = build_json(openapi, [])
    widget = next(iter(out.values()))
    # ``$.``-prefixed keys lifted to widget root from both var_schema
    # and form_route's widget_config.
    assert widget.get("runButton") is True
    assert widget.get("refetchInterval") == 30
    # Non-prefixed keys merge into form_params.
    form_param = next((p for p in widget["params"] if p.get("type") == "form"), None)
    assert form_param is not None
    assert form_param.get("label") == "Custom Form Label"


def test_build_json_post_route_with_var_schema_widget_config_dollar_keys():
    """A POST route (no form_endpoint) whose request-body schema has
    ``x-widget_config`` with ``$.``-prefixed keys lifts them to the
    widget config — exercises lines 538-557.
    """
    openapi = {
        "components": {
            "schemas": {
                "PostSchema": {
                    "title": "Post Schema",
                    "type": "object",
                    "properties": {"x": {"type": "number"}},
                    "x-widget_config": {
                        "$.refetchInterval": 60,
                        "$.gridData": {"w": 30, "h": 10},
                    },
                }
            }
        },
        "paths": {
            "/api/v1/post_widget": {
                "post": {
                    "operationId": "post_widget_op",
                    "summary": "S",
                    "description": "D",
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
                                "schema": {"$ref": "#/components/schemas/PostSchema"}
                            }
                        }
                    },
                }
            }
        },
    }
    # POST routes get added to exclude_filter; capture the side-effect.
    exclude_filter: list = []
    build_json(openapi, exclude_filter)
    # Side effect confirmed (POST route excluded) — we're really
    # exercising the var_schema processing code path, even though the
    # output is empty.
    assert any("post_widget" in item for item in exclude_filter)


def test_build_json_data_widget_config_extracts_x_widget_keys():
    """When the data schema's ``x-widget_config`` contains ``$.``-prefixed
    keys, those land at the widget root (not inside ``data``).
    Exercises lines 639-657.
    """
    openapi = {
        "components": {
            "schemas": {
                "OBBject_RootedData_": {
                    "title": "OBBject_RootedData_",
                    "properties": {
                        "results": {
                            "anyOf": [
                                {
                                    "items": {
                                        "$ref": "#/components/schemas/RootedData"
                                    },
                                    "type": "array",
                                },
                                {"type": "null"},
                            ]
                        }
                    },
                },
                "RootedData": {
                    "title": "RootedData",
                    "properties": {"value": {"type": "number"}},
                    "x-widget_config": {
                        "$.runButton": True,
                        "$.refetchInterval": 60,
                    },
                },
            }
        },
        "paths": {
            "/api/v1/rooted": {
                "get": {
                    "operationId": "rooted_op",
                    "parameters": [],
                    "summary": "S",
                    "description": "D",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/OBBject_RootedData_"
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    out = build_json(openapi, [])
    widget = next(iter(out.values()))
    # ``$.runButton`` lifted to root.
    assert widget.get("runButton") is True
    assert widget.get("refetchInterval") == 60


# ---------------------------------------------------------------------------
# SSRM auto-promotion in build_json
# ---------------------------------------------------------------------------


def _ssrm_post_openapi(
    *,
    request_schema: str = "AgGridRowsRequest",
    response_schema: str | None = "AgGridRowsResponse_FooRow_",
    schemas: dict | None = None,
    widget_config: dict | None = None,
) -> dict:
    """Build an OpenAPI doc for a POST route shaped as an ag-grid SSRM
    endpoint — body $ref to ``request_schema``, response $ref to
    ``response_schema``.
    """
    default_schemas = {
        "AgGridRowsRequest": {"title": "AgGridRowsRequest"},
        "FooRow": {
            "title": "FooRow",
            "properties": {
                "symbol": {"type": "string"},
                "price": {"type": "number"},
                "as_of_date": {"type": "string", "format": "date"},
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
    schemas = {**default_schemas, **(schemas or {})}
    response_block: dict = (
        {"$ref": f"#/components/schemas/{response_schema}"}
        if response_schema
        else {"type": "object"}
    )
    op: dict = {
        "operationId": "ssrm_op",
        "summary": "SSRM",
        "description": "Server-side row model endpoint",
        "responses": {
            "200": {"content": {"application/json": {"schema": response_block}}}
        },
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {"$ref": f"#/components/schemas/{request_schema}"}
                }
            }
        },
    }
    if widget_config is not None:
        op["widget_config"] = widget_config
    return {
        "components": {"schemas": schemas},
        "paths": {"/api/v1/ssrm/foo": {"post": op}},
    }


def test_build_json_ssrm_auto_promotes_type_and_runbutton():
    """A POST whose body is ``AgGridRowsRequest`` and response is
    ``AgGridRowsResponse_FooRow_`` is auto-promoted: ``type`` becomes
    ``ssrm_table``, ``runButton`` defaults to True, ``dataKey`` stays
    empty (no OBBject envelope), and the route survives the POST
    exclusion filter that drops every other POST widget.
    """
    openapi = _ssrm_post_openapi()
    exclude_filter: list = []
    out = build_json(openapi, exclude_filter)
    # Exactly one widget surfaces — the SSRM table itself.
    assert len(out) == 1
    widget = next(iter(out.values()))
    assert widget["type"] == "ssrm_table"
    assert widget["runButton"] is True
    assert widget["data"]["dataKey"] == ""
    # And the POST exclusion (line 699) didn't filter it.
    assert widget["widgetId"] not in exclude_filter


def test_build_json_ssrm_request_only_signal_is_sufficient():
    """Body alone (``$ref`` to ``AgGridRowsRequest``) is enough — even
    when the response schema doesn't match the canonical SSRM shape.
    """
    openapi = _ssrm_post_openapi(response_schema=None)
    out = build_json(openapi, [])
    assert len(out) == 1
    assert next(iter(out.values()))["type"] == "ssrm_table"


def test_build_json_ssrm_response_only_signal_is_sufficient():
    """Response alone (``rowData`` + ``rowCount``) is enough — body
    can be any other type.
    """
    openapi = _ssrm_post_openapi(
        request_schema="UnrelatedBody",
        schemas={"UnrelatedBody": {"title": "UnrelatedBody"}},
    )
    out = build_json(openapi, [])
    assert len(out) == 1
    assert next(iter(out.values()))["type"] == "ssrm_table"


def test_build_json_ssrm_subclass_request_body_still_promoted():
    """``AgGridRowsRequest`` subclasses (allOf chain in OpenAPI) are
    detected by walking the inheritance chain.
    """
    openapi = _ssrm_post_openapi(
        request_schema="ProviderRowsRequest",
        schemas={
            "ProviderRowsRequest": {
                "title": "ProviderRowsRequest",
                "allOf": [{"$ref": "#/components/schemas/AgGridRowsRequest"}],
            }
        },
    )
    out = build_json(openapi, [])
    assert next(iter(out.values()))["type"] == "ssrm_table"


def test_build_json_ssrm_explicit_runbutton_override_wins():
    """Author can opt out of the SSRM ``runButton: True`` default with
    an explicit ``widget_config={"runButton": False}``. The deep-merge
    after construction lets the explicit value win.
    """
    openapi = _ssrm_post_openapi(widget_config={"runButton": False})
    out = build_json(openapi, [])
    widget = next(iter(out.values()))
    assert widget["type"] == "ssrm_table"
    assert widget["runButton"] is False


def test_build_json_ssrm_columns_defs_derived_from_row_model():
    """The ``rowData[].FooRow`` properties drive the auto-generated
    ``columnsDefs`` — so the existing per-column inferences (date
    detection, pinning) flow through to SSRM tables for free.
    """
    openapi = _ssrm_post_openapi()
    out = build_json(openapi, [])
    widget = next(iter(out.values()))
    cols = widget["data"]["table"].get("columnsDefs", [])
    assert cols, "expected columnsDefs to be auto-derived from FooRow"
    by_field = {c["field"]: c for c in cols}
    assert by_field["symbol"]["cellDataType"] == "text"
    assert by_field["price"]["cellDataType"] == "number"
    # ``format: "date"`` (no time component) → ``dateString`` so the
    # value renders verbatim as YYYY-MM-DD instead of being parsed as
    # a timestamp.
    assert by_field["as_of_date"]["cellDataType"] == "dateString"
    # ``symbol`` is in the hardcoded pinned-left set in
    # data_schema_to_columns_defs.
    assert by_field["symbol"].get("pinned") == "left"


def test_build_json_non_ssrm_post_route_unchanged():
    """A POST route that doesn't match either SSRM signal stays a
    plain table widget and gets the standard POST-exclusion treatment.
    Regression guard against the auto-promotion firing too eagerly.
    """
    openapi = _minimal_openapi(
        {
            "/api/v1/regular_post": {
                "post": {
                    "operationId": "regular_post_op",
                    "summary": "S",
                    "description": "D",
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
                                "schema": {"type": "object", "properties": {}}
                            }
                        }
                    },
                }
            }
        }
    )
    exclude_filter: list = []
    out = build_json(openapi, exclude_filter)
    # Standard POST exclusion: not promoted, gets filtered out.
    assert out == {}
    assert any("regular_post" in item for item in exclude_filter)


# ---------------------------------------------------------------------------
# Coverage gaps in the ``$.``-prefixed widget_config hierarchy
# ---------------------------------------------------------------------------
#
# These branches drive how widget properties cascade across three levels:
#
#   1. **Param level** — a query param's ``x-widget_config`` can wipe a
#      label that the known-acronym fallback (CIK, ISIN, ...) just
#      assigned; a second fallback pass restores it.
#   2. **POST/form level** — ``$.``-prefixed keys on the request-body
#      model (or on the form route's own ``widget_config``) lift to the
#      widget root, with override semantics when the route's explicit
#      ``widget_config`` already carries the same unprefixed key.
#   3. **Data-model level** — same lifting from the response model's
#      ``x-widget_config``, with the same override behavior.
#
# All three layers feed into ``widget_config_dict`` and finally
# ``deep_merge_configs`` onto the base widget — so they have to be
# tested end-to-end with explicit overrides at each level to confirm
# the priority order.


def test_modify_query_schema_known_acronym_label_recovered_after_xwidget_wipe():
    """The second known-acronym pass at line 184-192 only fires when the
    first pass set the label and a per-provider ``x-widget_config`` then
    explicitly nulls it (``deep_merge_configs`` treats ``None`` as an
    explicit empty value). The fallback re-uppercases ``cik`` → ``CIK``
    so the user never sees a blank label.
    """
    out = modify_query_schema(
        [
            {
                "parameter_name": "cik",
                "type": "text",
                "x-widget_config": {"custom": {"label": None}},
            }
        ],
        "custom",
    )
    item = next(p for p in out if p.get("paramName") == "cik")
    assert item["label"] == "CIK"


def test_build_json_form_endpoint_with_params_skips_auto_submit_when_button_present():
    """When the form's input model already exposes a param of
    ``type: "button"`` (via per-provider ``x-widget_config``), the
    auto-submit append should be skipped — exercises the early-break
    at lines 421-425.
    """
    openapi = {
        "components": {
            "schemas": {
                "FormInput": {
                    "title": "FormInput",
                    "type": "object",
                    "properties": {
                        "field_a": {"$ref": "#/components/schemas/FieldA"},
                    },
                },
                "FieldA": {
                    "title": "FieldA",
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        # This property gets promoted to ``type: "button"``
                        # via ``process_parameter``'s ``p.update(...)`` —
                        # ``post_query_schema_for_widget`` runs with
                        # ``providers=["Custom"]`` (capital, hardcoded at
                        # line 1167 of openapi.py), so the x-widget_config
                        # key MUST match that casing for the unwrap to fire.
                        "go": {
                            "type": "string",
                            "x-widget_config": {"Custom": {"type": "button"}},
                        },
                    },
                },
            }
        },
        "paths": {
            "/api/v1/data_widget": {
                "get": {
                    "operationId": "data_widget_op",
                    "parameters": [],
                    "summary": "S",
                    "description": "D",
                    "widget_config": {"form_endpoint": "/api/v1/data_widget_submit"},
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                }
            },
            "/api/v1/data_widget_submit": {
                "post": {
                    "operationId": "data_widget_submit_op",
                    "summary": "Submit",
                    "description": "Submit data",
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
                                "schema": {"$ref": "#/components/schemas/FormInput"}
                            }
                        }
                    },
                }
            },
        },
    }
    out = build_json(openapi, [])
    widget = next(iter(out.values()))
    form_param = next(p for p in widget["params"] if p.get("type") == "form")
    button_params = [p for p in form_param["inputParams"] if p.get("type") == "button"]
    # Exactly one button — the user-defined ``go``, no synthetic
    # ``submit`` was appended.
    assert len(button_params) == 1
    assert button_params[0]["paramName"] == "go"


def test_build_json_form_endpoint_with_params_var_schema_xwidget_merges_into_form_params():
    """When the request-body schema carries a model-level
    ``x-widget_config`` (NO ``$.`` prefix), it deep-merges into the
    ``form_params`` block — so authors can set form-level UI hints
    (label, description, popup width) without touching the route
    decorator. Exercises line 448.
    """
    openapi = {
        "components": {
            "schemas": {
                "FormInput": {
                    "title": "FormInput",
                    "type": "object",
                    "properties": {
                        "field_a": {"$ref": "#/components/schemas/FieldA"},
                    },
                    "x-widget_config": {
                        "label": "Custom Form Label",
                        "description": "Custom form description",
                    },
                },
                "FieldA": {
                    "title": "FieldA",
                    "type": "object",
                    "properties": {"value": {"type": "number"}},
                },
            }
        },
        "paths": {
            "/api/v1/data_widget": {
                "get": {
                    "operationId": "data_widget_op",
                    "parameters": [],
                    "summary": "S",
                    "description": "D",
                    "widget_config": {"form_endpoint": "/api/v1/data_widget_submit"},
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                }
            },
            "/api/v1/data_widget_submit": {
                "post": {
                    "operationId": "data_widget_submit_op",
                    "summary": "Submit",
                    "description": "Submit data",
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
                                "schema": {"$ref": "#/components/schemas/FormInput"}
                            }
                        }
                    },
                }
            },
        },
    }
    out = build_json(openapi, [])
    widget = next(iter(out.values()))
    form_param = next(p for p in widget["params"] if p.get("type") == "form")
    # Non-prefixed keys on var_schema landed on the form_params block.
    assert form_param["label"] == "Custom Form Label"
    assert form_param["description"] == "Custom form description"


def test_build_json_form_endpoint_dollar_key_overrides_existing_widget_config_key():
    """When the form route's request-body schema lifts a ``$.``-prefixed
    key whose unprefixed form is *already* in the GET route's explicit
    ``widget_config``, the lifted value wins — exercises line 533. The
    cascade order is: GET ``widget_config`` < lifted ``$.`` keys
    (because the lifted assignment happens before the final
    ``deep_merge_configs`` and the lifted keys go through
    ``widget_config_dict.update``).
    """
    openapi = {
        "components": {
            "schemas": {
                "FormSchema": {
                    "title": "Form Schema",
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "x-widget_config": {"$.runButton": True},
                }
            }
        },
        "paths": {
            "/api/v1/data_widget": {
                "get": {
                    "operationId": "data_widget_op",
                    "parameters": [],
                    "summary": "S",
                    "description": "D",
                    "widget_config": {
                        "form_endpoint": "/api/v1/data_widget_submit",
                        "runButton": False,
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            }
                        }
                    },
                }
            },
            "/api/v1/data_widget_submit": {
                "post": {
                    "operationId": "data_widget_submit_op",
                    "summary": "Submit",
                    "description": "Submit data",
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
                                "schema": {"$ref": "#/components/schemas/FormSchema"}
                            }
                        }
                    },
                }
            },
        },
    }
    out = build_json(openapi, [])
    widget = next(iter(out.values()))
    # ``$.runButton: True`` lifted from the var_schema overrode the
    # GET route's explicit ``runButton: False``.
    assert widget["runButton"] is True


def test_build_json_post_dollar_key_overrides_existing_widget_config_key():
    """Same override semantics as the form-endpoint case, exercised on
    a plain POST (no form_endpoint). The route's explicit
    ``widget_config.runButton: False`` is overwritten by the
    ``$.runButton: True`` on the request-body schema — exercises line
    554.
    """
    openapi = {
        "components": {
            "schemas": {
                "PostSchema": {
                    "title": "Post Schema",
                    "type": "object",
                    "properties": {"x": {"type": "number"}},
                    "x-widget_config": {"$.runButton": True},
                }
            }
        },
        "paths": {
            "/api/v1/post_widget": {
                "post": {
                    "operationId": "post_widget_op",
                    "summary": "S",
                    "description": "D",
                    # Explicit ``runButton: False`` plus an SSRM-ish
                    # type so the widget escapes the POST exclusion
                    # and we can inspect the final config.
                    "widget_config": {
                        "type": "ssrm_table",
                        "runButton": False,
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
                                "schema": {"$ref": "#/components/schemas/PostSchema"}
                            }
                        }
                    },
                }
            }
        },
    }
    out = build_json(openapi, [])
    widget = next(iter(out.values()))
    # ``$.runButton: True`` from the request schema overrode the
    # explicit ``runButton: False`` on the route.
    assert widget["runButton"] is True


def test_build_json_data_dollar_key_overrides_existing_widget_config_key():
    """Same override pattern at the data-model level: when the route
    already declares ``runButton: False`` in ``widget_config`` and the
    response's ``RootedData.x-widget_config`` lifts a ``$.runButton:
    True``, the lifted value wins — exercises line 673.
    """
    openapi = {
        "components": {
            "schemas": {
                "OBBject_RootedData_": {
                    "title": "OBBject_RootedData_",
                    "properties": {
                        "results": {
                            "anyOf": [
                                {
                                    "items": {
                                        "$ref": "#/components/schemas/RootedData"
                                    },
                                    "type": "array",
                                },
                                {"type": "null"},
                            ]
                        }
                    },
                },
                "RootedData": {
                    "title": "RootedData",
                    "properties": {"value": {"type": "number"}},
                    "x-widget_config": {"$.runButton": True},
                },
            }
        },
        "paths": {
            "/api/v1/rooted": {
                "get": {
                    "operationId": "rooted_op",
                    "parameters": [],
                    "summary": "S",
                    "description": "D",
                    "widget_config": {"runButton": False},
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/OBBject_RootedData_"
                                    }
                                }
                            }
                        }
                    },
                }
            }
        },
    }
    out = build_json(openapi, [])
    widget = next(iter(out.values()))
    # ``$.runButton: True`` from the response model overrode the
    # explicit ``runButton: False`` on the route.
    assert widget["runButton"] is True


if __name__ == "__main__":
    pytest.main()
