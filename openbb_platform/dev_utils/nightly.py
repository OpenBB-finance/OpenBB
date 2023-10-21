import subprocess
import sys
from typing import Any, Dict

import toml
from dev_utils.dev_install import PLATFORM_PATH

PYPROJECT = PLATFORM_PATH / "pyproject.toml"
SUB_PACKAGES = {"platform": {}, "providers": {}, "extensions": {}}
PLUGINS = {"openbb_core_extension": {}, "openbb_provider_extension": {}}

PYPROJECT_TOML = toml.load(PYPROJECT)
POETRY_DICT: Dict[str, dict] = PYPROJECT_TOML["tool"]["poetry"]
DEPENDENCIES: Dict[str, Any] = {}

original_pyproject = PYPROJECT.read_text()
POETRY_DICT.pop("extras", None)

CMD = [sys.executable, "-m", "poetry", "build"]


def gather_metadata(sub_path: str):
    """Gather metadata from the pyproject.toml files.

    Parameters
    ----------
    sub_path : str
        The path to the sub packages.
    """
    for path in PLATFORM_PATH.rglob(f"{sub_path}/**/pyproject.toml"):
        pyproject_toml = toml.load(path)
        poetry_dict: Dict[str, dict] = pyproject_toml["tool"]["poetry"]
        package_name = poetry_dict["packages"][0]["include"]

        for extension in list(PLUGINS.keys()):
            PLUGINS[extension].update(poetry_dict.get("plugins", {}).get(extension, {}))

        DEPENDENCIES.update(pyproject_toml["tool"]["poetry"]["dependencies"])
        SUB_PACKAGES[sub_path][package_name] = path.relative_to(
            PLATFORM_PATH
        ).parent.as_posix()


def build():
    """Build the Platform package."""
    for sub_path in SUB_PACKAGES:
        gather_metadata(sub_path)

    # need to pop these from the dependencies
    DEPENDENCIES.pop("openbb-core", None)
    DEPENDENCIES.pop("openbb-provider", None)

    # add the sub packages
    for sub_path in list(SUB_PACKAGES.keys()):
        for package_name, path in SUB_PACKAGES[sub_path].items():
            POETRY_DICT["packages"].append(
                {"include": package_name, "from": f"./{path}"}
            )

    # add the plugins extensions
    for extension, plugins in PLUGINS.items():
        POETRY_DICT.setdefault("plugins", {}).setdefault(extension, {}).update(plugins)

    # update the dependencies and platform poetry dict
    POETRY_DICT["dependencies"] = DEPENDENCIES
    PYPROJECT_TOML["tool"]["poetry"] = POETRY_DICT

    temp_pyproject = toml.dumps(PYPROJECT_TOML)

    try:
        with open(PYPROJECT, "w", encoding="utf-8", newline="\n") as f:
            f.write(temp_pyproject)

        subprocess.run(CMD, cwd=PLATFORM_PATH, check=True)  # noqa: S603,PLW1510
    except (Exception, KeyboardInterrupt) as e:
        print(e)  # noqa: T201
        print("Restoring pyproject.toml")  # noqa: T201

    # we restore the original pyproject.toml
    with open(PYPROJECT, "w", encoding="utf-8", newline="\n") as f:
        f.write(original_pyproject)


if __name__ == "__main__":
    build()
