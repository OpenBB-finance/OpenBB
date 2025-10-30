"""FMP Currency Snapshots Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_snapshots import (
    CurrencySnapshotsData,
    CurrencySnapshotsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class FMPCurrencySnapshotsQueryParams(CurrencySnapshotsQueryParams):
    """FMP Currency Snapshots Query.

    Source: https://site.financialmodelingprep.com/developer/docs#all-forex-quotes
    """

    __json_schema_extra__ = {"base": {"multiple_items_allowed": True}}


class FMPCurrencySnapshotsData(CurrencySnapshotsData):
    """FMP Currency Snapshots Data."""

    __alias_dict__ = {
        "last_rate": "price",
        "high": "dayHigh",
        "low": "dayLow",
        "ma50": "priceAvg50",
        "ma200": "priceAvg200",
        "year_high": "yearHigh",
        "year_low": "yearLow",
        "prev_close": "previousClose",
        "change_percent": "changePercentage",
        "last_rate_timestamp": "timestamp",
    }

    change: float | None = Field(
        description="The change in the price from the previous close.", default=None
    )
    change_percent: float | None = Field(
        description="The change in the price from the previous close, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ma50: float | None = Field(description="The 50-day moving average.", default=None)
    ma200: float | None = Field(description="The 200-day moving average.", default=None)
    year_high: float | None = Field(description="The 52-week high.", default=None)
    year_low: float | None = Field(description="The 52-week low.", default=None)
    last_rate_timestamp: datetime | None = Field(
        description="The timestamp of the last rate.", default=None
    )

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize the percent."""
        return v / 100 if v is not None else None


class FMPCurrencySnapshotsFetcher(
    Fetcher[FMPCurrencySnapshotsQueryParams, list[FMPCurrencySnapshotsData]]
):
    """FMP Currency Snapshots Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCurrencySnapshotsQueryParams:
        """Transform the query parameters."""
        return FMPCurrencySnapshotsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCurrencySnapshotsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = f"https://financialmodelingprep.com/stable/batch-forex-quotes?short=false&apikey={api_key}"

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCurrencySnapshotsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FMPCurrencySnapshotsData]:
        """Filter by the query parameters and validate the model."""
        # pylint: disable=import-outside-toplevel
        from datetime import timezone  # noqa
        from numpy import nan
        from pandas import DataFrame, concat
        from openbb_core.provider.utils.helpers import safe_fromtimestamp

        if not data:
            raise EmptyDataError("No data was returned from the FMP endpoint.")

        # Drop all the zombie columns FMP returns.
        df = DataFrame(data).dropna(how="all", axis=1).drop(columns=["exchange"])

        new_df = DataFrame()

        # Filter for the base currencies requested and the quote_type.
        for symbol in query.base.split(","):
            temp = (
                df.query("`symbol`.str.startswith(@symbol)")
                if query.quote_type == "indirect"
                else df.query("`symbol`.str.endswith(@symbol)")
            ).rename(columns={"symbol": "base_currency", "name": "counter_currency"})
            temp["base_currency"] = symbol
            temp["counter_currency"] = (
                [d.split("/")[1] for d in temp["counter_currency"]]
                if query.quote_type == "indirect"
                else [d.split("/")[0] for d in temp["counter_currency"]]
            )
            # Filter for the counter currencies, if requested.
            if query.counter_currencies is not None:
                counter_currencies = (  # noqa: F841  # pylint: disable=unused-variable
                    query.counter_currencies
                    if isinstance(query.counter_currencies, list)
                    else query.counter_currencies.split(",")
                )
                temp = (
                    temp.query("`counter_currency`.isin(@counter_currencies)")
                    .set_index("counter_currency")
                    # Sets the counter currencies in the order they were requested.
                    .filter(items=counter_currencies, axis=0)
                    .reset_index()
                ).rename(columns={"index": "counter_currency"})
            # If there are no records, don't concatenate.
            if len(temp) > 0:
                # Convert the Unix timestamp to a datetime.
                temp.timestamp = temp.timestamp.apply(
                    lambda x: safe_fromtimestamp(x, tz=timezone.utc)
                )
                new_df = concat([new_df, temp])
            if len(new_df) == 0:
                raise EmptyDataError(
                    "No data was found using the applied filters. Check the parameters."
                )
            new_df = new_df.replace({nan: None})

        return [
            FMPCurrencySnapshotsData.model_validate(d)
            for d in new_df.reset_index(drop=True).to_dict(orient="records")
        ]
