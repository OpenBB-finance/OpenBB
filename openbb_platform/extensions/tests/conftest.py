"""Custom pytest configuration for the extensions."""
from typing import Dict, List

import pytest

from extensions.tests.utils.helpers import list_openbb_extensions


def parametrize(argnames: str, argvalues: List[Dict], **kwargs):
    """Custom parametrize decorator that filters test cases based on the environment."""

    extensions, providers = list_openbb_extensions()

    def decorator(function):
        """Patch the pytest.mark.parametrize decorator."""
        filtered_argvalues: List[Dict] = []
        extension_name = function.__name__.split("_")[1]
        if extension_name in extensions:
            for args in argvalues:
                if "provider" in args and args["provider"] in providers:
                    filtered_argvalues.append(args)
                elif "provider" not in args:
                    # Run the standard test case
                    filtered_argvalues.append(args)
            return pytest.mark.parametrize(argnames, filtered_argvalues, **kwargs)(
                function
            )
        else:
            return pytest.mark.skip(function)

    return decorator
