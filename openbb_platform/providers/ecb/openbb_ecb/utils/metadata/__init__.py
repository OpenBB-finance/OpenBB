"""ECB metadata package."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from openbb_ecb.utils.metadata._core import EcbMetadata

EcbMetadataDependency = Annotated[EcbMetadata, Depends(EcbMetadata)]

__all__ = ["EcbMetadata", "EcbMetadataDependency"]
