"""BLS Series Model."""

from datetime import date as dateType
from typing import Any
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.bls_series import (
    SeriesData,
    SeriesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

from openbb_bls.utils.constants import SURVEY_CATEGORIES, SURVEY_CATEGORY_NAMES

_API_PREFIX = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)

# Keep the change columns in the table but out of the chart so the value series
# (an index level) isn't plotted on the same axis as small percent changes.
_EXCLUDED_NUM: dict[str, Any] = {
    "x-widget_config": {"cellDataType": "number", "chartDataType": "excluded"}
}
_EXCLUDED_PCT: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-frontend_multiply": 100,
    "x-widget_config": {
        "cellDataType": "number",
        "chartDataType": "excluded",
        "formatterFn": "percent",
    },
}


def _earliest_begin_year(symbols: list[str], category: str | None) -> int | None:
    """Earliest ``begin_year`` among ``symbols`` in ``category``'s metadata.

    Lets a request with no ``start_date`` default to each series' full published
    history rather than an arbitrary fixed window. Returns ``None`` when the
    category / symbols can't be resolved so the caller can fall back.
    """
    if not category or not symbols:
        return None
    from openbb_bls.utils.metadata import BlsMetadata

    try:
        df = BlsMetadata().get_series(category)
    except (KeyError, FileNotFoundError, OSError):
        return None
    if "begin_year" not in df.columns:
        return None
    matched = df[df["series_id"].isin(set(symbols))]
    years = [int(y) for y in matched["begin_year"].tolist() if str(y).strip().isdigit()]
    return min(years) if years else None


class BlsSeriesQueryParams(SeriesQueryParams):
    """BLS Series Query Parameters."""

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{_API_PREFIX}/bls/series/symbol_choices",
                "optionsParams": {"category": "$category"},
                "style": {"popupWidth": 950},
            },
        },
        "category": {
            "x-widget_config": {
                "options": [
                    {"label": name, "value": code}
                    for code, name in SURVEY_CATEGORY_NAMES.items()
                ],
            },
        },
    }

    category: SURVEY_CATEGORIES = Field(
        default="cpi",
        description="Survey category that scopes the symbol picker's choices."
        " Does not filter the returned data (series are fetched by symbol);"
        " keep it in sync with the Search widget to drill down by clicking.",
    )
    calculations: bool = Field(
        default=True,
        description="Include calculations in the response, if available. Default is True.",
    )
    annual_average: bool = Field(
        default=False,
        description="Include annual averages in the response, if available. Default is False.",
    )
    aspects: bool = Field(
        default=False,
        description="Include all aspects associated with a data point for a given BLS series ID, if available."
        + " Returned with the series metadata, under `extras` of the response object. Default is False.",
    )


class BlsSeriesData(SeriesData):
    """BLS Series Data — column config tuned for line-charting value over time."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                # Table renders, with a line chart of the value over time one
                # click away (and active by default on the dashboard instance).
                "table": {
                    "showAll": True,
                    "enableCharts": True,
                    "chartView": {"enabled": True, "chartType": "line"},
                },
            }
        }
    )

    date: dateType = Field(
        description="Observation date.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Date", "chartDataType": "time"}
        },
    )
    symbol: str = Field(
        description="BLS series identifier.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Symbol", "chartDataType": "category"}
        },
    )
    value: float | None = Field(
        default=None,
        description="Observation value for the symbol and date.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Value",
                "cellDataType": "number",
                "chartDataType": "series",
            }
        },
    )
    change_1M: float | None = Field(
        default=None,
        description="One month change in value.",
        json_schema_extra=_EXCLUDED_NUM,
    )
    change_3M: float | None = Field(
        default=None,
        description="Three month change in value.",
        json_schema_extra=_EXCLUDED_NUM,
    )
    change_6M: float | None = Field(
        default=None,
        description="Six month change in value.",
        json_schema_extra=_EXCLUDED_NUM,
    )
    change_12M: float | None = Field(
        default=None,
        description="One year change in value.",
        json_schema_extra=_EXCLUDED_NUM,
    )
    change_percent_1M: float | None = Field(
        default=None,
        description="One month change in percent.",
        json_schema_extra=_EXCLUDED_PCT,
    )
    change_percent_3M: float | None = Field(
        default=None,
        description="Three month change in percent.",
        json_schema_extra=_EXCLUDED_PCT,
    )
    change_percent_6M: float | None = Field(
        default=None,
        description="Six month change in percent.",
        json_schema_extra=_EXCLUDED_PCT,
    )
    change_percent_12M: float | None = Field(
        default=None,
        description="One year change in percent.",
        json_schema_extra=_EXCLUDED_PCT,
    )
    latest: bool | None = Field(
        default=None,
        description="Latest value indicator.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    footnotes: str | None = Field(
        default=None,
        description="Footnotes accompanying the value.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )


class BlsSeriesFetcher(Fetcher[BlsSeriesQueryParams, list[BlsSeriesData]]):
    """BLS Series Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BlsSeriesQueryParams:
        """Transform query parameters."""
        return BlsSeriesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: BlsSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the BLS API."""
        import asyncio
        from datetime import datetime, timedelta

        from openbb_bls.utils.helpers import get_bls_timeseries

        api_key = credentials.get("bls_api_key") if credentials else ""
        symbols = (
            query.symbol.split(",") if isinstance(query.symbol, str) else query.symbol
        )
        now = datetime.now()
        if query.start_date:
            start_year = query.start_date.year
        else:
            # No start date -> the series' full published history (from the
            # cached metadata), or a 20-year window when it can't be resolved.
            start_year = (
                _earliest_begin_year(symbols, getattr(query, "category", None))
                or (now - timedelta(weeks=52 * 20)).year
            )
        end_year = query.end_date.year if query.end_date else now.year
        results: dict = {"data": [], "messages": [], "metadata": {}}
        messages: list = []

        # Per-request limits depend on registration: 50 symbols / 20-year range
        # with an API key, 25 symbols / 10-year range without. Chunk to fit so a
        # full-history default still issues valid requests either way.
        max_symbols = 50 if api_key else 25
        max_years = 20 if api_key else 10

        def chunk_list(lst, chunk_size):
            """Yield successive chunks from lst of size chunk_size."""
            for i in range(0, len(lst), chunk_size):
                yield lst[i : i + chunk_size]

        def chunk_years(start_year, end_year, chunk_size):
            """Yield successive year ranges of size chunk_size."""
            for year in range(start_year, end_year + 1, chunk_size):
                yield (year, min(year + chunk_size - 1, end_year))

        # Define a function to wrap as a coroutine.
        async def make_query(symbol, start, end):
            """Make a query to the BLS API."""
            data = await get_bls_timeseries(
                api_key=api_key,
                series_ids=symbol,
                start_year=start,
                end_year=end,
                calculations=query.calculations,
                catalog=True,
                annual_average=query.annual_average,
                aspects=query.aspects,
            )
            if isinstance(data, dict):
                results.update(
                    {
                        "data": results.get("data", []) + data.get("data", []),
                        "messages": list(
                            set(results.get("messages", []) + data.get("messages", []))
                        ),
                        "metadata": {
                            **results.get("metadata", {}),
                            **data.get("metadata", {}),
                        },
                    }
                )
            elif isinstance(data, EmptyDataError) and data.message:
                messages.append(data.__dict__.get("message", ""))

        # Create a list of tasks to run based on the API query limitations.
        tasks: list = []

        for symbol_chunk in chunk_list(symbols, max_symbols):
            for year_range in chunk_years(start_year, end_year, max_years):
                tasks.append(
                    asyncio.create_task(
                        make_query(
                            symbol_chunk,
                            year_range[0],
                            year_range[1],
                        )
                    )
                )

        await asyncio.gather(*tasks)

        if not results.get("data"):
            if messages:
                raise OpenBBError(",".join(set(messages)))
            raise EmptyDataError("The request was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: BlsSeriesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[list[BlsSeriesData]]:
        """Transform the data."""
        series_data = data.get("data", [])
        messages = data.get("messages", [])
        metadata = data.get("metadata", {})
        if messages:
            for message in messages:
                warn(message)

        results = sorted(
            [BlsSeriesData.model_validate(series) for series in series_data],
            key=lambda x: (x.date, x.symbol),
        )

        if query.start_date is not None:
            results = [r for r in results if r.date >= query.start_date]

        if query.end_date is not None:
            results = [r for r in results if r.date <= query.end_date]

        return AnnotatedResult(
            result=results,
            metadata=metadata,
        )
