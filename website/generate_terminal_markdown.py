import os
import traceback
from typing import Dict, List, Optional, Union

from openbb_terminal.rich_config import console
from website.controller_doc_classes import (
    LoadControllersDoc,
    ControllerDoc,
    sub_names_full,
)


def existing_markdown_file_examples(
    ctrl: ControllerDoc, cat: Dict[str, str]
) -> Dict[str, Optional[Union[str, List[str]]]]:
    """Get existing markdown file examples"""

    examples_path = f"content/terminal/{'/'.join(ctrl.trailmap.split('.'))}/{cat['cmd_name']}/_index.md"
    examples_dict: Dict[str, Optional[Union[str, List[str]]]] = {}

    if os.path.exists(examples_path):

        with open(examples_path, encoding="utf-8") as f:
            content = f.read()

            examples: Optional[str] = None
            if "Example:" in content:
                example_split = content.split("Example:")[1].split("```")
                if example_split and len(example_split) > 1:
                    examples = f"{example_split[1]}"

            examples_dict["example"] = examples
            images = [
                x for x in content.split("\n") if x.startswith("!") and "TODO" not in x
            ]
            examples_dict["images"] = images

    return examples_dict


def get_parser(ctrl: ControllerDoc) -> Dict[str, List[Dict[str, str]]]:
    """Get commands and parsers from ControllerDoc"""

    commands = []
    for cmd, parser in ctrl.cmd_parsers.items():

        actions = []
        for action in parser._actions:  # pylint: disable=protected-access
            if action.dest == "help":
                continue

            if action.default is not None:
                default = action.default
                if isinstance(default, list):
                    default = ", ".join([str(x) for x in default])
            else:
                default = None

            choices = action.choices
            if choices is not None:

                if isinstance(choices, list):
                    listdict = []
                    for choice in choices:
                        if isinstance(choice, dict):
                            listdict.append([f"{k}:  {v}" for k, v in choice.items()])

                    if listdict:
                        choices = listdict

                    choices = (
                        ", ".join([str(choice) for choice in choices])
                        if choices
                        else None
                    )
                elif isinstance(choices, dict):
                    choices = [f"{k}:  {v}" for k, v in choices.items()]
                    choices = ",  ".join(choices)

            doc = action.help
            if doc is not None:
                # We do this to fix multiline docstrings for the markdown
                doc = " ".join(doc.split())

            for attr in [action.dest, action.default, doc]:
                if attr is not None:
                    attr = (
                        str(attr).replace("<", "").replace(">", "").replace("call_", "")
                    )

            actions.append(
                {
                    "opt_name": action.dest if action.dest else "",
                    "doc": doc if doc else "",
                    "default": str(default),
                    "optional": action.required,
                    "choices": choices,
                }
            )

        desc = parser.description
        if desc is not None:
            # We do this to fix multiline docstrings for the markdown
            desc = " ".join(desc.split())
            desc = desc.replace("<", "").replace(">", "")

        param = {
            "cmd_name": cmd.replace("call_", ""),
            "actions": actions,
            "usage": parser.format_usage(),
            "description": desc if desc else "",
        }
        commands.append(param)

    return {
        "category_name": ctrl.name,
        "cmds": commands,
    }


def generate_markdown(cmd_meta: Dict[str, str], examples: Dict[str, str]):
    """Generate markdown string"""
    if not cmd_meta:
        raise ValueError("No command metadata found")

    markdown = f"""---
title: {cmd_meta["cmd_name"]}
description: OpenBB Terminal Function
---\n\n"""

    markdown += f"# {cmd_meta['category_name']}\n\n"
    markdown += generate_markdown_section(cmd_meta, examples)

    return markdown


def generate_markdown_section(meta: Dict[str, str], examples: Dict[str, str]) -> str:
    """Generate markdown section"""

    # head meta https://docusaurus.io/docs/markdown-features/head-metadata
    markdown = f"## {meta['cmd_name']}\n\n"
    markdown += f"### Description: \n\n{meta['description']}\n\n"
    markdown += f"### Usage: \n```python\n{meta['usage']}```\n\n"

    if meta["actions"]:
        markdown += "## Parameters\n\n"
        markdown += "| Name | Description | Default | Optional | Choices |\n"
        markdown += "| ---- | ----------- | ------- | -------- | ------- |\n"

        for param in meta["actions"]:
            if isinstance(param, dict):
                markdown += (
                    f"| {param['opt_name']} | {param['doc']} | {param['default']} "
                    f"| {param['optional']} | {param['choices']} |\n"
                )
    markdown += "\n\n"

    if examples.get("example", None):
        markdown += "## Examples\n\n"
        markdown += f"```python\n{examples['example']}\n```\n\n"
        if examples.get("images", []):
            for image in examples["images"]:
                markdown += f"{image}\n\n"

    return markdown


def main():
    """Main function to generate markdown files"""
    console.print(
        "Loading Controllers... Please wait and ignore any errors, this is normal."
    )

    load_ctrls = LoadControllersDoc()
    ctrls = load_ctrls.available_controllers()

    console.print("Generating markdown files... Don't ignore any errors now")
    for ctrlstr in ctrls:
        try:
            ctrl = load_ctrls.get_controller_doc(ctrlstr)
            cmd_meta = get_parser(ctrl)

            for cat in cmd_meta["cmds"]:
                examples = existing_markdown_file_examples(ctrl, cat)

                cat["category_name"] = (
                    ctrl.name.title()
                    if ctrl.name not in sub_names_full
                    else sub_names_full[ctrl.name]
                )
                markdown = generate_markdown(cat, examples)

                if cat["cmd_name"] == "index":
                    cat["cmd_name"] = "index_cmd"

                filepath = f"terminaltest/{'/'.join(ctrl.trailmap.split('.'))}/{cat['cmd_name']}.md"

                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(markdown)

        except Exception as e:
            traceback.print_exc()
            console.print(f"[red]Failed to generate markdown for {ctrlstr}: {e}[/red]")

    console.print("[green]Markdown files generated, check the functions folder[/green]")


if __name__ == "__main__":
    main()
