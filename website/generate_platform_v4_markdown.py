"""Platform V4 Markdown Generator Script."""

import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Union

from fastapi.routing import APIRoute
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import RouterLoader
from openbb_core.provider import standard_models
from pydantic_core import PydanticUndefined

# Number of spaces to substitute tabs for indentation
TAB_WIDTH = 4

# Paths to use for generating and storing the markdown files
WEBSITE_PATH = Path(__file__).parent.absolute()
SEO_METADATA_PATH = Path(WEBSITE_PATH / "metadata/platform_v4_seo_metadata.json")
PLATFORM_CONTENT_PATH = Path(WEBSITE_PATH / "content/platform")
PLATFORM_REFERENCE_PATH = Path(WEBSITE_PATH / "content/platform/reference")
PLATFORM_DATA_MODELS_PATH = Path(WEBSITE_PATH / "content/platform/data_models")

# Imports used in the generated markdown files
PLATFORM_REFERENCE_IMPORT = "import ReferenceCard from '@site/src/components/General/NewReferenceCard';"  # fmt: skip
PLATFORM_REFERENCE_UL_ELEMENT = '<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">'  # noqa: E501


def save_metadata(path: Path) -> Dict[str, Dict[str, Union[str, List[str]]]]:
    """Save SEO metadata"""
    regex = re.compile(
        r"---\ntitle: (.*)\ndescription: (.*)\nkeywords:(.*)\n---\n\nimport HeadTitle",
        re.MULTILINE | re.DOTALL,
    )

    metadata = {}
    for file in path.rglob("*/**/*.md"):
        context = file.read_text(encoding="utf-8")
        match = regex.search(context)
        if match:
            title, description, keywords = match.groups()
            key = file.relative_to(path).as_posix().removesuffix(".md")
            metadata[key.replace("/", ".")] = {
                "title": title,
                "description": description,
                "keywords": [
                    keyword.strip() for keyword in keywords.split("\n- ") if keyword
                ],
            }

    filepath = WEBSITE_PATH / "metadata/platform_v4_seo_metadata2.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata


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


def get_provider_parameter_info(route: APIRoute) -> Dict[str, str]:
    """Get the name, type, description, default value and optionality
    information for the provider parameter.

    Function signature is insepcted to get the parameters of the router
    endpoint function. The provider parameter is then extracted from the
    function type annotations then the information is extracted from it.

    Args:
        route (APIRoute): Router object containing the endpoint details

    Returns:
        Dict[str, str]: Dictionary of the provider parameter information
    """

    # TODO: Find a better way to fetch this without inspecting the signature of the function
    params_dict = route.endpoint.__annotations__
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
        type, description, default and optionality of each provider.
    """

    provider_field_params = [
        {
            "name": field,
            "type": get_field_data_type(field_info.annotation),
            "description": str(field_info.description)
            .strip()
            .replace("\n", " ")
            .replace("  ", " ")
            .replace('"', "'"),
            "default": "" if field_info.default is PydanticUndefined else str(field_info.default),  # fmt: skip
            "optional": not field_info.is_required(),
        }
        for field, field_info in model_map[provider][params_type]["fields"].items()
    ]

    return provider_field_params


def get_post_method_parameters_info(annotations, docstring):
    parameters_info = []
    descriptions = {}
    section = docstring.split("Parameters")[1].split("Returns")[0]

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
            current_param = None  # Reset current_param to ensure each description is correctly associated

    for param, type_ in annotations.items():
        detail = {
            "name": param,
            "type": get_field_data_type(type_),
            "description": descriptions.get(param, ""),
            "default": "None",  # Assuming "None" as default; specific defaults need to be manually extracted if needed
            "optional": "Optional" in str(type_),
        }
        parameters_info.append(detail)

    return parameters_info


def get_post_method_returns_info(annotations, docstring):
    section = docstring.split("Parameters")[1].split("Returns")[-1]

    # Directly capturing return description (assuming single return value for simplicity)
    description_lines = section.strip().split("\n")
    description = description_lines[-1].strip() if len(description_lines) > 1 else ""
    return_type = annotations["return"].model_fields["results"].annotation

    returns_info = {
        "name": "results",
        "type": get_field_data_type(return_type),
        "description": description,
    }

    return returns_info


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
        reference[path]["description"] = route.description

        # Add endpoint examples
        reference[path]["examples"] = route.openapi_extra.get("examples", [])

        # Add endpoint parameters fields for standard provider
        if route_method == {"GET"}:
            # openbb provider is always present hence its the standard field
            reference[path]["parameters"]["standard"] = get_provider_field_params(
                model_map, "QueryParams"
            )

            # Add `provider` parameter fields to the openbb provider
            provider_parameter_fields = get_provider_parameter_info(route)
            reference[path]["parameters"]["standard"].append(
                {
                    "name": provider_parameter_fields["name"],
                    "type": provider_parameter_fields["type"],
                    "description": provider_parameter_fields["description"],
                    "default": provider_parameter_fields["default"],
                    "optional": provider_parameter_fields["optional"],
                }
            )

            # Add endpoint data fields for standard provider
            reference[path]["data"]["standard"] = get_provider_field_params(
                model_map, "Data"
            )

            for provider in model_map:
                if provider == "openbb":
                    continue

                # Adds standard parameters to the provider parameters since they are inherited by the model
                # A copy is used to prevent the standard parameters fields from being modified
                reference[path]["parameters"][provider] = reference[path]["parameters"][
                    "standard"
                ].copy()
                provider_query_params = get_provider_field_params(
                    model_map, "QueryParams", provider
                )
                reference[path]["parameters"][provider].extend(provider_query_params)

                # Adds standard data fields to the provider data fields since they are inherited by the model
                # A copy is used to prevent the standard data fields from being modified
                reference[path]["data"][provider] = reference[path]["data"][
                    "standard"
                ].copy()
                provider_data = get_provider_field_params(model_map, "Data", provider)
                reference[path]["data"][provider].extend(provider_data)

        elif route_method == {"POST"}:
            route_annotations = route.endpoint.__annotations__.copy()
            route_docstring = route.endpoint.__doc__

            returns_annotations = {"return": route_annotations.pop("return")}
            parameters_annotations = route_annotations

            # Add endpoint parameters fields for POST methods
            reference[path]["parameters"]["standard"] = get_post_method_parameters_info(
                parameters_annotations, route_docstring
            )

        # Add endpoint returns data
        # Currently only OBBject object is returned
        if route_method == {"GET"}:
            reference[path]["returns"]["OBBject"] = [
                {
                    "name": "results",
                    "type": f"List[{standard_model}]",
                    "description": "Serializable Results.",
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
            returns_info = get_post_method_returns_info(
                returns_annotations, route_docstring
            )
            reference[path]["returns"]["OBBject"] = [
                {
                    "name": returns_info["name"],
                    "type": returns_info["type"],
                    "description": returns_info["description"],
                }
            ]

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
        cleaned_title = seo_metadata[path]["title"].replace("_", " ")
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
        cleaned_title = path.split(".")[-1].replace("_", " ")
        # Get the first sentence of the description
        cleaned_description = description.split(".")[0].strip()
        keywords = "- " + "\n- ".join(path.split("."))

    markdown = (
        f"---\n"
        f'title: "{cleaned_title}"\n'
        f'description: "{cleaned_description}"\n'
        f"keywords:\n{keywords}\n"
        f"---\n\n"
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
        "import HeadTitle from '@site/src/components/General/HeadTitle.tsx';\n\n"
        f'<HeadTitle title="{path} - Reference | OpenBB Platform Docs" />\n\n'
        f"{deprecation_message}"
        "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
        "import Tabs from '@theme/Tabs';\n"
        "import TabItem from '@theme/TabItem';\n\n"
        f"{description}\n\n"
    )

    return markdown


def create_reference_markdown_examples(examples: List[str]) -> str:
    """Create the example section for the markdown file.

    Args:
        examples (List[str]): List of examples

    Returns:
        str: Example section for the markdown file
    """

    examples_str = "from openbb import obb\n" + "\n".join(examples)
    markdown = f"Example\n-------\n\n```python\n{examples_str}\n```\n\n---\n\n"
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
        # Parameter information for every provider is extracted
        # from the dictionary and joined to form a row of the table.
        # A `|` is added at the start and end of the row to
        # create the table cell.
        params_table_rows = [
            f"| {' | '.join(map(str, params.values()))} |" for params in params_list
        ]
        # All rows are joined to form the table.
        params_table_rows_str = "\n".join(params_table_rows)

        tables_list.append(
            f"\n<TabItem value='{provider}' label='{provider}'>\n\n"
            "| Name | Type | Description | Default | Optional |\n"
            "| ---- | ---- | ----------- | ------- | -------- |\n"
            f"{params_table_rows_str}\n"
            "</TabItem>\n"
        )

    # For easy debugging of the created strings
    tables = "".join(tables_list)
    markdown = f"## {heading}\n\n<Tabs>\n{tables}\n</Tabs>\n\n---\n\n"

    return markdown


def create_reference_markdown_returns_section(returns: List[Dict[str, str]]) -> str:
    """Create the returns section for the markdown file.

    Args:
        returns (List[Dict[str, str]]): List of returns

    Returns:
        str: Returns section for the markdown file
    """

    returns_data = ""

    for params in returns:
        returns_data += f"{TAB_WIDTH*' '}{params['name']} : {params['type']}\n"
        returns_data += f"{TAB_WIDTH*' '}{TAB_WIDTH*' '}{params['description']}\n"

    markdown = (
        "## Returns\n\n"
        "```python wordwrap\n"
        "OBBject\n"
        f"{returns_data}"
        "```\n\n"
        "---\n\n"
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
    """Generate index.mdx and _category_.json files for the reference sub-directories.

    Args:
        reference_content (Dict[str, str]): Dictionary containing
        the endpoints and their corresponding descriptions
    """

    # Generate the _category_.json file for the reference directory
    print("Generating the _category_.json for the reference directory...")
    reference_category = {"label": "Reference", "position": 5}
    with open(PLATFORM_REFERENCE_PATH / "_category_.json", "w", encoding="utf-8") as f:
        json.dump(reference_category, f, indent=2)

    for path, description in reference_content.items():
        directories = path.strip("/").split("/")
        current_path = PLATFORM_REFERENCE_PATH

        for directory in directories[:-1]:
            current_path /= directory

        # Locate sub-directories for the Menus section
        sub_dirs = [d for d in current_path.iterdir() if d.is_dir()]
        # Locate markdown files for the Commands section
        markdown_files = [
            f for f in current_path.iterdir() if f.is_file() and f.suffix == ".md"
        ]

        index_content = f"# {directories[-2]}\n\n"
        index_content += f"{PLATFORM_REFERENCE_IMPORT}\n\n"

        # Building Menus section for sub-directories
        if sub_dirs:
            index_content += "### Menus\n"
            # Add the unordered list element for the menus
            index_content += PLATFORM_REFERENCE_UL_ELEMENT + "\n"

            for sub_dir in sub_dirs:
                # Format file name as the title for the ReferenceCard component
                title = sub_dir.name.replace("_", " ").capitalize()
                # Get the first sentence from the description
                cleaned_description = description.split(".")[0].strip()
                # Construct the URL for the sub-directory
                url = f"/platform/reference/{'/'.join(directories[:-1])}/{sub_dir.name}"
                # Add a ReferenceCard component for the sub-directory
                index_content += (
                    "<ReferenceCard "
                    f'title="{title}" '
                    f'description="{cleaned_description}" '
                    f'url="{url} "'
                    "/>\n"
                )
            index_content += "</ul>\n\n"

        # Commands section for markdown files
        if markdown_files:  # Check if there are any markdown files
            index_content += "### Commands\n"  # Add a Commands section header
            index_content += (
                PLATFORM_REFERENCE_UL_ELEMENT + "\n"
            )  # Add the unordered list element for the commands
            for file in markdown_files:  # Iterate through each markdown file
                if file.name != "index.mdx":  # Exclude the index file itself
                    # Format file name as the title for the ReferenceCard component
                    title = file.stem.replace("_", " ").capitalize()
                    # Get the first sentence from the description
                    cleaned_description = description.split(".")[0].strip()
                    # Construct the URL for the markdown file
                    url = (
                        f"/platform/reference/{'/'.join(directories[:-1])}/{file.stem}"
                    )
                    # Add a ReferenceCard component for the markdown file
                    index_content += (
                        "<ReferenceCard "
                        f'title="{title}" '
                        f'description="{cleaned_description}" '
                        f'url="{url} "'
                        "/>\n"
                    )
            index_content += "</ul>\n\n"

        # Generate the index.mdx file for the current directory
        print(f"Generating the index.json for the {current_path} directory...")
        with open(current_path / "index.mdx", "w", encoding="utf-8") as f:
            f.write(index_content)

        # Generate the _category_.json for the current directory
        print(f"Generating the _category_.json for the {current_path} directory...")
        category_content = {
            "label": directories[-2].capitalize(),
            "position": len(directories) - 2,
        }
        with open(current_path / "_category_.json", "w", encoding="utf-8") as f:
            json.dump(category_content, f, indent=2)


def generate_reference_top_level_index() -> None:
    """Generate the top-level index.mdx file for the reference directory."""

    # Maximum number of cards to display on the Reference page
    MAX_CARDS = 10

    # Get the sub-directories in the reference directory
    reference_dirs = [d for d in PLATFORM_REFERENCE_PATH.iterdir() if d.is_dir()]
    reference_cards_content = ""

    for dir_path in reference_dirs:
        # Sub-directory name is used as the title for the ReferenceCard component
        title = dir_path.name
        markdown_files = []

        # Recursively find all markdown files in the directory and subdirectories
        for file in dir_path.rglob("*.md"):
            markdown_files.append(file.stem.replace("_", " ").capitalize())

        # Format description as a comma-separated string
        description_str = f"{', '.join(markdown_files[:MAX_CARDS])},..."

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
    print("Generating the top-level index.mdx for the reference directory...")
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
    print("Generating the index.mdx for the data_models directory...")
    with open(PLATFORM_DATA_MODELS_PATH / "index.mdx", "w", encoding="utf-8") as f:
        f.write(index_content)

    # Generate the _category_.json file for the data_models directory
    print("Generating the _category_.json for the data_models directory...")
    category_content = {"label": "Data Models", "position": 8}
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
    print(f"Generating the {file_name} file for the {directory} directory...")
    with open(directory_path / file_name, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)


def generate_platform_markdown() -> None:
    """Generate markdown files for OpenBB Docusaurus website."""

    data_models_index_content = ""
    reference_index_content_dict = {}

    # Generate and read the reference.json file
    print("Generating reference.json file...")
    generate_reference_file()
    with open(PLATFORM_CONTENT_PATH / "reference.json") as f:
        reference = json.load(f)

    print("Generating markdown files...")

    # Clear the platform/reference folder
    print("Clearing the platform/reference folder...")
    shutil.rmtree(PLATFORM_REFERENCE_PATH, ignore_errors=True)

    # Clear the platform/data_models folder
    print("Clearing the platform/data_models folder...")
    shutil.rmtree(PLATFORM_DATA_MODELS_PATH, ignore_errors=True)

    for path, path_data in reference.items():
        reference_markdown_content = ""
        data_markdown_content = ""

        # model = path_data["model"]
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
        reference_markdown_content += create_reference_markdown_examples(
            path_data["examples"]
        )

        if path_parameters_fields := path_data["parameters"]:
            reference_markdown_content += create_reference_markdown_tabular_section(
                path_parameters_fields, "Parameters"
            )

        if path_data_fields := path_data["data"]:
            reference_markdown_content += create_reference_markdown_tabular_section(
                path_data_fields, "Data"
            )

        reference_markdown_content += create_reference_markdown_returns_section(
            path_data["returns"]["OBBject"]
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
            data_models_index_content += create_data_models_index(
                data_markdown_title, description, model
            )

            generate_markdown_file(model, data_markdown_content, "data_models")

    # Generate the index.mdx and _category_.json files for the reference directory
    generate_reference_index_files(reference_index_content_dict)
    generate_reference_top_level_index()

    # Generate the index.mdx and _category_.json files for the data_models directory
    generate_data_models_index_files(data_models_index_content)
    print(
        f"Markdown files generated, check the {PLATFORM_REFERENCE_PATH} and {PLATFORM_DATA_MODELS_PATH} folders."
    )


if __name__ == "__main__":
    generate_platform_markdown()
