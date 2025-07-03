"""OpenAPI parsing Utils."""

from typing import Optional

from openbb_core.provider.utils.helpers import to_snake_case

TO_CAPS_STRINGS = [
    "Pe",
    "Peg",
    "Sloos",
    "Eps",
    "Ebit",
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
    "Ttm",
    "Id",
    "Ytd",
    "Yoy",
    "Dte",
    "Url",
    "Sedol",
    "Isin",
    "Figi",
    "Cusip",
    "Pdf",
    "Otm",
    "Atm",
    "Itm",
    "Fomc",
]


def extract_providers(params: list[dict]) -> list[str]:
    """
    Extract provider options from parameters.

    Parameters
    ----------
    params : List[Dict]
        List of parameter dictionaries.

    Returns
    -------
    List[str]
        List of provider options.
    """
    provider_params = [p for p in params if p["name"] == "provider"]
    if provider_params:
        if provider_params[0].get("schema", {}).get("enum"):
            return provider_params[0]["schema"]["enum"]
        if provider_params[0].get("schema", {}).get("default"):
            return [str(provider_params[0]["schema"]["default"])]
    return []


def set_parameter_type(p: dict, p_schema: dict):
    """
    Determine and set the type for the parameter.

    Parameters
    ----------
    p : Dict
        Processed parameter dictionary.
    p_schema : Dict
        Schema dictionary for the parameter.
    """
    p_type = p_schema.get("type") if not p.get("type") else p.get("type")

    if p_type == "string":
        p["type"] = "text"

    if p_type in ("float", "integer") or (
        not isinstance(p["value"], bool) and isinstance(p["value"], (int, float))
    ):
        p["type"] = "number"

    if (
        p_type == "boolean"
        or p_schema.get("type") == "boolean"
        or ("anyOf" in p_schema and p_schema["anyOf"][0].get("type") == "boolean")
    ):
        p["type"] = "boolean"

    if p["parameter_name"] == "date" or "_date" in p["parameter_name"]:
        p["type"] = "date"

    if "timeframe" in p["parameter_name"]:
        p["type"] = "text"

    if p["parameter_name"] == "limit":
        p["type"] = "number"

    if p.get("type") in ("array", "list") or isinstance(p.get("type"), (list, dict)):
        p["type"] = "text"

    return p


def set_parameter_options(  # noqa: PLR0912  # pylint: disable=too-many-branches
    p: dict, p_schema: dict, providers: list[str]
) -> dict:
    """
    Set options for the parameter based on the schema.

    Parameters
    ----------
    p : Dict
        Processed parameter dictionary.
    p_schema : Dict
        Schema dictionary for the parameter.
    providers : List[str]
        List of provider options.

    Returns
    -------
    Dict
        Updated parameter dictionary with options.
    """
    choices: dict[str, list[dict[str, str]]] = (
        p.get("options", {})
        if p.get("options")
        else p_schema.get("options", {}) if p_schema.get("options") else {}
    )
    widget_configs: dict[str, dict] = {}
    multiple_items_allowed_dict: dict = {}
    is_provider_specific = False
    available_providers: set = set()
    unique_general_choices: list = []
    provider: str = ""

    # Extract provider from title if present
    title_providers = []
    if (
        p_schema.get("title")
        and p_schema["title"] != p.get("parameter_name")
        and p_schema.get("title", "").islower()
    ):
        # Handle comma-separated providers in title field
        for title_name in p_schema["title"].lower().split(","):
            if title_name in [
                prov.lower() for prov in providers
            ]:  # Only actual providers
                title_providers.append(title_name)
                is_provider_specific = True
                available_providers.add(title_name)

    # Handle provider-specific choices
    for provider in providers:
        if provider in p_schema or (len(providers) == 1):
            is_provider_specific = True
            provider_choices: list = []
            if provider not in available_providers:
                available_providers.add(provider)
            if provider in p_schema:
                provider_choices = p_schema[provider].get("choices", [])
                if widget_def := p_schema[provider].get("x-widget_config"):
                    widget_configs[provider] = widget_def
            elif len(providers) == 1 and "enum" in p_schema:
                provider_choices = p_schema["enum"]
                p_schema.pop("enum")

            if provider_choices:
                choices[provider] = [
                    {"label": str(c), "value": c} for c in provider_choices
                ]
            if provider in p_schema and p_schema[provider].get(
                "multiple_items_allowed", False
            ):
                multiple_items_allowed_dict[provider] = True

    # Handle title provider choices if present
    if title_providers and "anyOf" in p_schema:
        # If we have multiple providers in title and multiple enum lists in anyOf
        # try to match them in order
        if (
            len(title_providers) > 1
            and len([s for s in p_schema["anyOf"] if "enum" in s]) > 1
        ):
            for i, provider in enumerate(title_providers):
                # Only process if this provider doesn't already have choices
                if provider not in choices or not choices[provider]:
                    # Try to match enum at the same position as the provider in the title
                    enum_index = min(i, len(p_schema["anyOf"]) - 1)
                    if "enum" in p_schema["anyOf"][enum_index]:
                        provider_choices = p_schema["anyOf"][enum_index]["enum"]
                        choices[provider] = [
                            {"label": str(c), "value": c}
                            for c in provider_choices
                            if c not in ["null", None]
                        ]
        else:
            # Existing code for single provider or multiple providers with one enum
            all_provider_choices = []
            for sub_schema in p_schema["anyOf"]:
                if "enum" in sub_schema:
                    all_provider_choices.extend(sub_schema["enum"])

            if all_provider_choices:
                for provider in title_providers:
                    if provider not in choices or not choices[provider]:
                        choices[provider] = [
                            {"label": str(c), "value": c}
                            for c in all_provider_choices
                            if c not in ["null", None]
                        ]

    # Check title for provider-specific information from description
    if p_schema.get("description") and "(provider:" in p_schema["description"]:
        desc_provider = (
            p_schema["description"].split("(provider:")[1].strip().rstrip(")")
        )
        if desc_provider and desc_provider not in available_providers:
            available_providers.add(desc_provider)
            is_provider_specific = True

    # Handle general choices
    general_choices: list = []
    if "enum" in p_schema:
        general_choices.extend(
            [
                {"label": str(c), "value": c}
                for c in p_schema["enum"]
                if c not in ["null", None]
            ]
        )
    elif "anyOf" in p_schema and not title_providers:
        for sub_schema in p_schema["anyOf"]:
            if "enum" in sub_schema:
                general_choices.extend(
                    [
                        {"label": str(c), "value": c}
                        for c in sub_schema["enum"]
                        if c not in ["null", None]
                    ]
                )

    if general_choices:
        # Remove duplicates by converting list of dicts to a set of tuples and back to list of dicts
        unique_general_choices = sorted(
            [dict(t) for t in {tuple(d.items()) for d in general_choices}],
            key=lambda x: x["label"],
        )
        if not is_provider_specific:
            if len(providers) == 1:
                choices[providers[0]] = unique_general_choices
                multiple_items_allowed_dict[providers[0]] = p_schema.get(
                    "multiple_items_allowed", False
                )
            else:
                choices["other"] = unique_general_choices
                multiple_items_allowed_dict["other"] = p_schema.get(
                    "multiple_items_allowed", False
                )

    # Use general choices as fallback for providers without specific options
    for provider in available_providers:
        if provider not in choices:
            if "anyOf" in p_schema and p_schema["anyOf"]:
                fallback_choices = p_schema["anyOf"][0].get("enum", [])
                choices[provider] = [
                    {"label": str(c), "value": c}
                    for c in fallback_choices
                    if c not in ["null", None]
                ]
            else:
                choices[provider] = unique_general_choices

        if provider in p_schema and p_schema[provider].get("x-widget_config"):
            widget_configs[provider] = p_schema[provider].get("x-widget_config")

    p["multiple_items_allowed"] = multiple_items_allowed_dict

    if choices:
        filtered_choices = {
            provider: choice for provider, choice in choices.items() if choice
        }
        p["options"] = (
            filtered_choices if filtered_choices else {provider: []} if provider else []
        )

    if is_provider_specific and len(available_providers) > 1:
        p["available_providers"] = list(available_providers)
        p["x-widget_config"] = widget_configs

    else:
        p["x-widget_config"] = (
            widget_configs.get(provider, {}) if provider else widget_configs
        )

    return p


def process_parameter(param: dict, providers: list[str]) -> dict:
    """Process a single parameter and return the processed dictionary."""
    p: dict = {}
    schema = param.get("schema", {})

    param_name = param["name"]
    p["parameter_name"] = param_name
    p["label"] = (
        param_name.replace("_", " ").replace("fixedincome", "fixed income").title()
    )

    if not p.get("label") or p.get("label") == "":
        p["label"] = schema.get("title") or param.get("title")

    p["description"] = (
        (param.get("description", param_name).split(" (provider:")[0].strip())
        .split("Multiple comma separated items allowed")[0]
        .strip()
        if param.get("description")
        else (schema.get("description") or p.get("label"))
    )
    p["optional"] = param.get("required", False) is False

    # Set type first so we can use it for value determination
    p["type"] = param.get("type", "text")

    # Get default value from schema if present
    default_value = param.get("default")

    if default_value is None:
        default_value = schema.get("default")

    p["value"] = default_value if default_value is not None else param.get("value")

    # Special handling for provider parameter
    if param_name == "provider":
        p["type"] = "text"
        p["label"] = "Provider"
        p["description"] = "Source of the data."
        p["show"] = False
        p["available_providers"] = providers
        p["value"] = None
        return p

    multiple_items_allowed_dict: dict = {}
    for _provider in providers:
        if param.get("schema", {}).get(_provider, {}).get(
            "multiple_items_allowed"
        ) and param["schema"][_provider].get("multiple_items_allowed"):
            multiple_items_allowed_dict[_provider] = True

    p["multiple_items_allowed"] = multiple_items_allowed_dict

    # Safe check for description
    if (
        p.get("description")
        and "Multiple comma separated items allowed" in p["description"]
    ):
        p["description"] = (
            p["description"].split("Multiple comma separated items allowed")[0].strip()
        )

    if x_widget_config := param.get(
        "x-widget_config", param.get("schema", {}).get("x-widget_config", {})
    ):
        p["x-widget_config"] = x_widget_config

    p_schema = param.get("schema", {}) or param

    # Initialize provider specificity tracking
    provider_specific = False
    available_providers_list = (
        []
    )  # Start with empty list - only add providers that match

    # Extract providers from title
    if p_schema.get("title"):
        # Handle comma-separated list of providers in the title
        if "," in p_schema["title"]:
            title_providers = [p.strip().lower() for p in p_schema["title"].split(",")]
            available_providers_list.extend(title_providers)
            provider_specific = True
        elif p_schema["title"].lower() in [p.lower() for p in providers]:
            # Single provider in title
            available_providers_list.append(p_schema["title"].lower())
            provider_specific = True

    # Extract providers from description
    description = param.get("description", "")
    if description and "(provider:" in description:
        desc_parts = description.split("(provider:")
        for part in desc_parts[1:]:  # Skip the first part (before any provider mention)
            desc_provider_text = part.split(")")[0].strip()
            # Handle multiple providers separated by commas in description
            for dp in desc_provider_text.split(","):
                desc_provider = dp.strip().lower()
                if desc_provider and desc_provider not in available_providers_list:
                    available_providers_list.append(desc_provider)
                    provider_specific = True

    # Process options and types
    p = set_parameter_options(p, p_schema, providers)
    p = set_parameter_type(p, p_schema)

    # Ensure options has the expected format: {"provider": []} rather than just []
    if "options" not in p:
        p["options"] = {} if providers else []
        if providers:
            for provider in providers:
                p["options"][provider] = []

    # Handle widget config
    if _widget_config := p_schema.get("x-widget_config", {}):
        for provider in providers:
            if provider in _widget_config:
                _widget_config = _widget_config[provider]
                break
        p.update(_widget_config)

    # Check if this parameter is provider-specific and filter appropriately
    if provider_specific and available_providers_list:
        # ONLY include providers that are actually in the provided providers list
        valid_provider_list = [
            p
            for p in available_providers_list
            if p.lower() in [prov.lower() for prov in providers]
        ]

        if valid_provider_list:
            p["available_providers"] = valid_provider_list

            # Check if any of our current providers match the validated available providers list
            valid_for_current_providers = any(
                current_provider.lower()
                in [valid_p.lower() for valid_p in valid_provider_list]
                for current_provider in providers
            )

            # If parameter is provider-specific but not valid for any of our current providers, skip it
            if not valid_for_current_providers:
                return {}

    return p


def get_query_schema_for_widget(
    openapi_json: dict, command_route: str
) -> tuple[list[dict], bool]:
    """
    Extract the query schema for a widget.

    Parameters
    ----------
    openapi_json : dict
        The OpenAPI specification as a dictionary.
    command_route : str
        The route of the command in the OpenAPI specification.

    Returns
    -------
    Tuple[List[Dict], bool]
        A tuple containing the list of processed parameters and a boolean indicating if a chart is present.
    """
    has_chart = False
    command = openapi_json["paths"][command_route]
    command = command.get("get", {})
    params = command.get("parameters", [])
    route_params: list[dict] = []
    providers: list[str] = extract_providers(params)

    if not providers:
        providers = ["custom"]

    for param in params:
        if param["name"] in ["sort", "order"]:
            continue
        if param["name"] == "chart":
            has_chart = True
            continue

        p = process_parameter(param, providers)
        if "show" not in p:
            p["show"] = True

        if not p.get("exclude") and not p.get("x-widget_config", {}).get("exclude"):
            route_params.append(p)

    return route_params, has_chart


def get_data_schema_for_widget(openapi_json, operation_id, route: Optional[str] = None):
    """
    Get the data schema for a widget based on its operationId.

    Args:
        openapi (dict): The OpenAPI specification as a dictionary.
        operation_id (str): The operationId of the widget.

    Returns:
        dict: The schema dictionary for the widget's data.
    """
    # Find the route and method for the given operationId

    if not route:
        for path, methods in openapi_json["paths"].items():
            for _method, details in methods.items():
                if details.get("operationId") == operation_id:
                    route = path
                    break

    _route = openapi_json["paths"].get(route, {}).get("get", {})

    if (
        schema := _route.get("responses", {})
        .get("200", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    ):
        # Get the reference to the schema from the successful response

        if "items" in schema:
            response_ref = schema["items"].get("$ref")
        else:
            response_ref = schema.get("$ref") or _route["responses"]["200"]["content"][
                "application/json"
            ].get("schema")

        if isinstance(response_ref, dict) and "type" in response_ref:
            response_ref = response_ref["type"]

        if response_ref and isinstance(response_ref, str):
            # Extract the schema name from the reference
            schema_name = response_ref.split("/")[-1]
            # Fetch and return the schema from components
            if schema_name and schema_name in openapi_json.get("components", {}).get(
                "schemas", {}
            ):
                props = openapi_json["components"]["schemas"][schema_name].get(
                    "properties", {}
                )
                if props and "results" in props:
                    return props["results"]

            return openapi_json["components"]["schemas"].get(schema_name, schema_name)
    # Return None if the schema is not found
    return None


def data_schema_to_columns_defs(  # noqa: PLR0912  # pylint: disable=too-many-branches
    openapi_json,
    operation_id,
    provider,
    route: Optional[str] = None,
    get_widget_config: bool = False,
):
    """Convert data schema to column definitions for the widget."""
    # Initialize an empty list to hold the schema references
    schema_refs: list = []

    result_schema_ref = get_data_schema_for_widget(openapi_json, operation_id, route)

    # Check if 'anyOf' is in the result_schema_ref and handle the nested structure
    if result_schema_ref and "anyOf" in result_schema_ref:
        for item in result_schema_ref["anyOf"]:
            # When there are multiple providers a 'oneOf' is used
            if "items" in item and "oneOf" in item["items"]:
                # Extract the $ref values
                schema_refs.extend(
                    [
                        oneOf_item["$ref"].split("/")[-1]
                        for oneOf_item in item["items"]["oneOf"]
                        if "$ref" in oneOf_item
                    ]
                )
            # When there's only one model there is no oneOf
            elif "items" in item and "$ref" in item["items"]:
                schema_refs.append(item["items"]["$ref"].split("/")[-1])
            elif "$ref" in item:
                schema_refs.append(item["$ref"].split("/")[-1])
            elif "oneOf" in item:
                for ref in item.get("oneOf", []):
                    maybe_ref = ref.get("$ref").split("/")[-1]
                    if maybe_ref.lower().startswith(provider):
                        schema_refs.append(maybe_ref)
                        break

    # Fetch the schemas using the extracted references
    schemas = [
        openapi_json["components"]["schemas"][ref]
        for ref in schema_refs
        if ref and ref in openapi_json["components"]["schemas"]
    ]

    if not schemas and result_schema_ref and "properties" in result_schema_ref:
        schemas.append(result_schema_ref)

    # Proceed with finding common keys and generating column definitions
    if not schemas:
        return []

    target_schema: dict = {}

    if len(schemas) == 1:
        target_schema = schemas[0]
    else:
        for schema in schemas:
            if (
                schema.get("description", "")
                .lower()
                .startswith(provider.lower().replace("tradingeconomics", "te"))
            ) or (
                schema.get("description", "").lower().startswith("us government")
                or (schema.get("description", "").lower().startswith(provider))
            ):
                target_schema = schema
                break

    if get_widget_config:
        return target_schema.get("x-widget_config", {})

    keys = list(target_schema.get("properties", {}))

    column_defs: list = []
    for key in keys:
        cell_data_type = None
        formatterFn = None
        prop = target_schema.get("properties", {}).get(key)
        # Handle prop types for both when there's a single prop type or multiple
        if "items" in prop:
            items = prop.get("items", {})
            items = items.get("anyOf", items)
            prop["anyOf"] = items if isinstance(items, list) else [items]
            types = [
                sub_prop.get("type") for sub_prop in prop["anyOf"] if "type" in sub_prop
            ]
            if "number" in types or "integer" in types or "float" in types:
                cell_data_type = "number"
            elif "string" in types and any(
                sub_prop.get("format") in ["date", "date-time"]
                for sub_prop in prop["anyOf"]
                if "format" in sub_prop
            ):
                cell_data_type = "date"
            else:
                cell_data_type = "text"
        elif "anyOf" in prop:
            types = [
                sub_prop.get("type") for sub_prop in prop["anyOf"] if "type" in sub_prop
            ]
            if "number" in types or "integer" in types or "float" in types:
                cell_data_type = "number"
            elif "string" in types and any(
                sub_prop.get("format") in ["date", "date-time"]
                for sub_prop in prop["anyOf"]
                if "format" in sub_prop
            ):
                cell_data_type = "date"
            else:
                cell_data_type = "text"
        else:
            prop_type = prop.get("type", None)
            if prop_type in ["number", "integer", "float"]:
                cell_data_type = "number"
                if prop_type == "integer":
                    formatterFn = "int"
            elif "format" in prop and prop["format"] in ["date", "date-time"]:
                cell_data_type = "date"
            else:
                cell_data_type = "text"

        column_def: dict = {}
        # OpenAPI changes some of the field names.
        k = to_snake_case(key)
        column_def["field"] = k
        if k in [
            "date",
            "symbol",
            "name",
            "symbol_root",
            "series_id",
        ]:
            column_def["pinned"] = "left"

        column_def["formatterFn"] = formatterFn
        header_name = prop.get("title", key.title())
        column_def["headerName"] = " ".join(
            [
                (word.upper() if word in TO_CAPS_STRINGS else word)
                for word in header_name.replace("_", " ").split(" ")
            ]
        )
        column_def["headerTooltip"] = prop.get(
            "description", prop.get("title", key.title())
        )
        column_def["cellDataType"] = cell_data_type
        measurement = prop.get("x-unit_measurement")

        if measurement == "percent":
            column_def["formatterFn"] = (
                "normalizedPercent"
                if prop.get("x-frontend_multiply") == 100
                else "percent"
            )
            column_def["renderFn"] = "greenRed"
            column_def["cellDataType"] = "number"

        if k in [
            "cik",
            "isin",
            "figi",
            "cusip",
            "sedol",
            "symbol",
            "children",
            "element_id",
            "parent_id",
        ]:
            column_def["cellDataType"] = "text"
            column_def["formatterFn"] = "none"
            column_def["renderFn"] = None
            if k not in ["symbol", "children", "element_id", "parent_id"]:
                column_def["headerName"] = column_def["headerName"].upper()

        if k in ["fiscal_year", "year", "year_born", "calendar_year"]:
            column_def["cellDataType"] = "number"
            column_def["formatterFn"] = "none"

        if (
            route
            and route.endswith("chains")
            and column_def.get("field")
            in [
                "underlying_symbol",
                "contract_symbol",
                "underlying_price",
                "contract_symbol",
            ]
        ):
            column_def["hide"] = True

        if column_def.get("field") in [
            "delta",
            "gamma",
            "theta",
            "vega",
            "rho",
            "vega",
            "charm",
            "vanna",
            "vomma",
        ]:
            column_def["formatterFn"] = "none"
            if column_def["field"] in ["delta", "theta", "rho"]:
                column_def["renderFn"] = "greenRed"

        if (
            route
            and route.endswith("chains")
            and column_def["field"] == "implied_volatility"
        ):
            column_def["formatterFn"] = "normalizedPercent"

        if column_def.get("field") == "change":
            column_def["renderFn"] = "greenRed"

        if (
            route
            and route.endswith("chains")
            and column_def.get("field")
            in [
                "underlying_symbol",
                "contract_symbol",
                "underlying_price",
                "contract_symbol",
            ]
        ):
            column_def["hide"] = True

        if column_def.get("field") in [
            "delta",
            "gamma",
            "theta",
            "vega",
            "rho",
            "vega",
            "charm",
            "vanna",
            "vomma",
        ]:
            column_def["formatterFn"] = "none"
            if column_def["field"] in ["delta", "theta", "rho"]:
                column_def["renderFn"] = "greenRed"

        if (
            route
            and route.endswith("chains")
            and column_def["field"] == "implied_volatility"
        ):
            column_def["formatterFn"] = "normalizedPercent"

        if column_def.get("field") == "change":
            column_def["renderFn"] = "greenRed"

        if _widget_config := prop.get("x-widget_config", {}):

            if _widget_config.get("exclude"):
                continue

            column_def.update(_widget_config)

        column_defs.append(column_def)
    return column_defs


def post_query_schema_for_widget(
    openapi_json,
    operation_id,
    route: Optional[str] = None,
    target_schema: Optional[str] = None,
):
    """
    Get the POST query schema for a widget based on its operationId.

    Args:
        openapi (dict): The OpenAPI specification as a dictionary.
        operation_id (str): The operationId of the widget.
        route (str): The route of the widget, if any.
        target_schema (str): The target schema to extract, if any.

    Returns:
        list[dict]: The schema dictionary for the widget's data.
    """

    new_params: dict = {}

    def set_param(k, v):
        """Set the parameter."""
        nonlocal new_params

        new_params[k] = {}
        new_params[k]["name"] = k
        new_params[k]["type"] = (
            "text"
            if v.get("type") == "object"
            else "date" if "date" in v.get("format", "") else v.get("type", "text")
        )
        new_params[k]["title"] = v.get("title")
        new_params[k]["description"] = v.get("description")
        new_params[k]["default"] = v.get("default")
        new_params[k]["x-widget_config"] = v.get("x-widget_config", {})
        choices: list = (
            [{"label": c, "value": c} for c in v.get("choices", []) if c]
            if v.get("choices")
            else []
        )

        if isinstance(v, dict) and "anyOf" in v:
            param_types = []
            for item in v["anyOf"]:
                if "type" in item and item.get("type") != "null":
                    param_types.append(item["type"])
                if "enum" in item:
                    choices.extend({"label": c, "value": c} for c in item["enum"])

            if param_types:
                new_params[k]["type"] = (
                    "number"
                    if "number" in param_types
                    or "integer" in param_types
                    and "string" not in param_types
                    and "date" not in param_types
                    else (
                        "date"
                        if any(
                            "date" in sub_prop.get("format", "")
                            for sub_prop in v["anyOf"]
                            if isinstance(sub_prop, dict)
                        )
                        else "text"
                    )
                )
            else:
                new_params[k]["type"] = (
                    "text"
                    if v.get("type") == "object"
                    else (
                        "date"
                        if "date" in v.get("format", "")
                        else v.get("type", "text")
                    )
                )
        elif isinstance(v, dict) and "enum" in v:
            choices.extend({"label": c, "value": c} for c in v["enum"] if c)

        if choices:
            new_params[k]["options"] = {"custom": choices}

    if not route:
        for path, methods in openapi_json["paths"].items():
            for _method, details in methods.items():
                if details.get("operationId") == operation_id:
                    route = path
                    break

    _route = openapi_json["paths"].get(route, {}).get("post", {})

    if (
        schema := _route.get("requestBody", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    ):
        # Get the reference to the schema for the request body.

        param_ref = (
            schema["items"].get("$ref")
            if "items" in schema
            else schema.get("$ref") or schema
        )

        if isinstance(param_ref, dict) and "type" in param_ref:
            param_ref = param_ref["type"]

        if param_ref and isinstance(param_ref, str):
            # Extract the schema name from the reference
            schema_name = param_ref.split("/")[-1]
            schema = openapi_json["components"]["schemas"].get(schema_name, schema_name)
            props = {} if isinstance(schema, str) else schema.get("properties", {})

            for k, v in props.items():
                if target_schema and target_schema != k:
                    continue
                if nested_schema := v.get("$ref"):
                    nested_schema_name = nested_schema.split("/")[-1]
                    nested_schema = openapi_json["components"]["schemas"].get(
                        nested_schema_name, {}
                    )
                    for nested_k, nested_v in nested_schema.get(
                        "properties", {}
                    ).items():
                        set_param(nested_k, nested_v)

                else:
                    set_param(k, v)

            route_params: list[dict] = []
            providers = ["custom"]

            for new_param_values in new_params.values():
                _new_values = new_param_values.copy()
                p = process_parameter(_new_values, providers)
                if not p.get("exclude") and not p.get("x-widget_config", {}).get(
                    "exclude"
                ):
                    route_params.append(p)

            return route_params

    # Return None if the schema is not found
    return None
