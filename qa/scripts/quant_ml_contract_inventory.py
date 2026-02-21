"""Generate backend contract inventory tables for Quant ML."""

from __future__ import annotations

import csv
import hashlib
import inspect
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from openbb_quant_ml import models

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs" / "architecture"
INV_DIR = DOCS_DIR / "contract_inventory"


def _iter_model_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for name, obj in inspect.getmembers(models):
        if not inspect.isclass(obj) or not issubclass(obj, BaseModel):
            continue
        if obj is BaseModel:
            continue
        for field_name, field in obj.model_fields.items():
            rows.append(
                {
                    "model": name,
                    "field_name": field_name,
                    "type": str(field.annotation),
                    "unit": "",
                    "shape": "scalar",
                    "index_format": "",
                    "nullable": str(field.is_required() is False).lower(),
                    "owner_layer": "backend",
                    "compute_responsibility": "server",
                }
            )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _hash_file(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> None:
    rows = _iter_model_rows()
    _write_csv(
        INV_DIR / "backend_models.csv",
        rows,
        [
            "model",
            "field_name",
            "type",
            "unit",
            "shape",
            "index_format",
            "nullable",
            "owner_layer",
            "compute_responsibility",
        ],
    )
    matrix_rows = [
        {
            "artifact": "models.py",
            "signature_hash": _hash_file(
                ROOT
                / "openbb_platform"
                / "extensions"
                / "quant_ml"
                / "openbb_quant_ml"
                / "models.py"
            ),
            "owner_layer": "backend",
        }
    ]
    _write_csv(
        INV_DIR / "responsibility_matrix.csv",
        matrix_rows,
        ["artifact", "signature_hash", "owner_layer"],
    )
    md = (
        "# Quant ML Current Structure\n\n"
        "- Source of truth models: `openbb_platform/extensions/quant_ml/openbb_quant_ml/models.py`\n"
        "- Inventory CSV: `docs/architecture/contract_inventory/backend_models.csv`\n"
        "- Responsibility matrix: `docs/architecture/contract_inventory/responsibility_matrix.csv`\n"
    )
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "current_structure.md").write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
