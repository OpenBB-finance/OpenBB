from pathlib import Path
import os

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

# core
print(f"Publishing core: {core_dir.name}")
os.chdir(core_dir)
os.system(VERSION_BUMP_CMD)
os.system(PUBLISH_CMD)

# provider
print(f"Publishing provider: {provider_dir.name}")
os.chdir(provider_dir)
os.system(VERSION_BUMP_CMD)
os.system(PUBLISH_CMD)

# extensions
for extension in extensions:
    print(f"Publishing extension: {extension.name}")

    if extension.name in ["__pycache__", "tests"]:
        continue

    os.chdir(extension)
    os.system(VERSION_BUMP_CMD)
    os.system(PUBLISH_CMD)

# providers
for provider in providers:
    print(f"Publishing provider: {provider.name}")

    if provider.name in ["__pycache__", "tests"]:
        continue

    os.chdir(provider)
    os.system(VERSION_BUMP_CMD)
    os.system(PUBLISH_CMD)
