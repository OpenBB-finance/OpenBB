"""Custom pytest configuration for the extensions."""

import pytest
from openbb_core.app.router import CommandMap

from .utils.helpers import list_openbb_extensions

cm = CommandMap()
commands = list(cm.map.keys())

# ruff: noqa: SIM114


def parametrize(argnames: str, argvalues: list, **kwargs):
    """Apply a custom parametrize decorator that filters test cases based on the environment."""

    routers, providers, obbject_ext = list_openbb_extensions()

    def decorator(function):
        """Patch the pytest.mark.parametrize decorator."""
        filtered_argvalues: list[dict] = []
        name = function.__name__.split("_")[1]
        # This is a patch to handle the charting extension name
        extension_name = "openbb_" + name if name == "charting" else name
        function_name = "/" + "/".join(function.__name__.split("_")[1:])
        # this handles edge cases where the function name has an underscore
        function_name_v2 = (
            function_name.rsplit("/", 1)[0] + "_" + function_name.rsplit("/", 1)[1]
        )
        function_name_v3 = (
            function_name.rsplit("/", 2)[0]
            + "_"
            + function_name.rsplit("/", 2)[1]
            + "_"
            + function_name.rsplit("/", 1)[1].replace("/", "_")
        )
        if extension_name in routers | obbject_ext:
            for args in argvalues:
                if "provider" in args and args["provider"] in providers:
                    filtered_argvalues.append(args)
                elif "provider" not in args and function_name in commands:
                    # Run the standard test case
                    filtered_argvalues.append(args)
                elif "provider" not in args and function_name_v2 in commands:
                    # Handle edge case
                    filtered_argvalues.append(args)
                elif "provider" not in args and function_name_v3 in commands:
                    # Handle edge case
                    filtered_argvalues.append(args)
                elif extension_name in obbject_ext:
                    filtered_argvalues.append(args)

            # If filtered_argvalues is empty, pytest will skip the test!
            return pytest.mark.parametrize(argnames, filtered_argvalues, **kwargs)(
                function
            )

        return pytest.mark.skip(function)

    return decorator
