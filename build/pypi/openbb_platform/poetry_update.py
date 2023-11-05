import subprocess
import sys
from pathlib import Path
from typing import List, Optional

PLATFORM_PATH = Path(__file__).parent.parent.parent.parent.resolve() / "openbb_platform"

def update_lock_file(packages: Optional[List[str]] = None) -> None:
    """Update the poetry lock files in all the packages or in the given packages."""
    for path in PLATFORM_PATH.rglob("pyproject.toml"):
        if packages and path.parent.name not in packages:
            print(f"Skipping {path.parent.name}")  # noqa: T201
            continue

        print(f"\nUpdating lock file in {path.parent.name}")  # noqa: T201
        CMD = [sys.executable, "-m", "poetry", "lock", "--no-update"]
        subprocess.run(CMD, cwd=path.parent, check=True)  # noqa: S603,PLW1510

        lock_file = path.parent / "poetry.lock"
        lock_text = lock_file.read_text()

        # Fix line endings and encoding
        with open(lock_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(lock_text)


if __name__ == "__main__":
    args = sys.argv[1:]
    update_lock_file(packages=args if args else None)
