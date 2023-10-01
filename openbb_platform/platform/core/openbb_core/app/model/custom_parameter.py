import sys
from dataclasses import dataclass
from typing import Optional

# `slots` is available on Python >= 3.10
if sys.version_info >= (3, 10):
    slots_true = {"slots": True}
else:
    slots_true = {}


class BaseMetadata:
    """Base class for all metadata.

    This exists mainly so that implementers
    can do `isinstance(..., BaseMetadata)` while traversing field annotations.
    """

    __slots__ = ()


@dataclass(frozen=True, **slots_true)
class OpenBBCustomParameter(BaseMetadata):
    """Custom parameter for OpenBB."""

    description: Optional[str] = None
