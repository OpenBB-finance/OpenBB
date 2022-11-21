import csv
import importlib
import inspect
import os

from types import FunctionType
from typing import Dict, List, Literal, Optional

from docstring_parser import parse

from openbb_terminal.rich_config import console
from openbb_terminal.core.library.trail_map import FORECASTING, MISCELLANEOUS_DIRECTORY

MAP_PATH = MISCELLANEOUS_DIRECTORY / "library" / "trail_map.csv"
MAP_FORECASTING_PATH = MISCELLANEOUS_DIRECTORY / "library" / "trail_map_forecasting.csv"


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


class Trailmap:
    def __init__(self, trailmap: str, model: str, view: Optional[str] = None):
        tmap = trailmap.split(".")
        if len(tmap) == 1:
            tmap = ["", tmap[0]]
        self.class_attr: str = tmap.pop(-1)
        self.category = tmap[0]
        self.location_path = tmap
        self.model = model
        self.view = view if view else None
        self.model_func: Optional[str] = model if model else None
        self.view_func: Optional[str] = view if view else None
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
                self.func_attr[key] = getattr(module, function_name)

                add_juan = 0
                if "__wrapped__" in dir(self.func_attr[key]):
                    self.func_attr[key] = self.func_attr[key].__wrapped__
                    if "__wrapped__" in dir(self.func_attr[key]):
                        self.func_attr[key] = self.func_attr[key].__wrapped__
                    add_juan = 1
                self.lineon[key] = (
                    inspect.getsourcelines(self.func_attr[key])[1] + add_juan
                )

                self.func_def[key] = self.get_definition(key)
                self.long_doc[key] = self.func_attr[key].__doc__
                self.short_doc[key] = clean_attr_desc(self.func_attr[key])
                full_path = (
                    inspect.getfile(self.func_attr[key])
                    .replace("\\", "/")
                    .split("openbb_terminal/")[1]
                )
                self.full_path[key] = f"openbb_terminal/{full_path}"

    def get_definition(self, key: str) -> str:
        """Creates the function definition to be used in SDK docs."""
        funcspec = inspect.getfullargspec(self.func_attr[key])

        definition = ""
        added_comma = False
        for arg in funcspec.args:
            annotation = (
                funcspec.annotations[arg] if arg in funcspec.annotations else "Any"
            )
            if arg in funcspec.annotations:
                annotation = (
                    str(annotation)
                    .replace("<class '", "")
                    .replace("'>", "")
                    .replace("typing.", "")
                    .replace("pandas.core.frame.", "pd.")
                    .replace("pandas.core.series.", "pd.")
                    .replace("openbb_terminal.portfolio.", "")
                )
            definition += f"{arg}: {annotation}, "
            added_comma = True

        if added_comma:
            definition = definition[:-2]

        return_def = (
            funcspec.annotations["return"].__name__
            if "return" in funcspec.annotations
            and hasattr(funcspec.annotations["return"], "__name__")
            and funcspec.annotations["return"] is not None
            else "None"
        )
        definition = f"def {getattr(self, f'{key}_func').split('.')[-1]}({definition }) -> {return_def}"
        return definition


def get_trailmaps() -> List[Trailmap]:
    trailmaps = []
    for tmap_csv in [MAP_PATH, MAP_FORECASTING_PATH]:
        if tmap_csv == MAP_FORECASTING_PATH and not FORECASTING:
            console.print(
                "[bold red]Forecasting is disabled. Forecasting will not be included in the Generation of Docs[/bold red]"
            )
            break
        with open(tmap_csv) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            next(reader)
            for row in reader:
                trailmaps.append(Trailmap(*row))

    return trailmaps


def get_function_meta(trailmap: Trailmap, trail_type: Literal["model", "view"]):
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
        params.append(
            {
                "name": param.arg_name,
                "doc": param.description,
                "type": param.type_name,
                "default": param.default,
                "optional": param.is_optional,
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
        if example.description:
            examples.append(
                {"snippet": example.snippet, "description": example.description}
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


def generate_markdown(meta_model, meta_view):
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
<TabItem value="view" label="View">\n
{generate_markdown_section(meta_view)}\n
</TabItem>
</Tabs>"""
    else:
        markdown += generate_markdown_section(main_model)
    return markdown


def generate_markdown_section(meta):
    # head meta https://docusaurus.io/docs/markdown-features/head-metadata
    # use real description but need to parse it
    markdown = f"## {meta['function_name']}\n\n"
    markdown += f"```python title='{meta['path']}'\n{meta['func_def']}\n```\n"
    markdown += f"[Source Code]({meta['source_code_url']})\n\n"
    markdown += f"Description: {meta['description']}\n\n"

    markdown += "## Parameters\n\n"
    if meta["params"]:
        markdown += "| Name | Type | Description | Default | Optional |\n"
        markdown += "| ---- | ---- | ----------- | ------- | -------- |\n"
        for param in meta["params"]:
            description = param["doc"].replace("\n", "<br/>")
            markdown += f"| {param['name']} | {param['type']} | {description} | {param['default']} | {param['optional']} |\n"  # noqa: E501
        markdown += "\n"
    else:
        markdown += "This function does not take any parameters.\n\n"

    markdown += "## Returns\n\n"
    if meta["returns"]:
        markdown += "| Type | Description |\n"
        markdown += "| ---- | ----------- |\n"
        return_desc = (
            meta["returns"]["doc"].replace("\n", "<br/>")
            if meta["returns"]["doc"]
            else ""
        )
        markdown += f"| {meta['returns']['type']} | {return_desc} |\n\n"
    else:
        markdown += "This function does not return anything\n\n"

    markdown += "## Examples\n\n"
    for example in meta["examples"]:
        markdown += f"{example['description']}\n"

        if isinstance(example["snippet"], str):
            snippet = example["snippet"].replace(">>> ", "")
            markdown += f"```python\n{snippet}\n```\n\n"

    return markdown


def main():
    print("Loading trailmaps...")
    trailmaps = get_trailmaps()
    print("Generating markdown files...")
    for trailmap in trailmaps:
        model_meta = get_function_meta(trailmap, "model") if trailmap.model else None
        view_meta = get_function_meta(trailmap, "view") if trailmap.view else None
        markdown = generate_markdown(model_meta, view_meta)

        if trailmap.class_attr == "index":
            trailmap.class_attr = "index_cmd"

        filepath = (
            "functions/"
            + "/".join(trailmap.location_path)
            + "/"
            + trailmap.class_attr
            + ".md"
        )
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)
    print("Markdown files generated, check the functions folder")


if __name__ == "__main__":
    main()
