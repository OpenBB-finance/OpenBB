"""Bronze/Silver/Gold data-layer contract helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from openbb_quant_ml.service.storage import save_json


@dataclass
class DataLayerMeta:
    """One data-layer metadata row."""

    layer: str
    data_version: str
    as_of_cutoff: str
    quality_flags: dict[str, Any]


def write_data_layer_meta(
    run_dir: Path,
    *,
    layer: str,
    data_version: str,
    as_of_cutoff: str,
    quality_flags: dict[str, Any] | None = None,
) -> None:
    """Persist one bronze/silver/gold layer metadata contract."""
    payload = asdict(
        DataLayerMeta(
            layer=layer,
            data_version=data_version,
            as_of_cutoff=as_of_cutoff,
            quality_flags=quality_flags or {},
        )
    )
    save_json(run_dir / f"{layer}_layer_meta.json", payload)
