"""Backwards-compatibility shim.

The router-attached ``agents.json`` discovery / merge flow moved to
``openbb_platform_api.service.agents_service`` in the V5 layout
reorganization. This module preserves the legacy import path; new
code should import from the ``service`` subpackage directly.
"""

from openbb_platform_api.service.agents_service import (
    get_additional_agents,
    has_additional_agents,
)

__all__ = ["get_additional_agents", "has_additional_agents"]
