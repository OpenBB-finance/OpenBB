"""Intrinio Market Snapshots Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.market_snapshots import (
    MarketSnapshotsData,
    MarketSnapshotsQueryParams,
)
from pydantic import Field


class IntrinioMarketSnapshotsQueryParams(MarketSnapshotsQueryParams):
    """Intrinio Market Snapshots Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_security_snapshots_v2
    """

    date: Optional[Union[dateType, datetime, str]] = Field(
        default=None,
        description="The date of the data. Can be a datetime or an ISO datetime string."
        + " Historical data appears to go back to mid-June 2022."
        + " Example: '2024-03-08T12:15:00+0400'",
    )


class IntrinioMarketSnapshotsData(MarketSnapshotsData):
    """Intrinio Market Snapshots Data."""

    __alias_dict__ = {
        "last_price": "trade_price",
        "last_size": "trade_size",
        "last_volume": "total_trade_volume",
    }

    last_price: Optional[float] = Field(
        default=None,
        description="The last trade price.",
    )
    last_size: Optional[int] = Field(
        default=None,
        description="The last trade size.",
    )
    last_volume: Optional[int] = Field(
        default=None,
        description="The last trade volume.",
    )
    last_trade_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp of the last trade.",
    )
    bid_size: Optional[int] = Field(
        default=None,
        description="The size of the last bid price. Bid price and size is not always available.",
    )
    bid_price: Optional[float] = Field(
        default=None,
        description="The last bid price. Bid price and size is not always available.",
    )
    ask_price: Optional[float] = Field(
        default=None,
        description="The last ask price. Ask price and size is not always available.",
    )
    ask_size: Optional[int] = Field(
        default=None,
        description="The size of the last ask price. Ask price and size is not always available.",
    )
    last_bid_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp of the last bid price. Bid price and size is not always available.",
    )
    last_ask_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp of the last ask price. Ask price and size is not always available.",
    )


class IntrinioMarketSnapshotsFetcher(
    Fetcher[
        IntrinioMarketSnapshotsQueryParams,
        list[IntrinioMarketSnapshotsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> IntrinioMarketSnapshotsQueryParams:
        """Transform the query params."""
        # pylint: disable=import-outside-toplevel
        from pytz import timezone

        transformed_params = params

        if "date" in transformed_params:
            if isinstance(transformed_params["date"], datetime):
                dt = transformed_params["date"]
                dt = dt.astimezone(tz=timezone("America/New_York"))
            if isinstance(transformed_params["date"], dateType):
                dt = transformed_params["date"]  # type: ignore
                if isinstance(dt, dateType):
                    dt = datetime(
                        dt.year,
                        dt.month,
                        dt.day,
                        20,
                        0,
                        0,
                        0,
                        tzinfo=timezone("America/New_York"),
                    )
            if isinstance(transformed_params["date"], str):
                dt = datetime.fromisoformat(transformed_params["date"])
            else:
                try:
                    dt = datetime.fromisoformat(str(transformed_params["date"]))  # type: ignore
                except ValueError as exc:
                    raise OpenBBError(
                        "Invalid date format. Please use '2024-03-08T12:15-0400'."
                    ) from exc

            transformed_params["date"] = (
                dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                .replace("+", "-")
                .replace("T00:", "T20:")
                if isinstance(dt, datetime)
                else dt
            )
        return IntrinioMarketSnapshotsQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioMarketSnapshotsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import gzip  # noqa
        from datetime import timezone as datetime_timezone  # noqa
        from io import BytesIO  # noqa
        from openbb_core.provider.utils.helpers import (
            amake_request,
            safe_fromtimestamp,
        )  # noqa
        from pandas import DataFrame, notna, read_csv, to_datetime  # noqa

        api_key = credentials.get("intrinio_api_key") if credentials else ""

        # This gets the URL to the actual file.
        url = f"https://api-v2.intrinio.com/securities/snapshots?api_key={api_key}"
        if query.date:
            url += f"&at_datetime={query.date}"

        response = await amake_request(url, **kwargs)

        if isinstance(response, dict) and "error" in response:
            raise OpenBBError(
                f"Error: {response.get('error')}. Message: {response.get('message')}"
            )
        urls: list = []
        # Get the URL to the CSV file.
        if response.get("snapshots"):  # type: ignore
            for d in response["snapshots"]:  # type: ignore
                if d.get("files"):
                    for f in d["files"]:
                        if f.get("url"):
                            urls.append(f.get("url"))
        if not urls:
            raise OpenBBError("No snapshots found.")

        results: list = []

        async def response_callback(response, _):
            """Response Callback."""
            return await response.read()

        async def get_csv(url):
            """Return the CSV data."""
            response = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            df = DataFrame()
            if isinstance(response, bytes):
                file = gzip.decompress(response)
                df = read_csv(BytesIO(file))
            if df.empty:
                raise OpenBBError("Empty CSV file.")
            df.columns = df.columns.str.lower().str.replace(" ", "_")

            df = (
                df.dropna(how="all", axis=1)
                .dropna(subset=["trade_price", "last_trade_timestamp", "symbol"])
                .sort_values("last_trade_timestamp", ascending=False)
            )[
                [
                    "symbol",
                    "trade_price",
                    "trade_size",
                    "total_trade_volume",
                    "bid_size",
                    "bid_price",
                    "ask_price",
                    "ask_size",
                    "last_trade_timestamp",
                    "last_bid_timestamp",
                    "last_ask_timestamp",
                ]
            ]

            for col in [
                "last_trade_timestamp",
                "last_bid_timestamp",
                "last_ask_timestamp",
            ]:
                df[col] = (
                    to_datetime(
                        df[col].apply(
                            lambda x: (
                                safe_fromtimestamp(x, tz=datetime_timezone.utc)
                                if notna(x)
                                else x
                            )
                        )
                    )
                    .dt.tz_convert("America/New_York")
                    .dt.floor("s")
                )

            for c in ["trade_size", "total_trade_volume"]:
                df[c] = df[c].astype("int64")

            # Clear out NaN and non-numeric values with None.
            df = (
                df.replace("Max", None)
                .replace("Min", None)
                .replace(0, None)
                .fillna("N/A")
                .replace("N/A", None)
            )

            if len(df) > 0:
                results.extend(df.reset_index(drop=True).to_dict(orient="records"))

        await asyncio.gather(*[get_csv(url) for url in urls])

        return results

    @staticmethod
    def transform_data(
        query: IntrinioMarketSnapshotsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[IntrinioMarketSnapshotsData]:
        """Return the transformed data."""
        return [IntrinioMarketSnapshotsData.model_validate(d) for d in data]
