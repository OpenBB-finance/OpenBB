"""Government CA metadata package.

Re-exports the public symbols of the metadata subsystem so callers
can write::

    from openbb_government_ca.utils.metadata import (
        GovernmentCaMetadata,
        GovernmentCaMetadataDependency,
    )
"""

from openbb_government_ca.utils.metadata._constants import (
    _SHIPPED_CACHE_DIR,
    _SHIPPED_CACHE_FILE,
    _USER_CACHE_FILE,
    BOC_VALET_BASE_URL,
    STATSCAN_HOMEPAGE_JSON_URL,
    STATSCAN_SDMX_BASE_URL,
)
from openbb_government_ca.utils.metadata._core import (
    GovernmentCaMetadata,
    GovernmentCaMetadataDependency,
)

__all__ = [
    "BOC_VALET_BASE_URL",
    "GovernmentCaMetadata",
    "GovernmentCaMetadataDependency",
    "STATSCAN_HOMEPAGE_JSON_URL",
    "STATSCAN_SDMX_BASE_URL",
    "_SHIPPED_CACHE_DIR",
    "_SHIPPED_CACHE_FILE",
    "_USER_CACHE_FILE",
]
