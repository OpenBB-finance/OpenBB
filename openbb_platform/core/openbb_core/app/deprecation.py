"""
OpenBB-specific deprecation warnings.

This implementation was inspired from Pydantic's specific warnings and modified to suit OpenBB's needs.
"""

from typing import Optional, Tuple


class OpenBBDeprecationWarning(DeprecationWarning):
    """
    A OpenBB specific deprecation warning.

    This warning is raised when using deprecated functionality in OpenBB. It provides information on when the
    deprecation was introduced and the expected version in which the corresponding functionality will be removed.

    Attributes
    ----------
        message: Description of the warning.
        since: Version in what the deprecation was introduced.
        expected_removal: Version in what the corresponding functionality expected to be removed.
    """

    message: str
    since: Tuple[int, int]
    expected_removal: Tuple[int, int]

    def __init__(
        self,
        message: str,
        *args: object,
        since: Tuple[int, int],
        expected_removal: Optional[Tuple[int, int]] = None,
    ) -> None:
        super().__init__(message, *args)
        self.message = message.rstrip(".")
        self.since = since
        self.expected_removal = expected_removal or (since[0] + 1, 0)
        self.long_message = (
            f"{self.message}. Deprecated in OpenBB Platform V{self.since[0]}.{self.since[1]}"
            f" to be removed in V{self.expected_removal[0]}.{self.expected_removal[1]}."
        )

    def __str__(self) -> str:
        """Return the warning message."""
        return self.long_message
