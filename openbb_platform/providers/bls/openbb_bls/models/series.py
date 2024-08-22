"""BLS Series Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.bls_series import (
    SeriesData,
    SeriesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class BlsSeriesQueryParams(SeriesQueryParams):
    """BLS Series Query Parameters."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
    }

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
    """BLS Series Data."""

    change_1M: Optional[float] = Field(
        default=None,
        description="One month change in value.",
    )
    change_3M: Optional[float] = Field(
        default=None,
        description="Three month change in value.",
    )
    change_6M: Optional[float] = Field(
        default=None,
        description="Six month change in value.",
    )
    change_12M: Optional[float] = Field(
        default=None,
        description="One year change in value.",
    )
    change_percent_1M: Optional[float] = Field(
        default=None,
        description="One month change in percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    change_percent_3M: Optional[float] = Field(
        default=None,
        description="Three month change in percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    change_percent_6M: Optional[float] = Field(
        default=None,
        description="Six month change in percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    change_percent_12M: Optional[float] = Field(
        default=None,
        description="One year change in percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    latest: Optional[bool] = Field(
        default=None,
        description="Latest value indicator.",
    )
    footnotes: Optional[str] = Field(
        default=None,
        description="Footnotes accompanying the value.",
    )


class BlsSeriesFetcher(Fetcher[BlsSeriesQueryParams, List[BlsSeriesData]]):
    """BLS Series Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BlsSeriesQueryParams:
        """Transform query parameters."""
        return BlsSeriesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: BlsSeriesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract the data from the BLS API."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from datetime import datetime, timedelta
        from openbb_bls.utils.helpers import get_bls_timeseries

        api_key = credentials.get("bls_api_key") if credentials else ""
        symbols = (
            query.symbol.split(",") if isinstance(query.symbol, str) else query.symbol
        )
        now = datetime.now()
        start_year = (
            query.start_date.year
            if query.start_date
            else (now - timedelta(weeks=52 * 3)).year
        )
        end_year = query.end_date.year if query.end_date else now.year
        results: Dict = {"data": [], "messages": [], "metadata": {}}
        messages: List = []

        # The max number of symbols per request is 50.
        # The max year range is 20.
        # We chunk the request to handle the provided start/end date by the user.
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
        tasks: List = []

        for symbol_chunk in chunk_list(symbols, 50):
            for year_range in chunk_years(start_year, end_year, 20):
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
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[BlsSeriesData]]:
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
