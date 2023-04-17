import os
import subprocess
import re
from pathlib import Path

import json

TERMINAL_PATH = Path(__file__).parent.parent.parent.parent / "terminal.py"

OPENBB_DATA_SOURCES_DEFAULT_FILE = (
    Path(__file__).parent.parent.parent
    / "miscellaneous"
    / "sources"
    / "openbb_default.json"
)

GPT_DATA_FOLDER = (
    Path(__file__).parent.parent.parent / "miscellaneous" / "gpt_index" / "data"
)

with open(OPENBB_DATA_SOURCES_DEFAULT_FILE) as file:
    default_sources = json.load(file)


def get_argparse_help_text(command):
    output = ""
    try:
        openbb_terminal_command = f"python {TERMINAL_PATH}"

        full_command = f"{openbb_terminal_command}" + ' "' + command + ' -h"' + "/exit"
        output_text = subprocess.check_output(full_command, shell=True, text=True)

        # Specify the start and end phrases that indicate the argparse help text section
        start_phrase = "usage"
        end_phrase = "to access the related guide."

        start_index = output_text.find(start_phrase)
        end_index = output_text.find(end_phrase) + len(end_phrase)

        if start_index != -1 and end_index != -1:
            output = output_text[start_index:end_index]
            output = output.replace("\n", " ")

            # Remove ANSI escape sequences
            ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
            output = ansi_escape.sub("", output)

    except subprocess.CalledProcessError as e:
        output = e.output
    return output


def generate_command_paths(dictionary, current_path=None):
    if current_path is None:
        current_path = []

    paths = []

    # From the default sources file, generate all possible command paths in the Terminal
    for key, value in (dictionary).items():
        new_path = current_path + [key]

        if isinstance(value, list):
            paths.append(new_path)
        elif isinstance(value, dict):
            paths.extend(generate_command_paths(value, new_path))

    return paths


def filter_by_menu(paths, menu_name="economy"):
    filtered_paths = []
    for path in paths:
        if menu_name in path:
            filtered_paths.append(path)

    filtered_paths_list = []
    for path in filtered_paths:
        filtered_paths_list.append("/".join(path))

    return filtered_paths_list


def main(menus=["etf", "forex"]):
    paths = generate_command_paths(default_sources)

    for menu in menus:
        menu_paths = filter_by_menu(paths, menu)

        data_folder = f"{GPT_DATA_FOLDER}/{menu}"
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        for command in menu_paths:
            file_name = f"{command.split('/')[1]}.txt"
            file_path = os.path.join(data_folder, file_name)
            print(f"Writing help text for '{command}' to {file_path}")

            help_text = get_argparse_help_text(command)

            with open(file_path, "w") as f:
                f.write(help_text)


if __name__ == "__main__":
    main()
