"""Tests for charting backend override resolution.

Backends are discovered through real entry points from a genuine installed
package (see ``conftest.py``); the ``openbb_charting_backend`` group and the
``SystemService`` config are never mocked.
"""

from openbb_core.app.charting import get_charting_backend_class


class TestChartingBackend:
    """Resolve an opt-in rendering-backend override via real entry points."""

    def test_no_selection_returns_none(self):
        """Without a configured selection, no override is applied."""
        assert get_charting_backend_class() is None

    def test_config_selection_by_name(self, charting_config):
        """``charting_backend`` selects a backend by entry-point name."""
        charting_config(charting_backend="fake_backend")
        assert get_charting_backend_class().__name__ == "PrimaryBackend"

    def test_missing_config_returns_none(self, charting_config):
        """A configured backend name that isn't registered resolves to None."""
        charting_config(charting_backend="does_not_exist")
        assert get_charting_backend_class() is None

    def test_config_disambiguates_between_backends(self, charting_config):
        """Config selects one of several registered backends by name."""
        charting_config(charting_backend="fake_secondary_backend")
        assert get_charting_backend_class().__name__ == "SecondaryBackend"

    def test_explicit_name_argument_selects_backend(self):
        """An explicit name argument selects among registered backends."""
        assert (
            get_charting_backend_class(name="fake_secondary_backend").__name__
            == "SecondaryBackend"
        )
        assert (
            get_charting_backend_class(name="fake_backend").__name__ == "PrimaryBackend"
        )
