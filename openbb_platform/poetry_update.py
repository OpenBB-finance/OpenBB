import os
import sys
from pathlib import Path
from typing import List, Optional


def update_lock_file(packages: Optional[List[str]] = None) -> None:
    """Updates the poetry lock files in all the packages or in the given packages."""
    for path in Path.cwd().rglob("pyproject.toml"):
        if packages and path.parent.name not in packages:
            print(f"Skipping {path.parent.name}")  # noqa: T201
            continue

        print(f"\nUpdating lock file in {path.parent.name}")  # noqa: T201
        os.chdir(path.parent)
        os.system("poetry lock --no-update")

        # Fix line endings and encoding
        lock_file = path.parent / "poetry.lock"
        lock_file.write_text(
            lock_file.read_text(),
            encoding="utf-8",
            newline="\n",
        )


if __name__ == "__main__":
    args = sys.argv[1:]
    update_lock_file(packages=args if args else None)
