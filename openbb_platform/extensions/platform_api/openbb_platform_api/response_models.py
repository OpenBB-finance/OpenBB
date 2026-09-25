"""Backwards-compatibility shim.

The Workspace response models moved to
``openbb_platform_api.models.response`` in the V5 layout
reorganization. This module preserves the legacy import path for
external callers — new code should import from the ``models``
subpackage directly.
"""

from openbb_platform_api.models.response import (
    MetricResponseModel,
    OmniWidgetResponseModel,
    PdfResponseModel,
)

__all__ = [
    "MetricResponseModel",
    "OmniWidgetResponseModel",
    "PdfResponseModel",
]
