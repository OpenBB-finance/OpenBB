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

EXPORT_FILE_PATH = "documentation/documentation_commands"
EXPORT_FILE_PATH_SDK = "documentation/documentation_commands_sdk"


def read_yaml_file(path: Path) -> dict:
    with open(path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc


def get_command_list(en_dict: dict) -> list:
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
    df = pd.read_csv(trail_map)
    return df["trail"].tolist()


def get_content_from_md_file(file_path: str, code_blocks_only: bool) -> str:
    def get_code_blocks_from_md_file(file_path: str) -> str:
        code_blocks = ""
        with open(file_path) as f:
            md = f.read()

            # find fenced code blocks using regular expression
            fenced_blocks = re.findall(r"```(?:\w+\n)?([\s\S]*?)```", md)

            # find backtick code blocks using regular expression
            backtick_blocks = re.findall(r"`{3}[\s\S]*?`{3}|`[^`\n]+`", md)

            code_blocks = fenced_blocks + backtick_blocks
            code_blocks = "".join(code_blocks).replace("\n", "").replace("`", "")
        return code_blocks

    if code_blocks_only:
        return get_code_blocks_from_md_file(file_path)

    with open(file_path) as f:
        return f.read()


def find_commands_in_files(
    files: list, commands: list, code_blocks_only: bool = True
) -> dict:
    found_commands = defaultdict(list)

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
        export_to_json(path=f"{EXPORT_FILE_PATH}.{extension}", commands=found_commands)
        export_to_json(
            path=f"{EXPORT_FILE_PATH_SDK}.{extension}", commands=found_commands_sdk
        )

    else:
        export_to_csv(path=f"{EXPORT_FILE_PATH}.{extension}", commands=found_commands)
        export_to_csv(
            path=f"{EXPORT_FILE_PATH_SDK}.{extension}", commands=found_commands_sdk
        )


if __name__ == "__main__":
    en_file_as_dict = read_yaml_file(path=EN_FILE)
    cmds = get_command_list(en_dict=en_file_as_dict)
    cmds_sdk = [
        cmd for trail_map in TRAIL_MAPS for cmd in get_sdk_command_list(trail_map)
    ]

    terminal_commands = find_commands_in_files(
        files=MD_FILES, commands=cmds, code_blocks_only=True
    )
    sdk_commands = find_commands_in_files(
        files=MD_FILES, commands=cmds_sdk, code_blocks_only=True
    )

    handle_export(
        extension="csv",
        found_commands=terminal_commands,
        found_commands_sdk=sdk_commands,
    )
