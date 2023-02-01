import json
import os
import re
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

from openbb_terminal.core.config.paths import USER_DATA_DIRECTORY
from openbb_terminal.rich_config import console
from website.controller_doc_classes import (
    ControllerDoc,
    LoadControllersDoc,
    sub_names_full as subnames,
)

website_path = Path(__file__).parent.absolute()
USER_PATH = (f"{USER_DATA_DIRECTORY}", "`USER_DATA_DIRECTORY`")


def existing_markdown_file_examples(
    trailmap: str, cmd_dict: Dict[str, str]
) -> Dict[str, Union[str, List[str]]]:
    """Get existing markdown file examples

    Parameters
    ----------
    trailmap : str
        The trailmap to the function
    cmd_dict : Dict[str, str]
        The dictionary of the command

    Returns
    -------
    Dict[str, Union[str, List[str]]]
        Updated dictionary of the command with examples and images keys
    """
    trail = trailmap.split(".")
    for sub in trail:
        if sub in ["ba", "ta", "qa"]:
            trail.remove(trailmap.split(".")[0])

    examples_path = (
        f"old_content/terminal/{'/'.join(trail)}/{cmd_dict['cmd_name']}/_index.md"
    )
    examples_dict: Dict[str, Union[str, List[str]]] = {}

    if os.path.exists(website_path / examples_path):

        with open(website_path / examples_path, encoding="utf-8") as f:
            content = f.read()

            examples: str = ""
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
def process_cmd_parsers(ctrl: ControllerDoc) -> List[Dict[str, str]]:
    """Process command parsers from ControllerDoc"""

    commands = []
    for cmd, parser in ctrl.cmd_parsers.items():

        actions = []
        for action in parser._actions:  # pylint: disable=protected-access
            if action.dest == "help":
                continue

            if (default := action.default) is not None:

                if isinstance(default, list):
                    default = ", ".join([str(x) for x in default])

                elif isinstance(default, datetime):
                    if "start" in action.dest:
                        default = "datetime.now() - timedelta(days=365)"
                    elif "end" in action.dest or "date" in action.dest:
                        default = "datetime.now()"

            if (choices := action.choices) is not None:

                # We do this so that range(0, N) objects are not converted to a list
                if isinstance(choices, (dict, type({}.keys()), list)):

                    listdict: list = []
                    for choice in choices:
                        # We check for nested dicts
                        if isinstance(choice, (dict, type({}.keys()))):
                            listdict.append([f"{k}" for k in choice])

                    choices = listdict or [f"{x}" for x in choices]
                    choices = ", ".join(choices) if len(choices) > 0 else "None"

                if action.dest == "file":
                    new_desc = "File in `EXPORTS` or `CUSTOM_IMPORTS` directories"

                    if (file_ext := re.compile(r"\.(\w{3,5})").findall(choices)) != []:
                        exts = set(file_ext)
                        ext_examples = "file_name." + ", file_name.".join(exts)
                        new_desc += f" (e.g: `{ext_examples}`)"
                        action.choices = [f"`{ext_examples}`"]

                    choices = new_desc

            if (doc := action.help) is not None:
                # We do this to fix multiline docstrings for the markdown
                doc = " ".join(doc.split()).replace(*USER_PATH)

            actions.append(
                {
                    "opt_name": action.dest if action.dest else "",
                    "doc": doc if doc else "",
                    "default": f"{default}".replace(*USER_PATH),
                    "optional": not action.required,
                    "choices": choices,
                }
            )

        if (desc := parser.description) is not None:
            # We do this to fix multiline docstrings for the markdown
            desc = " ".join(desc.split()).replace(*USER_PATH)

        param = {
            "cmd_name": cmd.replace("call_", ""),
            "actions": actions,
            "usage": " ".join(parser.format_usage().split()).replace("usage: ", ""),
            "description": desc if desc else "",
        }
        commands.append(param)

    return commands


def generate_markdown(
    cmd_meta: Dict[str, str], examples: Dict[str, Union[str, List[str]]]
) -> str:
    """Generate markdown section

    Parameters
    ----------
    cmd_meta : Dict[str, str]
        Command metadata
    examples : Dict[str, Union[str, List[str]]]
        Command examples

    Returns
    -------
    str
        Markdown string
    """
    if not cmd_meta:
        raise ValueError("No command metadata found")

    markdown = f"""---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: {cmd_meta["cmd_name"]}
description: OpenBB Terminal Function
---\n\n"""

    # head meta https://docusaurus.io/docs/markdown-features/head-metadata
    markdown += f"# {cmd_meta['cmd_name']}\n\n{cmd_meta['description']}\n\n"
    markdown += f"### Usage\n\n```python wordwrap\n{cmd_meta['usage']}\n```\n\n"

    markdown += "---\n\n## Parameters\n\n"
    if cmd_meta["actions"]:
        markdown += "| Name | Description | Default | Optional | Choices |\n"
        markdown += "| ---- | ----------- | ------- | -------- | ------- |\n"

        for param in cmd_meta["actions"]:
            if isinstance(param, dict):
                markdown += (
                    f"| {param['opt_name']} | {param['doc']} | {param['default']} "
                    f"| {param['optional']} | {param['choices']} |\n"
                )
    else:
        markdown += "This command has no parameters\n\n"

    if examples.get("example", ""):
        markdown += "\n\n---\n\n## Examples\n\n"
        markdown += f"```python\n{examples['example']}\n```"

    markdown += "\n"

    if isinstance(examples.get("images", None), list):
        for image in examples["images"]:
            markdown += f"{image}\n\n"

    markdown += "---\n"
    return markdown.replace("<", "").replace(">", "")


def add_todict(d: dict, location_path: list, cmd_name: str, full_path: str) -> dict:
    """Adds the trailmap to the dictionary. This function creates the dictionary paths to the function.


    Parameters
    ----------
    d : dict
        The dictionary to add the path to
    location_path : list
        The path to the function
    cmd_name : str
        The name of the function
    full_path : str
        The full path to the function

    Returns
    -------
    dict
        The updated dictionary
    """

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
    wopen_kwargs = {"encoding": "utf-8", "newline": "\n"}

    console.print(
        "[bright_yellow]Generating markdown files... Don't ignore any errors now[/bright_yellow]"
    )
    content_path: Path = website_path / "content/terminal/reference"
    terminal_ref: Dict[str, dict] = {}

    for file in content_path.glob("*"):
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)

    for ctrl_trailmap in ctrls:
        try:
            ctrl = load_ctrls.get_controller_doc(ctrl_trailmap)
            ctrl_cmds = process_cmd_parsers(ctrl)

            for cmd in ctrl_cmds:
                examples = existing_markdown_file_examples(ctrl_trailmap, cmd)
                markdown = generate_markdown(cmd, examples)

                if cmd["cmd_name"] == "index":
                    cmd["cmd_name"] = "index_cmd"

                trail = ctrl_trailmap.split(".")

                terminal_ref = add_todict(terminal_ref, trail, cmd["cmd_name"], trail)
                filepath = content_path / f"{'/'.join(trail)}/{cmd['cmd_name']}.md"

                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, "w", **wopen_kwargs) as f:  # type: ignore
                    f.write(markdown)

        except Exception as e:
            traceback.print_exc()
            console.print(
                f"[red]Failed to generate markdown for {ctrl_trailmap}: {e}[/red]"
            )
            return False

    terminal_ref = {
        k: dict(sorted(v.items(), key=lambda item: item[0]))
        for k, v in sorted(terminal_ref.items(), key=lambda item: item[0])
    }

    # Generate root "_category_.json" file
    with open(content_path / "_category_.json", "w", **wopen_kwargs) as f:  # type: ignore
        f.write(json.dumps({"label": "Terminal Reference", "position": 4}, indent=2))

    # Generate root "index.md" file
    with open(content_path / "index.md", "w", **wopen_kwargs) as f:  # type: ignore
        f.write(
            f"# OpenBB Terminal Features\n\n{generate_index_markdown('', terminal_ref, 2)}"
        )

    def gen_category_json(fname: str, path: Path):
        """Generate category json"""
        fname = subnames[fname.lower()] if fname.lower() in subnames else fname.title()
        with open(path / "_category_.json", "w", **wopen_kwargs) as f:  # type: ignore
            f.write(json.dumps({"label": fname}, indent=2))

    def gen_category_recursive(nested_path: Path):
        """Generate category json recursively"""
        for folder in nested_path.iterdir():
            if folder.is_dir():
                gen_category_json(folder.name, folder)
                gen_category_recursive(folder)  # pylint: disable=cell-var-from-loop

    # Generate modules/sub category json and index files
    gen_category_recursive(content_path)

    console.print(
        "[green]Markdown files generated, check the website/content/terminal/reference/ folder[/green]"
    )

    return True


def generate_index_markdown(markdown: str, d: dict, level: int) -> str:
    """Generate index markdown

    Parameters
    ----------
    markdown : str
        The markdown to add to
    d : dict
        The dictionary to recursively generate markdown from
    level : int
        The level of the markdown header

    Returns
    -------
    str
        Generated index file markdown string
    """
    for key in d:
        if isinstance(d[key], dict):
            markdown += f"\n{'#' * level} {key}\n\n"
            markdown = generate_index_markdown(markdown, d[key], level + 1)
        else:
            markdown += f"- [{key}]({d[key]})\n"
    return markdown


if __name__ == "__main__":
    main()
