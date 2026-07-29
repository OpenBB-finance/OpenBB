"""DTCC Swap Summary Model."""

from typing import Any

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_cftc.models.swap_valuation import (
    CftcSwapValuationFetcher,
    CftcSwapValuationQueryParams,
)


class CftcSwapSummaryQueryParams(CftcSwapValuationQueryParams):
    """DTCC Swap Summary Query Parameters."""


class CftcSwapSummaryData(Data):
    """DTCC Swap Summary Data."""

    metric: str = Field(
        description="Name of the summary metric.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Metric",
                "cellDataType": "text",
                "formatterFn": "none",
            }
        },
    )
    value: str = Field(
        description="Value of the summary metric, formatted in its own unit.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Value",
                "cellDataType": "text",
                "formatterFn": "none",
            }
        },
    )
    detail: str | None = Field(
        default=None,
        description="Context the metric carries beyond its value.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Detail",
                "cellDataType": "text",
                "formatterFn": "none",
            }
        },
    )


def _money(amount: float, currency: str | None) -> str:
    """Format a monetary amount in its currency."""
    text = f"{amount:,.2f}"

    return f"{text} {currency}" if currency else text


def _rate(value: float) -> str:
    """Format a rate in percent."""
    return f"{value:.4f} %"


def _payment_totals(payments: list[dict], kind: str) -> str | None:
    """Total a payment type per currency, joined for display."""
    totals: dict[str, float] = {}

    for payment in payments:
        if payment["type"] == kind:
            key = payment["currency"] or ""
            totals[key] = totals.get(key, 0.0) + payment["amount"]

    if not totals:
        return None

    return "; ".join(_money(amount, ccy or None) for ccy, amount in totals.items())


def carry_rows(metadata: dict, currency: str | None) -> list[dict]:
    """Split elapsed carry into what has settled and what is still accruing."""
    note = metadata.get("carry_note")
    settled = metadata.get("settled_carry")
    accrued = metadata.get("accrued_carry")

    return [
        {
            "metric": "Settled Carry",
            "value": _money(settled, currency)
            if settled is not None
            else "unavailable",
            "detail": note or "coupons whose payment date has passed",
        },
        {
            "metric": "Accrued Carry",
            "value": _money(accrued, currency)
            if accrued is not None
            else "unavailable",
            "detail": note or "earned since the last payment, not yet settled",
        },
    ]


def _summary_rows(metadata: dict, side: str) -> list[dict]:
    """Build the summary's metric rows from the valuation's own metadata."""
    currency = metadata.get("currency")
    is_inflation = metadata.get("trade_type") == "inflation"
    is_spread = metadata.get("trade_type") in ("basis", "cross_currency")
    rows: list[dict] = [
        {
            "metric": "Trade",
            "value": str(
                metadata.get("trade_key")
                or metadata.get("dissemination_identifier")
                or ""
            ),
            "detail": f"disseminated {metadata.get('trade_date')}",
        },
        {
            "metric": "Product",
            "value": str(metadata.get("upi_fisn") or ""),
            "detail": metadata.get("underlier"),
        },
        {
            "metric": "Term",
            "value": f"{metadata.get('effective_date')} to"
            f" {metadata.get('expiration_date')}",
            "detail": None,
        },
        {
            "metric": "Notional",
            "value": _money(metadata.get("notional") or 0.0, currency),
            "detail": (
                "reported at the Part 43 cap"
                if metadata.get("notional_capped")
                else None
            ),
        },
    ]

    cleared = metadata.get("cleared")

    if cleared:
        rows.append(
            {
                "metric": "Cleared",
                "value": str(cleared),
                "detail": {
                    "Y": "cleared",
                    "I": "intent to clear",
                    "N": "bilateral",
                }.get(str(cleared)),
            }
        )

    if is_inflation:
        label = "Traded Breakeven"
    elif is_spread:
        label = "Traded Spread"
    else:
        label = "Fixed Rate"

    rows.append(
        {
            "metric": label,
            "value": _rate(metadata.get("fixed_rate") or 0.0),
            "detail": None,
        }
    )
    rows.append(
        {
            "metric": "Breakeven (Now)" if is_inflation else "Par Rate (Now)",
            "value": _rate(metadata.get("par_rate") or 0.0),
            "detail": f"breakevens {metadata.get('breakeven_date')}"
            if is_inflation
            else f"curve {metadata.get('curve_date')}",
        }
    )

    if is_inflation:
        rows.append(
            {
                "metric": "Index",
                "value": str(metadata.get("underlier") or ""),
                "detail": metadata.get("inflation_index"),
            }
        )
        rows.append(
            {
                "metric": "Index Ratio",
                "value": f"{metadata.get('index_ratio') or 0.0:,.6f}",
                "detail": "reference index at maturity over the base index",
            }
        )
        realized = metadata.get("realized_ratio")
        rows.append(
            {
                "metric": "Realized Ratio",
                "value": f"{realized:,.6f}" if realized is not None else "not started",
                "detail": f"{metadata.get('elapsed_years')} years elapsed",
            }
        )
        rows.append(
            {
                "metric": "Projected Ratio",
                "value": f"{metadata.get('projected_ratio') or 0.0:,.6f}",
                "detail": f"{metadata.get('remaining_years')} years at"
                f" {_rate(metadata.get('forward_breakeven') or 0.0)}",
            }
        )

    if metadata.get("spot") is not None:
        rows.append(
            {
                "metric": "Spot",
                "value": f"{metadata['spot']:,.6f}",
                "detail": f"{metadata.get('other_currency')}/{currency}",
            }
        )

    rows.append(
        {
            "metric": "Swap NPV (Now)",
            "value": _money(metadata.get("npv") or 0.0, currency),
            "detail": f"signed to {side}",
        }
    )

    if metadata.get("exchange_pv") is not None:
        rows.append(
            {
                "metric": "Exchange PV",
                "value": _money(metadata["exchange_pv"], currency),
                "detail": "terminal notional exchange",
            }
        )

    rows.extend(carry_rows(metadata, currency))

    payments = metadata.get("other_payments") or []

    if metadata.get("upfront_amount") is not None:
        rows.append(
            {
                "metric": "Upfront Payment (UFRO)",
                "value": _money(metadata["upfront_amount"], currency),
                "detail": f"entry cost {_money(metadata['entry_cost'], currency)},"
                f" signed to {side}",
            }
        )

    exchanges = _payment_totals(payments, "PEXH")

    if exchanges:
        rows.append(
            {
                "metric": "Principal Exchanges (PEXH)",
                "value": exchanges,
                "detail": None,
            }
        )

    unwinds = _payment_totals(payments, "UWIN")

    if unwinds:
        rows.append(
            {
                "metric": "Unwind Payments (UWIN)",
                "value": unwinds,
                "detail": None,
            }
        )

    if metadata.get("package_price") is not None:
        rows.append(
            {
                "metric": "Package Price",
                "value": _money(
                    metadata["package_price"], metadata.get("package_price_currency")
                ),
                "detail": "as disseminated for the package",
            }
        )
    elif metadata.get("package_indicator"):
        rows.append(
            {
                "metric": "Package",
                "value": "yes",
                "detail": "part of a package transaction",
            }
        )

    note = metadata.get("other_payment_note")

    if note:
        rows.append({"metric": "Other Payments", "value": "see note", "detail": note})

    rows.append(
        {
            "metric": "Net P&L (Now)",
            "value": _money(metadata.get("net_pnl") or 0.0, currency),
            "detail": "NPV + settled and accrued carry - entry cost",
        }
    )
    rows.append(
        {
            "metric": "Winning Side (Now)",
            "value": str(metadata.get("winning_side") or ""),
            "detail": None,
        }
    )

    return rows


async def _fx_metadata(query: CftcSwapSummaryQueryParams, record: dict) -> dict:
    """Value an FX print against the forex and rates slices of its own session."""
    from datetime import date as dateType

    from openbb_core.provider.utils.errors import EmptyDataError

    from openbb_cftc.utils.dtcc import get_slice
    from openbb_cftc.utils.fx_valuation import value_fx_trade
    from openbb_cftc.utils.swap import record_disseminated_day

    day = record_disseminated_day(record)

    if day is None:
        raise EmptyDataError(
            f"'{query.dissemination_identifier}' carries no dissemination date."
        )

    forex = await get_slice("forex", day, use_cache=query.use_cache)
    rates = await get_slice("rates", day, use_cache=query.use_cache)
    valued = value_fx_trade(
        record,
        forex,
        rates,
        dateType.fromisoformat(day),
        min_notional=query.min_notional,
        min_trades=query.min_trades,
    )

    if valued is None:
        raise EmptyDataError(
            f"'{query.dissemination_identifier}' has no priceable FX terms against"
            + f" the {day} tape."
        )

    return {**valued, "trade_date": day, "curve_date": day}


def _fx_summary_rows(metadata: dict, side: str) -> list[dict]:
    """Build an FX print's metric rows from its own valuation."""
    quote = metadata.get("quote")
    sign = 1.0 if side == "pay" else -1.0
    rows = [
        {
            "metric": "Trade",
            "value": str(
                metadata.get("trade_key")
                or metadata.get("dissemination_identifier")
                or ""
            ),
            "detail": f"disseminated {metadata.get('trade_date')}",
        },
        {
            "metric": "Product",
            "value": str(metadata.get("upi_fisn") or ""),
            "detail": metadata.get("product"),
        },
        {
            "metric": "Term",
            "value": f"{metadata.get('effective_date')} to"
            f" {metadata.get('expiration_date')}",
            "detail": f"{metadata.get('days')} days remaining",
        },
        {
            "metric": "Notional",
            "value": _money(metadata.get("notional") or 0.0, metadata.get("base")),
            "detail": metadata.get("pair"),
        },
        {
            "metric": "Traded Rate",
            "value": f"{metadata.get('traded_rate') or metadata.get('strike') or 0.0:,.6f}",
            "detail": f"{quote} per {metadata.get('base')}",
        },
        {
            "metric": "Spot (Now)",
            "value": f"{metadata.get('spot') or 0.0:,.6f}",
            "detail": f"curve {metadata.get('curve_date')}",
        },
        {
            "metric": "Forward (Now)",
            "value": f"{metadata.get('market_rate') or 0.0:,.6f}",
            "detail": "at the trade's remaining tenor",
        },
    ]

    if metadata.get("implied_vol") is not None:
        rows.append(
            {
                "metric": "Implied Volatility",
                "value": f"{100.0 * metadata['implied_vol']:.2f} %",
                "detail": "from the day's prints of the same option family",
            }
        )
        rows.append(
            {
                "metric": "Premium Paid",
                "value": _money(metadata.get("premium") or 0.0, quote),
                "detail": "entry cost",
            }
        )

    npv = sign * (metadata.get("npv") or 0.0)
    rows.append(
        {
            "metric": "NPV (Now)",
            "value": _money(npv, quote),
            "detail": f"signed to the {'long' if side == 'pay' else 'short'}"
            f" {metadata.get('base')} side",
        }
    )
    rows.append(
        {
            "metric": "Winning Side",
            "value": (
                f"long {metadata.get('base')}"
                if (metadata.get("npv") or 0.0) > 0
                else f"short {metadata.get('base')}"
                if (metadata.get("npv") or 0.0) < 0
                else "flat"
            ),
            "detail": "against the session's forward curve",
        }
    )

    return rows


class CftcSwapSummaryFetcher(
    Fetcher[CftcSwapSummaryQueryParams, list[CftcSwapSummaryData]]
):
    """DTCC Swap Summary Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CftcSwapSummaryQueryParams:
        """Transform the query params."""
        return CftcSwapSummaryQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CftcSwapSummaryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> tuple:
        """Fetch through the valuation the print's own asset class is priced by."""
        from openbb_cftc.utils import store
        from openbb_cftc.utils.fx_valuation import classify_fx_trade

        record = (
            store.get_trade_record(query.dissemination_identifier)
            if query.dissemination_identifier
            else None
        )

        if record is not None and classify_fx_trade(record) is not None:
            return ("fx", await _fx_metadata(query, record))

        return await CftcSwapValuationFetcher.aextract_data(query, credentials)

    @staticmethod
    def transform_data(
        query: CftcSwapSummaryQueryParams,
        data: tuple,
        **kwargs: Any,
    ) -> AnnotatedResult[list[CftcSwapSummaryData]]:
        """Summarize the valuation's own metadata into metric rows."""
        if isinstance(data, tuple) and len(data) == 2 and data[0] == "fx":
            metadata = data[1]

            return AnnotatedResult(
                result=[
                    CftcSwapSummaryData.model_validate(row)
                    for row in _fx_summary_rows(metadata, query.side)
                ],
                metadata=metadata,
            )

        valued = CftcSwapValuationFetcher.transform_data(query, data)
        metadata = valued.metadata or {}

        return AnnotatedResult(
            result=[
                CftcSwapSummaryData.model_validate(row)
                for row in _summary_rows(metadata, query.side)
            ],
            metadata=metadata,
        )
