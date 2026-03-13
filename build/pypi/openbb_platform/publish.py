"""Publish the OpenBB Platform to PyPi."""

import argparse
import logging
import sys
from functools import partial
from pathlib import Path
from subprocess import PIPE, run
from typing import Literal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
logger.addHandler(console)
formatter = logging.Formatter("[%(levelname)s] %(message)s")
console.setFormatter(formatter)

DIR_PLATFORM = Path(__file__).parent.parent.parent.parent.resolve() / "openbb_platform"
DIR_CORE = ["core"]
DIR_EXTENSIONS = ["extensions", "providers", "obbject_extensions"]


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
        help="Publish extension packages, such as openbb-equity or openbb-fmp.",
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
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the tool in verbose mode.",
        default=False,
        dest="verbose",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Answer input questions.",
        default=False,
        dest="yes",
    )
    parser.add_argument(
        "--semver",
        help="Semantic version.",
        default="patch",
        choices=["patch", "minor", "major", "none"],
        dest="semver",
    )
    return parser.parse_args()


def publish(
    dry_run: bool = False,
    core: bool = False,
    extensions: bool = False,
    openbb: bool = False,
    verbose: bool = False,
    semver: Literal["patch", "minor", "major", "none"] = "patch",
):
    """Publish the Platform to PyPi with optional core or extensions."""
    package_directories = []
    if core:
        package_directories.extend(DIR_CORE)
    if extensions:
        package_directories.extend(DIR_EXTENSIONS)

    partial_run = partial(
        run,
        check=True,
        stdout=None if verbose else PIPE,
        stderr=None if verbose else PIPE,
    )

    for _dir in package_directories:
        is_extension = _dir in DIR_EXTENSIONS
        paths = [
            p
            for p in sorted(DIR_PLATFORM.rglob(f"{_dir}/**/pyproject.toml"))
            if "devtools" not in str(p)
        ]
        total = len(paths)
        logger.info("~~~ /%s ~~~", _dir)
        for i, path in enumerate(paths):
            logger.info(
                "🚀 (%s/%s) Publishing openbb-%s...",
                i + 1,
                total,
                path.parent.stem.replace("_", "-"),
            )
            try:
                # Update openbb-core to latest in each pyproject.toml
                if is_extension:
                    partial_run(
                        [
                            sys.executable,
                            "-m",
                            "poetry",
                            "add",
                            "openbb-core=latest",
                            "--lock",
                        ],
                        cwd=path.parent,
                    )
                # Bump pyproject.toml version
                if semver != "none":
                    partial_run(
                        [sys.executable, "-m", "poetry", "version", semver],
                        cwd=path.parent,
                    )
                # Publish (if not dry running)
                if not dry_run:
                    partial_run(
                        [
                            sys.executable,
                            "-m",
                            "poetry",
                            "publish",
                            "--build",
                        ],
                        cwd=path.parent,
                    )
                logger.info("✅ Success")
            except Exception as e:
                logger.error("❌ Failed to publish %s:\n\n%s", path.parent.stem, e)

    if openbb:
        STEPS = 7
        logger.info("~~~ /openbb ~~~")
        logger.info("🧩 (1/%s) Installing poetry-plugin-up...", STEPS)
        partial_run(
            ["pip", "install", "poetry-plugin-up"],
            cwd=DIR_PLATFORM,
        )
        logger.info("⏫ (2/%s) Updating openbb pyproject.toml...", STEPS)
        partial_run(
            [sys.executable, "-m", "poetry", "up", "--latest"],
            cwd=DIR_PLATFORM,
        )
        logger.info("🔒 (3/%s) Writing openbb poetry.lock...", STEPS)
        partial_run(
            [sys.executable, "-m", "poetry", "up", "--latest"],
            cwd=DIR_PLATFORM,
        )
        logger.info("📍 (4/%s) Installing openbb from /%s...", STEPS, DIR_PLATFORM.stem)
        partial_run(
            ["pip", "install", "-U", "--editable", "."],
            cwd=DIR_PLATFORM,
        )
        logger.info("🚧 (5/%s) Building python interface...", STEPS)
        result = run(
            [sys.executable, "-c", "import openbb; openbb.build()"],  # noqa: S603
            cwd=DIR_PLATFORM,
            check=True,
            capture_output=True,
            text=True,
        )
        if verbose:
            logger.info("Captured result -> %s", result)
        if result.stderr:
            logger.error("❌ stderr is not empty!")
            raise Exception(result.stderr)
        logger.info("🧪 (6/%s) Unit testing...", STEPS)
        partial_run(
            ["pytest", "tests", "-m", "not integration"],
            cwd=DIR_PLATFORM,
        )
        logger.info("🚭 (7/%s) Smoke testing...", STEPS)
        # TODO: Improve smoke test coverage here
        result = run(  # noqa: S603
            [  # noqa: S603
                sys.executable,
                "-c",
                "from openbb import obb; obb.equity.price.historical('AAPL', provider='yfinance')",
            ],
            cwd=DIR_PLATFORM,
            check=True,
            capture_output=True,
            text=True,
        )
        if verbose:
            logger.info("Captured result -> %s", result)
        if result.stderr:
            logger.error("❌ stderr is not empty!")
            raise Exception(result.stderr)
        logger.info("👍 Great success! 👍")
        logger.info(
            "Confirm any files changed and run `poetry publish --build` from /openbb_platform"
        )


if __name__ == "__main__":
    msg = (
        "\nYou are about to publish a new version of OpenBB Platform to PyPI."
        + "\n\nPlease ensure you've read the PUBLISH.md file and double check with "
        + "`poetry config --list` if you're publishing to PyPI or TestPyPI."
    )
    args = parse_args()
    if not args.dry_run:
        msg += "\n\n🛑 You are NOT using the --dry-run flag!"
    res = "y" if args.yes else input(f"{msg}\n\nDo you want to continue? [y/N] ")
    print("")  # noqa: T201
    if res.lower() == "y":
        logger.info("Process started. Press Ctrl+C to abort.")
        try:
            publish(
                dry_run=args.dry_run,
                core=args.core,
                extensions=args.extensions,
                openbb=args.openbb,
                verbose=args.verbose,
                semver=args.semver,
            )
        except KeyboardInterrupt:
            sys.exit(1)
