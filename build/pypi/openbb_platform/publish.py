"""Publish the OpenBB Platform to PyPi."""

import argparse
import subprocess
import sys
from pathlib import Path

DIR_PLATFORM = Path(__file__).parent.parent.parent.parent.resolve() / "openbb_platform"
DIR_CORE = ["core"]
DIR_EXTENSIONS = ["extensions", "providers", "obbject_extensions"]

CMD_POETRY = [sys.executable, "-m", "poetry"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Publish OpenBB Platform to PyPi with optional core or extensions flag."
    )
    parser.add_argument(
        "-c", "--core", action="store_true", help="Publish core packages.", dest="core"
    )
    parser.add_argument(
        "-e",
        "--extensions",
        action="store_true",
        help="Publish extension packages.",
        dest="extensions",
    )
    parser.add_argument(
        "-o",
        "--openbb",
        action="store_true",
        help="Publish openbb package.",
        dest="openbb",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the commands without actually publishing.",
        default=False,
        dest="dry_run",
    )
    return parser.parse_args()


def publish(
    dry_run: bool = False,
    core: bool = False,
    extensions: bool = False,
    openbb: bool = False,
):
    """Publish the Platform to PyPi with optional core or extensions."""
    package_directories = []
    if core:
        package_directories.extend(DIR_CORE)
    if extensions:
        package_directories.extend(DIR_EXTENSIONS)

    for _dir in package_directories:
        is_extension = _dir in DIR_EXTENSIONS
        paths = sorted(DIR_PLATFORM.rglob(f"{_dir}/**/pyproject.toml"))
        total = len(paths)
        print(f"\n~~~ {_dir.upper()} ~~~")  # noqa: T201
        for i, path in enumerate(paths):
            print(f"\n🚀 {i+1}/{total} | {path.parent.stem}")  # noqa: T201
            try:
                # Update openbb-core to latest
                if is_extension and "devtools" not in str(path):
                    subprocess.run(
                        CMD_POETRY
                        + ["add", "openbb-core=latest", "--lock"],  # noqa: S603
                        cwd=path.parent,
                        check=True,
                    )
                    print("")
                # Bump toml version
                subprocess.run(
                    CMD_POETRY + ["version", "patch"], cwd=path.parent, check=True
                )  # noqa: S603
                # Publish (if not dry run)
                if not dry_run:
                    subprocess.run(
                        CMD_POETRY + ["build"],  # noqa: S603  # ["publish", "--build"]
                        cwd=path.parent,
                        check=True,  # noqa: S603
                    )
                print("✅ Success\n")
            except Exception as e:
                print(
                    f"\n❌ Failed to publish {path.parent.stem}:\n\n{e}\n"
                )  # noqa: T201

    if openbb:
        subprocess.run(
            CMD_POETRY + ["self", "add", "poetry-plugin-up"],
            check=True,
        )
        subprocess.run(
            CMD_POETRY + ["up", "--latest"],
            cwd=DIR_PLATFORM,
            check=True,
        )
        subprocess.run(
            ["pip", "install", "-U", "--editable", "."],
            cwd=DIR_PLATFORM,
            check=True,
        )
        subprocess.run(
            [sys.executable, "-c", '"import openbb; openbb.build()"'],
            cwd=DIR_PLATFORM,
            check=True,
        )
        subprocess.run(
            [sys.executable, "-c", '"import openbb"'],
            cwd=DIR_PLATFORM,
            check=True,
        )


if __name__ == "__main__":
    msg = """
    You are about to publish a new version of OpenBB Platform to PyPI.
    Please ensure you've read the "PUBLISH.md" file.
    Also, please double check with `poetry config --list` if you're publishing to PyPI or TestPyPI.
    """
    args = parse_args()
    if not args.dry_run:
        msg += "\n\n🛑 You are NOT using the --dry-run flag!"
    res = input(f"{msg}\n\nDo you want to continue? [y/N] ")

    if res.lower() == "y":
        publish(
            dry_run=args.dry_run,
            core=args.core,
            extensions=args.extensions,
            openbb=args.openbb,
        )
