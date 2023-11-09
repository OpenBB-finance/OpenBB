""" Publish the OpenBB Platform to PyPi"""
import subprocess
import sys
from pathlib import Path

PLATFORM_PATH = Path(__file__).parent.parent.parent.parent.resolve() / "openbb_platform"

SUB_PACKAGES = ["platform/provider", "platform/core", "extensions", "providers"]

CMD = [sys.executable, "-m", "poetry"]
VERSION_BUMP_CMD = ["version", "prerelease"]
PUBLISH_CMD = ["publish", "--build"]


def run_cmds(directory: Path):
    """Run the commands for publishing"""
    print(f"Publishing: {directory.name}")  # noqa: T201

    subprocess.run(CMD + VERSION_BUMP_CMD, cwd=directory, check=True)  # noqa: S603
    subprocess.run(CMD + PUBLISH_CMD, cwd=directory, check=True)  # noqa: S603


def publish():
    """Publish the Platform to PyPi"""
    for sub_path in SUB_PACKAGES:
        for path in PLATFORM_PATH.rglob(f"{sub_path}/**/pyproject.toml"):
            run_cmds(path.parent)

    # openbb
    run_cmds(PLATFORM_PATH)


if __name__ == "__main__":
    msg = """
    You are about to publish a new version of OpenBB Platform to PyPI.
    Please ensure you've read the "PUBLISH.md" file.
    Also, please double check with `poetry config --list` if you're publishing to PyPI or TestPyPI.
    """

    res = input(f"{msg}\n\nDo you want to continue? [y/N] ")

    if res.lower() == "y":
        publish()
