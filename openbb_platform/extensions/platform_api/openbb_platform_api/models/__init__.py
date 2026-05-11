"""Pydantic models for the OpenBB Platform API extension.

Re-exports the public surface so callers can write
``from openbb_platform_api.models import OmniWidgetInput`` rather than
having to know the exact module each model lives in.
"""

from openbb_platform_api.models.query import OmniWidgetInput
from openbb_platform_api.models.response import (
    MetricResponseModel,
    OmniWidgetResponseModel,
    PdfResponseModel,
)

__all__ = [
    "MetricResponseModel",
    "OmniWidgetInput",
    "OmniWidgetResponseModel",
    "PdfResponseModel",
]
