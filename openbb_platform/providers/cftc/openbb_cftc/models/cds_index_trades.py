"""DTCC Public Price Dissemination CDS Index Trades Model."""

from collections.abc import Iterable
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, model_validator

from openbb_cftc.utils.constants import CDS_INDEX_UNDERLIERS

_NUMERIC_FIELDS = frozenset(
    {
        "coupon",
        "coupon_payment_frequency_multiplier",
        "index_factor",
        "notional_amount",
        "spread",
        "upfront_amount",
    }
)


def _upfront_payment(record: dict) -> dict:
    """Resolve a semicolon-joined other-payment list to the upfront that prices the print."""
    from openbb_cftc.utils.swap import parse_other_payments

    payments = parse_other_payments(record)

    if len(payments) < 2:
        return {}

    chosen = next((p for p in payments if p["type"] == "UFRO"), payments[0])

    return {
        "Other payment type": chosen["type"],
        "Other payment amount": repr(chosen["amount"]),
        "Other payment currency": chosen["currency"] or "",
    }


class CftcCdsIndexTradesQueryParams(QueryParams):
    """DTCC Public Price Dissemination CDS Index Trades Query Parameters."""

    index: str | None = Field(
        default=None,
        description="Filter by index family, matched against the UPI Underlier Name."
        + " E.g., 'CDX.NA.IG'. Matching is exact and case-insensitive, because"
        + " 'ITRAXX EUROPE' is a substring of two other index families."
        + " Default is every index.",
        json_schema_extra={
            "x-widget_config": {
                "options": [
                    {"label": underlier, "value": underlier}
                    for underlier in CDS_INDEX_UNDERLIERS
                ]
            }
        },
    )
    date: dateType | None = Field(
        default=None,
        description="Dissemination date (UTC). Default is the most recent date whose"
        + " file holds index prints matching the query; a file is published every"
        + " calendar day, but weekends and holidays carry almost none."
        + " Files are retained for 366 days.",
        json_schema_extra={"x-widget_config": {"value": "$currentDate-1d"}},
    )
    tenor: str | None = Field(
        default=None,
        description="Filter by the print's tenor at execution. E.g., '5Y'."
        + " Default is every tenor.",
        json_schema_extra={
            "x-widget_config": {
                "options": [
                    {"label": label, "value": label}
                    for label in ("1Y", "2Y", "3Y", "5Y", "7Y", "10Y")
                ]
            }
        },
    )
    min_notional: float | None = Field(
        default=None,
        description="Filter out prints whose leg 1 notional is disseminated below this"
        + " amount. A print above the reporting cap is disseminated at the cap, which"
        + " is only a floor on its true size, so a threshold above a cap drops prints"
        + " that may in fact exceed it. Caps vary by index, tenor and currency.",
    )
    limit: int | None = Field(
        default=None,
        description="Number of prints to return. Default is all matching.",
    )
    use_cache: bool = Field(
        default=True,
        description="Cache the daily file locally, revalidating it against the source ETag.",
    )


class CftcCdsIndexTradesData(Data):
    """DTCC Public Price Dissemination CDS Index Trades Data."""

    model_config = ConfigDict(extra="ignore")

    __alias_dict__ = {
        "trade_key": "Trade Key",
        "action_type": "Action type",
        "event_type": "Event type",
        "event_timestamp": "Event timestamp",
        "execution_timestamp": "Execution Timestamp",
        "index": "UPI Underlier Name",
        "upi_fisn": "UPI FISN",
        "unique_product_identifier": "Unique Product Identifier",
        "effective_date": "Effective Date",
        "maturity_date": "Expiration Date",
        "coupon": "Fixed rate-Leg 1",
        "coupon_day_count": "Fixed rate day count convention-leg 1",
        "coupon_payment_frequency": "Fixed rate payment frequency period-Leg 1",
        "coupon_payment_frequency_multiplier": "Fixed rate payment frequency period multiplier-Leg 1",
        "upfront_amount": "Other payment amount",
        "upfront_type": "Other payment type",
        "upfront_currency": "Other payment currency",
        "spread": "Spread-Leg 1",
        "spread_notation": "Spread notation-Leg 1",
        "spread_currency": "Spread currency-Leg 1",
        "index_factor": "Index factor",
        "notional_amount": "Notional amount-Leg 1",
        "notional_currency": "Notional currency-Leg 1",
        "venue": "Platform identifier",
        "cleared": "Cleared",
        "block_trade": "Block trade election indicator",
        "package_trade": "Package indicator",
    }

    dissemination_date: dateType = Field(
        description="Date the SDR publicly disseminated the print, being the report"
        + " date of the file it was published in. The cumulative file carries no"
        + " per-message dissemination timestamp.",
        json_schema_extra={"x-widget_config": {"headerName": "Dissemination Date"}},
    )
    trade_key: str | None = Field(
        default=None,
        description="Asset-class-qualified dissemination identifier, e.g."
        + " 'CR:4411567497000000101'. The qualifier keeps the 19-digit identifier out of"
        + " IEEE-754 double range, which truncates it past its 16th digit.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Trade",
                "cellDataType": "text",
                "formatterFn": "none",
            }
        },
    )
    action_type: str | None = Field(
        default=None,
        description="Type of action taken on the swap transaction: NEWT (new), MODI"
        + " (modify), CORR (correct), EROR (error), TERM (terminate), or REVI (revive).",
        json_schema_extra={
            "x-widget_config": {"headerName": "Action Type", "hide": True}
        },
    )
    event_type: str | None = Field(
        default=None,
        description="Explanation or reason for the action being taken on the swap"
        + " transaction: TRAD (trade), NOVA (novation/step-in), COMP (compression or"
        + " post trade risk reduction exercise), ETRM (early termination), CLRG"
        + " (clearing), EXER (exercise), or CREV (credit event).",
        json_schema_extra={
            "x-widget_config": {"headerName": "Event Type", "hide": True}
        },
    )
    event_timestamp: datetime | None = Field(
        default=None,
        description="Date and time of occurrence of the event, as determined by the"
        + " reporting counterparty or a service provider.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Event Timestamp", "hide": True}
        },
    )
    execution_timestamp: datetime | None = Field(
        default=None,
        description="Date and time the transaction was originally executed, resulting"
        + " in the generation of a new UTI. It remains unchanged throughout the life of"
        + " the UTI, so on a correction or termination it dates the original trade.",
        json_schema_extra={"x-widget_config": {"headerName": "Execution Timestamp"}},
    )
    index: str | None = Field(
        default=None,
        description="Name of the asset or index underlying the product corresponding to"
        + " the UPI. It names the index family only and carries no series number, so"
        + " `maturity_date` is what pins the series.",
        json_schema_extra={"x-widget_config": {"headerName": "Index"}},
    )
    upi_fisn: str | None = Field(
        default=None,
        description="ISO 18774 Financial Instrument Short Name issued by the UPI"
        + " Service Provider. 'NA/CDS Corp Idx Tra' marks a tranche print.",
        json_schema_extra={"x-widget_config": {"headerName": "UPI FISN", "hide": True}},
    )
    unique_product_identifier: str | None = Field(
        default=None,
        description="ISO 4914 Unique Product Identifier (UPI), a unique set of"
        + " characters that represents a particular OTC derivative.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Unique Product Identifier", "hide": True}
        },
    )
    effective_date: dateType | None = Field(
        default=None,
        description="Unadjusted date at which obligations under the transaction come"
        + " into effect. For a credit index this should be the effective date of the"
        + " contract, usually one or two days after execution, and not the roll date of"
        + " the underlying index.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Effective Date", "hide": True}
        },
    )
    maturity_date: dateType | None = Field(
        default=None,
        description="Unadjusted date at which obligations under the transaction stop"
        + " being effective, as included in the confirmation ('Expiration date')."
        + " Early termination does not affect it. Together with `index` it identifies"
        + " the series traded.",
        json_schema_extra={"x-widget_config": {"headerName": "Maturity Date"}},
    )
    tenor: str | None = Field(
        default=None,
        description="Years from `execution_timestamp` to `maturity_date`, snapped to"
        + " the nearest standard CDS index tenor within one year, else the rounded year"
        + " count. Derived, not disseminated.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Tenor",
                "cellDataType": "text",
                "chartDataType": "category",
            }
        },
    )
    coupon: float | None = Field(
        default=None,
        description="Per annum rate of the fixed leg, expressed as a decimal"
        + " (0.05 is 500bp). The index's standardised coupon, and with"
        + " `upfront_amount` the price of the print.",
        json_schema_extra={"x-widget_config": {"headerName": "Coupon"}},
    )
    coupon_day_count: str | None = Field(
        default=None,
        description="ISO 20022 day count convention of the fixed leg. A004 is ACT/360.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Coupon Day Count", "hide": True}
        },
    )
    coupon_payment_frequency: str | None = Field(
        default=None,
        description="Time unit associated with the frequency of fixed leg payments:"
        + " DAIL, WEEK, MNTH, YEAR, ADHO, or EXPI (payment at term).",
        json_schema_extra={
            "x-widget_config": {"headerName": "Coupon Frequency", "hide": True}
        },
    )
    coupon_payment_frequency_multiplier: float | None = Field(
        default=None,
        description="Number of time units of `coupon_payment_frequency` between"
        + " payments. MNTH with a multiplier of 3 is quarterly.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Coupon Frequency Mult.", "hide": True}
        },
    )
    upfront_amount: float | None = Field(
        default=None,
        description="Payment amount corresponding to `upfront_type`, in"
        + " `upfront_currency`. With `coupon` it prices the print.",
        json_schema_extra={"x-widget_config": {"headerName": "Upfront Amount"}},
    )
    upfront_type: str | None = Field(
        default=None,
        description="Type of the other payment amount. UFRO is an upfront payment: the"
        + " initial payment made by one of the counterparties either to bring a"
        + " transaction to fair value or for any other reason that may be the cause of"
        + " an off-market transaction. UWIN is an unwind or full termination payment;"
        + " PEXH is a principal exchange.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Upfront Type", "hide": True}
        },
    )
    upfront_currency: str | None = Field(
        default=None,
        description="Currency in which `upfront_amount` is denominated.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Upfront Currency", "hide": True}
        },
    )
    spread: float | None = Field(
        default=None,
        description="Reported spread on the leg 1 index reference price, as"
        + " disseminated. Conditional: it is required only where `coupon` is not"
        + " populated and `upfront_type` is not 'UFRO', so it is an alternative to the"
        + " coupon-plus-upfront quote rather than the price of the print. Read it"
        + " together with `spread_notation` - the field also carries a price in points"
        + " of par on the price-quoted indices. See the package README.",
        json_schema_extra={"x-widget_config": {"headerName": "Spread"}},
    )
    spread_notation: str | None = Field(
        default=None,
        description="Manner in which `spread` is expressed: 1 (monetary amount, in"
        + " `spread_currency`), 3 (decimal, e.g. 0.0257 for 2.57%), or 4 (basis"
        + " points, e.g. 257 for 2.57%).",
        json_schema_extra={
            "x-widget_config": {"headerName": "Spread Notation", "hide": True}
        },
    )
    spread_currency: str | None = Field(
        default=None,
        description="Currency in which `spread` is denominated. Only applicable when"
        + " `spread_notation` is 1.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Spread Currency", "hide": True}
        },
    )
    index_factor: float | None = Field(
        default=None,
        description="The index version factor or percent, expressed as a decimal value,"
        + " that multiplied by the notional amount yields the notional amount covered"
        + " by the seller of protection. Below 1 once a constituent has defaulted.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Index Factor", "hide": True}
        },
    )
    notional_amount: float | None = Field(
        default=None,
        description="Leg 1 notional amount specified in the contract, gross of any"
        + " version incrementing due to a credit event. Values above the reporting cap"
        + " are disseminated at the cap and flagged by `is_capped`.",
        json_schema_extra={"x-widget_config": {"headerName": "Notional"}},
    )
    notional_currency: str | None = Field(
        default=None,
        description="Currency in which the leg 1 notional amount is denominated.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Notional Currency", "hide": True}
        },
    )
    is_capped: bool | None = Field(
        default=None,
        description="Whether any amount on the print was disseminated at a reporting"
        + " cap rather than its true value. Other disseminated amounts are"
        + " proportionally scaled when the notional is capped.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Is Capped", "hide": True}
        },
    )
    venue: str | None = Field(
        default=None,
        description="ISO 10383 segment MIC of the trading facility the transaction was"
        + " executed on. XOFF marks a transaction in a listed instrument executed off"
        + " venue, XXXX an instrument not listed on any venue, and BILT a reporting"
        + " counterparty that could not determine whether the instrument is listed.",
        json_schema_extra={"x-widget_config": {"headerName": "Venue"}},
    )
    cleared: str | None = Field(
        default=None,
        description="Whether the transaction has been cleared, or is intended to be"
        + " cleared, by a central counterparty: Y (centrally cleared), N (not centrally"
        + " cleared), or I (intent to clear, for original swaps planned to be submitted"
        + " to clearing).",
        json_schema_extra={"x-widget_config": {"headerName": "Cleared"}},
    )
    block_trade: bool | None = Field(
        default=None,
        description="Whether an election has been made to report the transaction as a"
        + " block trade, by the reporting counterparty or as calculated by the SDR on"
        + " its behalf or by a third party.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Block Trade", "hide": True}
        },
    )
    package_trade: bool | None = Field(
        default=None,
        description="Whether the transaction is part of a package transaction, being"
        + " two or more transactions negotiated together as the product of a single"
        + " economic agreement.",
        json_schema_extra={"x-widget_config": {"headerName": "Package", "hide": True}},
    )

    @model_validator(mode="before")
    @classmethod
    def _normalize_values(cls, values):
        """Drop empty strings, strip cap markers and thousands separators."""
        if not isinstance(values, dict):
            return values

        values = {**values, **_upfront_payment(values)}
        alias_to_field = {v: k for k, v in cls.__alias_dict__.items()}
        normalized: dict = {}
        capped = False

        for key, value in values.items():
            if not isinstance(value, str):
                if value is not None:
                    normalized[key] = value
                continue

            text = value.strip()

            if not text:
                continue

            field = alias_to_field.get(key, key)

            if field in _NUMERIC_FIELDS:
                if text.endswith("+"):
                    text = text[:-1]
                    capped = True

                text = text.replace(",", "")

                if not text:
                    continue

            normalized[key] = text

        normalized.setdefault("is_capped", capped)

        return normalized


class CftcCdsIndexTradesFetcher(
    Fetcher[CftcCdsIndexTradesQueryParams, list[CftcCdsIndexTradesData]]
):
    """DTCC Public Price Dissemination CDS Index Trades Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CftcCdsIndexTradesQueryParams:
        """Transform the query params."""
        return CftcCdsIndexTradesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CftcCdsIndexTradesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch one dissemination date's credits file and select its index prints."""
        from openbb_cftc.utils.cds import extract_prints
        from openbb_cftc.utils.dtcc import get_latest_viable_slice, get_slice

        def _select(records: Iterable[dict], report_date: dateType) -> list[dict]:
            return extract_prints(
                records,
                dissemination_date=report_date,
                index=query.index,
                tenor=query.tenor,
                min_notional=query.min_notional,
                limit=query.limit,
            )

        if query.date:
            records = await get_slice(
                "credits", query.date.isoformat(), use_cache=query.use_cache
            )
            prints = _select(records, query.date)

            if not prints:
                raise EmptyDataError(
                    "No CDS index prints matched the query for"
                    f" {query.date.isoformat()}."
                )

            return prints

        records, report_date = await get_latest_viable_slice(
            "credits",
            lambda recs, date: bool(_select(recs, date)),
            use_cache=query.use_cache,
        )

        return _select(records, dateType.fromisoformat(report_date))

    @staticmethod
    def transform_data(
        query: CftcCdsIndexTradesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[CftcCdsIndexTradesData]]:
        """Validate the prints and insert metadata."""
        from openbb_cftc.utils.dtcc import qualified_keys

        results = [
            CftcCdsIndexTradesData.model_validate({**d, **qualified_keys(d)})
            for d in data
        ]

        return AnnotatedResult(
            result=results,
            metadata={
                "dissemination_date": results[0].dissemination_date.isoformat(),
                "prints": len(results),
                "indexes": sorted({r.index for r in results if r.index}),
                "tenors": sorted({r.tenor for r in results if r.tenor}),
                "capped_prints": sum(1 for r in results if r.is_capped),
            },
        )
