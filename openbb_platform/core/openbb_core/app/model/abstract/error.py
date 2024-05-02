"""OpenBB Error."""

from typing import Optional, Union


class OpenBBError(Exception):
    """OpenBB Error."""

    def __init__(self, original: Optional[Union[str, Exception]] = None):
        """Initialize the OpenBBError."""
        self.original = original
        super().__init__(str(original))
