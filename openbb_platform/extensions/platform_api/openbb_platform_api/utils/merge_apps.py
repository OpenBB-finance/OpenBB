"""Backwards-compatibility shim.

The router-attached ``apps.json`` discovery / merge flow moved to
``openbb_platform_api.service.apps_service`` in the V5 layout
reorganization. This module preserves the legacy import path; new
code should import from the ``service`` subpackage directly.
"""

from openbb_platform_api.service.apps_service import (
    get_additional_apps,
    has_additional_apps,
)

__all__ = ["get_additional_apps", "has_additional_apps"]
