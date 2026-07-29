"""DTCC Overnight Index Swap Curve History Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

MAX_CONCURRENT_DOWNLOADS = 4


def _tenor_field(label: str) -> Any:
    """Build a pivot column for one benchmark tenor."""
    return Field(
        default=None,
        description=f"{label} node of the curve, expressed as a decimal."
        + " Returned when pivot is True.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": label,
                "cellDataType": "number",
                "chartDataType": "series",
                "formatterFn": "normalizedPercent",
            },
        },
    )


class CftcOisCurveHistoryQueryParams(QueryParams):
    """DTCC Overnight Index Swap Curve History Query Parameters."""

    __json_schema_extra__ = {
        "currency": {"multiple_items_allowed": False},
        "measure": {"multiple_items_allowed": False},
        "aggregation": {"multiple_items_allowed": False},
        "tenor": {"multiple_items_allowed": True},
        "interpolation": {"multiple_items_allowed": False},
    }

    currency: Literal[
        "USD",
        "EUR",
        "GBP",
        "JPY",
        "CAD",
        "CHF",
        "MXN",
        "SGD",
        "INR",
        "COP",
        "ZAR",
        "CLP",
        "THB",
        "ILS",
        "BRL",
        "AUD",
        "NZD",
        "CNY",
    ] = Field(
        default="USD",
        description="Currency of the swap curve.",
    )
    start_date: dateType | None = Field(
        default=None,
        description="Start date of the history. Default is 30 days before the end date."
        + " Files are retained for 366 days.",
        json_schema_extra={"x-widget_config": {"value": "$currentDate-30d"}},
    )
    end_date: dateType | None = Field(
        default=None,
        description="End date of the history. Default is the most recent date published.",
        json_schema_extra={"x-widget_config": {"value": "$currentDate-1d"}},
    )
    measure: Literal["par_rate", "zero_rate", "discount_factor", "forward_rate"] = (
        Field(
            default="par_rate",
            description="Curve measure to return for each tenor.",
        )
    )
    tenor: str | None = Field(
        default=None,
        description="Filter to specific benchmark tenors. Default is all tenors."
        + " E.g., '2Y,5Y,10Y'.",
    )
    aggregation: Literal["median", "mean", "vwap"] = Field(
        default="median",
        description="How each node's executed rates are reduced to a par rate.",
    )
    min_trades: int = Field(
        default=1,
        description="Drop nodes priced by fewer than this many trades on a given date."
        + " The default keeps every node, because one executed trade is still a price.",
    )
    interpolation: Literal["log_linear", "log_cubic"] = Field(
        default="log_linear",
        description="How discount factors are interpolated between pillars, on the log"
        + " of the discount factor. 'log_linear' is piecewise linear; 'log_cubic' is a"
        + " monotone Hermite cubic giving smooth forwards. Only affects zero_rate,"
        + " discount_factor and forward_rate, not par_rate.",
    )
    pivot: bool = Field(
        default=True,
        description="Return a date-by-tenor table. Set to False for flat, long-form rows.",
    )
    use_cache: bool = Field(
        default=True,
        description="Cache the daily files locally, revalidating against the source ETag.",
    )

    @field_validator("currency", mode="before")
    @classmethod
    def _to_upper(cls, v):
        """Accept a currency in any case."""
        return v.upper() if isinstance(v, str) else v


class CftcOisCurveHistoryData(Data):
    """DTCC Overnight Index Swap Curve History Data."""

    date: dateType = Field(
        description="Report date of the curve.",
        json_schema_extra={"x-widget_config": {"chartDataType": "time"}},
    )
    tenor: str | None = Field(
        default=None,
        description="Tenor of the observation. Returned when pivot is False.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Tenor",
                "cellDataType": "text",
                "chartDataType": "category",
            }
        },
    )
    value: float | None = Field(
        default=None,
        description="Value of the measure at the tenor, expressed as a decimal."
        + " Returned when pivot is False.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Value",
                "cellDataType": "number",
                "chartDataType": "series",
                "formatterFn": "normalizedPercent",
            },
        },
    )
    tenor_1w: float | None = _tenor_field("1W")
    tenor_2w: float | None = _tenor_field("2W")
    tenor_1m: float | None = _tenor_field("1M")
    tenor_2m: float | None = _tenor_field("2M")
    tenor_3m: float | None = _tenor_field("3M")
    tenor_4m: float | None = _tenor_field("4M")
    tenor_6m: float | None = _tenor_field("6M")
    tenor_9m: float | None = _tenor_field("9M")
    tenor_1y: float | None = _tenor_field("1Y")
    tenor_18m: float | None = _tenor_field("18M")
    tenor_2y: float | None = _tenor_field("2Y")
    tenor_3y: float | None = _tenor_field("3Y")
    tenor_4y: float | None = _tenor_field("4Y")
    tenor_5y: float | None = _tenor_field("5Y")
    tenor_6y: float | None = _tenor_field("6Y")
    tenor_7y: float | None = _tenor_field("7Y")
    tenor_8y: float | None = _tenor_field("8Y")
    tenor_9y: float | None = _tenor_field("9Y")
    tenor_10y: float | None = _tenor_field("10Y")
    tenor_12y: float | None = _tenor_field("12Y")
    tenor_15y: float | None = _tenor_field("15Y")
    tenor_20y: float | None = _tenor_field("20Y")
    tenor_25y: float | None = _tenor_field("25Y")
    tenor_30y: float | None = _tenor_field("30Y")
    tenor_40y: float | None = _tenor_field("40Y")
    tenor_50y: float | None = _tenor_field("50Y")


class CftcOisCurveHistoryFetcher(
    Fetcher[CftcOisCurveHistoryQueryParams, list[CftcOisCurveHistoryData]]
):
    """DTCC Overnight Index Swap Curve History Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CftcOisCurveHistoryQueryParams:
        """Transform the query params."""
        return CftcOisCurveHistoryQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CftcOisCurveHistoryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Build a curve for every published date in the range."""
        import asyncio
        from datetime import timedelta

        from openbb_cftc.utils.cfets import cny_curve_records
        from openbb_cftc.utils.constants import curve_fisn
        from openbb_cftc.utils.curve import build_curve
        from openbb_cftc.utils.dtcc import get_available_dates, get_slice
        from openbb_cftc.utils.store import RecordChain

        available = await get_available_dates("rates")

        if not available:
            raise EmptyDataError("No PPD interest-rate files are currently published.")

        end_date = query.end_date or dateType.fromisoformat(available[-1])
        start_date = query.start_date or (end_date - timedelta(days=30))
        targets = [
            d for d in available if start_date <= dateType.fromisoformat(d) <= end_date
        ]

        if not targets:
            raise EmptyDataError(
                f"No PPD files were published between {start_date} and {end_date}."
            )

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

        async def _one(report_date: str) -> list[dict]:
            async with semaphore:
                try:
                    records = await get_slice(
                        "rates", report_date, use_cache=query.use_cache
                    )

                    if query.currency == "CNY":
                        extra = await cny_curve_records(
                            dateType.fromisoformat(report_date),
                            use_cache=query.use_cache,
                        )

                        if extra:
                            records = RecordChain(records, extra)

                    return build_curve(
                        records,
                        trade_date=dateType.fromisoformat(report_date),
                        fisn=curve_fisn(query.currency),
                        currency=query.currency,
                        granularity="benchmark",
                        aggregation=query.aggregation,
                        min_trades=query.min_trades,
                        interpolation=query.interpolation,
                        use_cache=query.use_cache,
                    )
                except EmptyDataError:
                    return []

        curves = await asyncio.gather(*[_one(d) for d in targets])
        nodes = [node for curve in curves for node in curve]

        if not nodes:
            raise EmptyDataError(
                f"No {query.currency} curve nodes could be built between"
                f" {start_date} and {end_date}."
            )

        return nodes

    @staticmethod
    def transform_data(
        query: CftcOisCurveHistoryQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[CftcOisCurveHistoryData]]:
        """Reduce the nodes to the requested measure, pivoting when asked."""
        from openbb_cftc.utils.constants import BENCHMARK_TENORS, curve_spec

        wanted: set[str] | None = None

        if query.tenor:
            wanted = {t.strip().upper() for t in query.tenor.split(",") if t.strip()}

        order = [label for label, _ in BENCHMARK_TENORS]
        rows: list[dict] = []

        if query.pivot:
            by_date: dict[dateType, dict] = {}

            for node in data:
                label = node["tenor"]

                if wanted and label.upper() not in wanted:
                    continue

                slot = by_date.setdefault(node["date"], {"date": node["date"]})
                slot[f"tenor_{label.lower()}"] = node.get(query.measure)

            rows = [by_date[key] for key in sorted(by_date)]
        else:
            for node in sorted(
                data,
                key=lambda n: (
                    n["date"],
                    order.index(n["tenor"]) if n["tenor"] in order else len(order),
                ),
            ):
                label = node["tenor"]

                if wanted and label.upper() not in wanted:
                    continue

                rows.append(
                    {
                        "date": node["date"],
                        "tenor": label,
                        "value": node.get(query.measure),
                    }
                )

        if not rows:
            raise EmptyDataError(
                f"No curve nodes matched the requested tenors: {query.tenor}."
            )

        return AnnotatedResult(
            result=[CftcOisCurveHistoryData.model_validate(r) for r in rows],
            metadata={
                "currency": query.currency,
                "index": curve_spec(query.currency)["index"],
                "measure": query.measure,
                "dates": len({node["date"] for node in data}),
                "pivot": query.pivot,
            },
        )
