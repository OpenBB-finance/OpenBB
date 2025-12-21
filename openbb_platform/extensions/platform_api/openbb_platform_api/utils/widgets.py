"""Utils for building the widgets.json file."""

from copy import deepcopy


def deep_merge_configs(
    base: dict,
    update: dict,
    match_keys: str | tuple | list | None = None,
) -> dict:
    """Deep merge two nested dictionaries."""

    if match_keys is None:
        match_keys = ["paramName", "field"]

    if isinstance(match_keys, str):
        match_keys = (match_keys,)

    def merge_values(base_val, update_val):
        """Merge two values."""
        # Handle explicit empty values
        if update_val in ([], {}, None):
            return update_val

        if isinstance(update_val, dict) and isinstance(base_val, dict):
            return deep_merge_configs(base_val, update_val, match_keys)

        if isinstance(update_val, list) and isinstance(base_val, list):
            return merge_lists(base_val, update_val)

        return update_val

    def merge_lists(base_list: list, update_list: list) -> list:
        """Merge two lists."""
        new_list: list = []
        update_items: dict = {}

        # Handle nested structures in lists
        for item in update_list:
            if isinstance(item, dict):
                for match_key in match_keys:
                    if match_key in item:
                        update_items[item[match_key]] = item
                        break
            elif isinstance(item, (list, dict)):
                new_list.append(item)

        for base_item in base_list:
            if isinstance(base_item, dict):
                matched = False
                for match_key in match_keys:
                    if match_key in base_item:
                        item_id = base_item[match_key]
                        if item_id in update_items:
                            merged = base_item.copy()
                            update_item = update_items.pop(item_id)
                            for k, v in update_item.items():
                                merged[k] = merge_values(merged.get(k), v)
                            new_list.append(merged)
                            matched = True
                            break
                if not matched:
                    new_list.append(base_item)
            elif isinstance(base_item, list):
                matching_update = next(
                    (x for x in update_list if isinstance(x, list)), None
                )
                if matching_update:
                    new_list.append(merge_lists(base_item, matching_update))
                else:
                    new_list.append(base_item)
            else:
                new_list.append(base_item)

        new_list.extend(update_items.values())

        return new_list

    for key, value in update.items():
        if key in base:
            base[key] = merge_values(base[key], value)
        else:
            base[key] = value

    return base


def modify_query_schema(query_schema: list[dict], provider_value: str):
    """Modify query_schema and the description for the current provider."""
    # pylint: disable=import-outside-toplevel
    from .openapi import (
        TO_CAPS_STRINGS,
    )

    modified_query_schema: list = []
    if not query_schema:
        return modified_query_schema
    for item in query_schema:
        # copy the item
        _item = deepcopy(item)
        provider_value_options: dict = {}
        provider_value_widget_config: dict = {}
        # Exclude provider parameter. Those will be added last.
        if "parameter_name" in _item and _item["parameter_name"] == "provider":
            continue

        # Exclude parameters that are not available for the current provider.
        if (
            "available_providers" in _item
            and provider_value not in _item["available_providers"]
        ):
            continue

        if (
            provider_value
            and isinstance(_item, dict)
            and provider_value in _item.get("multiple_items_allowed", {})
            and _item.get("multiple_items_allowed", {}).get(provider_value, False)
        ):
            _item["description"] = (
                _item["description"] + " Multiple comma separated items allowed."
            )
            _item["type"] = "text"
            _item["multiSelect"] = True

        if "options" in _item and _item.get("options"):
            provider_value_options = _item.pop("options", None)
            if isinstance(provider_value_options, list):
                provider_value_options = {provider_value: provider_value_options}

        if provider_value in provider_value_options and bool(
            provider_value_options[provider_value]
        ):
            _item["options"] = provider_value_options[provider_value]
            _item["type"] = "text"
        elif len(provider_value_options) == 1 and "other" in provider_value_options:
            _item["options"] = provider_value_options["other"]
            _item["type"] = "text"

        _ = _item.pop("multiple_items_allowed", None)

        if "available_providers" in _item:
            _item.pop("available_providers")

        _item["paramName"] = _item.pop("parameter_name", None)

        if not _item.get("label") and _item["paramName"] in [
            "url",
            "cik",
            "lei",
            "cusip",
            "isin",
            "sedol",
        ]:
            _item["label"] = _item["paramName"].upper()

        if _label := _item.get("label"):
            _item["label"] = " ".join(
                [
                    (word.upper() if word in TO_CAPS_STRINGS else word)
                    for word in _label.split()
                ]
            )

        if xwidget := _item.pop("x-widget_config", {}):
            provider_value_widget_config[
                provider_value if provider_value else "custom"
            ] = xwidget.get(provider_value if provider_value else "custom", {})

        if (
            provider_value_widget_config
            and provider_value in provider_value_widget_config
        ):
            if provider_value_widget_config[provider_value].get("exclude"):
                continue

            if provider_value_widget_config[provider_value]:
                _item = deep_merge_configs(
                    _item,
                    provider_value_widget_config[provider_value],
                    ["paramName", "value"],
                )

        if not _item.get("label") and _item["paramName"] in [
            "url",
            "cik",
            "lei",
            "cusip",
            "isin",
            "sedol",
        ]:
            _item["label"] = _item["paramName"].upper()

        if _label := _item.get("label"):
            _item["label"] = " ".join(
                [
                    (word.upper() if word in TO_CAPS_STRINGS else word)
                    for word in _label.split()
                ]
            )

        if (
            _item.get("multiSelect") is True
            and _item.get("type") == "text"
            and not _item.get("options")
            and "semicolon" not in _item.get("description", "")
        ):
            _item["multiple"] = True
            _item["style"] = (
                _item.get("style", {}) if _item.get("style") else {"popupWidth": 400}
            )

        modified_query_schema.append(_item)

    if provider_value != "custom":
        modified_query_schema.append(
            {"paramName": "provider", "value": provider_value, "show": False}
        )

    return modified_query_schema


def get_form_input_paths(openapi: dict) -> dict:
    """Get a mapping of form input paths, defined by 'widget_config.form_endpoint'."""
    return {
        path: config.get("form_endpoint")
        for path, path_config in openapi["paths"].items()
        if (config := path_config.get("get", {}).get("widget_config"))
        and config.get("form_endpoint")
    }


def build_json(  # noqa: PLR0912  # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    openapi: dict, widget_exclude_filter: list
):
    """Build the widgets.json file."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.service.system_service import SystemService  # noqa
    from .openapi import (
        TO_CAPS_STRINGS,
        data_schema_to_columns_defs,
        extract_providers,
        get_query_schema_for_widget,
        post_query_schema_for_widget,
    )

    if not openapi:
        return {}

    starred_list: list = []
    api_prefix = SystemService().system_settings.api_settings.prefix or ""

    for item in widget_exclude_filter.copy():
        if "*" in item:
            starred_list.append(item)
            widget_exclude_filter.remove(item)

    # Collect all routes that are designated as form endpoints to exclude them from direct widget generation
    form_endpoint_paths = get_form_input_paths(openapi)
    widgets_json: dict = {}
    routes = [
        p
        for p in openapi["paths"]
        if openapi["paths"].get(p, {})
        and ("get" in openapi["paths"][p] or "post" in openapi["paths"][p])
    ]
    for route in routes:
        # Skip routes that are only used as form endpoints for other routes
        if route in form_endpoint_paths.values() or route.endswith("widgets.json"):
            continue

        route_api = openapi["paths"][route]

        has_form_endpoint = route in list(form_endpoint_paths)
        form_endpoint_path = form_endpoint_paths.get(route) if has_form_endpoint else ""
        form_route: dict = (
            openapi["paths"][form_endpoint_path]["post"] if has_form_endpoint else {}
        )
        # Determine the primary method for the widget
        # If a GET exists, it's the primary. Otherwise, it's a POST.
        route_method = "get" if "get" in route_api else "post"

        skip = False
        for starred in starred_list:
            if route.startswith(
                starred.replace("*", "")
                .replace("[", "")
                .replace("]", "")
                .replace('"', "")
                .replace("'", "")
            ):
                skip = True
                break

        if skip is True:
            continue

        route_copy = route.replace(api_prefix, "")
        widget_id = (
            route_copy[1:].replace("/", "_")
            if route_copy[0] == "/"
            else route_copy.replace("/", "_")
        )

        if widget_id in widget_exclude_filter:
            continue

        widget_config_dict = route_api.get(route_method, {}).get("widget_config", {})

        # If the widget is marked as excluded, skip it.
        if widget_config_dict.get("exclude") is True:
            continue

        response_schema = (
            route_api.get(route_method, {})
            .get("responses", {})
            .get("200", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )

        # Extract providers from raw params BEFORE building query_schema
        # This allows us to build provider-specific schemas
        if route_method == "get":
            raw_params = route_api.get("get", {}).get("parameters", [])
            providers = extract_providers(raw_params)
            has_chart = any(p["name"] == "chart" for p in raw_params)
        else:  # post
            providers = []
            has_chart = False

        if not providers:
            providers = ["custom"]

        for provider in providers:
            # Build query schema PER PROVIDER to get provider-specific descriptions/defaults
            if route_method == "get":
                query_schema, _ = get_query_schema_for_widget(openapi, route, provider)
            else:  # post
                query_schema = (
                    post_query_schema_for_widget(
                        openapi, route_api.get("post", {}).get("operationId", ""), route
                    )
                    or []
                )

            columns_defs = (
                data_schema_to_columns_defs(openapi, widget_id, provider, route)
                if widget_config_dict.get("type")
                not in ["multi_file_viewer", "pdf", "metric"]
                else []
            )
            _cats = [
                r
                for r in route.split("/")
                if r and r != "api" and r[0].lower() != "v" and not r[1:].isdigit()
            ]
            category = _cats[0].title() if _cats else ""
            category = category.replace("Fixedincome", "Fixed Income")
            subcat = (
                _cats[1].title().replace("_", " ")
                if len(_cats) > 2
                else _cats[1].replace("_", " ").title() if len(_cats) > 1 else None
            )
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

            param_names: list = []
            var_schema: dict = {}

            # Determine the source of the POST body schema
            post_body_source = None
            if has_form_endpoint:
                post_body_source = form_route
            elif route_method == "post":
                post_body_source = route_api.get("post")

            if post_body_source:
                if (
                    _schema := post_body_source.get("requestBody", {})
                    .get("content", {})
                    .get("application/json", {})
                    .get("schema", {})
                ):
                    schema_name = _schema.get("$ref", "").split("/")[-1]
                    var_schema = openapi["components"]["schemas"].get(schema_name, {})

                    if var_schema:
                        var_props = var_schema.get("properties", {})
                        for k, v in var_props.items():
                            if "$ref" in v:
                                param_names.append(k)

                if param_names:
                    for _param in param_names:
                        post_params = post_query_schema_for_widget(
                            openapi, post_body_source.get("operationId"), route, _param
                        )
                        modified_post_params = modify_query_schema(
                            post_params,  # type: ignore
                            provider,  # type: ignore
                        )

                        if has_form_endpoint:
                            has_submit = False
                            for item in modified_post_params:
                                if item.get("type") == "button":
                                    has_submit = True
                                    break

                            if not has_submit:
                                modified_post_params.append(
                                    {
                                        "paramName": "submit",
                                        "label": "Submit",
                                        "type": "button",
                                        "value": True,
                                        "description": "Submit the form.",
                                    }
                                )

                            form_params = {
                                "type": "form",
                                "paramName": _param,
                                "label": "Form",
                                "description": "Form Data",
                                "endpoint": form_endpoint_path,
                                "inputParams": modified_post_params,
                            }

                            if post_config := var_schema.get("x-widget_config", {}):
                                form_params = deep_merge_configs(
                                    form_params,
                                    post_config,
                                )

                            modified_query_schema.append(form_params)
                        else:
                            # For non-form endpoints, extend with the modified params directly
                            modified_query_schema.extend(modified_post_params)
                else:  # This handles POST requests with no parameters in the body
                    post_params = post_query_schema_for_widget(
                        openapi,
                        post_body_source.get("operationId"),
                        form_endpoint_path if has_form_endpoint else route,
                    )
                    modified_post_params = modify_query_schema(
                        post_params,  # type: ignore
                        provider,  # type: ignore
                    )

                    if has_form_endpoint:
                        has_submit = False
                        for item in modified_post_params:
                            if item.get("type") == "button":
                                has_submit = True
                                break

                        if not has_submit:
                            modified_post_params.append(
                                {
                                    "paramName": "submit",
                                    "label": "Submit",
                                    "value": True,
                                    "type": "button",
                                    "description": "Submit the form.",
                                }
                            )

                        form_params = {
                            "type": "form",
                            "paramName": "form",
                            "label": var_schema.get("title", "Form"),
                            "description": var_schema.get("description", ""),
                            "endpoint": form_endpoint_path,
                            "inputParams": modified_post_params,
                        }

                        var_key: dict = {}
                        # Widget Config at the model level goes first.
                        if post_config := var_schema.get("x-widget_config", {}):
                            for key, value in post_config.copy().items():
                                if key.startswith("$."):
                                    var_key[key] = value
                                else:
                                    form_params[key] = value

                            form_params = deep_merge_configs(
                                form_params,
                                post_config,
                            )

                        # Then the widget config at the POST endpoint level takes priority.
                        if post_config := form_route.get("widget_config", {}):
                            for key, value in post_config.copy().items():
                                if key.startswith("$."):
                                    var_key[key] = value

                            form_params = deep_merge_configs(
                                form_params,
                                {
                                    k: v
                                    for k, v in post_config.items()
                                    if not k.startswith("$.")
                                },
                            )

                        modified_query_schema.append(form_params)

                        if var_key:
                            for key, value in var_key.items():
                                if (
                                    key.replace("$.", "") in widget_config_dict
                                    and "params" not in key
                                    and "inputParams" not in key
                                ):
                                    widget_config_dict.update(
                                        {key.replace("$.", ""): value}
                                    )
                                else:
                                    widget_config_dict[key.replace("$.", "")] = value

                    elif route_method == "post":
                        var_key = {}
                        # Widget Config at the model level goes first.
                        if post_config := var_schema.get("x-widget_config", {}):
                            for key, value in post_config.copy().items():
                                if key.startswith("$."):
                                    var_key[key] = value

                        if var_key:
                            for key, value in var_key.items():
                                if (
                                    key.replace("$.", "") in widget_config_dict
                                    and "params" not in key
                                    and "inputParams" not in key
                                ):
                                    widget_config_dict.update(
                                        {key.replace("$.", ""): value}
                                    )
                                else:
                                    widget_config_dict[key.replace("$.", "")] = value

            provider_map = {
                "tmx": "TMX",
                "ecb": "ECB",
                "econdb": "EconDB",
                "eia": "EIA",
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

            data_key = (
                "results"
                if response_schema
                and isinstance(response_schema, dict)
                and "$ref" in response_schema
                and "/OBBject" in response_schema.get("$ref", "")
                else ""
            )
            widget_type = (
                "markdown"
                if isinstance(response_schema, dict)
                and response_schema.get("type") == "string"
                else "table"
            )
            widget_config = {
                "name": f"{name}" if name else route_api[route_method].get("summary"),
                "description": route_api[route_method].get("description", ""),
                "category": category.replace("_", " ").title(),
                "type": widget_type,
                "searchCategory": category.replace("_", " ").title(),
                "widgetId": f"{widget_id}_{provider}_obb",
                "mcp_tool": {
                    "mcp_server": "Open Data Platform",
                    "tool_id": f"{widget_id}",
                },
                "params": modified_query_schema,
                "endpoint": route,
                "runButton": False,
                "gridData": {"w": 40, "h": 15},
                "data": {
                    "dataKey": data_key,
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

            data_var_key: dict = {}

            if data_config := data_schema_to_columns_defs(
                openapi, widget_id, provider, route, True
            ):
                for key, value in data_config.copy().items():  # type: ignore
                    if key.startswith("$."):
                        data_var_key[key] = value

                widget_config["data"] = deep_merge_configs(
                    widget_config["data"],
                    {k: v for k, v in data_config.items() if not k.startswith("$.")},  # type: ignore
                )

            if data_var_key:
                for key, value in data_var_key.items():
                    if (
                        key.replace("$.", "") in widget_config_dict
                        and key != "$.data"
                        and "columnsDefs" not in key
                    ):
                        widget_config_dict.update({key.replace("$.", ""): value})
                    else:
                        widget_config_dict[key.replace("$.", "")] = value

            # Update the widget configuration with any supplied configurations in @router.command
            if widget_config_dict:
                widget_config = deep_merge_configs(
                    widget_config,
                    widget_config_dict,
                )

            if widget_config.get("type") == "table":
                widget_config["data"]["table"]["enableAdvanced"] = True

            if widget_config.get("type") == "metric":
                widget_config["gridData"]["w"] = (
                    4
                    if widget_config["gridData"].get("w") == 40
                    and "gridData" not in widget_config_dict
                    else widget_config["gridData"].get("w")
                )
                widget_config["gridData"]["h"] = (
                    5
                    if widget_config["gridData"].get("h") == 15
                    and "gridData" not in widget_config_dict
                    else widget_config["gridData"].get("h")
                )
            elif widget_config.get("type") == "pdf":
                widget_config["gridData"]["w"] = (
                    20
                    if widget_config["gridData"].get("w") == 40
                    and "gridData" not in widget_config_dict
                    else widget_config["gridData"].get("w")
                )
                widget_config["gridData"]["h"] = (
                    25
                    if widget_config["gridData"].get("h") == 15
                    and "gridData" not in widget_config_dict
                    else widget_config["gridData"].get("h")
                )

            if source := widget_config_dict.get("source", []):
                widget_config["source"] = source

            if route_method == "post" and widget_config.get("type", "") not in [
                "ssrm_table",
                "omni",
                "multi_file_viewer",
            ]:
                widget_exclude_filter.append(widget_config["widgetId"])

            # Add the widget configuration to the widgets.json
            if widget_config["widgetId"] not in widget_exclude_filter:
                widgets_json[widget_config["widgetId"]] = widget_config

            if has_chart:
                widget_config_chart = deepcopy(widget_config)
                widget_config_chart["type"] = "chart"
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
                widget_config_chart["gridData"]["h"] = widget_config_dict.get(
                    "gridData", {}
                ).get("h", 20)
                widget_config_chart["gridData"]["w"] = widget_config_dict.get(
                    "gridData", {}
                ).get("w", 40)
                widget_config_chart["defaultViz"] = "chart"
                widget_config_chart["data"]["dataKey"] = (
                    "chart.content" if data_key else ""
                )
                if widget_config_chart["widgetId"] not in widget_exclude_filter:
                    widgets_json[widget_config_chart["widgetId"]] = widget_config_chart

    return widgets_json
