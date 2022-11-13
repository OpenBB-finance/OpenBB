import os
from typing import Literal

from docstring_parser import parse

from generate_sdk import get_trailmaps


def get_function_meta(trailmap, trail_type: Literal["model", "view"]):
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
        "function_name": function_name,
        "func_def": func_def,
        "source_code_url": source_code_url,
        "description": doc_parsed.short_description,
        "params": params,
        "returns": returns,
        "examples": examples,
    }


def generate_markdown(meta):
    # head meta https://docusaurus.io/docs/markdown-features/head-metadata
    markdown = f"""---
    title: {meta["name"]}
    description: {meta["description"]}
    ---\n"""
    markdown += f"# {meta['name']}\n\n"
    markdown += f"## {meta['function_name']}\n\n"
    markdown += f"```python\n{meta['func_def']}\n```\n"
    markdown += f"[Source Code]({meta['source_code_url']})\n\n"
    markdown += f"Description: {meta['description']}\n\n"
    markdown += "## Parameters\n\n"
    markdown += "| Name | Type | Description | Default | Optional |\n"
    markdown += "| ---- | ---- | ----------- | ------- | -------- |\n"
    for param in meta["params"]:
        markdown += f"| {param['name']} | {param['type']} | {param['doc']} | {param['default']} | {param['optional']} |\n"
    markdown += "\n"

    markdown += "## Returns\n\n"
    if meta["returns"]:
        markdown += "| Type | Description |\n"
        markdown += "| ---- | ----------- |\n"
        markdown += f"| {meta['returns']['type']} | {meta['returns']['doc']} |\n"
        markdown += "\n"
    else:
        markdown += "None\n\n"

    markdown += "## Examples\n\n"
    for example in meta["examples"]:
        snippet = example["snippet"].replace(">>> ", "")
        markdown += f"{example['description']}\n"
        markdown += f"```python\n{snippet}\n```\n\n"

    return markdown


def main():
    print("Loading trailmaps...")
    trailmaps = get_trailmaps()
    print("Generating markdown files...")
    for trailmap in trailmaps:
        model_meta = get_function_meta(trailmap, "model") if trailmap.model else None
        view_meta = get_function_meta(trailmap, "view") if trailmap.view else None
        if model_meta:
            markdown = generate_markdown(model_meta)
            filepath = (
                "functions/"
                + "/".join(trailmap.location_path)
                + "/"
                + trailmap.class_attr
                + ".md"
            )
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(markdown)
        if view_meta:
            markdown = generate_markdown(view_meta)
            print(trailmap.class_attr)
            filepath = (
                "functions/"
                + "/".join(trailmap.location_path)
                + "/"
                + trailmap.class_attr
                + "_view.md"
            )
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(markdown)
    print("Markdown files generated, check the functions folder")


if __name__ == "__main__":
    main()
