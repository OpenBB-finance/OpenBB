import subprocess
import sys
from pathlib import Path

repo_dir = Path(__file__).parent.parent

# core and provider
core_dir = repo_dir / "openbb_platform/platform/core"
provider_dir = repo_dir / "openbb_platform/platform/provider"

# extensions
extensions_dir = repo_dir / "openbb_platform/extensions"
extensions = [x for x in extensions_dir.iterdir() if x.is_dir()]

# providers
providers_dir = repo_dir / "openbb_platform/providers"
providers = [x for x in providers_dir.iterdir() if x.is_dir()]

# openbb
openbb_dir = repo_dir / "openbb_platform"

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

    # provider
    run_cmds(provider_dir)

    # core
    run_cmds(core_dir)

    # extensions
    for extension in extensions:
        if extension.name in ["__pycache__", "tests"]:
            continue

        run_cmds(extension)

    # providers
    for provider in providers:
        if provider.name in ["__pycache__", "tests"]:
            continue

        run_cmds(provider)

    # openbb
    run_cmds(openbb_dir)


if __name__ == "__main__":
    raise Exception(
        "If you're ar running this script for the first time,"
        "ensure you have changed `VERSION` on System Settings "
        "before you publish the `openbb-core` package to Pypi."
    )

    publish()
