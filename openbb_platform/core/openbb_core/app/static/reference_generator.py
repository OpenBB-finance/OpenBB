import inspect
import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, List

from pydantic_core import PydanticUndefined

from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import RouterLoader
from openbb_core.app.static.package_builder import MethodDefinition

# Paths to use for generating and storing the markdown files
WEBSITE_PATH = Path(__file__).parent.absolute()
SEO_METADATA_PATH = Path(WEBSITE_PATH / "metadata/platform_v4_seo_metadata.json")
PLATFORM_CONTENT_PATH = Path(WEBSITE_PATH / "content/platform")
PLATFORM_REFERENCE_PATH = Path(WEBSITE_PATH / "content/platform/reference")
PLATFORM_DATA_MODELS_PATH = Path(WEBSITE_PATH / "content/platform/data_models")


def get_field_data_type(field_type: Any) -> str:
    """Get the implicit data type from the field type.

    String manipulation is used to extract the implicit
    data type from the field type.

    Args:
        field_type (Any): typing object field type

    Returns:
        str: String representation of the implicit field tzxype
    """

    try:
        if "BeforeValidator" in str(field_type):
            field_type = "int"

        if "Optional" in str(field_type):
            field_type = str(field_type.__args__[0])

        if "Annotated[" in str(field_type):
            field_type = str(field_type).rsplit("[", maxsplit=1)[-1].split(",")[0]

        if "models" in str(field_type):
            field_type = str(field_type).rsplit(".", maxsplit=1)[-1]

        field_type = (
            str(field_type)
            .replace("<class '", "")
            .replace("'>", "")
            .replace("typing.", "")
            .replace("pydantic.types.", "")
            .replace("openbb_core.provider.abstract.data.", "")
            .replace("datetime.datetime", "datetime")
            .replace("datetime.date", "date")
            .replace("NoneType", "None")
            .replace(", None", "")
        )
    except TypeError:
        field_type = str(field_type)

    return field_type


def get_provider_parameter_info(endpoint: Callable) -> Dict[str, str]:
    """Get the name, type, description, default value and optionality
    information for the provider parameter.

    Function signature is insepcted to get the parameters of the router
    endpoint function. The provider parameter is then extracted from the
    function type annotations then the information is extracted from it.

    Args:
        endpoint (Callable): Router endpoint function

    Returns:
        Dict[str, str]: Dictionary of the provider parameter information
    """

    params_dict = endpoint.__annotations__
    model_type = params_dict["provider_choices"].__args__[0]
    provider_params_field = model_type.__dataclass_fields__["provider"]

    # Type is Union[Literal[<provider_name>], None]
    default = provider_params_field.type.__args__[0]
    description = (
        "The provider to use for the query, by default None. "
        "If None, the provider specified in defaults is selected "
        f"or '{default}' if there is no default."
    )

    provider_parameter_info = {
        "name": provider_params_field.name,
        "type": str(provider_params_field.type).replace("typing.", ""),
        "description": description,
        "default": default,
        "optional": True,
        "standard": True,
    }

    return provider_parameter_info


def get_provider_field_params(
    model_map: Dict[str, Any],
    params_type: str,
    provider: str = "openbb",
) -> List[Dict[str, Any]]:
    """Get the fields of the given parameter type for the given provider
    of the standard_model.

    Args:
        provider_map (Dict[str, Any]): Model Map containing the QueryParams and Data parameters
        params_type (str): Parameters to fetch data for (QueryParams or Data)
        provider (str, optional): Provider name. Defaults to "openbb".

    Returns:
        List[Dict[str, str]]: List of dictionaries containing the field name,
        type, description, default, optional flag and standard flag for each provider.
    """

    provider_field_params = []
    expanded_types = MethodDefinition.TYPE_EXPANSION

    for field, field_info in model_map[provider][params_type]["fields"].items():
        # Determine the field type, expanding it if necessary and if params_type is "Parameters"
        field_type = get_field_data_type(field_info.annotation)

        if params_type == "QueryParams" and field in expanded_types:
            expanded_type = get_field_data_type(expanded_types[field])
            field_type = f"Union[{expanded_type}, {field_type}]"

        cleaned_description = (
            str(field_info.description)
            .strip().replace("\n", " ").replace("  ", " ").replace('"', "'")
        )  # fmt: skip

        # Add information for the providers supporting multiple symbols
        if params_type == "QueryParams" and field_info.json_schema_extra:
            multiple_items = ", ".join(
                field_info.json_schema_extra["multiple_items_allowed"]
            )
            cleaned_description += (
                f" Multiple items allowed for provider(s): {multiple_items}."
            )
            # Manually setting to List[<field_type>] for multiple items
            # Should be removed if TYPE_EXPANSION is updated to include this
            field_type = f"Union[{field_type}, List[{field_type}]]"

        default_value = "" if field_info.default is PydanticUndefined else str(field_info.default)  # fmt: skip

        provider_field_params.append(
            {
                "name": field,
                "type": field_type,
                "description": cleaned_description,
                "default": default_value,
                "optional": not field_info.is_required(),
                "standard": provider == "openbb",
            }
        )

    return provider_field_params


def get_function_params_default_value(endpoint: Callable) -> Dict:
    """Get the default for the endpoint function parameters.

    Args:
        endpoint (Callable): Router endpoint function

    Returns:
        Dict: Endpoint function parameters and their default values
    """

    default_values = {}

    signature = inspect.signature(endpoint)
    parameters = signature.parameters

    for name, param in parameters.items():
        if param.default is not inspect.Parameter.empty:
            default_values[name] = param.default
        else:
            default_values[name] = ""

    return default_values


def get_post_method_parameters_info(endpoint: Callable) -> List[Dict[str, str]]:
    """Get the parameters for the POST method endpoints.

    Args:
        endpoint (Callable): Router endpoint function

    Returns:
        List[Dict[str, str]]: List of dictionaries containing the name,
        type, description, default and optionality of each parameter.
    """
    parameters_info = []
    descriptions = {}

    parameters_default_values = get_function_params_default_value(endpoint)
    section = endpoint.__doc__.split("Parameters")[1].split("Returns")[0]  # type: ignore

    lines = section.split("\n")
    current_param = None
    for line in lines:
        cleaned_line = line.strip()

        if ":" in cleaned_line:  # This line names a parameter
            current_param = cleaned_line.split(":")[0]
            current_param = current_param.strip()
        elif current_param:  # This line describes the parameter
            description = cleaned_line.strip()
            descriptions[current_param] = description
            # Reset current_param to ensure each description is
            # correctly associated with the parameter
            current_param = None

    for param, param_type in endpoint.__annotations__.items():
        if param == "return":
            continue

        parameters_info.append(
            {
                "name": param,
                "type": get_field_data_type(param_type),
                "description": descriptions.get(param, ""),
                "default": parameters_default_values.get(param, ""),
                "optional": "Optional" in str(param_type),
            }
        )

    return parameters_info


def get_post_method_returns_info(endpoint: Callable) -> List[Dict[str, str]]:
    """Get the returns information for the POST method endpoints.

    Args:
        endpoint (Callable): Router endpoint function

    Returns:
        Dict[str, str]: Dictionary containing the name, type, description of the return value
    """
    section = endpoint.__doc__.split("Parameters")[1].split("Returns")[-1]  # type: ignore
    description_lines = section.strip().split("\n")
    description = description_lines[-1].strip() if len(description_lines) > 1 else ""
    return_type = endpoint.__annotations__["return"].model_fields["results"].annotation

    # Only one item is returned hence its a list with a single dictionary.
    # Future changes to the return type will require changes to this code snippet.
    return_info = [
        {
            "name": "results",
            "type": get_field_data_type(return_type),
            "description": description,
        }
    ]

    return return_info


# mypy: disable-error-code="attr-defined,arg-type"
def generate_reference_file() -> None:
    """Generate reference.json file using the ProviderInterface map."""

    # ProviderInterface Map contains the model and its
    # corresponding QueryParams and Data fields
    pi_map = ProviderInterface().map
    reference: Dict[str, Dict] = {}

    # Fields for the reference dictionary to be used in the JSON file
    REFERENCE_FIELDS = [
        "deprecated",
        "description",
        "examples",
        "parameters",
        "returns",
        "data",
    ]

    # Router object is used to get the endpoints and their
    # corresponding APIRouter object
    router = RouterLoader.from_extensions()
    route_map = {route.path: route for route in router.api_router.routes}

    for path, route in route_map.items():
        # Initialize the reference fields as empty dictionaries
        reference[path] = {field: {} for field in REFERENCE_FIELDS}

        # Route method is used to distinguish between GET and POST methods
        route_method = route.methods

        # Route endpoint is the callable function
        route_func = route.endpoint

        # Standard model is used as the key for the ProviderInterface Map dictionary
        standard_model = route.openapi_extra["model"] if route_method == {"GET"} else ""

        # Model Map contains the QueryParams and Data fields for each provider for a standard model
        model_map = pi_map[standard_model] if standard_model else ""

        # Add endpoint model for GET methods
        reference[path]["model"] = standard_model

        # Add endpoint deprecation details
        deprecated_value = getattr(route, "deprecated", None)
        reference[path]["deprecated"] = {
            "flag": bool(deprecated_value),
            "message": route.summary if deprecated_value else None,
        }

        # Add endpoint description
        if route_method == {"GET"}:
            reference[path]["description"] = route.description
        elif route_method == {"POST"}:
            # POST method router `description` attribute is unreliable as it may or
            # may not contain the "Parameters" and "Returns" sections. Hence, the
            # endpoint function docstring is used instead.
            description = route.endpoint.__doc__.split("Parameters")[0].strip()
            # Remove extra spaces in between the string
            reference[path]["description"] = re.sub(" +", " ", description)

        # Add endpoint examples
        reference[path]["examples"] = route.openapi_extra.get("examples", [])

        # Add endpoint parameters fields for standard provider
        if route_method == {"GET"}:
            # openbb provider is always present hence its the standard field
            reference[path]["parameters"]["standard"] = get_provider_field_params(
                model_map, "QueryParams"
            )

            # Add `provider` parameter fields to the openbb provider
            provider_parameter_fields = get_provider_parameter_info(route_func)
            reference[path]["parameters"]["standard"].append(provider_parameter_fields)

            # Add endpoint data fields for standard provider
            reference[path]["data"]["standard"] = get_provider_field_params(
                model_map, "Data"
            )

            for provider in model_map:
                if provider == "openbb":
                    continue

                # Adds standard parameters to the provider parameters since they are
                # inherited by the model.
                # A copy is used to prevent the standard parameters fields from being
                # modified.
                reference[path]["parameters"][provider] = reference[path]["parameters"][
                    "standard"
                ].copy()
                provider_query_params = get_provider_field_params(
                    model_map, "QueryParams", provider
                )
                reference[path]["parameters"][provider].extend(provider_query_params)

                # Adds standard data fields to the provider data fields since they are
                # inherited by the model.
                # A copy is used to prevent the standard data fields from being modified.
                reference[path]["data"][provider] = reference[path]["data"][
                    "standard"
                ].copy()
                provider_data = get_provider_field_params(model_map, "Data", provider)
                reference[path]["data"][provider].extend(provider_data)

        elif route_method == {"POST"}:
            # Add endpoint parameters fields for POST methods
            reference[path]["parameters"]["standard"] = get_post_method_parameters_info(
                route_func
            )

        # Add endpoint returns data
        # Currently only OBBject object is returned
        if route_method == {"GET"}:
            reference[path]["returns"]["OBBject"] = [
                {
                    "name": "results",
                    "type": f"List[{standard_model}]",
                    "description": "Serializable results.",
                },
                {
                    "name": "provider",
                    "type": f"Optional[{provider_parameter_fields['type']}]",
                    "description": "Provider name.",
                },
                {
                    "name": "warnings",
                    "type": "Optional[List[Warning_]]",
                    "description": "List of warnings.",
                },
                {
                    "name": "chart",
                    "type": "Optional[Chart]",
                    "description": "Chart object.",
                },
                {
                    "name": "extra",
                    "type": "Dict[str, Any]",
                    "description": "Extra info.",
                },
            ]

        elif route_method == {"POST"}:
            reference[path]["returns"]["OBBject"] = get_post_method_returns_info(
                route_func
            )

    # Dumping the reference dictionary as a JSON file
    with open(PLATFORM_CONTENT_PATH / "reference.json", "w", encoding="utf-8") as f:
        json.dump(reference, f, indent=4)
