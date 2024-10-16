"""Utils for building the widgets.json file."""

from copy import deepcopy

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
    "Cusip",
]


def modify_query_schema(query_schema: list[dict], provider_value: str):
    """Modify query_schema and the description for the current provider."""
    modified_query_schema: list = []
    for item in query_schema:
        # copy the item
        _item = deepcopy(item)
        provider_value_options: dict = {}

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

    if provider_value != "custom":
        modified_query_schema.append(
            {"paramName": "provider", "value": provider_value, "show": False}
        )

    return modified_query_schema


def build_json(openapi: dict, widget_exclude_filter: list):
    """Build the widgets.json file."""
    # pylint: disable=import-outside-toplevel
    from .openapi import data_schema_to_columns_defs, get_query_schema_for_widget

    if not openapi:
        return {}

    widgets_json: dict = {}
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
        providers: list = []
        for item in query_schema:
            if item["parameter_name"] == "provider":
                providers = item["available_providers"]

        if not providers:
            providers = ["custom"]

        for provider in providers:
            columns_defs = data_schema_to_columns_defs(openapi, widget_id, provider)
            _cat = route.split("v1/")[-1]
            _cats = _cat.split("/")
            category = _cats[0].title()
            category = category.replace("Fixedincome", "Fixed Income")
            subcat = _cats[1].title().replace("_", " ") if len(_cats) > 2 else None
            name = (
                widget_id.replace("fixedincome", "fixed income")
                .replace("_", " ")
                .title()
                .replace(category if category else "", "")
                .replace(subcat if subcat else "", "")
                .strip()
            )

            name = " ".join(
                [
                    (word.upper() if word in TO_CAPS_STRINGS else word)
                    for word in name.split()
                ]
            )

            modified_query_schema = modify_query_schema(query_schema, provider)

            provider_map = {
                "tmx": "TMX",
                "ecb": "ECB",
                "econdb": "EconDB",
                "fmp": "FMP",
                "oecd": "OECD",
                "finra": "FINRA",
                "fred": "FRED",
                "imf": "IMF",
                "bls": "BLS",
                "yfinance": "yFinance",
                "sec": "SEC",
                "cftc": "CFTC",
                "tradingeconomics": "Trading Economics",
                "wsj": "WSJ",
            }
            provider_name = provider_map.get(
                provider.lower(), provider.replace("_", " ").title()
            )

            widget_config = {
                "name": f"{name}",
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
                        "showAll": True,
                    },
                },
                "source": [provider_name],
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

            if columns_defs:
                widget_config["data"]["table"]["columnsDefs"] = columns_defs

            # Add the widget configuration to the widgets.json
            if widget_config["widgetId"] not in widget_exclude_filter:
                widgets_json[widget_config["widgetId"]] = widget_config

            if has_chart:
                widget_config_chart = deepcopy(widget_config)
                widget_config_chart["name"] = widget_config_chart["name"] + " (Chart)"
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
                if widget_config_chart["widgetId"] not in widget_exclude_filter:
                    widgets_json[widget_config_chart["widgetId"]] = widget_config_chart

    return widgets_json
