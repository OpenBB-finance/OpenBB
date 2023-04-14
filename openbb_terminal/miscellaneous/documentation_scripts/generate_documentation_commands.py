import argparse
import glob
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Literal

import pandas as pd
import yaml

from openbb_terminal.core.config.paths import (
    I18N_DICT_LOCATION,
    MAP_FORECASTING_PATH,
    MAP_OPTIMIZATION_PATH,
    MAP_PATH,
)

TRAIL_MAPS = [MAP_PATH, MAP_FORECASTING_PATH, MAP_OPTIMIZATION_PATH]

EN_FILE = I18N_DICT_LOCATION / "en.yml"

MD_FILES = ["CONTRIBUTING.md", "README.md", "openbb_terminal/SDK_README.md"]
MD_FILES.extend(glob.glob("website/content/sdk/faqs/*.md", recursive=True))
MD_FILES.extend(glob.glob("website/content/terminal/usage/basics/*.md", recursive=True))
MD_FILES.extend(glob.glob("website/content/terminal/usage/guides/*.md", recursive=True))
MD_FILES.extend(glob.glob("website/content/terminal/usage/intros/*.md", recursive=True))
MD_FILES.extend(glob.glob("website/content/sdk/usage/basics/*.md", recursive=True))
MD_FILES.extend(glob.glob("website/content/sdk/usage/guides/*.md", recursive=True))
MD_FILES.extend(glob.glob("website/content/sdk/usage/intros/*.md", recursive=True))

EXPORT_FILE_PATH = (
    "openbb_terminal/miscellaneous/documentation_scripts/documentation_commands"
)
EXPORT_FILE_PATH_SDK = (
    "openbb_terminal/miscellaneous/documentation_scripts/documentation_commands_sdk"
)


def read_yaml_file(path: Path) -> dict:
    """Read a YAML file and return its contents as a dictionary.

    Parameters
    ----------
    path : Path
        The path to the YAML file.

    Returns
    -------
    dict
        A dictionary containing the contents of the YAML file.

    Raises
    ------
    yaml.YAMLError
        If the YAML file could not be read or parsed, this exception is raised.
    """
    with open(path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc


def get_command_list(en_dict: dict) -> list:
    """
    Extract a list of commands from a dictionary.
    The function looks for keys in the "en" dictionary of `en_dict` that do not start
    with an underscore ("_").
    If a key contains a forward slash ("/"), the part of the key after the last slash
    is considered to be a potential command.
    If this potential command also starts with an underscore, it is ignored.

    Parameters
    ----------
    en_dict : dict
        A dictionary containing commands as keys.
        The values of the dictionary are not used.

    Returns
    -------
    list
        A list of commands extracted from the dictionary.

    Examples
    --------
    ```
    en_dict = {
        "en": {
            "run_command": "Execute a command.",
            "run_command/cmd_option": "Execute a command with an option.",
            "_helper": "A helper command that should be ignored."
        }
    }
    command_list = get_command_list(en_dict)
    # command_list == ["run_command", "cmd_option"]
    ```
    """
    commands = []
    for key in en_dict["en"]:
        if key.startswith("_"):
            continue
        if "/" in key:
            potential_command = key.split("/")[-1]
            if potential_command.startswith("_"):
                continue
            commands.append(potential_command)
        else:
            commands.append(key)
    return commands


def get_sdk_command_list(trail_map: Path) -> list:
    """
    Extract a list of commands from a CSV file.
    The function reads the CSV file at the specified path into a pandas DataFrame and
    extracts the "trail" column as a list of commands.

    Parameters
    ----------
    trail_map : Path
        A path to the CSV file containing the trail map.

    Returns
    -------
    list
        A list of commands extracted from the CSV file.
    """
    df = pd.read_csv(trail_map)
    return df["trail"].tolist()


def get_content_from_md_file(file_path: str, code_blocks_only: bool) -> str:
    """
    Read a Markdown file and return its content, optionally including only code blocks.

    If `code_blocks_only` is True, the function finds all fenced code blocks
    (using regular expression),
    and all backtick code blocks in the Markdown file and concatenates them into a
    single string.
    The backtick code blocks can be either inline or multiline.
    If `code_blocks_only` is False, the function returns the full contents of the
    Markdown file as a string.

    Parameters
    ----------
    file_path : str
        The path to the Markdown file.
    code_blocks_only : bool
        If True, return only the code blocks found in the Markdown file.
        If False, return the full contents of the Markdown file. By default, False.

    Returns
    -------
    str
        The contents of the Markdown file as a string.

    Examples
    --------
    ```
    file_path = "example.md"
    full_content = get_content_from_md_file(file_path, False)
    code_blocks = get_content_from_md_file(file_path, True)
    ```
    """

    def get_code_blocks_from_md_file(file_path: str) -> str:
        code_blocks = ""
        with open(file_path) as f:
            md = f.read()

            # find fenced code blocks using regular expression
            fenced_blocks = re.findall(r"```(?:\w+\n)?([\s\S]*?)```", md)

            # find backtick code blocks using regular expression
            backtick_blocks = re.findall(r"`{3}[\s\S]*?`{3}|`[^`\n]+`", md)

            code_blocks = fenced_blocks + backtick_blocks  # type: ignore
            code_blocks = "".join(code_blocks).replace("\n", "").replace("`", "")
        return code_blocks

    if code_blocks_only:
        return get_code_blocks_from_md_file(file_path)

    with open(file_path) as f:
        return f.read()


def find_commands_in_files(
    files: list, commands: list, code_blocks_only: bool = True
) -> dict:
    """
    Search for specified commands in the content of Markdown files and return a
    dictionary of the files where each command was found.

    The function reads the contents of each Markdown file in `files`, and for each
    `command` in `commands`, searches for occurrences of the command within the file
    contents.
    The search is performed using regular expression to match whole words only.
    If `code_blocks_only` is True, the function searches only within fenced code blocks
    and backtick code blocks in the Markdown files.


    Parameters
    ----------
    files : list
        A list of file paths to the Markdown files to search.
    commands : list
        A list of commands to search for.
    code_blocks_only : bool, optional
        If True, search only within code blocks in the Markdown files.
        If False, search within the full contents of the Markdown files.
        By default, True.

    Returns
    -------
    dict
        A dictionary where each key is a command that was found in one or more files,
        and the value is a list of file paths where the command was found.

    Examples
    --------
    ```
    files = ["file1.md", "file2.md", "file3.md"]
    commands = ["command1", "command2", "command3"]
    results = find_commands_in_files(files, commands)
    ```
    """
    found_commands = defaultdict(list)  # type: ignore

    for file_path in files:
        file_contents = get_content_from_md_file(file_path, code_blocks_only)

        for command in commands:
            # pattern to match whole words only
            pattern = rf"\b{re.escape(command)}\b"
            matches = re.finditer(pattern, file_contents)

            for _ in matches:
                found_commands.setdefault(command, [])
                if file_path not in found_commands[command]:
                    found_commands[command].append(file_path)

    return found_commands


def handle_export(
    extension: Literal["json", "csv"], found_commands: dict, found_commands_sdk: dict
):
    """
    Handle exporting the found commands into a file.

    Parameters
    ----------
    extension : Literal["json", "csv"]
        The extension type of the file to be exported. Can only be "json" or "csv".
    found_commands : dict
        The dictionary containing the commands found in the Markdown files and their
        corresponding file paths.
    found_commands_sdk : dict
        The dictionary containing the SDK commands found in the Markdown files and their
        corresponding file paths.
    """

    def export_to_json(path: Path, commands: dict):
        with open(path, "w") as fp:
            json.dump(commands, fp, indent=4)

    def export_to_csv(path: Path, commands: dict):
        df = pd.DataFrame.from_dict(commands, orient="index").transpose()
        df = pd.melt(df)
        df.rename(columns={"variable": "command", "value": "file"}, inplace=True)
        df = df[["file", "command"]]
        df.sort_values(by=["file"], inplace=True)
        df = df.dropna()
        df.to_csv(path, index=False)

    if extension == "json":
        export_to_json(path=f"{EXPORT_FILE_PATH}.{extension}", commands=found_commands)  # type: ignore
        export_to_json(
            path=f"{EXPORT_FILE_PATH_SDK}.{extension}", commands=found_commands_sdk  # type: ignore
        )

    else:
        export_to_csv(path=f"{EXPORT_FILE_PATH}.{extension}", commands=found_commands)  # type: ignore
        export_to_csv(
            path=f"{EXPORT_FILE_PATH_SDK}.{extension}", commands=found_commands_sdk  # type: ignore
        )


def generate_documentation_commands(
    export_extension: Literal["json", "csv"], code_blocks_only: bool
):
    """
    Generate documentation commands based on commands in Markdown files.

    Parameters
    ----------
    export_extension : Literal["json", "csv"]
        The file extension of the export file. Valid values are "json" and "csv".
    code_blocks_only : bool
        If True, only code blocks from the Markdown files will be searched for
        documentation commands.
        If False, the entire contents of the Markdown files will be searched.
    """
    en_file_as_dict = read_yaml_file(path=EN_FILE)
    cmds = get_command_list(en_dict=en_file_as_dict)
    cmds_sdk = [
        cmd for trail_map in TRAIL_MAPS for cmd in get_sdk_command_list(trail_map)
    ]

    terminal_commands = find_commands_in_files(
        files=MD_FILES, commands=cmds, code_blocks_only=code_blocks_only
    )
    sdk_commands = find_commands_in_files(
        files=MD_FILES, commands=cmds_sdk, code_blocks_only=code_blocks_only
    )

    handle_export(
        extension=export_extension,
        found_commands=terminal_commands,
        found_commands_sdk=sdk_commands,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="generate_documentation_commands",
        description="Generate documentation commands based on commands in Markdown files.",
    )
    parser.add_argument(
        "-e",
        "--export",
        dest="export_extension",
        default="csv",
        choices=["json", "csv"],
        help="Export the list of commands to a json or csv file",
    )
    parser.add_argument(
        "-c",
        "--code-blocks-only",
        dest="code_blocks_only",
        default=True,
        action="store_true",
        help="Search only within code blocks in the Markdown files",
    )
    args = parser.parse_args()

    generate_documentation_commands(
        export_extension=args.export_extension, code_blocks_only=args.code_blocks_only
    )
