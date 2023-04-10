import glob
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

from openbb_terminal.core.config.paths import I18N_DICT_LOCATION

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


if __name__ == "__main__":
    en_file_as_dict = read_yaml_file(path=en_file)
    cmds = get_command_list(en_dict=en_file_as_dict)

    found_commands = defaultdict(list)

    # Find commands in markdown files
    for file_path in md_files:
        with open(file_path) as file:
            file_contents = file.read()

            for command in cmds:
                pattern = rf"\b{re.escape(command)}\b"  # create regex pattern for whole word match
                matches = re.finditer(pattern, file_contents)

                for match in matches:
                    found_commands.setdefault(command, [])
                    if file_path not in found_commands[command]:
                        found_commands[command].append(file_path)

    with open("documentation/documentation_commands.json", "w") as fp:
        json.dump(found_commands, fp, indent=4)
