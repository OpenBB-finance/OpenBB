"""Tests for ``openbb_charting.core.dummy_backend``."""

from __future__ import annotations

import pytest

from openbb_charting.core.dummy_backend import DummyBackend


class TestDummyBackend:
    """Tests for the no-op ``DummyBackend`` fallback."""

    def test_init_without_theme(self):
        """It initializes with no theme when none is supplied."""
        backend = DummyBackend()
        assert backend.theme is None

    def test_init_with_theme(self):
        """It stores the theme passed as a keyword argument."""
        backend = DummyBackend(theme="dark")
        assert backend.theme == "dark"

    def test_show_plotly_raises_not_implemented(self):
        """``show_plotly`` raises ``NotImplementedError``."""
        with pytest.raises(NotImplementedError, match="pywry is not installed"):
            DummyBackend().show_plotly(figure=object())

    def test_show_dataframe_raises_not_implemented(self):
        """``show_dataframe`` raises ``NotImplementedError``."""
        with pytest.raises(NotImplementedError, match="pywry is not installed"):
            DummyBackend().show_dataframe(data=object())

    def test_show_raises_not_implemented(self):
        """``show`` raises ``NotImplementedError``."""
        with pytest.raises(NotImplementedError, match="pywry is not installed"):
            DummyBackend().show(content="<html></html>")

    def test_emit_is_noop(self):
        """``emit`` accepts arbitrary arguments and returns ``None``."""
        assert DummyBackend().emit("event", {"a": 1}, "label") is None

    def test_close_is_noop(self):
        """``close`` accepts keyword arguments and returns ``None``."""
        assert DummyBackend().close(reset=True) is None

    def test_destroy_is_noop(self):
        """``destroy`` returns ``None``."""
        assert DummyBackend().destroy() is None
