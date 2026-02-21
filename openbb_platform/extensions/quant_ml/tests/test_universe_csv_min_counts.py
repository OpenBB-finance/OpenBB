"""Guardrail test for committed universe CSV minimum counts."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
from openbb_quant_ml.service.universe import UNIVERSE_ALIASES, UNIVERSE_MINIMUM_COUNTS
from openbb_quant_ml.service.universe_builder import UNIVERSE_INPUT_DIR


def _read_symbols(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        next(reader, None)
        return [str(row[0]).strip() for row in reader if row and str(row[0]).strip()]


@pytest.mark.parametrize("universe_id,minimum", sorted(UNIVERSE_MINIMUM_COUNTS.items()))
def test_universe_csv_meets_minimum_count(universe_id: str, minimum: int):
    resolved_universe_id = UNIVERSE_ALIASES.get(universe_id, universe_id)
    path = Path(UNIVERSE_INPUT_DIR) / f"{resolved_universe_id}.csv"
    assert path.exists(), f"missing universe csv: {path}"

    symbols = {symbol.upper() for symbol in _read_symbols(path)}
    assert len(symbols) >= int(minimum), (
        f"undersized universe csv: {universe_id}; "
        f"actual_count={len(symbols)}; minimum_required={minimum}"
    )
