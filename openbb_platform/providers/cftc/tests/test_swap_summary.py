import asyncio

from openbb_core.provider.abstract.annotated_result import AnnotatedResult

from openbb_cftc.models.swap_summary import (
    CftcSwapSummaryData,
    CftcSwapSummaryFetcher,
    CftcSwapSummaryQueryParams,
    _money,
    _payment_totals,
    _rate,
    _summary_rows,
)


def test_transform_query_accepts_valuation_params():
    query = CftcSwapSummaryFetcher.transform_query(
        {"currency": "usd", "dissemination_identifier": "4391821108000000101"}
    )

    assert isinstance(query, CftcSwapSummaryQueryParams)
    assert query.currency == "USD"
    assert query.dissemination_identifier == "4391821108000000101"


def test_money_and_rate_formatting():
    assert _money(1234567.891, "USD") == "1,234,567.89 USD"
    assert _money(-3184.04, None) == "-3,184.04"
    assert _rate(4.335811) == "4.3358 %"


def test_payment_totals_sums_per_currency():
    payments = [
        {"type": "PEXH", "amount": 100.0, "currency": "USD"},
        {"type": "PEXH", "amount": 50.0, "currency": "EUR"},
        {"type": "PEXH", "amount": 25.0, "currency": "USD"},
        {"type": "UFRO", "amount": 9.0, "currency": "USD"},
    ]

    assert _payment_totals(payments, "PEXH") == "125.00 USD; 50.00 EUR"
    assert _payment_totals(payments, "UWIN") is None


FULL_METADATA = {
    "dissemination_identifier": "4391821108000000101",
    "trade_date": "2026-07-24",
    "upi_fisn": "NA/Swap Flt Flt EUR USD",
    "underlier": "EUR USD",
    "trade_type": "cross_currency",
    "currency": "EUR",
    "curve_date": "2026-07-24",
    "effective_date": "2024-06-20",
    "expiration_date": "2034-06-20",
    "notional": 483090000.0,
    "notional_capped": True,
    "cleared": "N",
    "fixed_rate": -0.0025,
    "par_rate": 0.0409,
    "spot": 1.145652,
    "other_currency": "USD",
    "npv": 53262.83,
    "exchange_pv": -1200.5,
    "settled_carry": 0.0,
    "accrued_carry": 210.4,
    "upfront_amount": 631228.0,
    "entry_cost": 631228.0,
    "other_payments": [
        {"type": "UFRO", "amount": 631228.0, "currency": "EUR"},
        {"type": "PEXH", "amount": 549997965.0, "currency": "USD"},
        {"type": "PEXH", "amount": 483090000.0, "currency": "EUR"},
        {"type": "UWIN", "amount": 12873.64, "currency": "EUR"},
    ],
    "package_price": -1311809.0,
    "package_price_currency": "USD",
    "other_payment_note": "note text",
    "net_pnl": -577754.77,
    "winning_side": "receive",
}


def test_summary_rows_cover_a_fully_disseminated_print():
    rows = {row["metric"]: row for row in _summary_rows(FULL_METADATA, "pay")}

    assert rows["Trade"]["value"] == "4391821108000000101"
    assert rows["Trade"]["detail"] == "disseminated 2026-07-24"
    assert rows["Product"]["detail"] == "EUR USD"
    assert rows["Notional"]["detail"] == "reported at the Part 43 cap"
    assert rows["Cleared"]["detail"] == "bilateral"
    assert rows["Traded Spread"]["value"] == "-0.0025 %"
    assert rows["Par Rate (Now)"]["detail"] == "curve 2026-07-24"
    assert rows["Spot"]["detail"] == "USD/EUR"
    assert rows["Swap NPV (Now)"]["value"] == "53,262.83 EUR"
    assert rows["Exchange PV"]["value"] == "-1,200.50 EUR"
    assert rows["Accrued Carry"]["value"] == "210.40 EUR"
    assert rows["Upfront Payment (UFRO)"]["value"] == "631,228.00 EUR"
    assert "entry cost 631,228.00 EUR" in rows["Upfront Payment (UFRO)"]["detail"]
    assert (
        rows["Principal Exchanges (PEXH)"]["value"]
        == "549,997,965.00 USD; 483,090,000.00 EUR"
    )
    assert rows["Unwind Payments (UWIN)"]["value"] == "12,873.64 EUR"
    assert rows["Package Price"]["value"] == "-1,311,809.00 USD"
    assert rows["Other Payments"]["detail"] == "note text"
    assert rows["Net P&L (Now)"]["value"] == "-577,754.77 EUR"
    assert rows["Winning Side (Now)"]["value"] == "receive"


def test_summary_rows_cover_a_plain_print():
    metadata = {
        "dissemination_identifier": "4391757227000000301",
        "trade_date": "2026-07-24",
        "upi_fisn": "NA/Swap OIS USD",
        "currency": "USD",
        "curve_date": "2026-07-24",
        "effective_date": "2024-06-20",
        "expiration_date": "2054-06-20",
        "notional": 100000.0,
        "notional_capped": False,
        "fixed_rate": 3.5,
        "par_rate": 4.405543,
        "npv": -3184.04,
        "settled_carry": None,
        "accrued_carry": None,
        "carry_note": "fixings unavailable",
        "package_indicator": True,
        "net_pnl": -3184.04,
        "winning_side": "receive",
    }
    rows = {row["metric"]: row for row in _summary_rows(metadata, "receive")}

    assert "Cleared" not in rows
    assert rows["Fixed Rate"]["value"] == "3.5000 %"
    assert rows["Notional"]["detail"] is None
    assert "Spot" not in rows
    assert "Exchange PV" not in rows
    assert rows["Accrued Carry"]["value"] == "unavailable"
    assert rows["Accrued Carry"]["detail"] == "fixings unavailable"
    assert "Upfront Payment (UFRO)" not in rows
    assert "Principal Exchanges (PEXH)" not in rows
    assert "Unwind Payments (UWIN)" not in rows
    assert "Package Price" not in rows
    assert rows["Package"]["value"] == "yes"
    assert "Other Payments" not in rows
    assert rows["Winning Side (Now)"]["value"] == "receive"


def test_aextract_delegates_to_the_valuation(monkeypatch):
    sentinel = ({"trade": 1}, [], "2026-07-24", {}, "USD", "2026-07-24")

    async def _extract(query, credentials, **kwargs):
        return sentinel

    monkeypatch.setattr(
        "openbb_cftc.models.swap_valuation.CftcSwapValuationFetcher.aextract_data",
        _extract,
    )

    result = asyncio.run(
        CftcSwapSummaryFetcher.aextract_data(CftcSwapSummaryQueryParams(), None)
    )

    assert result is sentinel


def test_transform_data_summarizes_the_valuation_metadata(monkeypatch):
    metadata = {
        "dissemination_identifier": "4391821108000000101",
        "trade_date": "2026-07-24",
        "upi_fisn": "NA/Swap OIS USD",
        "currency": "USD",
        "curve_date": "2026-07-24",
        "effective_date": "2026-07-24",
        "expiration_date": "2036-07-24",
        "notional": 17000000.0,
        "fixed_rate": 3.845,
        "par_rate": 4.335811,
        "npv": 627326.31,
        "settled_carry": 0.0,
        "accrued_carry": 0.0,
        "net_pnl": -3901.69,
        "winning_side": "receive",
    }

    def _transform(query, data, **kwargs):
        return AnnotatedResult(result=[], metadata=metadata)

    monkeypatch.setattr(
        "openbb_cftc.models.swap_valuation.CftcSwapValuationFetcher.transform_data",
        _transform,
    )

    result = CftcSwapSummaryFetcher.transform_data(
        CftcSwapSummaryQueryParams(side="pay"), ()
    )

    assert result.metadata == metadata
    assert all(isinstance(row, CftcSwapSummaryData) for row in result.result)
    values = {row.metric: row.value for row in result.result}
    assert values["Net P&L (Now)"] == "-3,901.69 USD"
    assert values["Winning Side (Now)"] == "receive"


INFLATION_METADATA = {
    "dissemination_identifier": "4198622606000001901",
    "trade_date": "2026-07-15",
    "upi_fisn": "NA/Swap Infl Idx GBP",
    "underlier": "UK-RPI",
    "trade_type": "inflation",
    "inflation_index": "UKRPI",
    "currency": "GBP",
    "curve_date": "2026-07-15",
    "effective_date": "2026-06-15",
    "expiration_date": "2035-06-15",
    "notional": 126981500.0,
    "notional_capped": True,
    "cleared": "I",
    "fixed_rate": 3.159882,
    "par_rate": 3.159194,
    "forward_breakeven": 3.159882,
    "index_ratio": 1.32326085,
    "realized_ratio": 1.0025,
    "projected_ratio": 1.31996095,
    "elapsed_years": 0.0822,
    "remaining_years": 8.9233,
    "npv": -6793.28,
    "settled_carry": None,
    "accrued_carry": None,
    "net_pnl": -6793.28,
    "winning_side": "receive",
}


def test_summary_rows_cover_an_inflation_print():
    rows = {row["metric"]: row for row in _summary_rows(INFLATION_METADATA, "pay")}

    assert rows["Traded Breakeven"]["value"] == "3.1599 %"
    assert rows["Breakeven (Now)"]["value"] == "3.1592 %"
    assert "Par Rate (Now)" not in rows
    assert "Fixed Rate" not in rows
    assert rows["Index"]["value"] == "UK-RPI"
    assert rows["Index"]["detail"] == "UKRPI"
    assert rows["Index Ratio"]["value"] == "1.323261"
    assert rows["Realized Ratio"]["value"] == "1.002500"
    assert rows["Realized Ratio"]["detail"] == "0.0822 years elapsed"
    assert rows["Projected Ratio"]["value"] == "1.319961"
    assert "8.9233 years at 3.1599 %" in rows["Projected Ratio"]["detail"]
    assert rows["Net P&L (Now)"]["value"] == "-6,793.28 GBP"


def test_summary_rows_report_an_unstarted_inflation_print():
    metadata = {**INFLATION_METADATA, "realized_ratio": None, "elapsed_years": 0.0}
    rows = {row["metric"]: row for row in _summary_rows(metadata, "pay")}

    assert rows["Realized Ratio"]["value"] == "not started"
