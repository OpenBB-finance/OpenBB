"""OpenBB Platform API Utils."""

from typing import Dict, List


def get_query_schema_for_widget(  # noqa: PLR0912
    openapi_json: dict, command_route: str
) -> tuple[list, bool]:
    """Extract the query schema for a widget.

    Does that based on operationId, with special handling for certain parameters like
    chart, sort, limit, order...

    Args:
        openapi_json (dict): The OpenAPI specification as a dictionary.
        route (str): The route of the widget.

    Returns:
        dict: A dictionary containing the query schema for the widget, excluding specified parameters.
        bool: A boolean indicating whether the widget has a chart parameter.
    """
    has_chart = False
    command = openapi_json["paths"][command_route]
    schema_method = list(command)[0]
    command = command[schema_method]
    params = command.get("parameters", [])
    route_params: List = []
    providers: List = []

    if params[0]["name"] == "provider":
        providers = params[0].get("schema", {}).get("enum", [])

    for param in params:
        multiple_items_allowed = False
        param_name = param["name"]
        if param_name in ["sort", "order"]:
            continue
        if param_name == "chart":
            has_chart = True
            continue

        p: Dict = {}
        p["paramName"] = param_name
        p["label"] = (
            param_name.replace("_", " ").replace("fixedincome", "fixed income").title()
        )
        p["description"] = param.get("description", param_name)
        p["optional"] = param.get("required", False) is False

        if param_name == "provider":
            p["type"] = "text"
            p["label"] = "Provider"
            p["description"] = "Source of the data."
            providers = param.get("schema", {}).get("enum", [])
            p["options"] = [{"label": p, "value": p} for p in providers]
            p["value"] = (
                "yfinance"
                if "yfinance" in providers
                else list(providers)[0] if providers else None
            )
            route_params.append(p)
            continue

        if p["optional"]:
            p["value"] = None

        p_schema = param.get("schema", {})
        choices: List = []

        if providers:
            p["value"] = p_schema.get("default", None)
            for provider in providers:
                _choices: List = []
                if provider in p_schema:
                    _choices = p_schema[provider].get("choices")
                    if p_schema[provider].get("multiple_items_allowed") is True:
                        multiple_items_allowed = True
                if "choices" in p_schema:
                    _choices = p_schema["choices"]
                    if p_schema.get("multiple_items_allowed"):
                        multiple_items_allowed = True
                if _choices:
                    choices.extend(_choices)
            p["options"] = (
                [{"label": str(c), "value": c} for c in list(set(choices))]
                if choices not in ["null", None]
                else []
            )

        if "choices" in p_schema:
            p["options"] = (
                [{"label": str(c), "value": c} for c in list(set(choices))]
                if choices not in ["null", None]
                else []
            )
            if p_schema.get("multiple_items_allowed") is True:
                multiple_items_allowed = True

        if "enum" in p_schema:
            choices = p_schema.get("enum", [])
            p["options"] = (
                [{"label": str(c), "value": c} for c in list(set(choices)) if c]
                if choices not in ["null", None]
                else []
            )
        elif "anyOf" in p_schema:
            choices_types: List = []
            for sub_schema in p_schema["anyOf"]:
                if "enum" in sub_schema:
                    choices.extend(
                        [
                            {"label": str(c), "value": c}
                            for c in sub_schema["enum"]
                            if c and c not in ["null", None]
                        ]
                    )
                elif sub_schema.get("type") == "null" or not sub_schema.get("type"):
                    continue
                elif sub_schema.get("type") == "boolean":
                    p["type"] = "boolean"
                else:
                    choices_types.append(sub_schema["type"])
            if choices:
                unique_choices = list(
                    {frozenset(item.items()): item for item in choices}.values()
                )
                sorted_choices = sorted(unique_choices, key=lambda x: x["value"])
                p["options"] = sorted_choices
            if choices_types and isinstance(choices_types, list):
                _choices = [d for d in choices_types if d and d != "null"]
                p["type"] = _choices[0] if _choices else "text"
            else:
                p["type"] = choices_types

        p["value"] = param["schema"].get("default", None)
        p_type = param["schema"].get("type") if not p.get("type") else p.get("type")

        if p_type == "string" or multiple_items_allowed:
            p["type"] = "text"
            p["multiple_items_allowed"] = multiple_items_allowed is True

        if p_type in ("float", "integer") or isinstance(p.get("value"), (int, float)):
            p["type"] = "number"

        if p_type == "boolean":
            p["type"] = "text" if p["value"] is None else "boolean"

        if "date" in p["paramName"]:
            p["type"] = "date"

        if param_name == "limit":
            p["type"] = "number"

        if p.get("multiple_items_allowed"):
            p["type"] = "text"

        if p.get("type") in ("array", "list") or isinstance(p.get("type"), list):
            p["type"] = "text"
            p["multiple_items_allowed"] = True

        p["show"] = True
        route_params.append(p)

    return route_params, has_chart


def get_data_schema_for_widget(openapi_json, operation_id):
    """
    Get the data schema for a widget based on its operationId.

    Args:
        openapi (dict): The OpenAPI specification as a dictionary.
        operation_id (str): The operationId of the widget.

    Returns:
        dict: The schema dictionary for the widget's data.
    """
    # Find the route and method for the given operationId
    for _, methods in openapi_json["paths"].items():
        for _, details in methods.items():
            if details.get("operationId") == operation_id:
                # Get the reference to the schema from the successful response
                response_ref = details["responses"]["200"]["content"][
                    "application/json"
                ]["schema"]["$ref"]
                # Extract the schema name from the reference
                schema_name = response_ref.split("/")[-1]
                # Fetch and return the schema from components
                return openapi_json["components"]["schemas"][schema_name]
    # Return None if the schema is not found
    return None


def data_schema_to_columns_defs(openapi_json, result_schema_ref):
    """Convert data schema to column definitions for the widget."""
    # Initialize an empty list to hold the schema references
    schema_refs: List = []

    # Check if 'anyOf' is in the result_schema_ref and handle the nested structure
    if "anyOf" in result_schema_ref:
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

    # Fetch the schemas using the extracted references
    schemas = [
        openapi_json["components"]["schemas"][ref]
        for ref in schema_refs
        if ref in openapi_json["components"]["schemas"]
    ]

    # Proceed with finding common keys and generating column definitions
    if not schemas:
        return []

    # If there's only one schema, use its properties directly
    if len(schemas) == 1:
        common_keys = schemas[0]["properties"].keys()
    else:
        # Find common keys across all schemas if there are multiple
        common_keys = set(schemas[0]["properties"].keys())
        for schema in schemas[1:]:
            common_keys.intersection_update(schema["properties"].keys())

    column_defs: List = []
    for key in common_keys:
        cell_data_type = None
        prop = schemas[0]["properties"][key]
        # Handle prop types for both when there's a single prop type or multiple
        if "anyOf" in prop:
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
            elif "format" in prop and prop["format"] in ["date", "date-time"]:
                cell_data_type = "date"
            else:
                cell_data_type = "text"

        column_def: Dict = {}
        column_def["field"] = key
        column_def["headerName"] = prop.get("title", key.title())
        column_def["description"] = prop.get(
            "description", prop.get("title", key.title())
        )
        column_def["cellDataType"] = cell_data_type

        column_def["chartDataType"] = (
            "series" if cell_data_type in ["number", "integer", "float"] else "category"
        )

        measurement = prop.get("x-unit_measurement")
        if measurement == "percent":
            column_def["formatterFn"] = (
                "normalizedPercent"
                if prop.get("x-frontend_multiply") == 100
                else "percent"
            )
        elif cell_data_type == "date":
            column_def["formatterFn"] = "date"
        elif cell_data_type == "number":
            column_def["formatterFn"] = "none"

        column_defs.append(column_def)

    return column_defs
