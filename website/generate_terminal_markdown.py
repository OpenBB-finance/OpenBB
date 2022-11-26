import json
import os
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from openbb_terminal.rich_config import console
from website.controller_doc_classes import (
    ControllerDoc,
    LoadControllersDoc,
    sub_names_full as subnames,
)

website_path = Path(__file__).parent.absolute()


def existing_markdown_file_examples(
    ctrl: ControllerDoc, cat: Dict[str, str]
) -> Dict[str, Optional[Union[str, List[str]]]]:
    """Get existing markdown file examples"""
    trail = ctrl.trailmap.split(".")
    for sub in trail:
        if sub in ["ba", "ta", "qa"]:
            trail.remove(ctrl.trailmap.split(".")[0])

    examples_path = (
        f"old_content/terminal/{'/'.join(trail)}/{cat['cmd_name']}/_index.md"
    )
    examples_dict: Dict[str, Optional[Union[str, List[str]]]] = {}

    if os.path.exists(website_path / examples_path):

        with open(website_path / examples_path, encoding="utf-8") as f:
            content = f.read()

            examples: Optional[str] = None
            if "Example:" in content:
                example_split = content.split("Example:")[1].split("```")
                if example_split and len(example_split) > 1:
                    examples = f"{example_split[1].strip()}"

            examples_dict["example"] = examples
            images = [
                x for x in content.split("\n") if x.startswith("!") and "TODO" not in x
            ]
            examples_dict["images"] = images

    return examples_dict


# pylint: disable=isinstance-second-argument-not-valid-type
def get_parser(ctrl: ControllerDoc) -> Dict[str, List[Dict[str, str]]]:
    """Get commands and parsers from ControllerDoc"""

    commands = []
    for cmd, parser in ctrl.cmd_parsers.items():

        actions = []
        for action in parser._actions:  # pylint: disable=protected-access
            if action.dest == "help":
                continue

            default = action.default
            if default is not None:
                if isinstance(default, list):
                    default = ", ".join([str(x) for x in default])
                elif isinstance(default, datetime):
                    if "start" in action.dest:
                        default = "datetime.now() - timedelta(days=365)"
                    elif "end" in action.dest or "date" in action.dest:
                        default = "datetime.now()"

            choices = action.choices
            if choices is not None:

                if isinstance(choices, list):
                    listdict = []
                    for choice in choices:
                        if isinstance(choice, (dict, type({}.keys()))):
                            listdict.append([f"{k}" for k in choice])

                    if listdict:
                        choices = listdict
                    else:
                        choices = [f"{x}" for x in choices]
                    choices = ", ".join(choices) if len(choices) > 0 else None

                elif isinstance(choices, (dict, type({}.keys()))):
                    choices = [f"{k}" for k in choices]
                    choices = ", ".join(choices) if len(choices) > 0 else None

            doc = action.help
            if doc is not None:
                # We do this to fix multiline docstrings for the markdown
                doc = " ".join(doc.split())

            actions.append(
                {
                    "opt_name": action.dest if action.dest else "",
                    "doc": doc if doc else "",
                    "default": default,
                    "optional": not action.required,
                    "choices": choices,
                }
            )

        desc = parser.description
        if desc is not None:
            # We do this to fix multiline docstrings for the markdown
            desc = " ".join(desc.split())

        param = {
            "cmd_name": cmd.replace("call_", ""),
            "actions": actions,
            "usage": " ".join(parser.format_usage().split()).replace("usage: ", ""),
            "description": desc if desc else "",
        }
        commands.append(param)

    return {"category_name": ctrl.name, "cmds": commands}


def generate_markdown(cmd_meta: Dict[str, str], examples: Dict[str, str]):
    """Generate markdown string"""
    if not cmd_meta:
        raise ValueError("No command metadata found")

    markdown = f"""---
title: {cmd_meta["cmd_name"]}
description: OpenBB Terminal Function
---\n\n"""

    markdown += generate_markdown_section(cmd_meta, examples)

    return markdown


def generate_markdown_section(meta: Dict[str, str], examples: Dict[str, str]) -> str:
    """Generate markdown section"""

    # head meta https://docusaurus.io/docs/markdown-features/head-metadata
    markdown = f"# {meta['cmd_name']}\n\n{meta['description']}\n\n"
    markdown += f"### Usage\n\n```python\n{meta['usage']}\n```\n\n"

    markdown += "---\n\n## Parameters\n\n"
    if meta["actions"]:
        markdown += "| Name | Description | Default | Optional | Choices |\n"
        markdown += "| ---- | ----------- | ------- | -------- | ------- |\n"

        for param in meta["actions"]:
            if isinstance(param, dict):
                markdown += (
                    f"| {param['opt_name']} | {param['doc']} | {param['default']} "
                    f"| {param['optional']} | {param['choices']} |\n"
                )
    else:
        markdown += "This command has no parameters\n\n"

    if examples.get("example", None):
        markdown += "\n\n---\n\n## Examples\n\n"
        markdown += f"```python\n{examples['example']}\n```"

    markdown += "\n"

    if examples.get("images", []):
        for image in examples["images"]:
            markdown += f"{image}\n\n"

    markdown += "---\n"
    return markdown.replace("<", "").replace(">", "")


def add_todict(d: dict, location_path: list, cmd_name: str, full_path: str) -> dict:
    """Adds the trailmap to the dictionary. This function creates the dictionary paths to the function."""

    if location_path[0] not in d:
        d[location_path[0]] = {}

    if len(location_path) > 1:
        add_todict(d[location_path[0]], location_path[1:], cmd_name, full_path)
    else:
        d[location_path[0]][
            cmd_name
        ] = f"/terminal/reference/{'/'.join(full_path)}/{cmd_name}"

    return d


def main() -> bool:
    """Main function to generate markdown files"""
    console.print(
        "[bright_yellow]Loading Controllers... Please wait and ignore any errors, this is normal.[/bright_yellow]"
    )

    load_ctrls = LoadControllersDoc()
    ctrls = load_ctrls.available_controllers()
    kwargs = {"encoding": "utf-8", "newline": "\n"}

    console.print(
        "[bright_yellow]Generating markdown files... Don't ignore any errors now[/bright_yellow]"
    )
    content_path = website_path / "content/terminal/reference"
    terminal_ref = {}

    for file in content_path.glob("*"):
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)

    for ctrlstr in ctrls:
        try:
            ctrl = load_ctrls.get_controller_doc(ctrlstr)
            cmd_meta = get_parser(ctrl)

            for cat in cmd_meta["cmds"]:
                examples = existing_markdown_file_examples(ctrl, cat)
                markdown = generate_markdown(cat, examples)

                if cat["cmd_name"] == "index":
                    cat["cmd_name"] = "index_cmd"

                trail = ctrl.trailmap.split(".")

                terminal_ref = add_todict(terminal_ref, trail, cat["cmd_name"], trail)
                filepath = f"{str(content_path)}/{'/'.join(trail)}/{cat['cmd_name']}.md"

                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", **kwargs) as f:
                    f.write(markdown)

        except Exception as e:
            traceback.print_exc()
            console.print(f"[red]Failed to generate markdown for {ctrlstr}: {e}[/red]")
            return False

    terminal_ref = {
        k: dict(sorted(v.items(), key=lambda item: item[0]))
        for k, v in sorted(terminal_ref.items(), key=lambda item: item[0])
    }

    with open(content_path / "_category_.json", "w", **kwargs) as f:
        f.write(json.dumps({"label": "Terminal Reference", "position": 4}, indent=2))

    with open(content_path / "index.md", "w", **kwargs) as f:
        f.write(
            f"# OpenBB Terminal Features\n\n{generate_index_markdown('', terminal_ref, 2)}"
        )

    def gen_category_json(fname: str, path: Path):
        """Generate category json"""
        fname = subnames[fname.lower()] if fname.lower() in subnames else fname.title()
        with open(path / "_category_.json", "w", **kwargs) as f:
            f.write(json.dumps({"label": fname}, indent=2))

    def gen_category_recursive(nested_path: Path):
        """Generate category json recursively"""
        for folder in nested_path.iterdir():
            if folder.is_dir():
                gen_category_json(folder.name, folder)
                gen_category_recursive(folder)  # pylint: disable=cell-var-from-loop

    gen_category_recursive(content_path)

    console.print(
        "[green]Markdown files generated, check the website/content/terminal/reference/ folder[/green]"
    )

    return True


def generate_index_markdown(markdown, d, level):
    for key in d:
        if isinstance(d[key], dict):
            markdown += f"\n{'#' * level} {key}\n\n"
            markdown = generate_index_markdown(markdown, d[key], level + 1)
        else:
            markdown += f"- [{key}]({d[key]})\n"
    return markdown


if __name__ == "__main__":
    main()
