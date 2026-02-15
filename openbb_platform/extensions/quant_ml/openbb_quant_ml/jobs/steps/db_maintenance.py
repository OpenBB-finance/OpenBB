"""Step: database maintenance."""

from __future__ import annotations

import sqlite3
from typing import Any

from openbb_quant_ml.service.macro_constants import MACRO_DB_PATH


def run(config: dict[str, Any]) -> dict[str, Any]:
    if not MACRO_DB_PATH.exists():
        return {"status": "skipped", "message": "macro db not found"}
    conn = sqlite3.connect(MACRO_DB_PATH)
    try:
        conn.execute("VACUUM;")
        conn.commit()
    finally:
        conn.close()
    return {"status": "ok", "db": str(MACRO_DB_PATH)}
