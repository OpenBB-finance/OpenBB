import csv
import importlib
import inspect
import json
import os
import shutil
from pathlib import Path
from types import FunctionType
from typing import Any, Callable, Dict, ForwardRef, List, Literal, Optional, Union

import pandas as pd
from docstring_parser import parse

from openbb_terminal.core.library.trail_map import (
    FORECASTING_TOOLKIT_ENABLED as FORECASTING,
    MISCELLANEOUS_DIRECTORY,
    OPTIMIZATION_TOOLKIT_ENABLED as OPTIMIZATION,
)
from openbb_terminal.rich_config import console
from website.controller_doc_classes import sub_names_full as subnames

MAP_PATH = MISCELLANEOUS_DIRECTORY / "library" / "trail_map.csv"
MAP_FORECASTING_PATH = MISCELLANEOUS_DIRECTORY / "library" / "trail_map_forecasting.csv"
MAP_OPTIMIZATION_PATH = (
    MISCELLANEOUS_DIRECTORY / "library" / "trail_map_optimization.csv"
)
website_path = Path(__file__).parent.absolute()


def clean_attr_desc(attr: Optional[FunctionType] = None) -> Optional[str]:
    """Clean the attribute description."""
    if attr.__doc__ is None:
        return None
    return (
        attr.__doc__.splitlines()[1].lstrip()
        if not attr.__doc__.splitlines()[0]
        else attr.__doc__.splitlines()[0].lstrip()
        if attr.__doc__
        else ""
    )


def get_signature_parameters(
    function: Callable[..., Any], globalns: Dict[str, Any]
) -> Dict[str, inspect.Parameter]:
    signature = inspect.signature(function)
    params = {}
    cache: dict[str, Any] = {}
    for name, parameter in signature.parameters.items():
        annotation = parameter.annotation
        if annotation is parameter.empty:
            params[name] = parameter
            continue
        if annotation is None:
            params[name] = parameter.replace(annotation=type(None))
            continue

        if isinstance(annotation, ForwardRef):
            annotation = annotation.__forward_arg__

        if isinstance(annotation, str):
            annotation = eval(annotation, globalns, cache)  # pylint: disable=W0123

        params[name] = parameter.replace(annotation=annotation)

    return params


class Trailmap:
    def __init__(self, trailmap: str, model: str, view: Optional[str] = None):
        tmap = trailmap.split(".")
        if len(tmap) == 1:
            tmap = ["", tmap[0]]
        self.class_attr: str = tmap.pop(-1)
        self.location_path = tmap
        self.model = model
        self.view = view if view else None
        self.short_doc: Dict[str, Optional[str]] = {}
        self.long_doc: Dict[str, str] = {}
        self.lineon: Dict[str, int] = {}
        self.full_path: Dict[str, str] = {}
        self.func_def: Dict[str, str] = {}
        self.func_attr: Dict[str, FunctionType] = {}
        self.params: Dict[str, Dict[str, inspect.Parameter]] = {}
        self.get_docstrings()

    def get_docstrings(self) -> None:
        """Gets the function docstrings. We get the short and long docstrings."""

        for key, func in zip(["model", "view"], [self.model, self.view]):
            if func:
                module_path, function_name = func.rsplit(".", 1)
                module = importlib.import_module(module_path)

                func_attr = getattr(module, function_name)
                add_juan = 0
                if hasattr(func_attr, "__wrapped__"):
                    func_attr = func_attr.__wrapped__
                    if hasattr(func_attr, "__wrapped__"):
                        func_attr = func_attr.__wrapped__
                    add_juan = 1

                self.func_attr[key] = func_attr
                self.lineon[key] = inspect.getsourcelines(func_attr)[1] + add_juan

                self.long_doc[key] = func_attr.__doc__
                self.short_doc[key] = clean_attr_desc(func_attr)

                self.params[key] = {}
                for k, p in get_signature_parameters(
                    func_attr, func_attr.__globals__
                ).items():
                    self.params[key][k] = p

                self.func_def[key] = self.get_definition(key)
                full_path = (
                    inspect.getfile(self.func_attr[key])
                    .replace("\\", "/")
                    .split("openbb_terminal/")[1]
                )
                self.full_path[key] = f"openbb_terminal/{full_path}"

    def get_definition(self, key: str) -> str:
        """Creates the function definition to be used in SDK docs."""
        funcspec = self.params[key]
        definition = ""
        added_comma = False
        for arg in funcspec:

            annotation = (
                (
                    str(funcspec[arg].annotation)
                    .replace("<class '", "")
                    .replace("'>", "")
                    .replace("typing.", "")
                    .replace("pandas.core.frame.", "pd.")
                    .replace("pandas.core.series.", "pd.")
                    .replace("openbb_terminal.portfolio.", "")
                )
                if funcspec[arg].annotation != inspect.Parameter.empty
                else "Any"
            )

            default = ""
            if funcspec[arg].default is not funcspec[arg].empty:
                arg_default = (
                    funcspec[arg].default
                    if funcspec[arg].default is not inspect.Parameter.empty
                    else "None"
                )
                default = (
                    f" = {arg_default}"
                    if not isinstance(arg_default, str)
                    else f' = "{arg_default}"'
                )
            definition += f"{arg}: {annotation}{default}, "
            added_comma = True

        if added_comma:
            definition = definition[:-2]

        trail = ".".join([t for t in self.location_path if t != ""])
        sdk_name = self.class_attr if key != "view" else f"{self.class_attr}_chart"
        sdk_path = f"{f'openbb.{trail}' if trail else 'openbb'}.{sdk_name}"

        definition = f"{sdk_path}({definition })"
        return definition


def get_trailmaps() -> List[Trailmap]:
    trailmaps = []

    def sort_csv(path: Path) -> None:
        columns = ["trail", "model", "view"]
        df = pd.read_csv(path, usecols=columns, keep_default_na=False)
        df.set_index("trail", inplace=True)
        df.sort_index(inplace=True)
        df.to_csv(path, index=True)

    for tmap_csv in [MAP_PATH, MAP_FORECASTING_PATH, MAP_OPTIMIZATION_PATH]:
        sort_csv(tmap_csv)
        if tmap_csv == MAP_FORECASTING_PATH and not FORECASTING:
            console.print(
                "[bold red]Forecasting is disabled. Forecasting will not be included in the Generation of Docs[/bold red]"
            )
            break
        if tmap_csv == MAP_OPTIMIZATION_PATH and not OPTIMIZATION:
            console.print(
                "[bold red]Optimization is disabled. Optimization will not be included in the Generation of Docs[/bold red]"  # noqa: E501
            )
            break
        with open(tmap_csv) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            next(reader)
            for row in reader:
                trailmaps.append(Trailmap(*row))

    return trailmaps


def get_function_meta(trailmap: Trailmap, trail_type: Literal["model", "view"]):
    """Gets the function meta data."""
    if trailmap.func_attr[trail_type] is None:
        return None
    doc_parsed = parse(trailmap.long_doc[trail_type])
    line = trailmap.lineon[trail_type]
    path = trailmap.full_path[trail_type]
    func_def = trailmap.func_def[trail_type]
    source_code_url = (
        "https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/"
        + path
        + "#L"
        + str(line)
    )
    function_name = trailmap.view if trail_type == "view" else trailmap.model
    params = []
    for param in doc_parsed.params:
        arg_default = (
            trailmap.params[trail_type][param.arg_name].default
            if param.arg_name in trailmap.params[trail_type]
            else None
        )
        params.append(
            {
                "name": param.arg_name,
                "doc": param.description,
                "type": param.type_name,
                "default": arg_default
                if arg_default is not inspect.Parameter.empty
                else None,
                "optional": bool(arg_default is not inspect.Parameter.empty)
                or param.is_optional,
            }
        )
    if doc_parsed.returns:
        returns = {
            "doc": doc_parsed.returns.description,
            "type": doc_parsed.returns.type_name,
        }
    else:
        returns = None

    examples = []

    for example in doc_parsed.examples:
        examples.append(
            {"snippet": example.snippet, "description": example.description.strip()}
        )

    return {
        "name": trailmap.class_attr,
        "path": path,
        "function_name": function_name,
        "func_def": func_def,
        "source_code_url": source_code_url,
        "description": doc_parsed.short_description,
        "params": params,
        "returns": returns,
        "examples": examples,
    }


def generate_markdown(meta_model: dict, meta_view: dict):
    main_model = meta_model
    if not meta_model:
        if not meta_view:
            raise ValueError("No model or view")
        main_model = meta_view
    markdown = f"""---
title: {main_model["name"]}
description: OpenBB SDK Function
---\n\n"""
    if meta_view and meta_model:
        markdown += """import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';\n\n"""

    markdown += f"# {main_model['name']}\n\n"

    if meta_view and meta_model:
        markdown += f"""<Tabs>
<TabItem value="model" label="Model" default>\n
{generate_markdown_section(meta_model)}\n
</TabItem>
<TabItem value="view" label="Chart">\n
{generate_markdown_section(meta_view)}\n
</TabItem>
</Tabs>"""
    else:
        markdown += generate_markdown_section(main_model)
    return markdown


def generate_markdown_section(meta: Dict[str, Any]):
    # head meta https://docusaurus.io/docs/markdown-features/head-metadata
    # use real description but need to parse it
    markdown = (
        f"{meta['description']}\n\nSource Code: [[link]({meta['source_code_url']})]\n\n"
    )
    markdown += f"```python wordwrap\n{meta['func_def']}\n```\n\n"

    markdown += "---\n\n## Parameters\n\n"
    if meta["params"]:
        markdown += "| Name | Type | Description | Default | Optional |\n"
        markdown += "| ---- | ---- | ----------- | ------- | -------- |\n"
        for param in meta["params"]:
            description = param["doc"].replace("\n", "<br/>") if param["doc"] else ""
            markdown += f"| {param['name']} | {param['type']} | {description} | {param['default']} | {param['optional']} |\n"  # noqa: E501
        markdown += "\n\n"
    else:
        markdown += "This function does not take any parameters.\n\n"

    markdown += "---\n\n## Returns\n\n"
    if meta["returns"]:
        markdown += "| Type | Description |\n"
        markdown += "| ---- | ----------- |\n"
        return_desc = (
            meta["returns"]["doc"].replace("\n", "<br/>")
            if meta["returns"]["doc"]
            else ""
        )
        markdown += f"| {meta['returns']['type']} | {return_desc} |\n"
    else:
        markdown += "This function does not return anything\n\n"

    markdown += "---\n\n## Examples\n\n" if meta["examples"] else ""
    prev_snippet = "  "
    for example in meta["examples"]:

        if isinstance(example["snippet"], str) and ">>>" in example["snippet"]:
            snippet = example["snippet"].replace(">>> ", "")
            markdown += f"```python\n{snippet}\n```\n\n"
            if example["description"] and prev_snippet != "":
                markdown += f"```\n{example['description']}\n```\n"
                prev_snippet = snippet.strip()
            else:
                if example["description"]:
                    markdown += f"\n{example['description']}\n\n"
        else:
            if example["description"]:
                markdown += f"\n{example['description']}\n\n"
            prev_snippet = ""

    markdown += "---\n\n"

    return markdown


def add_todict(d: dict, location_path: list, tmap: Trailmap) -> dict:
    """Adds the trailmap to the dictionary. A trailmap is a path to a function
    in the sdk. This function creates the dictionary paths to the function."""

    if location_path[0] not in d:
        d[location_path[0]] = {}

    if len(location_path) > 1:
        add_todict(d[location_path[0]], location_path[1:], tmap)
    else:
        d[location_path[0]][tmap.class_attr] = (
            f"/sdk/reference/{'/'.join(tmap.location_path)}/{tmap.class_attr}"
        ).replace("//", "/")

    return d


def get_nested_dict(d: dict, path: Path) -> Union[dict, None]:
    """Returns the nested dictionary for the given key."""
    root, sub = path.parent.name, path.name

    if sub in d:
        return d[sub]
    if root in d and sub in d[root]:
        return d[root][sub]
    for v in d.values():
        if isinstance(v, dict):
            item = get_nested_dict(v, path)
            if item is not None:
                return item

    return None


def get_subname(name: str) -> str:
    """Returns the subname of the given name."""
    if name != "reference":
        subname = (
            name.title() if name.lower() not in subnames else subnames[name.lower()]
        )
        return subname
    return ""


def main() -> bool:
    print("Loading trailmaps...")
    trailmaps = get_trailmaps()
    kwargs = {"encoding": "utf-8", "newline": "\n"}

    print("Generating markdown files...")
    content_path = website_path / "content/sdk/reference"
    functions_dict: dict = {}

    for file in content_path.glob("*"):
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)
    for trailmap in trailmaps:
        try:
            functions_dict = add_todict(
                functions_dict, trailmap.location_path, trailmap
            )
            model_meta = (
                get_function_meta(trailmap, "model") if trailmap.model else None
            )
            view_meta = get_function_meta(trailmap, "view") if trailmap.view else None
            markdown = generate_markdown(model_meta, view_meta)

            if trailmap.class_attr == "index":
                trailmap.class_attr = "index_cmd"

            filepath = f"{str(content_path)}/{'/'.join(trailmap.location_path)}/{trailmap.class_attr}.md"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", **kwargs) as f:  # type: ignore
                f.write(markdown)
        except Exception as e:
            print(f"Error generating {trailmap.class_attr} - {e}")
            return False

    functions_dict = {
        k: dict(sorted(v.items(), key=lambda item: item[0]))
        for k, v in sorted(functions_dict.items(), key=lambda item: item[0])
    }
    index_markdown = (
        f"# OpenBB SDK Reference\n\n{generate_index_markdown('', functions_dict, 2)}"
    )
    with open(content_path / "index.md", "w", **kwargs) as f:  # type: ignore
        f.write(index_markdown)

    with open(content_path / "_category_.json", "w", **kwargs) as f:  # type: ignore
        f.write(json.dumps({"label": "SDK Reference", "position": 4}, indent=2))

    def gen_category_json(fname: str, path: Path):
        """Generate category json"""
        fdict = {fname: get_nested_dict(functions_dict, path)}

        with open(path / "index.md", "w", **kwargs) as f:  # type: ignore
            f.write(f"# {fname}\n\n{generate_index_markdown('', fdict, 2, path)}")

    def gen_category_recursive(nested_path: Path):
        """Generate category json recursively"""
        for folder in nested_path.iterdir():
            if folder.is_dir():
                gen_category_json(folder.name, folder)
                gen_category_recursive(folder)  # pylint: disable=cell-var-from-loop

    gen_category_recursive(content_path)
    print("Markdown files generated, check the functions folder")

    return True


def generate_index_markdown(
    markdown: str, d: dict, level: int, path: Path = None
) -> str:
    """Generates the index markdown for the given dictionary."""
    if path is None:
        path = Path()
    for key in d:
        if isinstance(d[key], dict):
            if path and path.name != key:
                if key != "":
                    markdown += f"\n{'#' * level} {key}\n"
            markdown = generate_index_markdown(markdown, d[key], level + 1, path)
        else:
            markdown += f"- [{key}]({d[key]})\n"
    return markdown


if __name__ == "__main__":
    main()
