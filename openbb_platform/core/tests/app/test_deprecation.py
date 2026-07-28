"""Test deprecated commands."""

import unittest

from openbb_core.app.deprecation import DeprecationSummary, OpenBBDeprecationWarning
from openbb_core.app.static.package_builder import PathHandler
from openbb_core.app.version import VERSION, get_major_minor


def test_deprecation_summary_stores_metadata():
    """Lines 15-17: DeprecationSummary stores metadata attribute."""
    w = OpenBBDeprecationWarning("old feature", since=(4, 0), expected_removal=(5, 0))
    ds = DeprecationSummary("old feature is deprecated", w)
    assert ds.metadata is w
    assert "old feature is deprecated" in ds


def test_openbb_deprecation_warning_init_defaults():
    """Test __init__ sets message, since, expected_removal, long_message."""
    w = OpenBBDeprecationWarning("old feature.")
    assert w.message == "old feature"
    assert isinstance(w.since, tuple)
    assert w.expected_removal == (w.since[0] + 1, 0)
    assert "Deprecated" in w.long_message


def test_openbb_deprecation_warning_str():
    """Test __str__ returns long_message."""
    w = OpenBBDeprecationWarning("old feature", since=(4, 0), expected_removal=(5, 0))
    assert str(w) == w.long_message
    assert "V4.0" in str(w)
    assert "V5.0" in str(w)


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
                        ), (
                            f"The expected removal version of `{path}` matches the current version, please remove it."
                        )
