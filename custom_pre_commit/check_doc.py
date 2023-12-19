import argparse
import os
import sys
from typing import List, Optional


def clean_input(text: str) -> List[str]:
    text = text.replace(" str ", "")
    text = text.strip()
    text = text.replace("CHOICES_COMMANDS", "")
    text = text.replace("=", "")
    text = text.replace("[", "")
    text = text.replace("]", "")
    text = text.replace("[str]", "")
    text = text.replace("List", "")
    text = text.replace(":", "")
    text = text.replace("str ", "")
    text = text.replace('"', "")
    text = text.replace("'", "")
    text_list = text.split(",")
    return [x.strip() for x in text_list if x]


def main(ignore_files: Optional[str], ignore_commands: Optional[str]):
    """Checks commands in the repository to ensure they are documented

    Parameters
    ----------
    ignore_files : Optional[str]
        Files that should not be checked
    ignore_commands : Optional[str]
        Commands that should not be checked
    """

    ignore_file_list = ignore_files.split(",") if ignore_files else []
    ignore_cmds_list = ignore_commands.split(",") if ignore_commands else []
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gst_path = os.path.join(path, "openbb_terminal/")
    main_yaml_filename = os.path.join(path, "website/data/menu/main.yml")

    files = []
    commands = []
    for r, _, f in os.walk(gst_path):
        for file in f:
            if file.endswith("_controller.py") and file not in ignore_file_list:
                files.append(os.path.join(r, file))

    record = 0
    for item in files:
        with open(item) as controller:
            for line in controller:
                if "CHOICES_COMMANDS" in line or record == 1:
                    commands += clean_input(line)
                    record = 1
                    if "]" in line.replace("str]", ""):
                        record = 0
                        break

    clean_commands = {
        x for x in commands if x and "#" not in x and x not in ignore_cmds_list
    }

    with open(main_yaml_filename) as yaml:
        lines = yaml.read()

    undocumented = [command for command in clean_commands if command not in lines]
    if not undocumented:
        sys.exit(0)
    else:
        print("The following commands do not have documentation:")  # noqa: T201

        undocumented = list(undocumented)
        undocumented.sort()
        for item in undocumented:
            print(item)  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="check_doc",
        description="checks for proper documentation in gst",
    )
    parser.add_argument(
        "--ignore-files",
        dest="files",
        help="The files to not check.",
        type=str,
    )
    parser.add_argument(
        "--ignore-commands",
        dest="commands",
        help="The commands to not check.",
        type=str,
    )

    ns_parser = parser.parse_args()
    main(ns_parser.files, ns_parser.commands)
