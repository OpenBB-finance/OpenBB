"""IMF metadata package."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from openbb_imf.utils.metadata._core import ImfMetadata

ImfMetadataDependency = Annotated[ImfMetadata, Depends(ImfMetadata)]

__all__ = ["ImfMetadata", "ImfMetadataDependency"]
