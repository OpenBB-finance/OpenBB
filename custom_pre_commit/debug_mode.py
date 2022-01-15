""" Check debug mode """
__docformat__ = "numpy"

import sys
import os
from typing import List


def search(lst: List[str], search_item: str):
    for i, val in enumerate(lst):
        if search_item in val:
            return i, val
    return None


def main():
    base = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base, "gamestonk_terminal", "config_terminal.py")
    with open(path) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    debug_line, debug_val = search(lines, "DEBUG_MODE")

    if debug_val == "DEBUG_MODE = False":
        sys.exit(0)

    lines[debug_line] = "DEBUG_MODE = False"
    with open(path, "w") as file:
        for element in lines:
            file.write(element + "\n")

    sys.exit(1)


if __name__ == "__main__":
    main()
