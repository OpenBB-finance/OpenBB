import os
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

VERSION_BUMP_CMD = "poetry version prerelease"
PUBLISH_CMD = "poetry publish --build"

raise Exception(
    "If you're ar running this script for the first time,"
    "ensure you have changed `VERSION` on System Settings "
    "before you publish the `openbb-core` package to Pypi."
)


def run_cmds(directory: Path):
    print(f"Publishing: {directory.name}")  # noqa: T201
    os.chdir(directory)
    os.system(VERSION_BUMP_CMD)  # noqa: S605
    os.system(PUBLISH_CMD)  # noqa: S605


# core
run_cmds(core_dir)

# provider
run_cmds(provider_dir)

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
