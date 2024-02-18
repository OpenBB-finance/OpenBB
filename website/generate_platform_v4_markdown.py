import inspect
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Union

from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import Router, RouterLoader
from openbb_core.provider import standard_models
from pydantic_core import PydanticUndefined

WEBSITE_PATH = Path(__file__).parent.absolute()
SEO_METADATA_PATH = Path(WEBSITE_PATH / "metadata/platform_v4_seo_metadata.json")
PLATFORM_CONTENT_PATH = Path(WEBSITE_PATH / "content/platform")
PLATFORM_REFERENCE_PATH = Path(WEBSITE_PATH / "content/platform/reference")
PLATFORM_DATA_MODELS_PATH = Path(WEBSITE_PATH / "content/platform/data_models")

PLATFORM_REFERENCE_IMPORT = 'import ReferenceCard from "@site/src/components/General/NewReferenceCard";'  # fmt: skip
PLATFORM_REFERENCE_UL_ELEMENT = '<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">'  # fmt: skip


def get_field_data_type(field_type) -> str:
    try:
        if "BeforeValidator" in str(field_type):
            field_type = "int"

        if "Optional" in str(field_type):
            field_type = str(field_type.__args__[0])

        if "Annotated[" in str(field_type):
            field_type = str(field_type).split("[")[-1].split(",")[0]

        field_type = (
            str(field_type)
            .replace("<class '", "")
            .replace("'>", "")
            .replace("typing.", "")
            .replace("pydantic.types.", "")
            .replace("datetime.datetime", "datetime")
            .replace("datetime.date", "date")
            .replace("NoneType", "None")
            .replace(", None", "")
        )
    except TypeError:
        field_type = str(field_type)

    return field_type


def get_provider_parameter_params(route: Router) -> Dict[str, str]:
    # TODO: Find a better way to fetch this without inspecting the signature of the function
    params_dict = dict(inspect.signature(route.endpoint).parameters)
    model_type = params_dict["provider_choices"].annotation.__args__[0]
    provider_params_field = model_type.__dataclass_fields__["provider"]

    default = provider_params_field.type.__args__[0]
    description = (
        "The provider to use for the query, by default None. "
        "If None, the provider specified in defaults is selected "
        f"or '{default}' if there is no default."
    )

    return {
        "name": provider_params_field.name,
        "type": str(provider_params_field.type).replace("typing.", ""),
        "description": description,
        "default": default,
        "optional": True,
    }


def get_provider_field_params(
    pi: ProviderInterface,
    standard_model: str,
    params_type: str,
    provider: str = "openbb",
) -> List[Dict[str, Any]]:
    """Return the fields of the specified params_type for the specified provider of the standard_model.

    Args:
        pi (ProviderInterface): ProviderInterface class
        standard_model (str): Name of the model
        params_type (str): Paramters to fetch data for (QueryParams or Data)
        provider (str, optional): Provider name. Defaults to "openbb".

    Returns:
        List[Dict[str, str]]: List of dictionarties containing the field name, type, description, default and optional
    """
    return [
        {
            "name": field,
            "type": get_field_data_type(field_info.annotation),
            "description": field_info.description,
            "default": "" if field_info.default is PydanticUndefined else str(field_info.default),  # fmt: skip
            "optional": not field_info.is_required(),
        }
        for field, field_info in pi.map[standard_model][provider][params_type][
            "fields"
        ].items()
    ]


def generate_reference_file() -> None:
    """Generate reference.json file using the ProviderInterface."""
    pi = ProviderInterface()

    reference: Dict[str, Dict] = {}

    REFERENCE_FIELDS = [
        "deprecated",
        "description",
        "examples",
        "parameters",
        "returns",
        "data",
    ]

    router = RouterLoader.from_extensions()
    route_map = {route.path: route for route in router.api_router.routes}

    for path, route in route_map.items():
        if route.methods == {"POST"}:
            continue

        reference[path] = {field: {} for field in REFERENCE_FIELDS}

        # Add endpoint model
        # Standard model also is the key to access router data
        standard_model = route.openapi_extra["model"]
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

        # Add endpoint parameters and data fields
        # openbb provider is always present hence is the standard field
        reference[path]["parameters"]["standard"] = get_provider_field_params(
            pi, standard_model, "QueryParams"
        )
        provider_parameter_fields = get_provider_parameter_params(route)
        reference[path]["parameters"]["standard"].append(
            {
                "name": provider_parameter_fields["name"],
                "type": provider_parameter_fields["type"],
                "description": provider_parameter_fields["description"],
                "default": provider_parameter_fields["default"],
                "optional": provider_parameter_fields["optional"],
            }
        )
        reference[path]["data"]["standard"] = get_provider_field_params(
            pi, standard_model, "Data"
        )

        for provider in pi.map[standard_model]:
            if provider == "openbb":
                continue

            # Adds standard parameters to the provider parameters since they are inherited by the model
            reference[path]["parameters"][provider] = reference[path]["parameters"][
                "standard"
            ].copy()
            provider_query_params = get_provider_field_params(
                pi, standard_model, "QueryParams", provider
            )
            reference[path]["parameters"][provider].extend(provider_query_params)

            # Adds standard data fields to the provider data fields since they are inherited by the model
            reference[path]["data"][provider] = reference[path]["data"][
                "standard"
            ].copy()
            provider_data = get_provider_field_params(
                pi, standard_model, "Data", provider
            )
            reference[path]["data"][provider].extend(provider_data)

        # Add endpoint returns
        # Currently we only return an OBBject object with the results
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

    with open(PLATFORM_CONTENT_PATH / "reference.json", "w", encoding="utf-8") as f:
        json.dump(reference, f, indent=4)


def create_markdown_seo(path: str, description: str) -> str:
    with open(SEO_METADATA_PATH) as f:
        seo_metadata = json.load(f)

    path = path.replace("/", ".")
    description = description.strip().replace("\n", " ").replace("  ", " ")

    if seo_metadata.get(path, None):
        title = seo_metadata[path]["title"]
        description = seo_metadata[path]["description"]
        keywords = "- " + "\n- ".join(seo_metadata[path]["keywords"])
    else:
        title = path
        keywords = "- " + "\n- ".join(path.split("."))

    markdown = (
        f"---\n"
        f"title: {title}\n"
        f"description: {description}\n"
        f"keywords:\n{keywords}\n"
        f"---\n\n"
    )

    return markdown


def create_markdown_intro(
    path: str, description: str, deprecated: Dict[str, str]
) -> str:
    deprecation_message = (
        ":::caution Deprecated\n" f"{deprecated['message']}\n" ":::\n\n"
        if deprecated["flag"]
        else ""
    )
    description = description.strip().replace("\n", " ").replace("  ", " ")

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


def create_markdown_examples(examples: List[str]) -> str:
    markdown = "Example\n"
    markdown += "-------\n"
    examples_str = "\n".join(examples)
    markdown += f"```python\n{examples_str}\n```\n\n"
    markdown += "---\n\n"

    return markdown


def create_markdown_tabular_section(
    parameters: Dict[str, List[Dict[str, str]]], heading: str
) -> str:
    markdown = f"## {heading}\n\n"
    tabs = ""

    for provider, params_list in parameters.items():
        params_table_rows = []

        for params in params_list:
            params_table_rows.append(
                "| " + " | ".join(str(v) for v in params.values()) + " |"
            )

        tabs += (
            f"\n<TabItem value='{provider}' label='{provider}'>\n\n"
            "| Name | Type | Description | Default | Optional |\n"
            "| ---- | ---- | ----------- | ------- | -------- |\n"
            + "\n".join(params_table_rows)
            + "\n</TabItem>\n"
        )

    markdown += f"<Tabs>\n{tabs}\n</Tabs>\n\n"
    markdown += "---\n\n"

    return markdown


def create_markdown_returns_section(returns: List[Dict[str, str]]) -> str:
    markdown = "## Returns\n\n"
    returns_data = ""

    for params in returns:
        returns_data += f"\t{params['name']} : {params['type']}\n"
        returns_data += f"\t\t{params['description']}\n"

    markdown += "```python wordwrap\n"
    markdown += "OBBject\n"
    markdown += returns_data
    markdown += "```\n\n"
    markdown += "---\n\n"

    return markdown


def create_data_model_markdown(title: str, description: str, model: str) -> str:
    file_name = find_data_model_implementation_file(model)
    description = description.strip().replace("\n", " ").replace("  ", " ")

    markdown = "---\n"
    markdown += f"title: {title}\n"
    markdown += f"description: {description}\n"
    markdown += "---\n\n"
    markdown += "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
    markdown += "import Tabs from '@theme/Tabs';\n"
    markdown += "import TabItem from '@theme/TabItem';\n\n"
    markdown += "---\n\n"
    markdown += "## Implementation details\n\n"
    markdown += "### Class names\n\n"
    markdown += "| Model name | Parameters class | Data class |\n"
    markdown += "| ---------- | ---------------- | ---------- |\n"
    markdown += f"| `{model}` | `{model}QueryParams` | `{model}Data` |\n"
    markdown += "\n### Import Statement\n\n"
    markdown += "```python\n"
    markdown += f"from openbb_core.provider.standard_models.{file_name} import (\n"
    markdown += f"{model}Data,\n{model}QueryParams,\n"
    markdown += ")\n"
    markdown += "```\n\n"

    return markdown


def find_data_model_implementation_file(data_model: str) -> str:
    def search_in_file(file_path: Path, search_string: str) -> bool:
        with open(file_path, encoding="utf-8", errors="ignore") as file:
            if search_string in file.read():
                return True
        return False

    standard_models_path = Path(standard_models.__file__).parent
    file_name = ""

    for file in standard_models_path.glob("**/*.py"):
        if search_in_file(file, f"class {data_model}Data"):
            file_name = file.with_suffix("").name

    return file_name


def generate_reference_index_files(path_list: List[str]) -> None:
    for path in path_list:
        directories = path.strip("/").split("/")
        current_path = PLATFORM_REFERENCE_PATH
        for i, directory in enumerate(directories[:-1], 1):
            current_path /= directory
            current_path.mkdir(parents=True, exist_ok=True)
            if i == len(directories) - 1:
                index_content = f"""# {directory}

import ReferenceCard from "@site/src/components/General/NewReferenceCard";

### Commands
<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">
<ReferenceCard
    title="{directories[-1].capitalize()}"
    description="Description for {directories[-1]}"
    url="/platform/reference/{'/'.join(directories)}"
    command
/>
</ul>
"""
            else:
                index_content = f"""# {directory}

import ReferenceCard from "@site/src/components/General/NewReferenceCard";

### Menus
<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">
<ReferenceCard
    title="{directories[i].capitalize()}"
    description="Description for {directories[i]}"
    url="/platform/reference/{'/'.join(directories[:i+1])}"
/>
</ul>
"""
            with open(current_path / "index.mdx", "w", encoding="utf-8") as f:
                f.write(index_content)

            category_content = {"label": directory.capitalize(), "position": i}
            with open(current_path / "_category_.json", "w", encoding="utf-8") as f:
                json.dump(category_content, f, indent=2)


def create_data_models_index(title: str, description: str, model: str) -> str:
    description = description.strip().replace("\n", " ").replace("  ", " ")

    return (
        "<ReferenceCard\n"
        f'\ttitle="{title}"\n'
        f'\tdescription="{description}"\n'
        f'\turl="/platform/reference/{model}"\n'
        "/>\n"
    )


def generate_data_models_index_files(content: str) -> None:
    index_content = (
        "# Data Models\n\n"
        "import ReferenceCard from '@site/src/components/General/NewReferenceCard';\n\n"
        "<ul className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6'>\n"
        f"{content}\n"
        "</ul>\n"
    )
    with open(PLATFORM_DATA_MODELS_PATH / "index.mdx", "w", encoding="utf-8") as f:
        f.write(index_content)

    category_content = {"label": "Data Models", "position": 4}
    with open(
        PLATFORM_DATA_MODELS_PATH / "_category_.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(category_content, f, indent=2)


def generate_markdown_file(path: str, markdown_content: str, content_type: str) -> None:
    # Determine the base path based on the content type
    # For reference content, split the path to separate the
    # directory structure from the file name
    if content_type == "reference":
        parts = path.strip("/").split("/")
        file_name = f"{parts[-1]}.md"
        directory_path = PLATFORM_REFERENCE_PATH / "/".join(parts[:-1])
    # For data models, the file name is derived from the last
    # part of the path, and there's no additional directory structure
    elif content_type == "data_model":
        file_name = f"{path.split('/')[-1]}.md"
        directory_path = PLATFORM_DATA_MODELS_PATH
    else:
        raise ValueError("Invalid content type specified")

    # Ensure the directory exists
    directory_path.mkdir(parents=True, exist_ok=True)

    # Write the markdown content to the file
    with open(directory_path / file_name, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)


def generate_platform_markdown() -> None:
    """Generate markdown files for OpenBB Docusaurus website."""
    data_models_index_content = ""
    generate_reference_file()

    with open(PLATFORM_CONTENT_PATH / "reference.json") as f:
        reference = json.load(f)

    print("Generating markdown files...")

    # Clear the platform/reference folder
    shutil.rmtree(PLATFORM_REFERENCE_PATH, ignore_errors=True)

    # Clear the platform/data_models folder
    shutil.rmtree(PLATFORM_DATA_MODELS_PATH, ignore_errors=True)

    for path, path_data in reference.items():
        reference_markdown_content = ""
        data_markdown_content = ""

        model = path_data["model"]
        description = path_data["description"]
        path_parameters_fields = path_data["parameters"]
        path_data_fields = path_data["data"]

        reference_markdown_content = create_markdown_seo(path[1:], description)
        reference_markdown_content += create_markdown_intro(
            path[1:], description, path_data["deprecated"]
        )
        reference_markdown_content += create_markdown_examples(path_data["examples"])
        reference_markdown_content += create_markdown_tabular_section(
            path_parameters_fields, "Parameters"
        )
        reference_markdown_content += create_markdown_returns_section(
            path_data["returns"]["OBBject"]
        )
        reference_markdown_content += create_markdown_tabular_section(
            path_data_fields, "Data"
        )

        generate_markdown_file(path, reference_markdown_content, "reference")

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
        data_markdown_content += create_markdown_tabular_section(
            path_parameters_fields, "Parameters"
        )
        data_markdown_content += create_markdown_tabular_section(
            path_data_fields, "Data"
        )
        data_models_index_content += create_data_models_index(
            data_markdown_title, description, model
        )

        generate_markdown_file(model, data_markdown_content, "data_model")

    generate_reference_index_files(reference.keys())
    generate_data_models_index_files(data_models_index_content)
    print(f"Markdown files generated, check the {PLATFORM_CONTENT_PATH} folder.")


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


if __name__ == "__main__":
    generate_platform_markdown()
