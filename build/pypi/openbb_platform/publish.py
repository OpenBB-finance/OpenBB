"""Publish the OpenBB Platform to PyPi."""
import argparse
import subprocess
import sys
from pathlib import Path

PLATFORM_PATH = Path(__file__).parent.parent.parent.parent.resolve() / "openbb_platform"

CORE_PACKAGES = ["core"]
EXTENSION_PACKAGES = ["extensions", "providers"]

CMD = [sys.executable, "-m", "poetry"]
EXTENSION_DEPENDENCIES_UPDATE_CMD = ["add", "openbb-core=latest"]
VERSION_BUMP_CMD = ["version", "prerelease"]
PUBLISH_CMD = ["publish", "--build"]


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
        "--dry-run",
        action="store_true",
        help="Run the commands without actually publishing.",
        default=False,
        dest="dry_run",
    )
    return parser.parse_args()


def update_extension_dependencies(path: Path):
    """Update the extension dependencies"""
    subprocess.run(
        CMD + EXTENSION_DEPENDENCIES_UPDATE_CMD,  # noqa: S603
        cwd=path.parent,
        check=True,
    )


def bump_version(path: Path):
    """Bump the version of the package"""
    subprocess.run(CMD + VERSION_BUMP_CMD, cwd=path.parent, check=True)  # noqa: S603


def publish(dry_run: bool = False, core: bool = False, extensions: bool = False):
    """Publish the Platform to PyPi with optional core or extensions."""
    package_paths = []
    if core:
        print("Working with core packages...")  # noqa: T201
        package_paths.extend(CORE_PACKAGES)
    if extensions:
        print("Working with extensions...")  # noqa: T201
        package_paths.extend(EXTENSION_PACKAGES)

    for sub_path in package_paths:
        is_extension = sub_path in EXTENSION_PACKAGES

        for path in PLATFORM_PATH.rglob(f"{sub_path}/**/pyproject.toml"):
            try:
                # Update dependencies
                if is_extension and "devtools" not in str(path):
                    update_extension_dependencies(path)
                # Bump version
                bump_version(path)
                # Publish (if not dry run)
                if not dry_run:
                    subprocess.run(
                        CMD + PUBLISH_CMD, cwd=path.parent, check=True  # noqa: S603
                    )
            except Exception as e:
                print(f"Error publishing {path.parent}:\n{e}")  # noqa: T201


if __name__ == "__main__":
    msg = """
    You are about to publish a new version of OpenBB Platform to PyPI.
    Please ensure you've read the "PUBLISH.md" file.
    Also, please double check with `poetry config --list` if you're publishing to PyPI or TestPyPI.
    """
    args = parse_args()

    res = input(f"{msg}\n\nDo you want to continue? [y/N] ")

    if res.lower() == "y":
        publish(dry_run=args.dry_run, core=args.core, extensions=args.extensions)

        openbb_package_msg = """
        In order to publish the `openbb` package you need to manually update the
        versions in the `pyproject.toml` file. Follow the steps below:
        1. Bump version: `poetry version prerelease --next-phase`
        2. Re-build the static assets that are bundled with the package
        3. Publish: `poetry publish --build`
        """

        print(openbb_package_msg)  # noqa: T201
