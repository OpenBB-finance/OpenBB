"""Tests for pricing vehicle one-company-one-line rules."""

from __future__ import annotations

from datetime import date

import pandas as pd

from openbb_quant_ml.service.pricing_vehicle import select_pricing_vehicle


def test_select_pricing_vehicle_keeps_one_line_per_company() -> None:
    frame = pd.DataFrame(
        [
            {"symbol": "BRK.A", "company_id": "BRK", "two_year_dollar_volume": 10.0, "adv20_usd": 5.0},
            {"symbol": "BRK.B", "company_id": "BRK", "two_year_dollar_volume": 50.0, "adv20_usd": 6.0},
            {"symbol": "AAPL", "company_id": "AAPL", "two_year_dollar_volume": 60.0, "adv20_usd": 9.0},
        ]
    )
    excluded: list[dict[str, object]] = []
    out = select_pricing_vehicle(frame, as_of_date=date(2026, 2, 21), excluded=excluded)
    assert out.groupby("company_id")["symbol"].nunique().max() == 1
    assert "BRK.B" in set(out["symbol"])
    assert any("duplicate_company_non_primary_line" in row.get("reasons", []) for row in excluded)

