import glob
import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
import yaml

from openbb_terminal.core.config.paths import (
    I18N_DICT_LOCATION,
    MAP_FORECASTING_PATH,
    MAP_OPTIMIZATION_PATH,
    MAP_PATH,
)

trail_maps = [MAP_PATH, MAP_FORECASTING_PATH, MAP_OPTIMIZATION_PATH]

en_file = I18N_DICT_LOCATION / "en.yml"

md_files = ["CONTRIBUTING.md", "README.md", "openbb_terminal/SDK_README.md"]
md_files.extend(glob.glob("website/content/sdk/faqs/*.md", recursive=True))
md_files.extend(glob.glob("website/content/terminal/usage/basics/*.md", recursive=True))
md_files.extend(glob.glob("website/content/terminal/usage/guides/*.md", recursive=True))
md_files.extend(glob.glob("website/content/terminal/usage/intros/*.md", recursive=True))
md_files.extend(glob.glob("website/content/sdk/usage/basics/*.md", recursive=True))
md_files.extend(glob.glob("website/content/sdk/usage/guides/*.md", recursive=True))
md_files.extend(glob.glob("website/content/sdk/usage/intros/*.md", recursive=True))


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


def find_commands_in_files(files: list, commands: list) -> dict:
    found_commands = defaultdict(list)

    for file_path in files:
        with open(file_path) as file:
            file_contents = file.read()

            for command in commands:
                # pattern to match whole words only
                pattern = rf"\b{re.escape(command)}\b"
                matches = re.finditer(pattern, file_contents)

                for _ in matches:
                    found_commands.setdefault(command, [])
                    if file_path not in found_commands[command]:
                        found_commands[command].append(file_path)

    return found_commands


if __name__ == "__main__":
    en_file_as_dict = read_yaml_file(path=en_file)
    cmds = get_command_list(en_dict=en_file_as_dict)
    cmds_sdk = [
        cmd for trail_map in trail_maps for cmd in get_sdk_command_list(trail_map)
    ]

    terminal_commands = find_commands_in_files(files=md_files, commands=cmds)
    sdk_commands = find_commands_in_files(files=md_files, commands=cmds_sdk)

    with open("documentation/documentation_commands.json", "w") as fp:
        json.dump(terminal_commands, fp, indent=4)

    with open("documentation/documentation_commands_sdk.json", "w") as fp:
        json.dump(sdk_commands, fp, indent=4)
