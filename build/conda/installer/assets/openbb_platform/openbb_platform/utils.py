"""Utils for openbb_widgets_api."""

from datetime import datetime, timedelta


def get_query_schema_for_widget(
    openapi_json: dict, command_route: str
) -> tuple[dict, bool]:
    """Extract the query schema for a widget.

    Does that based on operationId, with special handling for certain parameters like
    chart, sort, limit, order...

    Args:
        openapi_json (dict): The OpenAPI specification as a dictionary.
        route (str): The route of the widget.

    Returns:
        dict: A dictionary containing the query schema for the widget, excluding specified parameters.
    """
    _query_schema: dict = {"optional": {}}
    _has_chart: bool = False

    command_schema = openapi_json["paths"][command_route]["get"]
    for param in command_schema.get("parameters", []):
        if param["in"] == "query":
            param_name = param["name"]
            # Skip "sort", "limit", "order" parameters. This is handled by the widget
            if param_name in ["sort", "limit", "order"]:
                continue
            # Identify if there is a "chart" available
            if param_name == "chart":
                _has_chart = True
                continue
            # Handle single provider
            if (
                param_name == "provider"
                and "enum" in param["schema"]
                and len(param["schema"]["enum"]) == 1
            ):
                _query_schema["provider"] = param["schema"]["enum"][0]
                continue

            # Direct enum in schema
            if "enum" in param["schema"]:
                _query_schema["optional"][param_name] = param["schema"]["enum"]
            # Enum within anyOf
            elif "anyOf" in param["schema"]:
                enums = []
                for sub_schema in param["schema"]["anyOf"]:
                    if "enum" in sub_schema:
                        enums.extend(sub_schema["enum"])
                if enums:  # If any enums were found, remove duplicates
                    _query_schema["optional"][param_name] = list(set(enums))
                else:  # Handle other types within anyOf
                    types = [
                        sub_schema.get("type")
                        for sub_schema in param["schema"]["anyOf"]
                        if "type" in sub_schema
                    ]
                    # Default handling for common types
                    if "string" in types:
                        _query_schema["optional"][param_name] = "string"
                    elif "integer" in types:
                        _query_schema["optional"][param_name] = 0
                    elif "null" in types:
                        _query_schema["optional"][param_name] = None

            # Handling other types not within anyOf
            elif param["schema"].get("type") == "string":
                _query_schema["optional"][param_name] = "string"
            elif param["schema"].get("type") == "integer":
                _query_schema["optional"][param_name] = 0

            # Handle default dates
            if param_name == "start_date":
                # Set the default start date 3 months in the past
                _query_schema["optional"]["start_date"] = (
                    datetime.now() - timedelta(days=90)
                ).strftime("%Y-%m-%d")

    return _query_schema, _has_chart


def get_data_schema_for_widget(openapi_json, operation_id):
    """
    Fetches the data schema for a widget based on its operationId.

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
    schema_refs = []

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

    column_defs = []
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

        column_def = {}
        column_def["field"] = key
        column_def["headerName"] = prop.get("title", key.title())
        column_def["description"] = prop.get("description", prop.get("title", key.title()))
        column_def["cellDataType"] = cell_data_type

        column_def["chartDataType"] = (
            "series" if cell_data_type in ["number", "integer", "float"] else "category"
        )

        measurement = prop.get("x-unit_measurement")
        if measurement == "percent":
            column_def["formatterFn"] = "normalizedPercent" if prop.get("x-frontend_multiply") == 100 else "percent"
        elif cell_data_type == "date":
            column_def["formatterFn"] = "date"
        elif cell_data_type == "number":
            column_def["formatterFn"] = "none"

        column_defs.append(column_def)

    return column_defs
