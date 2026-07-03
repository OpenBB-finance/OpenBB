"""Tests for ``openbb_charting.styles.colors``."""

from openbb_charting.styles import colors


class TestColors:
    """Exercise the color palette module."""

    def test_large_cycler_is_list_of_strings(self):
        """LARGE_CYCLER is a non-empty list whose entries are all strings."""
        assert isinstance(colors.LARGE_CYCLER, list)
        assert colors.LARGE_CYCLER
        assert all(isinstance(color, str) for color in colors.LARGE_CYCLER)

    def test_large_cycler_known_values(self):
        """LARGE_CYCLER contains the expected first and named entries."""
        assert colors.LARGE_CYCLER[0] == "#1f77b4"
        assert "burlywood" in colors.LARGE_CYCLER
        assert colors.LARGE_CYCLER[-1] == "#d9f202"

    def test_large_cycler_length(self):
        """LARGE_CYCLER has the full set of palette entries."""
        assert len(colors.LARGE_CYCLER) == 35
