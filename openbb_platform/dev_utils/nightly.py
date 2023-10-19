import subprocess
import sys
from pathlib import Path

import toml

repo_dir = Path(__file__).parent.parent.parent

# core
CORE_DIR = repo_dir / "openbb_platform/platform/core"
PYPROJECT_CORE = CORE_DIR / "pyproject.toml"

# providers
PROVIDERS_DIR = repo_dir / "openbb_platform/providers"
PROVIDERS = [x for x in PROVIDERS_DIR.iterdir() if x.is_dir()]

# extensions
EXTENSIONS_DIR = repo_dir / "openbb_platform/extensions"
EXTENSIONS = [x for x in EXTENSIONS_DIR.iterdir() if x.is_dir()]


PLATFORM_PATH = Path(__file__).parent.parent.resolve()
PYPROJECT = PLATFORM_PATH / "pyproject.toml"


def is_provider(dep: str):
    """Check if the dependency is a provider."""

    return dep in [provider.name for provider in PROVIDERS]


def is_extension(dep: str):
    """Check if the dependency is an extension."""

    return dep in [extension.name for extension in EXTENSIONS]


def change_pyproject():
    """Change the openbb_platform/pyproject.toml file"""

    pyproject_toml = toml.load(PYPROJECT)
    dependencies = pyproject_toml["tool"]["poetry"]["dependencies"]
    obb_dependencies = []

    # remove extras as we don't need them
    pyproject_toml["tool"]["poetry"].pop("extras", None)

    # remove all dependencies that start with openbb
    for dep in list(dependencies.keys()):
        if dep.startswith("openbb"):
            pyproject_toml["tool"]["poetry"]["dependencies"].pop(dep)
            obb_dependencies.append(dep)

    # add to included packages and adjust dependencies
    for dep in obb_dependencies:
        adjusted_dep = dep.replace("openbb-", "").replace("-", "_")

        # providers
        if is_provider(adjusted_dep):
            # add local package to included packages
            pyproject_toml["tool"]["poetry"]["packages"].append(
                {"include": f"providers/{adjusted_dep}"}
            )
            # point dependency to local package
            dep_name = f"openbb-{adjusted_dep.replace('_', '-')}"
            pyproject_toml["tool"]["poetry"]["dependencies"][dep_name] = {
                "path": f"providers/{adjusted_dep}"
            }
        # extensions
        elif is_extension(adjusted_dep):
            # add local package to included packages
            pyproject_toml["tool"]["poetry"]["packages"].append(
                {"include": f"extensions/{adjusted_dep}"}
            )
            # point dependency to local package
            dep_name = f"openbb-{adjusted_dep.replace('_', '-')}"
            pyproject_toml["tool"]["poetry"]["dependencies"][dep_name] = {
                "path": f"extensions/{adjusted_dep}"
            }
        # core
        else:
            # add local package to included packages
            pyproject_toml["tool"]["poetry"]["packages"].append(
                {"include": f"platform/{adjusted_dep}"}
            )
            # point dependency to local package
            dep_name = f"openbb-{adjusted_dep.replace('_', '-')}"
            pyproject_toml["tool"]["poetry"]["dependencies"][dep_name] = {
                "path": f"platform/{adjusted_dep}"
            }

    # provider
    # add local package to included packages
    pyproject_toml["tool"]["poetry"]["packages"].append(
        {"include": "platform/provider"}
    )
    # point dependency to local package
    pyproject_toml["tool"]["poetry"]["dependencies"]["openbb-provider"] = {
        "path": "platform/provider"
    }

    return pyproject_toml


def change_pyproject_core():
    """Change the openbb_platform/platform/core/pyproject.toml file"""

    pyproject_toml = toml.load(PYPROJECT_CORE)
    dependencies = pyproject_toml["tool"]["poetry"]["dependencies"]
    obb_dependencies = []

    # remove all dependencies that start with openbb
    for dep in list(dependencies.keys()):
        if dep.startswith("openbb"):
            pyproject_toml["tool"]["poetry"]["dependencies"].pop(dep)
            obb_dependencies.append(dep)

    if obb_dependencies:
        # provider
        pyproject_toml["tool"]["poetry"]["dependencies"]["openbb-provider"] = {
            "path": "../provider"
        }

    return pyproject_toml


def build():
    """Build the Platform package."""

    original_pyproject = PYPROJECT.read_text()
    original_pyproject_core = PYPROJECT_CORE.read_text()

    modified_pyproject_core = change_pyproject_core()
    modified_pyproject = change_pyproject()

    with open(PYPROJECT, "w") as f:
        toml.dump(modified_pyproject, f)

    with open(PYPROJECT_CORE, "w") as f:
        toml.dump(modified_pyproject_core, f)

    CMD = [sys.executable, "-m", "poetry"]

    subprocess.run(  # noqa: PLW1510
        CMD + ["build"], cwd=PLATFORM_PATH, check=True  # noqa: S603
    )

    # we restore the original pyproject files
    with open(PYPROJECT, "w", encoding="utf-8", newline="\n") as f:
        f.write(original_pyproject)
    with open(PYPROJECT_CORE, "w", encoding="utf-8", newline="\n") as f:
        f.write(original_pyproject_core)


if __name__ == "__main__":
    build()
