"""OpenBB Platform extension post-generation script."""

import re
import shutil
import subprocess
import sys
from pathlib import Path

MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"
MODULE_NAME = "{{ cookiecutter.package_name }}"
PROVIDER_NAME = "{{ cookiecutter.provider_name }}"
ROUTER_NAME = "{{ cookiecutter.router_name }}"
OBBJECT_NAME = "{{ cookiecutter.obbject_name }}"
EXTENSION_TYPES_RAW = "{{ cookiecutter.extension_types }}"
ALL_TYPES = {"router", "provider", "obbject", "on_command_output", "charting"}
LOCAL_ARTIFACTS = (".ruff_cache", ".pytest_cache", ".ipynb_checkpoints", "__pycache__", ".DS_Store")


def parse_extension_types(raw: str) -> set[str]:
    """Return the selected extension types, expanding ``all``.

    Parameters
    ----------
    raw : str
        Comma-separated extension types.

    Returns
    -------
    set[str]
        The selected extension types.
    """
    types = {t.strip().lower() for t in raw.split(",") if t.strip()}
    return set(ALL_TYPES) if "all" in types else types


def remove_path(path: Path) -> None:
    """Remove a generated file or directory if it exists.

    Parameters
    ----------
    path : Path
        The file or directory to remove.
    """
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def require_module_name(name: str, label: str) -> None:
    """Exit when a name is not a valid Python module name.

    Parameters
    ----------
    name : str
        The name to check.
    label : str
        What the name is used for, shown in the error.
    """
    if not re.match(MODULE_REGEX, name):
        print(f"ERROR: {label} '{name}' must be a lower snake_case Python name.")
        sys.exit(1)


types = parse_extension_types(EXTENSION_TYPES_RAW)
has_router = "router" in types
has_charting = "charting" in types
has_provider = "provider" in types
has_obbject = "obbject" in types
has_on_command_output = "on_command_output" in types

require_module_name(MODULE_NAME, "package_name")
if has_provider:
    require_module_name(PROVIDER_NAME, "provider_name")
if has_router or has_charting:
    require_module_name(ROUTER_NAME, "router_name")
if has_obbject or has_on_command_output:
    require_module_name(OBBJECT_NAME, "obbject_name")
if has_provider and has_obbject and PROVIDER_NAME == OBBJECT_NAME:
    print(
        f"ERROR: provider_name and obbject_name are both '{PROVIDER_NAME}'; "
        "they share the credentials namespace, so use different names."
    )
    sys.exit(1)

package = Path(MODULE_NAME)
routers = package / "routers"
obbject = package / "obbject"
tests = Path("tests")

if not has_router:
    remove_path(routers / f"{ROUTER_NAME}.py")
    remove_path(tests / "test_router.py")
if not has_charting:
    remove_path(routers / f"{ROUTER_NAME}_views.py")
    remove_path(tests / "test_views.py")
if not has_router and not has_charting:
    remove_path(routers)
if not has_provider:
    remove_path(package / "providers")
    remove_path(tests / "test_provider.py")
if not has_obbject:
    remove_path(tests / "test_obbject.py")
if not has_on_command_output:
    remove_path(obbject / OBBJECT_NAME / "on_command_output.py")
    remove_path(tests / "test_on_command_output.py")
if not has_obbject and not has_on_command_output:
    remove_path(obbject)

for artifact in LOCAL_ARTIFACTS:
    for path in sorted(Path().rglob(artifact), reverse=True):
        remove_path(path)

if ruff := shutil.which("ruff"):
    subprocess.run([ruff, "format", "--quiet", "--no-cache", "."], check=False)
