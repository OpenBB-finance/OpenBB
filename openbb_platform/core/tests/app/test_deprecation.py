"""Test deprecated commands."""

import unittest

from openbb_core.app.static.package_builder import PathHandler
from openbb_core.app.version import VERSION, get_major_minor


class DeprecatedCommandsTest(unittest.TestCase):
    """Test deprecated commands."""

    def test_deprecated_commands(self):
        """Test deprecated commands."""
        current_major_minor = get_major_minor(VERSION)
        route_map = PathHandler.build_route_map()

        for path, route in route_map.items():
            with self.subTest(i=path):
                if getattr(route, "deprecated", False):
                    deprecation_message = getattr(route, "summary", "")
                    if hasattr(deprecation_message, "metadata"):
                        obb_deprecation_warning = deprecation_message.metadata

                        assert (
                            obb_deprecation_warning.expected_removal
                            != current_major_minor
                        ), f"The expected removal version of `{path}` matches the current version, please remove it."
