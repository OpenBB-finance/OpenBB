"""OpenBB Error."""


class OpenBBError(Exception):
    """OpenBB Error."""

    def __init__(self, original: str | Exception | None = None):
        """Initialize the OpenBBError."""
        self.original = original
        super().__init__(str(original))
