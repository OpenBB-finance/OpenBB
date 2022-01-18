""" Check config_terminal.py """
__docformat__ = "numpy"

import sys
import os
from typing import List

# This is a dictionary of all settings to check in config_terminal.py
settings = {"DEBUG_MODE": "DEBUG_MODE = False"}


def search(lst: List[str], search_item: str):
    """
    Searches a list for an item

    Parameters
    ----------
    lst : List[str]
        The list of strings to search
    search_item : str
        The item to search for in the strings

    Returns
    ----------

    """
    for i, val in enumerate(lst):
        if search_item in val:
            return i, val
    return None


def check_setting(lines: List[str], setting: str, value: str) -> bool:
    """
    Checks the setting, replaces if not compliant

    Parameters
    ----------
    lines : List[str]
        The list of strings to search
    setting : str
        The setting to check
    value : str
        The correct value of the setting

    Returns
    ----------
    correct : bool
        Returns whether the setting was already correct
    """
    debug_line, debug_val = search(lines, setting)

    if debug_val == value:
        return True

    lines[debug_line] = "DEBUG_MODE = False"
    return False


def main():
    base = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base, "gamestonk_terminal", "config_terminal.py")
    with open(path) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    returns = [check_setting(lines, k, v) for k, v in settings.items()]

    if False not in returns:
        sys.exit(0)

    with open(path, "w") as file:
        for element in lines:
            file.write(element + "\n")

    sys.exit(1)


if __name__ == "__main__":
    main()
