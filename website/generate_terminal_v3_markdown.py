import json
import re
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from textwrap import shorten
from typing import Dict, List, TextIO, Union

from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.core.session.current_user import get_current_user
from website.controller_doc_classes import (
    ControllerDoc,
    LoadControllersDoc,
    console,
    sub_names_full as subnames,
)

set_system_variable("TEST_MODE", True)
set_system_variable("LOG_COLLECT", False)
website_path = Path(__file__).parent.absolute()
CONTENT_PATH: Path = website_path / "content/terminal/reference"
EXAMPLES_META: Dict[str, Dict[str, Union[str, List[str]]]] = json.loads(
    (website_path / "metadata/terminal_v3_examples.json").read_text()
)
SEO_META: Dict[str, Dict[str, Union[str, List[str]]]] = json.loads(
    (website_path / "metadata/terminal_v3_seo_metadata.json").read_text()
)

reference_import = (
    'import ReferenceCard from "@site/src/components/General/NewReferenceCard";\n\n'
)

refrence_ul_element = """<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">"""


USER_PATH = (
    f"{get_current_user().preferences.USER_DATA_DIRECTORY}",
    "`USER_DATA_DIRECTORY`",
)


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

    trail.append(cmd_dict["cmd_name"])

    return EXAMPLES_META.get(".".join(trail), {})


# pylint: disable=isinstance-second-argument-not-valid-type
def process_cmd_parsers(
    ctrl: ControllerDoc, ctrl_trailmap: str
) -> List[Dict[str, str]]:
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

                    if (file_ext := re.compile(r"\.(\w{3,5})").findall(choices)) != []:  # type: ignore
                        exts = set(file_ext)
                        ext_examples = "file_name." + ", file_name.".join(exts)
                        new_desc += f" (e.g: `{ext_examples}`)"
                        action.choices = [f"`{ext_examples}`"]

                    choices = new_desc

            if (doc := action.help) is not None:
                # We do this to fix multiline docstrings for the markdown
                doc = " ".join(doc.split()).replace(*USER_PATH)

            if (flags := action.option_strings) is not None:
                flags = "  ".join(flags)

            actions.append(
                {
                    "opt_name": action.dest if action.dest else "",
                    "flags": flags if flags else "",
                    "doc": doc if doc else "",
                    "default": f"{default}".replace(*USER_PATH),
                    "optional": not action.required,
                    "choices": choices,
                }
            )

        if (desc := parser.description) is not None:
            # We do this to fix multiline docstrings for the markdown
            desc = " ".join(desc.split()).replace(*USER_PATH)

        cmd_name = cmd.replace("call_", "")
        param = {
            "cmd_name": cmd_name,
            "actions": actions,
            "usage": " ".join(parser.format_usage().split()).replace("usage: ", ""),
            "description": desc if desc else "",
        }

        default_desc = (desc or " .").split(".").pop(0).strip().replace(":", "")
        header = f"title: {cmd_name}\ndescription: {default_desc}\nkeywords:\n- {ctrl_trailmap}\n- {cmd_name}"
        key = f"{ctrl_trailmap}.{cmd_name}"

        if cmd_meta := SEO_META.get(key, None):
            keywords = "\n- ".join(cmd_meta["keywords"])
            header = f"title: {cmd_meta['title']}\ndescription: {cmd_meta['description']}\nkeywords:\n- {keywords}"

        title = key.split(".")
        title[0] += " "

        param[
            "header"
        ] = f"""---\n{header}\n---\n
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="{'/'.join(title)} - Reference | OpenBB Terminal Docs" />\n\n"""

        commands.append(param)

    return commands  # type: ignore


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

    # head meta https://docusaurus.io/docs/markdown-features/head-metadata
    markdown = f"{cmd_meta['description']}\n\n"
    markdown += f"### Usage\n\n```python wordwrap\n{cmd_meta['usage']}\n```\n\n"

    markdown += "---\n\n## Parameters\n\n"
    if cmd_meta["actions"]:
        markdown += (
            "| Name | Parameter | Description | Default | Optional | Choices |\n"
            "| ---- | --------- | ----------- | ------- | -------- | ------- |\n"
        )

        for param in cmd_meta["actions"]:
            if isinstance(param, dict):
                markdown += (
                    f"| {param['opt_name']} | {param['flags']} | {param['doc']} "
                    f"| {param['default']} | {param['optional']} | {param['choices']} |\n"
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


def create_nested_menus_card(folder: Path, url: str) -> str:
    sub_categories = [
        sub.stem
        for sub in folder.rglob("**/**/*.md*")
        if sub.is_file() and sub.stem != "index"
    ]
    categories = shorten(", ".join(sub_categories), width=116, placeholder="...")
    url = f"/terminal/reference/{url}/{folder.name}".replace("//", "/")

    index_card = f"""<ReferenceCard
    title="{folder.name.title()}"
    description="{categories}"
    url="{url}"
/>\n"""
    return index_card


def create_cmd_cards(cmd_text: List[Dict[str, str]]) -> str:
    cmd_cards = ""
    for cmd in cmd_text:
        url = f"/terminal/reference/{cmd['url']}/{cmd['title']}".replace("//", "/")
        description = shorten(cmd["description"], width=116, placeholder="...")

        cmd_cards += f"""<ReferenceCard
    title="{cmd["title"].title()}"
    description="{description.replace('"', "'")}"
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
) -> None:
    """Write to the corresponding index.mdx file for a given folder, with the
    appropriate nested menus and command cards.

    Parameters
    ----------
    reference_cards : Dict[Path, List[Dict[str, str]]]
        Dictionary of command cards to be written to the index.md file.
    fname : str
        Name of the index.md file.
    path : Path
        Path to the folder to be written.
    rel_path : Path
        Relative path to the folder to be written.
    f : TextIO
        File to write to.
    """
    f.write(f"# {fname}\n\n{reference_import}")
    sub_folders = [sub for sub in path.glob("*") if sub.is_dir()]
    menus = []

    for folder in sub_folders:
        menus.append(create_nested_menus_card(folder, "/".join(rel_path.parts)))

    if menus:
        f.write(f"### Menus\n{refrence_ul_element}\n{''.join(menus)}</ul>\n")

    folder_cmd_cards: List[Dict[str, str]] = reference_cards.get(path, {})  # type: ignore

    if folder_cmd_cards:
        f.writelines(
            [
                f"\n\n### Commands\n{refrence_ul_element}\n",
                create_cmd_cards(folder_cmd_cards),
                "</ul>\n",
            ]
        )


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
    reference_cards: Dict[Path, List[Dict[str, str]]] = {}
    global_cmds = {"askobb": False, "hold": False, "about": False}

    for file in CONTENT_PATH.glob("*"):
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)

    for ctrl_trailmap in ctrls:
        try:
            ctrl = load_ctrls.get_controller_doc(ctrl_trailmap)
            ctrl_cmds = process_cmd_parsers(ctrl, ctrl_trailmap)

            for cmd in ctrl_cmds:
                trail = ctrl_trailmap.split(".")
                if (created := global_cmds.get(cmd["cmd_name"], None)) is not None:
                    if created:
                        continue
                    global_cmds[cmd["cmd_name"]] = True
                    trail = []

                examples = existing_markdown_file_examples(ctrl_trailmap, cmd)

                markdown = cmd["header"] + generate_markdown(cmd, examples)

                if cmd["cmd_name"] == "index":
                    cmd["cmd_name"] = "index_cmd"

                filepath = CONTENT_PATH / f"{'/'.join(trail + [cmd['cmd_name']])}.md"

                reference_cards.setdefault(filepath.parent, []).append(
                    dict(
                        title=cmd["cmd_name"],
                        description=cmd["description"],
                        url="/".join(trail),
                    )
                )
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, "w", **wopen_kwargs) as f:  # type: ignore
                    f.write(markdown)

        except Exception as e:
            traceback.print_exc()
            console.print(
                f"[red]Failed to generate markdown for {ctrl_trailmap}: {e}[/red]"
            )
            return False

    # Sort reference_cards
    reference_cards = dict(sorted(reference_cards.items(), key=lambda item: item[0]))

    # Generate root "_category_.json" file
    with open(CONTENT_PATH / "_category_.json", "w", **wopen_kwargs) as f:  # type: ignore
        f.write(json.dumps({"label": "Reference", "position": 4}, indent=2))

    # Generate root "index.md" file
    with open(CONTENT_PATH / "index.mdx", "w", **wopen_kwargs) as f:  # type: ignore
        fname = "OpenBB Terminal Features"
        rel_path = CONTENT_PATH.relative_to(CONTENT_PATH)
        write_reference_index(reference_cards, fname, CONTENT_PATH, rel_path, f)

    def gen_category_json(fname: str, path: Path, position: int = 1):
        """Generate category json"""
        fname = subnames[fname.lower()] if fname.lower() in subnames else fname.title()
        with open(path / "_category_.json", "w", **wopen_kwargs) as f:  # type: ignore
            f.write(json.dumps({"label": fname, "position": position}, indent=2))

        with open(path / "index.mdx", "w", **wopen_kwargs) as f:  # type: ignore
            rel_path = path.relative_to(CONTENT_PATH)
            write_reference_index(reference_cards, fname, path, rel_path, f)

    def gen_category_recursive(nested_path: Path):
        """Generate category json recursively"""
        position = 1
        for folder in nested_path.iterdir():
            if folder.is_dir():
                gen_category_json(folder.name, folder, position)
                gen_category_recursive(folder)  # pylint: disable=cell-var-from-loop
                position += 1

    # Generate modules/sub category json and index files
    gen_category_recursive(CONTENT_PATH)

    console.print(
        "[green]Markdown files generated, check the website/content/terminal/reference/ folder[/green]"
    )

    return True


def save_metadata() -> Dict[str, Dict[str, Union[str, List[str]]]]:
    """Save SEO metadata to json file."""

    regex = re.compile(
        r"---\ntitle: (.*)\ndescription: (.*)\nkeywords:(.*)\n---\n\nimport HeadTitle",
        re.MULTILINE | re.DOTALL,
    )

    metadata = {}
    for file in CONTENT_PATH.rglob("*/**/*.md"):
        context = file.read_text(encoding="utf-8")
        match = regex.search(context)
        if match:
            title, description, keywords = match.groups()
            key = file.relative_to(CONTENT_PATH).as_posix().removesuffix(".md")
            metadata[key.replace("/", ".")] = {
                "title": title,
                "description": description,
                "keywords": [
                    keyword.strip() for keyword in keywords.split("\n- ") if keyword
                ],
            }

    filepath = website_path / "metadata/sdk_v3_seo_metadata.json"
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(metadata, f, indent=2)

    return metadata


if __name__ == "__main__":
    main()
