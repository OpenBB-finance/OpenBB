"""Platform V4 Markdown Generator Script."""

# pylint: disable=too-many-lines

import inspect
import json
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from openbb_core.app.model.example import Example
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import RouterLoader
from openbb_core.app.static.package_builder import DocstringGenerator, MethodDefinition
from openbb_core.provider import standard_models
from pydantic_core import PydanticUndefined

# Number of spaces to substitute tabs for indentation
TAB_WIDTH = 4

# Maximum number of commands to display on the cards
MAX_COMMANDS = 8

# Paths to use for generating and storing the markdown files
WEBSITE_PATH = Path(__file__).parent.absolute()
SEO_METADATA_PATH = Path(WEBSITE_PATH / "metadata/platform_v4_seo_metadata.json")
PLATFORM_CONTENT_PATH = Path(WEBSITE_PATH / "content/platform")
PLATFORM_REFERENCE_PATH = Path(WEBSITE_PATH / "content/platform/reference")
PLATFORM_DATA_MODELS_PATH = Path(WEBSITE_PATH / "content/platform/data_models")

# Imports used in the generated markdown files
PLATFORM_REFERENCE_IMPORT = "import ReferenceCard from '@site/src/components/General/NewReferenceCard';"  # fmt: skip
PLATFORM_REFERENCE_UL_ELEMENT = '<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">'  # noqa: E501


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


def get_endpoint_examples(
    path: str,
    func: Callable,
    examples: Optional[List[Example]],
) -> str:
    """Get the examples for the given standard model or function.

    For a given standard model or function, the examples are fetched from the
    list of Example objects and formatted into a string.

    Args:
        path (str): Path of the router.
        func (Callable): Router endpoint function.
        examples (Optional[List[Example]]): List of Examples (APIEx or PythonEx type)
        for the endpoint.

    Returns:
        str: Formatted string containing the examples for the endpoint.
    """
    sig = inspect.signature(func)
    parameter_map = dict(sig.parameters)
    formatted_params = MethodDefinition.format_params(
        path=path, parameter_map=parameter_map
    )
    explicit_params = dict(formatted_params)
    explicit_params.pop("extra_params", None)
    param_types = {k: v.annotation for k, v in explicit_params.items()}

    return DocstringGenerator.build_examples(
        path.replace("/", "."),
        param_types,
        examples,
        "website",
    )


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
        if params_type == "QueryParams" and (
            field_extra := field_info.json_schema_extra
        ):
            multiple_items_list = field_extra.get("multiple_items_allowed", None)
            if multiple_items_list:
                multiple_items = ", ".join(multiple_items_list)
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
        examples = route.openapi_extra["examples"]
        reference[path]["examples"] = get_endpoint_examples(path, route_func, examples)

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


def create_reference_markdown_seo(path: str, description: str) -> str:
    """Create the SEO section for the markdown file.

    Args:
        path (str): Command path relative to the obb class
        description (str): Description of the command

    Returns:
        str: SEO section for the markdown file
    """

    with open(SEO_METADATA_PATH) as f:
        seo_metadata = json.load(f)

    # Formatting path to match the key format in the SEO metadata
    path = path.replace("/", ".")

    if seo_metadata.get(path, None):
        cleaned_title = seo_metadata[path]["title"]
        cleaned_description = (
            seo_metadata[path]["description"]
            .strip()
            .replace("\n", " ")
            .replace("  ", " ")
            .replace('"', "'")
        )
        keywords = "- " + "\n- ".join(seo_metadata[path]["keywords"])
    else:
        # Get the router name as the title
        cleaned_title = path.split(".")[-1]
        # Get the first sentence of the description
        cleaned_description = description.split(".")[0].strip()
        keywords = "- " + "\n- ".join(path.split("."))

    markdown = (
        "---\n"
        f'title: "{cleaned_title}"\n'
        f'description: "{cleaned_description}"\n'
        f"keywords:\n{keywords}\n"
    )

    return markdown


def create_reference_markdown_intro(
    path: str, description: str, deprecated: Dict[str, str]
) -> str:
    """Create the introduction section for the markdown file.

    Args:
        path (str): Command path relative to the obb class
        description (str): Description of the command
        deprecated (Dict[str, str]): Deprecated flag and message

    Returns:
        str: Introduction section for the markdown file
    """

    deprecation_message = (
        ":::caution Deprecated\n" f"{deprecated['message']}\n" ":::\n\n"
        if deprecated["flag"]
        else ""
    )

    markdown = (
        "---\n\n"
        "import HeadTitle from '@site/src/components/General/HeadTitle.tsx';\n\n"
        f'<HeadTitle title="{path} - Reference | OpenBB Platform Docs" />\n\n'
        f"{deprecation_message}"
        "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
        "import Tabs from '@theme/Tabs';\n"
        "import TabItem from '@theme/TabItem';\n\n"
        f"{description}\n\n"
    )

    return markdown


def create_reference_markdown_tabular_section(
    parameters: Dict[str, List[Dict[str, str]]], heading: str
) -> str:
    """Create the tabular section for the markdown file.

    Args:
        parameters (Dict[str, List[Dict[str, str]]]): Dictionary of
        providers and their corresponding parameters
        heading (str): Section heading for the tabular section

    Returns:
        str: Tabular section for the markdown file
    """

    tables_list = []

    # params_list is a list of dictionaries containing the
    # information for all the parameters of the provider.
    for provider, params_list in parameters.items():
        # Exclude the standard parameters from the table
        filtered_params = [
            {k: v for k, v in params.items() if k != "standard"}
            for params in params_list
        ]

        # Do not add default and optional columns in the Data section
        # because James and Andrew don't like it
        if heading == "Data":
            filtered_params = [
                {k: v for k, v in params.items() if k not in ["default", "optional"]}
                for params in filtered_params
            ]

        # Parameter information for every provider is extracted from the dictionary
        # and joined to form a row of the table.
        # A `|` is added at the start and end of the row to create the table cell.
        params_table_rows = [
            f"| {' | '.join(map(str, params.values()))} |" for params in filtered_params
        ]
        # All rows are joined to form the table.
        params_table_rows_str = "\n".join(params_table_rows)

        if heading == "Parameters":
            tables_list.append(
                f"\n<TabItem value='{provider}' label='{provider}'>\n\n"
                "| Name | Type | Description | Default | Optional |\n"
                "| ---- | ---- | ----------- | ------- | -------- |\n"
                f"{params_table_rows_str}\n"
                "</TabItem>\n"
            )
        elif heading == "Data":
            tables_list.append(
                f"\n<TabItem value='{provider}' label='{provider}'>\n\n"
                "| Name | Type | Description |\n"
                "| ---- | ---- | ----------- |\n"
                f"{params_table_rows_str}\n"
                "</TabItem>\n"
            )

    # For easy debugging of the created strings
    tables = "".join(tables_list)
    markdown = f"---\n\n## {heading}\n\n<Tabs>\n{tables}\n</Tabs>\n\n"

    return markdown


def create_reference_markdown_returns_section(returns: List[Dict[str, str]]) -> str:
    """Create the returns section for the markdown file.

    Args:
        returns (List[Dict[str, str]]): List of dictionaries containing
        the name, type and description of the returns

    Returns:
        str: Returns section for the markdown file
    """

    returns_data = ""

    for params in returns:
        returns_data += f"{TAB_WIDTH*' '}{params['name']} : {params['type']}\n"
        returns_data += f"{TAB_WIDTH*' '}{TAB_WIDTH*' '}{params['description']}\n\n"

    # Remove the last two newline characters to render Returns section properly
    returns_data = returns_data.rstrip("\n\n")

    markdown = (
        "---\n\n"
        "## Returns\n\n"
        "```python wordwrap\n"
        "OBBject\n"
        f"{returns_data}\n"
        "```\n\n"
    )

    return markdown


def create_data_model_markdown(title: str, description: str, model: str) -> str:
    """Create the basic markdown file content for the data model.

    Args:
        title (str): Title of the data model
        description (str): Description of the data model
        model (str): Model name

    Returns:
        str: Basic markdown file content for the data model
    """

    # File name is used in the import statement
    model_import_file = find_data_model_implementation_file(model)

    # Get the first sentence of the description
    cleaned_description = description.split(".")[0].strip()
    # SEO section for the markdown file
    seo_section = (
        "---\n"
        f'title: "{title}"\n'
        f'description: "{cleaned_description}"\n'
        "---\n\n"
    )
    # Introduction section for the markdown file
    intro_section = (
        "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
        "import Tabs from '@theme/Tabs';\n"
        "import TabItem from '@theme/TabItem';\n\n"
        "---\n\n"
        "## Implementation details\n\n"
    )
    # Tabular section for the markdown file
    tables_section = (
        "### Class names\n\n"
        "| Model name | Parameters class | Data class |\n"
        "| ---------- | ---------------- | ---------- |\n"
        f"| `{model}` | `{model}QueryParams` | `{model}Data` |\n"
    )
    # Import statement for the markdown file
    import_section = (
        "\n### Import Statement\n\n"
        "```python\n"
        f"from openbb_core.provider.standard_models.{model_import_file} import (\n"
        f"{model}Data,\n{model}QueryParams,\n"
        ")\n"
        "```\n\n"
    )
    # For easy debugging of the created strings
    markdown = seo_section + intro_section + tables_section + import_section

    return markdown


def find_data_model_implementation_file(data_model: str) -> str:
    """Find the file name containing the data model class.

    Args:
        data_model (str): Data model name

    Returns:
        str: File name containing the data model class
    """

    # Function to search for the data model class in the file
    def search_in_file(file_path: Path, search_string: str) -> bool:
        with open(file_path, encoding="utf-8", errors="ignore") as file:
            if search_string in file.read():
                return True
        return False

    # Path is derived using the openbb-core package from the
    # provider/standard_models folder
    standard_models_path = Path(standard_models.__file__).parent
    file_name = ""

    for file in standard_models_path.glob("**/*.py"):
        if search_in_file(file, f"class {data_model}Data"):
            file_name = file.with_suffix("").name

    return file_name


def generate_reference_index_files(reference_content: Dict[str, str]) -> None:
    """Generate index.mdx and _category_.json files for directories and sub-directories
    in the reference directory.

    Args:
        reference_content (Dict[str, str]): Endpoints and their corresponding descriptions.
    """

    def generate_index_and_category(
        path: Path, parent_label: str = "Reference", position: int = 5
    ):
        # Check for sub-directories and markdown files in the current directory
        sub_dirs = [d for d in path.iterdir() if d.is_dir()]
        markdown_files = [
            f for f in path.iterdir() if f.is_file() and f.suffix == ".md"
        ]

        # Generate _category_.json for the current directory
        category_content = {"label": parent_label, "position": position}
        with open(path / "_category_.json", "w", encoding="utf-8") as f:
            json.dump(category_content, f, indent=2)

        # Initialize index.mdx content with the parent label and import statement
        index_content = f"# {parent_label}\n\n{PLATFORM_REFERENCE_IMPORT}\n\n"

        # Menus section for sub-directories
        if sub_dirs:
            index_content += "### Menus\n"
            index_content += PLATFORM_REFERENCE_UL_ELEMENT + "\n"
            for sub_dir in sub_dirs:
                # Initialize the sub-directory description
                sub_dir_description = ""
                # Capitalize the sub-directory name to use as a title for display
                title = sub_dir.name.capitalize()
                # Get the relative path of the sub-directory from the platform reference path
                # and convert it to POSIX style for consistency across OS
                sub_dir_path = sub_dir.relative_to(PLATFORM_REFERENCE_PATH).as_posix()
                # List all markdown files in the sub-directory, excluding the index.mdx file,
                # to include in the description
                sub_dir_markdown_files = [
                    f.stem for f in sub_dir.glob("*.md") if f.name != "index.mdx"
                ]
                # If there are markdown files found, append their names to the sub-directory
                # description, separated by commas
                if sub_dir_markdown_files:
                    if len(sub_dir_markdown_files) <= MAX_COMMANDS:
                        sub_dir_description += ", ".join(sub_dir_markdown_files)
                    else:
                        sub_dir_description += (
                            f"{', '.join(sub_dir_markdown_files[:MAX_COMMANDS])},..."
                        )

                url = f"/platform/reference/{sub_dir_path}"
                index_content += f'<ReferenceCard title="{title}" description="{sub_dir_description}" url="{url}" />\n'
            index_content += "</ul>\n\n"

        # Commands section for markdown files
        if markdown_files:
            index_content += "### Commands\n"
            index_content += PLATFORM_REFERENCE_UL_ELEMENT + "\n"
            for file in markdown_files:
                # Check if the current file is not the index file to avoid self-referencing
                if file.name != "index.mdx":
                    # Extract the file name without extension to use as a title
                    title = file.stem.replace("_", " ")
                    # Generate a relative file path from the PLATFORM_REFERENCE_PATH,
                    # remove the file extension, and convert it to POSIX path format
                    # for consistency across OS
                    file_path = file.relative_to(PLATFORM_REFERENCE_PATH).with_suffix("").as_posix()  # fmt: skip
                    # Attempt to fetch the file's description from reference_content
                    # using its path,split by the first period to get the first sentence,
                    # and default to an empty string if not found
                    file_description = reference_content.get(f"/{file_path}", "").split(".")[0]  # fmt: skip
                    url = f"/platform/reference/{file_path}"
                    index_content += f'<ReferenceCard title="{title}" description="{file_description}" url="{url}" />\n'
            index_content += "</ul>\n\n"

        # Save the index.mdx file
        with open(path / "index.mdx", "w", encoding="utf-8") as f:
            f.write(index_content)

        # Recursively generate for sub-directories
        for i, sub_dir in enumerate(sub_dirs, start=1):
            generate_index_and_category(sub_dir, sub_dir.name.capitalize(), i)

    # Start the recursive generation from the PLATFORM_REFERENCE_PATH
    generate_index_and_category(PLATFORM_REFERENCE_PATH)


def generate_reference_top_level_index() -> None:
    """Generate the top-level index.mdx file for the reference directory."""

    # Get the sub-directories in the reference directory
    reference_dirs = [d for d in PLATFORM_REFERENCE_PATH.iterdir() if d.is_dir()]
    reference_dirs.sort()
    reference_cards_content = ""

    for dir_path in reference_dirs:
        # Sub-directory name is used as the title for the ReferenceCard component
        title = dir_path.name
        markdown_files = []

        # Recursively find all markdown files in the directory and subdirectories
        for file in dir_path.rglob("*.md"):
            markdown_files.append(file.stem)

        # Format description as a comma-separated string
        if len(markdown_files) <= MAX_COMMANDS:
            description_str = f"{', '.join(markdown_files)}"
        else:
            description_str = f"{', '.join(markdown_files[:MAX_COMMANDS])},..."

        reference_cards_content += (
            f"<ReferenceCard\n"
            f'{TAB_WIDTH*" "}title="{title.capitalize()}"\n'
            f'{TAB_WIDTH*" "}description="{description_str}"\n'
            f'{TAB_WIDTH*" "}url="/platform/reference/{title}"\n'
            "/>\n"
        )

    index_content = (
        "# Reference\n\n"
        f"{PLATFORM_REFERENCE_IMPORT}\n\n"
        "<ul className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6'>\n"
        f"{reference_cards_content}"
        "</ul>\n"
    )

    # Generate the top-level index.mdx file for the reference directory
    with (PLATFORM_REFERENCE_PATH / "index.mdx").open("w", encoding="utf-8") as f:
        f.write(index_content)


def create_data_models_index(title: str, description: str, model: str) -> str:
    """Create the index content for the data models.

    Args:
        title (str): Title of the data model
        description (str): Description of the data model
        model (str): Model name

    Returns:
        str: Index content for the data models
    """

    # Get the first sentence of the description
    description = description.split(".")[0].strip()

    # For easy debugging of the created strings
    index_content = (
        "<ReferenceCard\n"
        f'{TAB_WIDTH*" "}title="{title}"\n'
        f'{TAB_WIDTH*" "}description="{description}"\n'
        f'{TAB_WIDTH*" "}url="/platform/data_models/{model}"\n'
        "/>\n"
    )

    return index_content


def generate_data_models_index_files(content: str) -> None:
    """Generate index.mdx and _category_.json files for the data_models directory.

    Args:
        content (str): Content for the data models index file
    """

    index_content = (
        "# Data Models\n\n"
        f"{PLATFORM_REFERENCE_IMPORT}\n\n"
        "<ul className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6'>\n"
        f"{content}\n"
        "</ul>\n"
    )

    # Generate the index.mdx file for the data_models directory
    with open(PLATFORM_DATA_MODELS_PATH / "index.mdx", "w", encoding="utf-8") as f:
        f.write(index_content)

    # Generate the _category_.json file for the data_models directory
    category_content = {"label": "Data Models", "position": 6}
    with open(
        PLATFORM_DATA_MODELS_PATH / "_category_.json", "w", encoding="utf-8"
    ) as f:
        json.dump(category_content, f, indent=2)


def generate_markdown_file(path: str, markdown_content: str, directory: str) -> None:
    """Generate markdown file using the content of the specified path and directory.

    Args:
        path (str): Path to the markdown file
        markdown_content (str): Content for the markdown file
        directory (str): Directory to save the markdown file

    Raises:
        ValueError: If the content type is invalid
    """

    # For reference, split the path to separate the
    # directory structure from the file name
    if directory == "reference":
        parts = path.strip("/").split("/")
        file_name = f"{parts[-1]}.md"
        directory_path = PLATFORM_REFERENCE_PATH / "/".join(parts[:-1])
    # For data models, the file name is derived from the last
    # part of the path, and there's no additional directory structure
    elif directory == "data_models":
        file_name = f"{path.split('/')[-1]}.md"
        directory_path = PLATFORM_DATA_MODELS_PATH
    else:
        raise ValueError(f"Invalid directory: {directory}")

    # Ensure the directory exists
    directory_path.mkdir(parents=True, exist_ok=True)

    # Generate the markdown file for the specified path and directory
    with open(directory_path / file_name, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)


def generate_platform_markdown() -> None:
    """Generate markdown files for OpenBB Docusaurus website."""

    data_models_index_content = []
    reference_index_content_dict = {}

    print("[CRITICAL] Ensure all the extensions are installed before running this script!")  # fmt: skip

    # Generate and read the reference.json file
    print("[INFO] Generating the reference.json file...")
    generate_reference_file()
    with open(PLATFORM_CONTENT_PATH / "reference.json") as f:
        reference = json.load(f)

    # Clear the platform/reference folder
    print("[INFO] Clearing the platform/reference folder...")
    shutil.rmtree(PLATFORM_REFERENCE_PATH, ignore_errors=True)

    # Clear the platform/data_models folder
    print("[INFO] Clearing the platform/data_models folder...")
    shutil.rmtree(PLATFORM_DATA_MODELS_PATH, ignore_errors=True)

    print(f"[INFO] Generating the markdown files for the {PLATFORM_REFERENCE_PATH} sub-directories...")  # fmt: skip
    print(f"[INFO] Generating the markdown files for the {PLATFORM_DATA_MODELS_PATH} directory...")  # fmt: skip

    for path, path_data in reference.items():
        reference_markdown_content = ""
        data_markdown_content = ""

        description = path_data["description"]
        path_parameters_fields = path_data["parameters"]
        path_data_fields = path_data["data"]

        reference_index_content_dict[path] = description

        reference_markdown_content = create_reference_markdown_seo(
            path[1:], description
        )
        reference_markdown_content += create_reference_markdown_intro(
            path[1:], description, path_data["deprecated"]
        )
        reference_markdown_content += path_data["examples"]

        if path_parameters_fields := path_data["parameters"]:
            reference_markdown_content += create_reference_markdown_tabular_section(
                path_parameters_fields, "Parameters"
            )

        reference_markdown_content += create_reference_markdown_returns_section(
            path_data["returns"]["OBBject"]
        )

        if path_data_fields := path_data["data"]:
            reference_markdown_content += create_reference_markdown_tabular_section(
                path_data_fields, "Data"
            )

        generate_markdown_file(path, reference_markdown_content, "reference")

        if model := path_data["model"]:
            data_markdown_title = re.sub(
                r"([A-Z]{1}[a-z]+)|([A-Z]{3}|[SP500]|[EU])([A-Z]{1}[a-z]+)|([A-Z]{5,})",  # noqa: W605
                lambda m: (
                    f"{m.group(1) or m.group(4)} ".title()
                    if not any([m.group(2), m.group(3)])
                    else f"{m.group(2)} {m.group(3)} "
                ),
                path_data["model"],
            ).strip()
            data_markdown_content = create_data_model_markdown(
                data_markdown_title,
                description,
                model,
            )
            data_markdown_content += create_reference_markdown_tabular_section(
                path_parameters_fields, "Parameters"
            )
            data_markdown_content += create_reference_markdown_tabular_section(
                path_data_fields, "Data"
            )
            data_models_index_content.append(
                create_data_models_index(data_markdown_title, description, model)
            )

            generate_markdown_file(model, data_markdown_content, "data_models")

    # Generate the index.mdx and _category_.json files for the reference directory
    print(f"[INFO] Generating the index files for the {PLATFORM_REFERENCE_PATH} sub-directories...")  # fmt: skip
    generate_reference_index_files(reference_index_content_dict)
    print(
        f"[INFO] Generating the index files for the {PLATFORM_REFERENCE_PATH} directory..."
    )
    generate_reference_top_level_index()

    # Sort the data models index content alphabetically to display in the same order
    data_models_index_content.sort()
    data_models_index_content_str = "".join(data_models_index_content)

    # Generate the index.mdx and _category_.json files for the data_models directory
    print(f"[INFO] Generating the index files for the {PLATFORM_DATA_MODELS_PATH} directory...")  # fmt: skip
    generate_data_models_index_files(data_models_index_content_str)
    print("[INFO] Markdown files generated successfully!")


if __name__ == "__main__":
    generate_platform_markdown()
