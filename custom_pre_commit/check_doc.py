import os
import sys
from typing import List


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


def main():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gst_path = os.path.join(path, "gamestonk_terminal/")
    main_yaml_filename = os.path.join(path, "website/data/menu/main.yml")

    files = {}
    commands = []
    for r, _, f in os.walk(gst_path):
        for file in f:
            if file.endswith("_controller.py"):
                files[file] = os.path.join(r, file)

    record = 0
    for item in files.values():
        with open(item) as file:
            for line in file:
                if "CHOICES_COMMANDS" in line or record == 1:
                    commands += clean_input(line)
                    record = 1
                    if "]" in line.replace("str]", ""):
                        record = 0
                        break

    commands = {x for x in commands if x and "#" not in x}

    with open(main_yaml_filename) as file:
        lines = file.read()

    undocumented = []
    for command in commands:
        if command not in lines:
            undocumented.append(command)

    if not undocumented:
        sys.exit(0)
    else:
        print("The following commands do not have documentation:")

        undocumented = list(undocumented)
        undocumented.sort()
        for item in undocumented:
            print(item)
        print(undocumented)
        sys.exit(1)


if __name__ == "__main__":
    main()
