"""Backwards-compatibility shim.

The Workspace query models moved to ``openbb_platform_api.models.query``
in the V5 layout reorganization. This module preserves the legacy import
path for external callers — new code should import from the
``models`` subpackage directly.
"""

from openbb_platform_api.models.query import OmniWidgetInput

__all__ = ["OmniWidgetInput"]
