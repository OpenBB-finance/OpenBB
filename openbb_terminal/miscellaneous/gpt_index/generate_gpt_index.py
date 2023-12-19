"""To run from root directory:
python openbb_terminal/miscellaneous/gpt_index/generate_gpt_index.py
"""

import random
import re
import shutil
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Union

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY
from openbb_terminal.core.session.current_system import (
    get_current_system,
    set_current_system,
)
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.rich_config import console
from website.controller_doc_classes import (
    ControllerDoc,
    LoadControllersDoc,
)

current_system = get_current_system()
current_system.DOC_MODE = True  # type: ignore
set_current_system(current_system)

GPT_INDEX_DIRECTORY = MISCELLANEOUS_DIRECTORY / "gpt_index/"

USER_PATH = (
    f"{get_current_user().preferences.USER_DATA_DIRECTORY}",
    "`USER_DATA_DIRECTORY`",
)

SYMBOLS = {
    "ticker": [
        "AAPL",
        "MSFT",
        "AMZN",
        "GOOG",
        "META",
        "TSLA",
        "GME",
        "AMC",
        "AFRM",
        "NVDA",
        "CMG",
    ],
    "coin": [
        "BTC",
        "ETH",
        "XRP",
        "DOT",
        "ADA",
        "LTC",
        "LINK",
        "BCH",
        "BNB",
        "XLM",
        "DOGE",
    ],
}

SYMBOLS.update(dict(vs=SYMBOLS["coin"]))


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
                    default = [str(x) for x in default]

                elif isinstance(default, datetime):
                    if "start" in action.dest:
                        random_int = random.randint(1, 365)  # noqa: S311
                        default = (
                            datetime.now() - timedelta(days=random_int)
                        ).strftime("%Y-%m-%d")
                    elif "end" in action.dest or "date" in action.dest:
                        default = datetime.now().strftime("%Y-%m-%d")

            if (choices := action.choices) is not None:
                # We do this so that range(0, N) objects are not converted to a list
                if isinstance(
                    choices, (dict, type({}.keys()), list, type({}.values()))
                ):
                    listdict: list = []
                    for choice in choices:
                        # We check for nested dicts
                        if isinstance(choice, (type({}.keys()), type({}.values()))):
                            listdict.append([f"{k}" for k in choice])  # type: ignore
                        elif isinstance(choice, dict):
                            listdict.append([f"{k}: {v}" for k, v in choice.items()])

                    choices = listdict or [f"{x}" for x in choices]

                if action.dest == "file":
                    new_desc = "File in `EXPORTS` or `CUSTOM_IMPORTS` directories"
                    choices_str = " ".join(choices)

                    if (file_ext := re.compile(r"\.(\w{3,5})").findall(choices_str)) != []:  # type: ignore
                        exts = set(file_ext)
                        ext_examples = "file_name." + ", file_name.".join(exts)
                        new_desc += f" (e.g: `{ext_examples}`)"
                        action.choices = [f"`{ext_examples}`"]

                    choices = new_desc

            if (doc := action.help) is not None:
                # We do this to fix multiline docstrings for the markdown
                doc = " ".join(doc.split()).replace(*USER_PATH)

            key = action.dest.replace("s_", "")
            new_choices = SYMBOLS.get(action.dest.replace("s_", ""), choices)

            if key == "vs" and "currency" in doc:  # type: ignore
                new_choices = choices

            if (flags := action.option_strings) is not None:
                flags = list(flags)

            if default is None and not choices and isinstance(action.type, type):
                if action.type is bool:
                    default = ""
                elif action.type is int:
                    default = random.randint(1, 100)  # noqa: S311
                elif action.type is float:
                    default = random.uniform(1, 100)  # noqa: S311
                else:
                    default = "None"

            actions.append(
                {
                    "opt_name": action.dest if action.dest else "",
                    "flags": flags if flags else "",
                    "doc": doc if doc else "",
                    "default": f"{default}".replace(*USER_PATH),
                    "optional": not action.required,
                    "choices": new_choices,
                }
            )

        if (desc := parser.description) is not None:
            # We do this to fix multiline docstrings for the markdown
            desc = " ".join(desc.split()).replace(*USER_PATH)

        param = {
            "cmd_name": cmd.replace("call_", ""),
            "actions": actions,
            "usage": parser.format_help().replace(*USER_PATH),
            "description": desc if desc else "",
        }
        commands.append(param)

    return commands  # type: ignore


def generate_gpt_txt(cmd_meta: Dict[str, str], trail: str = "") -> str:
    """Generate GPT txt file

    Parameters
    ----------
    cmd_meta : Dict[str, str]
        Command metadata

    Returns
    -------
    str
        GPT txt file
    """
    if not cmd_meta:
        raise ValueError("No command metadata found")

    command_model = f"parent_command:{trail}\n{cmd_meta['usage']}\n\nExample:\n"

    examples = []  # type: ignore

    if cmd_meta["actions"]:
        required_params = [x for x in cmd_meta["actions"] if not x["optional"]]  # type: ignore
        optional_params = [x for x in cmd_meta["actions"] if x["optional"]]  # type: ignore

        def choices_type(choices: Union[dict, list]) -> list:
            """Get choices type"""
            if isinstance(choices, dict):
                return list({f"`{k}: {v}`" for k, v in choices.items()})

            return choices

        def get_examples(
            cmd_meta: Dict[str, str],
            examples_list: list,
            optional: bool,
            retry: int = 5,
        ) -> str:
            """Get examples"""
            example = f"{cmd_meta['cmd_name']}"

            for param in random.sample(required_params, len(required_params)):
                for flag in param["flags"]:  # type: ignore
                    if flag.startswith("-"):  # type: ignore
                        example += f" {flag}"
                        break
                if param["choices"]:  # type: ignore
                    example += f" {random.choice(choices_type(param['choices']))}"  # type: ignore # noqa: S311
                elif param["default"]:  # type: ignore
                    default = param["default"]  # type: ignore
                    if default in ["False", "True"]:
                        default = ""
                    example += f" {param['default']}" if default else ""  # type: ignore

            if optional:
                for param in random.sample(optional_params, len(optional_params) // 4):
                    for flag in param["flags"]:  # type: ignore
                        if flag.startswith("-"):
                            example += f" {flag}"
                            break
                    if param["choices"]:  # type: ignore
                        example += f" {random.choice(choices_type(param['choices']))}"  # type: ignore # noqa: S311
                    elif param["default"]:  # type: ignore
                        default = param["default"]  # type: ignore
                        if default in ["False", "True"]:
                            default = ""
                        example += f" {param['default']}" if default else ""  # type: ignore

            if example not in examples_list or retry == 0:
                return example

            retry -= 1

            return get_examples(cmd_meta, examples_list, optional, retry)

        for n in range(20):
            optional = n > 4
            example = get_examples(cmd_meta, examples, optional)
            if example not in examples:
                examples.append(example)

    else:
        command_model += f"{cmd_meta['cmd_name']}"

    # turn off examples to use ones from gpt_autocreate_examples.py
    # if examples:
    #     command_model += "\n".join(examples)

    return command_model


def main() -> bool:
    """Main function to generate GPT index"""
    console.print(
        "[bright_yellow]Loading Controllers... Please wait and ignore any errors, this is normal.[/bright_yellow]"
    )

    load_ctrls = LoadControllersDoc()
    ctrls = load_ctrls.available_controllers()
    wopen_kwargs = {"encoding": "utf-8", "newline": "\n"}

    console.print(
        "[bright_yellow]Generating markdown files... Don't ignore any errors now[/bright_yellow]"
    )
    content_path: Path = GPT_INDEX_DIRECTORY / "data"

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
                markdown = generate_gpt_txt(cmd, ctrl_trailmap.replace(".", "/"))

                if cmd["cmd_name"] == "index":
                    cmd["cmd_name"] = "index_cmd"

                trail = ctrl_trailmap.split(".")

                filepath = content_path / f"{'_'.join(trail)}_{cmd['cmd_name']}.txt"
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, "w", **wopen_kwargs) as f:  # type: ignore
                    f.write(markdown)

        except Exception as e:
            traceback.print_exc()
            console.print(
                f"[red]Failed to generate markdown for {ctrl_trailmap}: {e}[/red]"
            )
            return False

    console.print(
        "[green]Markdown files generated, check the website/content/terminal/reference/ folder[/green]"
    )

    return True


if __name__ == "__main__":
    main()
