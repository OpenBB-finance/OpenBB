"""OpenBB Platform Extension post-generation script."""

import os
import re
import shutil
import sys

MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"

MODULE_NAME = "{{ cookiecutter.package_name }}"
PROVIDER_NAME = "{{ cookiecutter.provider_name }}" or ""
ROUTER_NAME = "{{ cookiecutter.router_name }}" or ""
OBBJECT_NAME = "{{ cookiecutter.obbject_name }}" or ""
EXTENSION_TYPES_RAW = "{{ cookiecutter.extension_types }}"


def parse_extension_types(raw: str) -> set[str]:
    types = {t.strip().lower() for t in raw.split(",") if t.strip()}
    if "all" in types:
        return {"router", "provider", "obbject", "on_command_output", "charting"}
    return types


def remove_path(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


EXTENSION_TYPES = parse_extension_types(EXTENSION_TYPES_RAW)

if not re.match(MODULE_REGEX, MODULE_NAME):
    print(f"ERROR: {MODULE_NAME} is not a valid Python package name.")
    sys.exit(1)

has_router = "router" in EXTENSION_TYPES
has_charting = "charting" in EXTENSION_TYPES
has_provider = "provider" in EXTENSION_TYPES
has_obbject = "obbject" in EXTENSION_TYPES
has_on_command_output = "on_command_output" in EXTENSION_TYPES

if has_provider and PROVIDER_NAME and not re.match(MODULE_REGEX, PROVIDER_NAME):
    print(f"ERROR: {PROVIDER_NAME} should be in lower snakecase.")
    sys.exit(1)

if (
    (has_router or has_charting)
    and ROUTER_NAME
    and not re.match(MODULE_REGEX, ROUTER_NAME)
):
    print(f"ERROR: {ROUTER_NAME} should be in lower snakecase.")
    sys.exit(1)

if (
    (has_obbject or has_on_command_output)
    and OBBJECT_NAME
    and not re.match(MODULE_REGEX, OBBJECT_NAME)
):
    print(f"ERROR: {OBBJECT_NAME} should be in lower snakecase.")
    sys.exit(1)

routers_dir = os.path.join(MODULE_NAME, "routers")
providers_dir = os.path.join(MODULE_NAME, "providers")
obbject_dir = os.path.join(MODULE_NAME, "obbject")

if not has_router:
    remove_path(os.path.join(routers_dir, ROUTER_NAME + ".py"))
    remove_path(os.path.join(routers_dir, "depends.py"))

if not has_charting:
    remove_path(os.path.join(routers_dir, ROUTER_NAME + "_views.py"))

if not has_router and not has_charting:
    remove_path(routers_dir)

if not has_provider:
    remove_path(providers_dir)

if not has_obbject and not has_on_command_output:
    remove_path(obbject_dir)

if (has_obbject or has_on_command_output) and not has_router:
    try:
        from importlib.metadata import entry_points

        eps = entry_points()
        core_eps = (
            eps.select(group="openbb_core_extension")
            if hasattr(eps, "select")
            else eps.get("openbb_core_extension", [])
        )
        if not list(core_eps):
            print(
                "\n  WARNING: No 'openbb_core_extension' entry points found in the environment."
                "\n  The 'obbject' and 'on_command_output' extension types require at least"
                "\n  one router extension to be installed in order to function.\n"
            )
    except Exception:
        pass
