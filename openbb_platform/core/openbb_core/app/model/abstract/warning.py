"""Module for warnings."""

from warnings import WarningMessage

from pydantic import BaseModel


class Warning_(BaseModel):
    """Model for Warning."""

    category: str
    message: str


def cast_warning(w: WarningMessage) -> Warning_:
    """Cast a warning to a pydantic model."""
    return Warning_(
        category=w.category.__name__,
        message=str(w.message),
    )


class OpenBBWarning(Warning):
    """Base class for OpenBB warnings."""
