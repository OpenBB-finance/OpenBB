import inspect
import json
import re
import shutil
from pathlib import Path
from textwrap import shorten
from typing import Any, Dict, List, TextIO, Tuple, Union

from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import Router, RouterLoader
from openbb_core.provider import standard_models
from pydantic_core import PydanticUndefined

WEBSITE_PATH = Path(__file__).parent.absolute()
SEO_METADATA_PATH = Path(WEBSITE_PATH / "metadata/platform_v4_seo_metadata.json")
PLATFORM_CONTENT_PATH = Path(WEBSITE_PATH / "content/platform")
PLATFORM_REFERENCE_PATH = Path(WEBSITE_PATH / "content/platform/reference")
PLATFORM_DATA_MODELS_PATH = Path(WEBSITE_PATH / "content/platform/data_models")

PLATFORM_REFERENCE_IMPORT_UL = """import ReferenceCard from "@site/src/components/General/NewReferenceCard";

<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">
"""
PLATFORM_REFERENCE_IMPORT = (
    'import ReferenceCard from "@site/src/components/General/NewReferenceCard";\n\n'
)
PLATFORM_REFERENCE_UL_ELEMENT = """<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">"""


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


def generate_reference_file() -> List[str]:
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

    with open("website/content/platform/reference.json", "w") as f:
        json.dump(reference, f)

    return list(route_map.keys())


def create_markdown_seo(path: str, path_description: str) -> str:
    with open(SEO_METADATA_PATH) as f:
        seo_metadata = json.load(f)

    path = path.replace("/", ".")

    if seo_metadata.get(path, None):
        title = seo_metadata[path]["title"]
        description = seo_metadata[path]["description"]
        keywords = "- " + "\n- ".join(seo_metadata[path]["keywords"])
    else:
        title = path
        description = path_description
        keywords = "- " + "\n- ".join(path.split("."))

    title = seo_metadata[path]["title"]
    description = seo_metadata[path]["description"]
    keywords = "- " + "\n- ".join(seo_metadata[path]["keywords"])

    markdown = (
        f"---\n"
        f"title: {title}\n"
        f"description: {description}\n"
        f"keywords:\n{keywords}\n"
        f"---\n\n"
    )

    return markdown


def create_markdown_intro(
    path: str, path_description: str, deprecated: Dict[str, str]
) -> str:
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
        f"{path_description}\n\n"
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
            if params["name"] == "provider":
                params["default"] = f"'{params['default']}'"

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
    markdown += f"| {model} | {model}QueryParams | {model}Data |\n"
    markdown += "\n### Import Statement\n\n"
    markdown += "```python\n"
    markdown += f"from openbb_core.provider.standard_models.{file_name} import (\n"
    markdown += f"{model}Data,\n{model}QueryParams,\nData,\n"
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


def create_nested_menus_card(folder: Path, url: str, data_models: bool = False) -> str:
    sub_categories = [
        sub.stem
        for sub in folder.glob("**/**/*.md*")
        if sub.is_file() and sub.stem != "index"
    ]
    path = "reference" if not data_models else "data_models"
    categories = shorten(", ".join(sub_categories), width=116, placeholder="...")
    url = f"/platform/{path}/{url}/{folder.name}".replace("//", "/")

    index_card = f"""<ReferenceCard
    title="{folder.name.replace("_", " ").title()}"
    description="{categories}"
    url="{url}"
/>\n"""
    return index_card


def create_cmd_cards(cmd_text: List[Dict[str, str]], data_models: bool = False) -> str:
    path = "reference" if not data_models else "data_models"
    cmd_cards = ""
    for cmd in cmd_text:
        title = cmd["title"].replace("_", " ")
        url = f"/platform/{path}/{cmd['url']}".replace("//", "/")
        description = shorten(f"{cmd['description']}", width=116, placeholder="...")

        if not data_models:
            title = title.title()
            url = f"{url}/{cmd['title']}"

        cmd_cards += f"""<ReferenceCard
    title="{title}"
    description="{description.split(".").pop(0).strip().replace(":", "").replace('"', "'")}"
    url="{url}"
    command
/>\n"""
    return cmd_cards


def write_reference_index(
    reference_cards: Dict[Path, List[Dict[str, str]]],
    fname: str,
    path: Path,
    rel_path: Path,
    f: TextIO,
    data_models: bool = False,
) -> None:
    """Write to the corresponding index.mdx file for a given folder, with the
    appropriate nested menus and command cards.

    Parameters
    ----------
    reference_cards : Dict[Path, List[Dict[str, str]]]
        Dictionary of command cards to be written to the index.mdx file.
    fname : str
        Name of the index.mdx file.
    path : Path
        Path to the folder to be written.
    rel_path : Path
        Relative path to the folder to be written.
    f : TextIO
        File to write to.
    data_models : bool, optional
        Whether the folder is a data_models folder, by default False
    """
    f.write(
        f"# {fname}\n\n{PLATFORM_REFERENCE_IMPORT_UL if data_models else PLATFORM_REFERENCE_IMPORT}"
    )
    sub_folders = [sub for sub in path.glob("*") if sub.is_dir()]

    menus = []
    for folder in sub_folders:
        menus.append(
            create_nested_menus_card(folder, "/".join(rel_path.parts), data_models)
        )

    if sub_folders and not data_models:
        f.write(f"### Menus\n{PLATFORM_REFERENCE_UL_ELEMENT}\n{''.join(menus)}</ul>\n")

    folder_cmd_cards: List[Dict[str, str]] = reference_cards.get(path, {})  # type: ignore

    if folder_cmd_cards:
        if not data_models:
            f.write(f"\n\n### Commands\n{PLATFORM_REFERENCE_UL_ELEMENT}\n")
        f.write(create_cmd_cards(folder_cmd_cards, data_models) + "</ul>\n")


def create_data_model_card_info(meta: Dict[str, Any]) -> Tuple[str, str]:
    description = meta["description"]

    split_description = list(filter(None, description.split(".")))  # type: ignore
    title = split_description[0]
    description = ".".join(split_description[1:]) if len(split_description) > 1 else ""

    return title, description


def create_platform_markdown() -> None:
    """Generate markdown files for OpenBB Docusaurus website."""
    path_list = generate_reference_file()

    with open(PLATFORM_CONTENT_PATH / "reference.json") as f:
        reference = json.load(f)

    print("Generating markdown files...")
    kwargs = {"encoding": "utf-8", "newline": "\n"}
    reference_cards: Dict[Path, List[Dict[str, str]]] = {}
    data_reference_cards: Dict[Path, List[Dict[str, str]]] = {}

    # Clear the platform/reference folder
    shutil.rmtree(PLATFORM_REFERENCE_PATH, ignore_errors=True)

    # Clear the platform/data_models folder
    shutil.rmtree(PLATFORM_DATA_MODELS_PATH, ignore_errors=True)

    for path in path_list:
        reference_markdown = ""
        data_markdown = ""

        func_name = path.split("/")[-1]

        folder = "/".join(path.strip("/").split("/")[:-1])
        filepath = PLATFORM_REFERENCE_PATH / folder / f"{func_name}.md"

        reference_markdown = create_markdown_seo(
            path[1:], reference[path]["description"]
        )
        reference_markdown += create_markdown_intro(
            path[1:], reference[path]["description"], reference[path]["deprecated"]
        )
        reference_markdown += create_markdown_examples(reference[path]["examples"])
        reference_markdown += create_markdown_tabular_section(
            reference[path]["parameters"], "Parameters"
        )
        reference_markdown += create_markdown_returns_section(
            reference[path]["returns"]["OBBject"]
        )
        reference_markdown += create_markdown_tabular_section(
            reference[path]["data"], "Data"
        )

        data_markdown_title = re.sub(
            r"([A-Z]{1}[a-z]+)|([A-Z]{3}|[SP500]|[EU])([A-Z]{1}[a-z]+)|([A-Z]{5,})",  # noqa: W605
            lambda m: (
                f"{m.group(1) or m.group(4)} ".title()
                if not any([m.group(2), m.group(3)])
                else f"{m.group(2)} {m.group(3)} "
            ),
            reference[path]["model"],
        ).strip()
        data_markdown = create_data_model_markdown(
            data_markdown_title,
            reference[path]["description"],
            reference[path]["model"],
        )
        data_markdown += create_markdown_tabular_section(
            reference[path]["parameters"], "Parameters"
        )
        data_markdown += create_markdown_tabular_section(
            reference[path]["data"], "Data"
        )

        # if data_model := meta_command.get("model", None):
        #     ## title is the desc here - clean this later
        #     (
        #         data_model_card_title,
        #         data_model_card_description,
        #     ) = generate_data_model_card_info(meta_command)

        #     title = re.sub(
        #         r"([A-Z]{1}[a-z]+)|([A-Z]{3}|[SP500]|[EU])([A-Z]{1}[a-z]+)|([A-Z]{5,})",  # noqa: W605
        #         lambda m: (
        #             f"{m.group(1) or m.group(4)} ".title()
        #             if not any([m.group(2), m.group(3)])
        #             else f"{m.group(2)} {m.group(3)} "
        #         ),
        #         data_model,
        #     ).strip()

        #     data_markdown = (
        #         f"---\ntitle: {title}\n"
        #         f"description: {data_model_card_title}\n---\n\n"
        #         "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
        #         "import Tabs from '@theme/Tabs';\nimport TabItem from '@theme/TabItem';\n\n"
        #     )

        #     data_markdown += generate_implementation_details_markdown_section(
        #         data_model
        #     )

        #     data_model_markdown = generate_data_markdown_section(meta_command)
        #     data_markdown += "\n\n## Parameters\n\n"
        #     if meta_command["params"]:
        #         data_markdown += generate_params_markdown_section(meta_command)

        #     data_markdown += data_model_markdown
        #     markdown += data_model_markdown

        #     data_filepath = data_models_path / f"{data_model}.md"

        #     data_reference_cards.setdefault(data_filepath.parent, []).append(
        #         dict(
        #             title=title,
        #             description=data_model_card_title or "",
        #             url=data_models_path.relative_to(data_models_path) / data_model,
        #         )
        #     )
        #     data_filepath.parent.mkdir(parents=True, exist_ok=True)
        #     with open(data_filepath, "w", **kwargs) as f:  # type: ignore
        #         f.write(data_markdown)

        # reference_cards.setdefault(filepath.parent, []).append(
        #     dict(
        #         title=func_name,
        #         description=func.__doc__ or "",
        #         url="/".join((content_path / folder).relative_to(content_path).parts),
        #     )
        # )

        # filepath.parent.mkdir(parents=True, exist_ok=True)
        # with open(filepath, "w", **kwargs) as f:  # type: ignore
        #     f.write(markdown)

    reference_cards = dict(sorted(reference_cards.items(), key=lambda item: item[0]))
    data_reference_cards = {
        folder: sorted(cards, key=lambda item: item["title"])
        for folder, cards in data_reference_cards.items()
    }
    with open(content_path / "index.mdx", "w", **kwargs) as f:  # type: ignore
        fname = "OpenBB Platform Reference"
        rel_path = content_path.relative_to(content_path)
        write_reference_index(reference_cards, fname, content_path, rel_path, f)

    with open(data_models_path / "index.mdx", "w", **kwargs) as f:  # type: ignore
        fname = "Data Models"
        rel_path = data_models_path.relative_to(data_models_path)
        write_reference_index(
            data_reference_cards, fname, data_models_path, rel_path, f, True
        )

    with open(content_path / "_category_.json", "w", **kwargs) as f:  # type: ignore
        # Generate category json
        f.write(json.dumps({"label": "Reference", "position": 5}, indent=2))

    def gen_category_json(fname: str, path: Path, position: int = 1):
        """Generate category json"""
        with open(path / "_category_.json", "w", **kwargs) as f:  # type: ignore
            f.write(
                json.dumps({"label": fname.title(), "position": position}, indent=2)
            )

        with open(path / "index.mdx", "w", **kwargs) as f:  # type: ignore
            rel_path = path.relative_to(content_path)
            write_reference_index(reference_cards, fname, path, rel_path, f)

    def gen_category_recursive(nested_path: Path):
        """Generate category json recursively"""
        position = 1
        for folder in nested_path.iterdir():
            if folder.is_dir():
                gen_category_json(folder.name, folder, position)
                gen_category_recursive(folder)  # pylint: disable=cell-var-from-loop
                position += 1

    gen_category_recursive(content_path)
    print(f"Markdown files generated, check the {content_path} folder.")


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

    filepath = website_path / "metadata/platform_v4_seo_metadata2.json"
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(metadata, f, indent=2)

    return metadata


if __name__ == "__main__":
    generate_platform_markdown()
