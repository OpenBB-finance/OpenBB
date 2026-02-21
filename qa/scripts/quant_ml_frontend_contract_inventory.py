"""Generate frontend contract inventory from `desktop/src/types/quant.ts`."""

from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TYPES_PATH = ROOT / "desktop" / "src" / "types" / "quant.ts"
OUT_PATH = ROOT / "docs" / "architecture" / "contract_inventory" / "frontend_types.csv"

INTERFACE_RE = re.compile(
    r"export interface\s+(?P<name>[A-Za-z0-9_]+)\s*\{(?P<body>.*?)\n\}",
    flags=re.DOTALL,
)
FIELD_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9_]+)\??:\s*(?P<type>[^;]+);", flags=re.MULTILINE
)


def _hash_file(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> None:
    source = TYPES_PATH.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []
    for match in INTERFACE_RE.finditer(source):
        iface = match.group("name")
        body = match.group("body")
        for field in FIELD_RE.finditer(body):
            rows.append(
                {
                    "interface": iface,
                    "field_name": field.group("name"),
                    "type": field.group("type").strip(),
                    "unit": "",
                    "shape": "scalar",
                    "index_format": "",
                    "nullable": "true" if "?" in field.group(0) else "false",
                    "owner_layer": "frontend",
                    "compute_responsibility": "client_render_only",
                }
            )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "interface",
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
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    sig_path = (
        ROOT / "docs" / "architecture" / "contract_inventory" / "frontend_signature.csv"
    )
    with sig_path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=["artifact", "signature_hash"])
        writer.writeheader()
        writer.writerow(
            {"artifact": str(TYPES_PATH), "signature_hash": _hash_file(TYPES_PATH)}
        )


if __name__ == "__main__":
    main()
