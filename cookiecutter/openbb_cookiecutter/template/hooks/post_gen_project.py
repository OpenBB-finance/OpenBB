"""OpenBB Platform Extension post-generation script."""

import re
import sys

MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"

MODULE_NAME = "{{ cookiecutter.package_name }}"
PROVIDER_NAME = "{{ cookiecutter.provider_name }}" or ""
ROUTER_NAME = "{{ cookiecutter.router_name }}" or ""
OBBJECT_NAME = "{{ cookiecutter.obbject_name }}" or ""

if not re.match(MODULE_REGEX, MODULE_NAME):
    print(f"ERROR: {MODULE_NAME} is not a valid Python package name.")

    sys.exit(1)

if PROVIDER_NAME and not re.match(MODULE_REGEX, PROVIDER_NAME):
    print(f"ERROR: {PROVIDER_NAME} should be in lower snakecase.")

    sys.exit(1)

if ROUTER_NAME and not re.match(MODULE_REGEX, ROUTER_NAME):
    print(f"ERROR: {ROUTER_NAME} should be in lower snakecase.")

    sys.exit(1)

if OBBJECT_NAME and not re.match(MODULE_REGEX, OBBJECT_NAME):
    print(f"ERROR: {OBBJECT_NAME} should be in lower snakecase.")

    sys.exit(1)
