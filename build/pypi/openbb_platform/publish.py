"""Publish the OpenBB Platform to PyPi."""
import argparse
import subprocess
import sys
from pathlib import Path

PLATFORM_PATH = Path(__file__).parent.parent.parent.parent.resolve() / "openbb_platform"

CORE_PACKAGES = ["platform/provider", "platform/core"]
EXTENSION_PACKAGES = ["extensions", "providers"]

CMD = [sys.executable, "-m", "poetry"]
CORE_BUMP_CMD = ["add", "openbb-core=latest"]
VERSION_BUMP_CMD = ["version", "prerelease", "--next-phase"]
PUBLISH_CMD = ["publish", "--build"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Publish OpenBB Platform to PyPi with optional core or extensions flag."
    )
    parser.add_argument(
        "-c", "--core", action="store_true", help="Publish core packages only."
    )
    parser.add_argument(
        "-e",
        "--extensions",
        action="store_true",
        help="Publish extension packages only.",
    )
    return parser.parse_args()


def run_cmds(directory: Path):
    """Run the commands for publishing"""
    print(f"Publishing: {directory.name}")  # noqa: T201

    # TODO: Uncomment the following lines depending on your needs
    # subprocess.run(CMD + CORE_BUMP_CMD, cwd=directory, check=True)  # noqa: S603
    subprocess.run(CMD + VERSION_BUMP_CMD, cwd=directory, check=True)  # noqa: S603
    # subprocess.run(CMD + PUBLISH_CMD, cwd=directory, check=True)  # noqa: S603


def publish(core=False, extensions=False):
    """Publish the Platform to PyPi with optional core or extensions."""
    if core:
        package_paths = CORE_PACKAGES
        print("Working with core packages...")  # noqa: T201
    if extensions:
        package_paths = (
            package_paths.extend(EXTENSION_PACKAGES) if core else EXTENSION_PACKAGES
        )
        print("Working with extensions...")  # noqa: T201
    for sub_path in package_paths:
        for path in PLATFORM_PATH.rglob(f"{sub_path}/**/pyproject.toml"):
            run_cmds(path.parent)
    # TODO: Uncomment the following lines depending on your needs
    # # openbb
    # run_cmds(PLATFORM_PATH)


if __name__ == "__main__":
    msg = """
    You are about to publish a new version of OpenBB Platform to PyPI.
    Please ensure you've read the "PUBLISH.md" file.
    Also, please double check with `poetry config --list` if you're publishing to PyPI or TestPyPI.
    """
    args = parse_args()

    res = input(f"{msg}\n\nDo you want to continue? [y/N] ")

    if res.lower() == "y":
        publish(core=args.core, extensions=args.extensions)
