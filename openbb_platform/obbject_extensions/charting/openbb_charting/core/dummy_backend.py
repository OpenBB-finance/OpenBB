"""Dummy backend when pywry is not installed."""

from typing import Any


class DummyBackend:
    """No-op backend used when pywry is not installed."""

    def __init__(self, **kwargs):
        self.theme: Any = kwargs.get("theme")

    def show_plotly(self, **kwargs):
        """Raise NotImplementedError."""
        raise NotImplementedError("pywry is not installed")

    def show_dataframe(self, **kwargs):
        """Raise NotImplementedError."""
        raise NotImplementedError("pywry is not installed")

    def show(self, content="", **kwargs):
        """Raise NotImplementedError."""
        raise NotImplementedError("pywry is not installed")

    def emit(self, *args, **kwargs):
        """No-op."""

    def close(self, **kwargs):
        """No-op."""

    def destroy(self):
        """No-op."""
