"""Intrinio Options Snapshots Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_snapshots import (
    OptionsSnapshotsData,
    OptionsSnapshotsQueryParams,
)
from pydantic import Field

if TYPE_CHECKING:
    from pandas import DataFrame


class IntrinioOptionsSnapshotsQueryParams(OptionsSnapshotsQueryParams):
    """Intrinio Options Snapshots Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_options_snapshots_v2
    """

    date: Optional[Union[dateType, datetime, str]] = Field(
        default=None,
        description="The date of the data. Can be a datetime or an ISO datetime string."
        + " Data appears to go back to around 2022-06-01"
        + " Example: '2024-03-08T12:15:00+0400'",
    )
    only_traded: bool = Field(
        default=True,
        description="Only include options that have been traded during the session, default is True."
        + " Setting to false will dramatically increase the size of the response - use with caution.",
    )


class IntrinioOptionsSnapshotsData(OptionsSnapshotsData):
    """Intrinio Options Snapshots Data. Warning: This is a large file."""

    bid: List[Union[float, None]] = Field(
        default_factory=list,
        description="The last bid price at the time.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    bid_size: List[Union[int, None]] = Field(
        default_factory=list,
        description="The size of the last bid price.",
    )
    bid_timestamp: List[Union[datetime, None]] = Field(
        default_factory=list,
        description="The timestamp of the last bid price.",
    )
    ask: List[Union[float, None]] = Field(
        default_factory=list,
        description="The last ask price at the time.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_size: List[Union[int, None]] = Field(
        default_factory=list,
        description="The size of the last ask price.",
    )
    ask_timestamp: List[Union[datetime, None]] = Field(
        default_factory=list,
        description="The timestamp of the last ask price.",
    )
    total_bid_volume: List[Union[int, None]] = Field(
        default_factory=list,
        description="Total volume of bids.",
    )
    bid_high: List[Union[float, None]] = Field(
        default_factory=list,
        description="The highest bid price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    bid_low: List[Union[float, None]] = Field(
        default_factory=list,
        description="The lowest bid price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    total_ask_volume: List[Union[int, None]] = Field(
        default_factory=list,
        description="Total volume of asks.",
    )
    ask_high: List[Union[float, None]] = Field(
        default_factory=list,
        description="The highest ask price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_low: List[Union[float, None]] = Field(
        default_factory=list,
        description="The lowest ask price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )


class IntrinioOptionsSnapshotsFetcher(
    Fetcher[
        IntrinioOptionsSnapshotsQueryParams,
        List[IntrinioOptionsSnapshotsData],
    ]
):
    """Intrinio Options Snapshots Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioOptionsSnapshotsQueryParams:
        """Transform the query params."""
        # pylint: disable=import-outside-toplevel
        from pytz import timezone

        transformed_params = params.copy()
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
                        16,
                        15,
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
        return IntrinioOptionsSnapshotsQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioOptionsSnapshotsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> "DataFrame":
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        import gzip  # noqa
        from io import BytesIO  # noqa
        from openbb_core.provider.utils.helpers import amake_request  # noqa
        from pandas import DataFrame, read_csv  # noqa

        api_key = credentials.get("intrinio_api_key") if credentials else ""

        # This gets the URL to the actual file.
        url = f"https://api-v2.intrinio.com/options/snapshots?api_key={api_key}"
        if query.date:
            url += f"&at_datetime={query.date}"

        try:
            response = await amake_request(url, **kwargs)
        except Exception as exc:
            raise OpenBBError("Could not fetch data from Intrinio.") from exc

        if isinstance(response, dict) and "error" in response:
            raise OpenBBError(
                f"{response.get('error')}. Message: {response.get('message')}"
            )
        urls = []
        # Get the URL to the CSV file.
        if response.get("snapshots"):  # type: ignore
            for d in response["snapshots"]:  # type: ignore
                if d.get("files"):
                    for f in d["files"]:
                        if f.get("url"):
                            urls.append(f.get("url"))
        if not urls:
            raise OpenBBError("No snapshots found.")

        async def response_callback(response, _):
            """Response Callback."""
            return await response.read()

        async def get_csv(url) -> DataFrame:
            """Return the CSV data."""
            try:
                response = await amake_request(
                    url, response_callback=response_callback, **kwargs
                )
                df = DataFrame()
                if isinstance(response, bytes):
                    file = gzip.decompress(response)
                    df = read_csv(BytesIO(file))

                return df

            except Exception as exc:
                try:
                    df = read_csv(response)
                    return df
                except Exception:
                    raise OpenBBError("Could not read file from URL.") from exc

        # There should only be one URL with this bulk data.
        return await get_csv(urls[0])

    @staticmethod
    def transform_data(
        query: IntrinioOptionsSnapshotsQueryParams,
        data: "DataFrame",
        **kwargs: Any,
    ) -> List[IntrinioOptionsSnapshotsData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        import numpy as np
        from pandas import NaT, Series, to_datetime
        from pytz import timezone

        df = data
        if df.empty:
            raise OpenBBError("Empty CSV file")
        COL_MAP = {
            "CONTRACT ID": "contract_symbol",
            "OPEN INTEREST": "open_interest",
            "TRADE PRICE": "last_price",
            "TRADE SIZE": "last_size",
            "TOTAL TRADE VOLUME": "volume",
            "LAST TRADE TIMESTAMP": "last_timestamp",
            "TRADE HIGH PRICE": "high",
            "TRADE LOW PRICE": "low",
            "ASK PRICE": "ask",
            "ASK SIZE": "ask_size",
            "LAST ASK TIMESTAMP": "ask_timestamp",
            "BID PRICE": "bid",
            "BID SIZE": "bid_size",
            "LAST BID TIMESTAMP": "bid_timestamp",
            "TOTAL ASK VOLUME": "total_ask_volume",
            "ASK HIGH PRICE": "ask_high",
            "ASK LOW PRICE": "ask_low",
            "TOTAL BID VOLUME": "total_bid_volume",
            "BID HIGH PRICE": "bid_high",
            "BID LOW PRICE": "bid_low",
        }
        df = df.rename(columns=COL_MAP)
        to_drop_na = (
            ["bid_timestamp", "ask_timestamp", "last_timestamp"]
            if query.only_traded is True
            else ["bid_timestamp", "ask_timestamp"]
        )
        df = df.dropna(subset=to_drop_na + ["contract_symbol"])
        for col in ["last_timestamp", "bid_timestamp", "ask_timestamp"]:
            # Convert Unix timestamp to tz-aware datetime
            df[col] = (
                to_datetime(df[col].replace("", None).astype(float), unit="s")
                .dt.tz_localize(timezone("UTC"))
                .dt.tz_convert(timezone("America/New_York"))
                .dt.floor("s")
            )

        # Extract the underlying symbol, expiration, option type, and strike.
        symbols = Series(df["contract_symbol"].copy())
        df["underlying_symbol"] = symbols.str.extract(r"^(?P<underlying_symbol>[^_]*)")
        split_symbols = symbols.str.rsplit("_", n=1).str[-1]
        df["expiration"] = to_datetime(
            [symbol[:6] for symbol in split_symbols],
            format="%y%m%d",
        )
        df["option_type"] = split_symbols.str.extract(
            r"^\d*(?P<option_type>\D)"
        ).replace({"C": "call", "P": "put"})
        df["strike"] = [
            (
                symbol[7:].lstrip("0")[:-3] + "." + symbol[7:].lstrip("0")[-3:]
                if "." not in symbol[7:]
                else symbol[7:]
            )
            for symbol in split_symbols
        ]

        def calculate_dte(df):
            """Calculate the DTE."""
            new_df = df[
                ["expiration", "last_timestamp", "bid_timestamp", "ask_timestamp"]
            ].copy()
            conditions = [
                new_df["last_timestamp"].notna(),
                new_df["bid_timestamp"].notna(),
                new_df["ask_timestamp"].notna(),
            ]
            choices = [
                (new_df["expiration"].dt.date - new_df["last_timestamp"].dt.date)
                .apply(lambda x: x)
                .dt.days,
                (new_df["expiration"].dt.date - new_df["bid_timestamp"].dt.date)
                .apply(lambda x: x)
                .dt.days,
                (new_df["expiration"].dt.date - new_df["ask_timestamp"].dt.date)
                .apply(lambda x: x)
                .dt.days,
            ]
            new_df["dte"] = np.select(conditions, choices, default=None)
            return new_df["dte"]

        df["dte"] = calculate_dte(df)

        def apply_contract_symbol(x):
            """Construct the OCC Contract Symbol."""
            symbol = x.split("_")[0].replace("_", "")
            exp = x.rsplit("_")[-1][:6]
            cp = x.rsplit("_")[-1][6]
            strike = x.rsplit("_")[-1][7:]
            _strike = strike.split(".")
            front = "0" * (5 - len(_strike[0]))
            back = "0" * (3 - len(_strike[1]))
            strike = f"{front}{_strike[0]}{_strike[1]}{back}"
            return symbol + exp + cp + strike

        if symbols.str.contains(r"\.").any():  # noqa  # pylint: disable=W1401
            df["contract_symbol"] = df["contract_symbol"].apply(apply_contract_symbol)
        else:
            df["contract_symbol"] = symbols.str.replace("_", "")
        df = df.replace({NaT: None, np.nan: None})
        df = df.sort_values(by="volume", ascending=False)

        return [IntrinioOptionsSnapshotsData.model_validate(df.to_dict(orient="list"))]
