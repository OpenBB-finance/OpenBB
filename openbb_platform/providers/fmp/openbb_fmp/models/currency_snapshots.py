"""FMP Currency Snapshots Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_snapshots import (
    CurrencySnapshotsData,
    CurrencySnapshotsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class FMPCurrencySnapshotsQueryParams(CurrencySnapshotsQueryParams):
    """FMP Currency Snapshots Query.

    Source: https://site.financialmodelingprep.com/developer/docs#exchange-prices-quote
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
        "change_percent": "changesPercentage",
        "last_rate_timestamp": "timestamp",
    }

    change: Optional[float] = Field(
        description="The change in the price from the previous close.", default=None
    )
    change_percent: Optional[float] = Field(
        description="The change in the price from the previous close, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ma50: Optional[float] = Field(
        description="The 50-day moving average.", default=None
    )
    ma200: Optional[float] = Field(
        description="The 200-day moving average.", default=None
    )
    year_high: Optional[float] = Field(description="The 52-week high.", default=None)
    year_low: Optional[float] = Field(description="The 52-week low.", default=None)
    last_rate_timestamp: Optional[datetime] = Field(
        description="The timestamp of the last rate.", default=None
    )

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize the percent."""
        return v / 100 if v is not None else None


class FMPCurrencySnapshotsFetcher(
    Fetcher[FMPCurrencySnapshotsQueryParams, List[FMPCurrencySnapshotsData]]
):
    """FMP Currency Snapshots Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCurrencySnapshotsQueryParams:
        """Transform the query parameters."""
        return FMPCurrencySnapshotsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCurrencySnapshotsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request

        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = f"https://financialmodelingprep.com/api/v3/quotes/forex?apikey={api_key}"

        return await amake_request(url, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: FMPCurrencySnapshotsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPCurrencySnapshotsData]:
        """Filter by the query parameters and validate the model."""
        # pylint: disable=import-outside-toplevel
        from datetime import timezone  # noqa
        from pandas import DataFrame, concat  # noqa
        from openbb_core.provider.utils.helpers import safe_fromtimestamp  # noqa

        if not data:
            raise EmptyDataError("No data was returned from the FMP endpoint.")

        # Drop all the zombie columns FMP returns.
        df = (
            DataFrame(data)
            .dropna(how="all", axis=1)
            .drop(columns=["exchange", "avgVolume"])
        )

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
            # Fill and replace any NaN values with NoneType.
            new_df = new_df.fillna("N/A").replace("N/A", None)
        return [
            FMPCurrencySnapshotsData.model_validate(d)
            for d in new_df.reset_index(drop=True).to_dict(orient="records")
        ]
