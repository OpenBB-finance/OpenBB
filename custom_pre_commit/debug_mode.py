""" Check debug mode """
__docformat__ = "numpy"

import os
from typing import List


def search(lst: List[str], search_item: str):
    for _, val in enumerate(lst):
        if search_item in val:
            return val
    return None


def main():
    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "gamestonk_terminal",
        "config_terminal.py",
    )
    with open(path) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    debug_line = search(lines, "DEBUG_MODE")

    if debug_line == "DEBUG_MODE = False":
        return True
    return False


if __name__ == "__main__":
    main()
