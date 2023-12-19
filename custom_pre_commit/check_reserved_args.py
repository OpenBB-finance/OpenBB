"""Check reserved command arguments in Controllers"""
import glob
import os
import re
import sys
from typing import Any, Optional

RESERVED_ARGS = {
    "f": "file",
}


def process_file(file_path: str, exp: str):
    """Lint file

    Checks the file for short reserved arguments that don't match with the reserved
    long arguments

    Parameters
    ----------
    file_path : str
        Full path to the file
    exp : str
        Regular expression to find all reserved args
    """
    errors_found = 0
    with open(file_path, encoding="utf8") as f:
        code = f.read()
    match = re.search(pattern=exp, string=code)
    if match:
        short_arg = match.group()[2]
        long_arg: Optional[Any] = re.search(
            pattern=r"((?<=\--).*?(?=\"))", string=match.group()
        )
        if long_arg is not None:
            long_arg = long_arg.group()
        if long_arg not in ("HistoryManager.hist_file", RESERVED_ARGS[short_arg]):
            print(  # noqa: T201
                f"{file_path}: "
                f"'-{short_arg}' argument expected '{RESERVED_ARGS[short_arg]}'"
                f" but assigned to '{long_arg}'"
            )
            errors_found += 1
    return errors_found


# pylint:disable=anomalous-backslash-in-string
def main():
    expressions = [f'("-{sa}(.|\n)*?\\--.*?\\S*)' for sa in RESERVED_ARGS]
    exp = f"""({"|".join(expressions)})"""

    base = os.path.abspath(os.path.dirname(__file__))
    root = os.path.abspath(os.path.join(base, ".."))

    errors_found = 0
    for file_path in glob.iglob(
        os.path.join(root, "**", "*controller.py"), recursive=True
    ):
        errors_found += process_file(file_path=file_path, exp=exp)

    if errors_found == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
