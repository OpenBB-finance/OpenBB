"""Utils for building the widgets.json file."""

from copy import deepcopy
from typing import Dict, List

TO_CAPS_STRINGS = [
    "Pe",
    "Sloos",
    "Eps",
    "Ebitda",
    "Otc",
    "Cpi",
    "Pce",
    "Gdp",
    "Lbma",
    "Ipo",
    "Nbbo",
    "Ameribor",
    "Sonia",
    "Effr",
    "Sofr",
    "Iorb",
    "Estr",
    "Ecb",
    "Dpcredit",
    "Tcm",
    "Us",
    "Ice",
    "Bofa",
    "Hqm",
    "Sp500",
    "Sec",
    "Cftc",
    "Cot",
    "Etf",
    "Eu",
    "Tips",
    "Rss",
    "Sic",
    "Cik",
    "Bls",
    "Fred",
]

PROVIDER_SPECIFIC_PARAM_STRING = "(provider:"
COMMA_SEPARATED_PROVIDERS_STRING = (
    "Multiple comma separated items allowed for provider(s):"
)


def modify_query_schema(query_schema: List[Dict], provider_value: str):
    """Modify query_schema and the description for the current provider."""
    modified_query_schema = []
    for item in query_schema:
        # copy the item
        _item = deepcopy(item)
        provider_value_options = {}

        # Exclude provider parameter. Those will be added last.
        if "parameter_name" in _item and _item["parameter_name"] == "provider":
            continue

        # Exclude parameters that are not available for the current provider.
        if (
            "available_providers" in _item
            and provider_value not in _item["available_providers"]
        ):
            continue

        if provider_value in _item["multiple_items_allowed"] and _item[
            "multiple_items_allowed"
        ].get(provider_value, False):
            _item["description"] = (
                _item["description"] + " Multiple comma separated items allowed."
            )
            _item["type"] = "text"
            _item["multiSelect"] = True

        if "options" in _item:
            provider_value_options = _item.pop("options")

        if provider_value in provider_value_options and bool(
            provider_value_options[provider_value]
        ):
            _item["options"] = provider_value_options[provider_value]
            _item["type"] = "text"
        elif len(provider_value_options) == 1 and "other" in provider_value_options:
            _item["options"] = provider_value_options["other"]
            _item["type"] = "text"

        _item.pop("multiple_items_allowed")

        if "available_providers" in _item:
            _item.pop("available_providers")

        _item["paramName"] = _item.pop("parameter_name")

        modified_query_schema.append(_item)

    modified_query_schema.append(
        {"paramName": "provider", "value": provider_value, "show": False}
    )
    return modified_query_schema


def build_json(openapi: Dict):
    """Build the widgets.json file."""
    # pylint: disable=import-outside-toplevel
    from .openapi import get_query_schema_for_widget

    # TODO: Add the data schema to the widget_config once there is support for not displaying empty columns.
    # from .openapi import get_data_schema_for_widget

    widgets_json: Dict = {}
    routes = [
        p
        for p in openapi["paths"]
        if p.startswith("/api") and "get" in openapi["paths"][p]
    ]
    for route in routes:
        route_api = openapi["paths"][route]
        method = list(route_api)[0]
        widget_id = route_api[method]["operationId"]

        # Prepare the query schema of the widget
        query_schema, has_chart = get_query_schema_for_widget(openapi, route)

        # Extract providers from the query schema
        providers = []
        for item in query_schema:
            if item["parameter_name"] == "provider":
                providers = item["available_providers"]

        if not providers:
            providers = [{"value": "Custom"}]

        for provider in providers:

            # TODO: Add the data schema to the widget_config once there is support for not displaying empty columns.
            # # Prepare the data schema of the widget
            # data_schema = get_data_schema_for_widget(openapi, widget_id)
            # if (
            #     data_schema
            #     and "properties" in data_schema
            #     and "results" in data_schema["properties"]
            # ):
            #     response_schema_refs = data_schema["properties"]["results"]
            #     columns_defs = data_schema_to_columns_defs(  # noqa F841
            #         openapi, response_schema_refs
            #     )
            _cat = route.split("v1/")[-1]
            _cats = _cat.split("/")
            category = _cats[0].title()
            category = category.replace("Fixedincome", "Fixed Income")
            subcat = _cats[1].title().replace("_", " ") if len(_cats) > 2 else None
            name = (
                widget_id.replace("fixedincome", "fixed income")
                .replace("_", " ")
                .title()
            )

            name = " ".join(
                [
                    (word.upper() if word in TO_CAPS_STRINGS else word)
                    for word in name.split()
                ]
            )

            modified_query_schema = modify_query_schema(query_schema, provider)

            widget_config = {
                "name": f"{name} ({provider}) (OpenBB Platform API)",
                "description": route_api["get"]["description"],
                "category": category,
                "searchCategory": category,
                "widgetId": f"{widget_id}_{provider}_obb",
                "params": modified_query_schema,
                "endpoint": route.replace("/api", "api"),
                "gridData": {"w": 45, "h": 15},
                "data": {
                    "dataKey": "results",
                    "table": {
                        "showAll": False,
                    },
                },
            }

            if subcat:
                subcat = " ".join(
                    [
                        (word.upper() if word in TO_CAPS_STRINGS else word)
                        for word in subcat.split()
                    ]
                )
                subcat = (
                    subcat.replace("Estimates", "Analyst Estimates")
                    .replace("Fundamental", "Fundamental Analysis")
                    .replace("Compare", "Comparison Analysis")
                )
                widget_config["subCategory"] = subcat

            # TODO: Add columnsDefs to the widget_config once there is support for not displaying empty columns.
            # if columns_defs:
            #    widget_config["data"]["table"]["columnsDefs"] = columns_defs
            #    if "date" in columns_defs:
            #        widget_config["data"]["table"]["index"] = "date"
            #    if "period" in columns_defs:
            #        widget_config["data"]["table"]["index"] = "period"

            # Add the widget configuration to the widgets.json
            widgets_json[widget_config["widgetId"]] = widget_config

            if has_chart:
                widget_config_chart = deepcopy(widget_config)
                widget_config_chart["name"] = widget_config_chart["name"].replace(
                    " (OpenBB Platform API)", " Chart (OpenBB Platform API)"
                )
                widget_config_chart["widgetId"] = (
                    f"{widget_config_chart['widgetId']}_chart"
                )
                widget_config_chart["params"].append(
                    {
                        "paramName": "chart",
                        "label": "Chart",
                        "description": "Returns chart",
                        "optional": True,
                        "value": True,
                        "type": "boolean",
                        "show": False,
                    },
                )
                widget_config_chart["searchCategory"] = "chart"
                widget_config_chart["gridData"]["h"] = 20
                widget_config_chart["gridData"]["w"] = 50
                widget_config_chart["defaultViz"] = "chart"
                widget_config_chart["data"]["dataKey"] = "chart.content"
                widgets_json[widget_config_chart["widgetId"]] = widget_config_chart

    return widgets_json
