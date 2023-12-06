import inspect
import json
import re
import shutil
from inspect import Parameter, _empty, signature
from pathlib import Path
from textwrap import shorten
from typing import Any, Callable, Dict, List, TextIO, Tuple, Union

from docstring_parser import parse
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.static.package_builder import (
    DocstringGenerator,
    MethodDefinition,
    PathHandler,
)
from openbb_core.provider import standard_models
from pydantic.fields import FieldInfo

website_path = Path(__file__).parent.absolute()
SEO_META: Dict[str, Dict[str, Union[str, List[str]]]] = json.loads(
    (website_path / "metadata/platform_v4_seo_metadata.json").read_text()
)

REFERENCE_IMPORT_UL = """import ReferenceCard from "@site/src/components/General/NewReferenceCard";

<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">
"""

reference_import = (
    'import ReferenceCard from "@site/src/components/General/NewReferenceCard";\n\n'
)
refrence_ul_element = """<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">"""


def get_docstring_meta(
    func: Callable, full_command_path: str, formatted_params: Dict[str, Parameter]
) -> Dict[str, Any]:
    """Extracts the meta information from the docstring of a function with no standardized results model."""
    meta_command = {}
    doc_parsed = parse(func.__doc__)  # type: ignore

    cmd_params = []
    for param in doc_parsed.params:
        arg_default = (
            formatted_params[param.arg_name].default
            if param.arg_name in formatted_params
            else None
        )
        cmd_params.append(
            {
                "name": param.arg_name,
                "type": get_annotation_type(param.type_name),
                "default": str(arg_default)
                if arg_default is not inspect.Parameter.empty
                else None,
                "cleaned_type": re.sub(
                    r"Literal\[([^\"\]]*)\]",
                    f"Literal[{type(arg_default).__name__}]",
                    get_annotation_type(
                        formatted_params[param.arg_name].annotation
                        if param.arg_name in formatted_params
                        else param.type_name
                    ),
                ),
                "optional": bool(arg_default is not inspect.Parameter.empty)
                or param.is_optional,
                "doc": param.description,
            }
        )

    if doc_parsed.returns:
        meta_command["returns"] = {
            "type": doc_parsed.returns.type_name,
            "doc": doc_parsed.returns.description,
        }

    examples = []
    for example in doc_parsed.examples:
        examples.append(
            {
                "snippet": example.snippet,
                "description": example.description.strip(),  # type: ignore
            }
        )

    def_params = [
        f"{d['name']}: {d['cleaned_type']}{' = ' + d['default'] if d['default'] else ''}"
        for d in cmd_params
    ]
    meta_command.update(
        {
            "description": doc_parsed.short_description
            + (
                "\n\n" + doc_parsed.long_description
                if doc_parsed.long_description
                else ""
            ),
            "params": cmd_params,
            "func_def": f"{full_command_path}({', '.join(def_params)})",
            "examples": examples,
        }
    )

    return meta_command


def generate_markdown(meta_command: dict):
    markdown = meta_command["header"]

    markdown += "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
    markdown += (
        "import Tabs from '@theme/Tabs';\nimport TabItem from '@theme/TabItem';\n\n"
    )

    markdown += generate_markdown_section(meta_command)
    return markdown


def generate_markdown_section(meta: Dict[str, Any]):
    # Process description to handle docstring examples
    lines = meta["description"].split("\n")
    description = []
    example_code = []
    in_example_block = False

    for line in lines:
        if line.strip().startswith(">>>"):
            in_example_block = True
            # Remove leading '>>>' and spaces
            example_line = line.strip()[4:]
            example_code.append(example_line)
        else:
            if in_example_block:
                # We've reached the end of an example block
                in_example_block = False
                # Append the gathered example code as a block
                description.append("```python\n" + "\n".join(example_code) + "\n```\n")
                example_code = []  # Reset for the next example block
            # Add the current line to the description
            description.append(line.strip())

    prev_snippet = "  "
    for example in meta.get("examples", []):
        if isinstance(example["snippet"], str) and ">>>" in example["snippet"]:
            snippet = example["snippet"].replace(">>> ", "")
            example_code.append(snippet)
            if example["description"] and prev_snippet != "":
                example_code.append(example["description"])
                prev_snippet = snippet.strip()
            elif example["description"]:
                example_code.append(example["description"])
        else:
            if example["description"]:
                example_code.append(example["description"])
            prev_snippet = ""

    # Join the description parts and handle any remaining example code
    if example_code:  # If there's an example block at the end of the docstring
        if meta.get("examples", []):
            description.append("\nExample:\n-------\n")
        description.append("\n\n```python\n" + "\n".join(example_code) + "\n```")

    markdown_description = "\n".join(description)

    markdown = markdown_description
    markdown += "\n\n" if not markdown_description.endswith("\n\n") else ""

    # Only add function definition if there was no example code
    if not example_code and not re.search(r"```python", markdown):
        markdown += "```python wordwrap\n" + meta["func_def"] + "\n```\n\n"

    markdown += "---\n\n## Parameters\n\n"
    if meta["params"]:
        markdown += generate_params_markdown_section(meta)
    else:
        markdown += "This function does not take standardized parameters.\n\n"

    markdown += "---\n\n## Returns\n\n"
    if meta["returns"]:
        return_desc = meta["returns"]["doc"] if meta["returns"]["doc"] else ""
        markdown += f"```python wordwrap\n{return_desc}\n```\n\n"
    else:
        markdown += "This function does not return a standardized model\n\n"

    markdown += "---\n\n"

    return markdown


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
    f.write(f"# {fname}\n\n{REFERENCE_IMPORT_UL if data_models else reference_import}")
    sub_folders = [sub for sub in path.glob("*") if sub.is_dir()]

    menus = []
    for folder in sub_folders:
        menus.append(
            create_nested_menus_card(folder, "/".join(rel_path.parts), data_models)
        )

    if sub_folders and not data_models:
        f.write(f"### Menus\n{refrence_ul_element}\n{''.join(menus)}</ul>\n")

    folder_cmd_cards: List[Dict[str, str]] = reference_cards.get(path, {})  # type: ignore

    if folder_cmd_cards:
        if not data_models:
            f.write(f"\n\n### Commands\n{refrence_ul_element}\n")
        f.write(create_cmd_cards(folder_cmd_cards, data_models) + "</ul>\n")


provider_interface = ProviderInterface()


def get_annotation_type(annotation: Any) -> str:
    optional_regex = re.compile(r"Optional\[(.*)\]")
    annotated_regex = re.compile(r"Annotated\[(?P<type>.*)\,.*\]")

    subbed = re.sub(
        optional_regex,
        r"\1",
        str(annotation)
        .replace("<class '", "")
        .replace("'>", "")
        .replace("typing.", "")
        .replace("pydantic.types.", "")
        .replace("datetime.datetime", "datetime")
        .replace("datetime.date", "date")
        .replace("NoneType", "None")
        .replace(", None", "")
        .replace("openbb_core.provider.abstract.data.", "")
        .replace("pandas.core.frame.", "pd.")
        .replace("pandas.core.series.", "pd."),
    )
    if match := annotated_regex.match(subbed):
        subbed = match.group("type")

    return subbed


def get_command_meta(path: str, route_map: Dict[str, Any]) -> Dict[str, Any]:
    route = PathHandler.get_route(path=path, route_map=route_map)
    if not route:
        return {}

    func = route.endpoint  # type: ignore
    func_name = func.__name__
    model_name = route.openapi_extra.get("model", None) if route.openapi_extra else None

    sig = signature(func)
    parameter_map = dict(sig.parameters)
    formatted_params = MethodDefinition.format_params(path, parameter_map=parameter_map)

    meta_command: Dict[str, Union[List[Dict[str, str]], Any]] = {
        "name": func_name,
        "description": func.__doc__.strip() if func.__doc__ else "",
        "source_code_url": "",
        "func_def": "",
        "params": [],
        "provider_params": {},
        "returns": {},
        "schema": {},
        "model": model_name,
    }

    # Extract the full path from the 'path' variable, excluding the method name
    path_components = path.strip("/").split("/")
    # Construct the full command path, e.g., 'obb.equity.estimates.consensus'
    full_command_path = "obb." + ".".join(path_components[:-1])

    # Now add the actual function name
    func_name = route.endpoint.__name__
    full_command_path += f".{func_name}"

    if model_name:
        providers = provider_interface.map[model_name]

        obb_query_fields: Dict[str, FieldInfo] = providers["openbb"]["QueryParams"][
            "fields"
        ]

        meta_command["description"] += "\n\n" + DocstringGenerator.generate_example(
            model_name, obb_query_fields
        )

        available_fields = list(obb_query_fields.keys())
        available_fields.extend(["chart", "provider"])

        for param in formatted_params.values():
            if param.name not in available_fields:
                continue

            if param.name == "provider":
                # pylint: disable=W0212
                param_type = param._annotation  # type: ignore
                default = param._annotation.__args__[0].__args__[0]  # type: ignore
                description = (
                    "The provider to use for the query, by default None. "
                    f"If None, the provider specified in defaults is selected or '{default}' if there is no default."
                    ""
                )
                optional = "True"

            elif param.name == "chart":
                param_type = "bool"
                description = "Whether to create a chart or not, by default False."
                optional = "True"
                default = "False"
            else:
                description = obb_query_fields[param.name].description  # type: ignore

                param_type = param.annotation

                if param.default is Parameter.empty:
                    default = ""
                    optional = "False"
                else:
                    default = param.default
                    optional = "True"

            meta_command["params"].append(
                {
                    "name": param.name,
                    "type": get_annotation_type(param_type),
                    "default": str(default)
                    if not isinstance(default, str) or not default
                    else f'"{default}"',
                    "cleaned_type": re.sub(
                        r"Literal\[([^\"\]]*)\]",
                        f"Literal[{type(default).__name__}]",
                        get_annotation_type(param_type),
                    ),
                    "optional": optional,
                    "doc": (description or "").replace("\n", "<br/>").strip(),
                }
            )

        # Update the func_def to include the full path
        def_params = [
            f"{d['name']}: {d['cleaned_type']}{' = ' + d['default'] if d['default'] else ''}"
            for d in meta_command["params"]
        ]
        meta_command["func_def"] = f"{full_command_path}({', '.join(def_params)})"

        available_providers = re.sub(
            r"Optional\[Literal\[([^\]]*)\]",
            r"\1",
            str(
                getattr(formatted_params.get("provider", ""), "_annotation", "")
            ).replace("typing.", ""),
        )
        if sig.return_annotation != _empty:
            return_type = sig.return_annotation
            if hasattr(return_type, "__origin__"):
                return_type = return_type.__origin__

            description = f"""OBBject
    results : List[{model_name}]
        Serializable results.

    provider : Optional[Literal[{available_providers}]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution."""

            meta_command["returns"] = {
                "type": return_type.__name__,
                "doc": description,
            }

        standard, provider_extras, provider_params = {}, {}, {}  # type: ignore

        for provider_name, model_details in providers.items():
            data_fields: Dict[str, FieldInfo] = model_details["Data"]["fields"]
            query_fields: Dict[str, FieldInfo] = model_details["QueryParams"]["fields"]

            if provider_name == "openbb":
                for name, field in data_fields.items():
                    standard[name] = {
                        "type": get_annotation_type(field.annotation),
                        "doc": (field.description or "").replace("\n", "<br/>").strip(),
                    }
            else:
                for name, field in query_fields.items():
                    if name not in obb_query_fields:
                        provider_params.setdefault(provider_name, {})[name] = {
                            "type": get_annotation_type(field.annotation),
                            "doc": (field.description or "")
                            .replace("\n", "<br/>")
                            .strip(),
                            "optional": "True" if not field.is_required() else "False",
                            "default": str(field.default).replace(
                                "PydanticUndefined", ""
                            ),
                        }
                for name, field in data_fields.items():
                    if name not in providers["openbb"]["Data"]["fields"]:
                        provider_extras.setdefault(provider_name, {})[name] = {
                            "type": get_annotation_type(field.annotation),
                            "doc": (field.description or "")
                            .replace("\n", "<br/>")
                            .strip(),
                        }

        meta_command["schema"] = {
            "standard": standard,
            "provider_extras": provider_extras,
        }
        meta_command["provider_params"] = provider_params

    if not meta_command.get("params", None):
        meta_command.update(
            get_docstring_meta(func, full_command_path, formatted_params)
        )

    ref_path = full_command_path.replace("obb.", "")
    cmd_keywords = "\n- ".join(ref_path.split("."))
    default_desc = (
        meta_command.get("description", "").split(".").pop(0).strip().replace(":", "")
    )
    header = (
        f"title: {func_name}\ndescription: {default_desc}\nkeywords:\n- {cmd_keywords}"
    )

    if seo_meta := SEO_META.get(
        ref_path, SEO_META.get((".".join(path.split("/")[-2:])), None)
    ):
        keywords = "\n- ".join(seo_meta["keywords"])
        header = f"title: {seo_meta['title']}\ndescription: {seo_meta['description']}\nkeywords:\n- {keywords}"

    title = ref_path.split(".")
    title[0] += " "

    meta_command[
        "header"
    ] = f"""---\n{header}\n---\n
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="{'/'.join(title)} - Reference | OpenBB Platform Docs" />\n\n"""

    return meta_command


def generate_data_markdown_section(meta: Dict[str, Any], command: bool = True):
    if not meta.get("schema", None):
        return ""

    markdown = "## Data\n\n" if command else ""
    markdown += """<Tabs>
<TabItem value="standard" label="Standard">\n\n"""
    markdown += "| Name | Type | Description |\n"
    markdown += "| ---- | ---- | ----------- |\n"
    standard = ""
    for name, field in meta["schema"]["standard"].items():
        standard += f"| {name} | {field['type']} | {field['doc']} |\n"
    markdown += standard
    markdown += "</TabItem>\n\n"

    for provider, fields in meta["schema"]["provider_extras"].items():
        markdown += f"<TabItem value='{provider}' label='{provider}'>\n\n"
        markdown += "| Name | Type | Description |\n"
        markdown += "| ---- | ---- | ----------- |\n"
        markdown += standard
        for name, field in fields.items():
            markdown += f"| {name} | {field['type']} | {field['doc']} |\n"
        markdown += "</TabItem>\n\n"

    markdown += "</Tabs>\n\n"
    return markdown


def generate_params_markdown_section(meta: Dict[str, Any]):
    if not meta.get("params", None):
        return ""

    markdown = """<Tabs>
<TabItem value="standard" label="Standard">\n\n"""
    markdown += "| Name | Type | Description | Default | Optional |\n"
    markdown += "| ---- | ---- | ----------- | ------- | -------- |\n"
    standard = ""
    for param in meta["params"]:
        standard += f"| {param['name']} | {param['type']} | {param['doc']} | {param['default']} | {param['optional']} |\n"

    markdown += standard
    markdown += "</TabItem>\n\n"

    for provider, fields in meta["provider_params"].items():
        markdown += f"<TabItem value='{provider}' label='{provider}'>\n\n"
        markdown += "| Name | Type | Description | Default | Optional |\n"
        markdown += "| ---- | ---- | ----------- | ------- | -------- |\n"
        markdown += standard
        for name, field in fields.items():
            markdown += f"| {name} | {field['type']} | {field['doc']} | {field['default']} | {field['optional']} |\n"
        markdown += "</TabItem>\n\n"

    markdown += "</Tabs>\n\n"
    return markdown


def generate_data_model_card_info(meta: Dict[str, Any]) -> Tuple[str, str]:
    description = meta["description"]

    split_description = list(filter(None, description.split(".")))  # type: ignore
    title = split_description[0]
    description = ".".join(split_description[1:]) if len(split_description) > 1 else ""

    return title, description


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


def generate_implementation_details_markdown_section(data_model: str) -> str:
    markdown = "---\n\n## Implementation details\n\n"
    markdown += "### Class names\n\n"
    markdown += "| Model name | Parameters class | Data class |\n"
    markdown += "| ---------- | ---------------- | ---------- |\n"
    markdown += f"| `{data_model}` | `{data_model}QueryParams` | `{data_model}Data` |\n"
    markdown += "\n### Import Statement\n\n"
    markdown += "```python\n"

    file_name = find_data_model_implementation_file(data_model)

    markdown += f"from openbb_core.provider.standard_models.{file_name} import (\n"
    markdown += f"{data_model}Data,\n{data_model}QueryParams,\n"
    markdown += ")\n```"

    return markdown


def generate_platform_markdown() -> None:
    """Generate markdown files for OpenBB Docusaurus website."""
    route_map = PathHandler.build_route_map()
    path_list = sorted(PathHandler.build_path_list(route_map=route_map))

    print("Generating markdown files...")
    kwargs = {"encoding": "utf-8", "newline": "\n"}
    content_path = website_path / "content/platform/reference"
    data_models_path = website_path / "content/platform/data_models"
    reference_cards: Dict[Path, List[Dict[str, str]]] = {}
    data_reference_cards: Dict[Path, List[Dict[str, str]]] = {}

    for file in content_path.glob("*"):
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)
    for file in data_models_path.glob("*"):
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)

    for path in path_list:
        meta_command = get_command_meta(path, route_map)
        if not meta_command:
            continue
        func = PathHandler.get_route(path=path, route_map=route_map).endpoint

        func_name = func.__name__
        if func_name == "index":
            func_name = "index_cmd"

        folder = "/".join(path.strip("/").split("/")[:-1])
        filepath = content_path / folder / f"{func_name}.md"

        markdown = generate_markdown(meta_command=meta_command)

        if data_model := meta_command.get("model", None):
            ## title is the desc here - clean this later
            (
                data_model_card_title,
                data_model_card_description,
            ) = generate_data_model_card_info(meta_command)

            title = re.sub(
                r"([A-Z]{1}[a-z]+)|([A-Z]{3}|[SP500]|[EU])([A-Z]{1}[a-z]+)|([A-Z]{5,})",  # noqa: W605
                lambda m: f"{m.group(1) or m.group(4)} ".title()
                if not any([m.group(2), m.group(3)])
                else f"{m.group(2)} {m.group(3)} ",
                data_model,
            ).strip()

            data_markdown = (
                f"---\ntitle: {title}\n"
                f"description: {data_model_card_title}\n---\n\n"
                "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
                "import Tabs from '@theme/Tabs';\nimport TabItem from '@theme/TabItem';\n\n"
            )

            data_markdown += generate_implementation_details_markdown_section(
                data_model
            )

            data_model_markdown = generate_data_markdown_section(meta_command)
            data_markdown += "\n\n## Parameters\n\n"
            if meta_command["params"]:
                data_markdown += generate_params_markdown_section(meta_command)

            data_markdown += data_model_markdown
            markdown += data_model_markdown

            data_filepath = data_models_path / f"{data_model}.md"

            data_reference_cards.setdefault(data_filepath.parent, []).append(
                dict(
                    title=title,
                    description=data_model_card_title or "",
                    url=data_models_path.relative_to(data_models_path) / data_model,
                )
            )
            data_filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(data_filepath, "w", **kwargs) as f:  # type: ignore
                f.write(data_markdown)

        reference_cards.setdefault(filepath.parent, []).append(
            dict(
                title=func_name,
                description=func.__doc__ or "",
                url="/".join((content_path / folder).relative_to(content_path).parts),
            )
        )

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", **kwargs) as f:  # type: ignore
            f.write(markdown)

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
