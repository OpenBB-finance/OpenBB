"""FederalReserve Treasury Rates Model."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_rates import (
    TreasuryRatesData,
    TreasuryRatesQueryParams,
)
from pydantic import field_validator

if TYPE_CHECKING:
    from pandas import DataFrame

maturities = [
    "month_1",
    "month_3",
    "month_6",
    "year_1",
    "year_2",
    "year_3",
    "year_5",
    "year_7",
    "year_10",
    "year_20",
    "year_30",
]


class FederalReserveTreasuryRatesQueryParams(TreasuryRatesQueryParams):
    """FederalReserve Treasury Rates Query."""


class FederalReserveTreasuryRatesData(TreasuryRatesData):
    """FederalReserve Treasury Rates Data."""

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FederalReserveTreasuryRatesFetcher(
    Fetcher[
        FederalReserveTreasuryRatesQueryParams,
        list[FederalReserveTreasuryRatesData],
    ]
):
    """Transform the query, extract and transform the data from the FederalReserve endpoints."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveTreasuryRatesQueryParams:
        """Transform the query params. Start and end dates are set to a 90 day interval."""
        from datetime import timedelta

        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=365)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FederalReserveTreasuryRatesQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: FederalReserveTreasuryRatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> "DataFrame":
        """Return the raw data from the FederalReserve endpoint."""
        from io import BytesIO

        from numpy import nan
        from openbb_core.provider.utils.helpers import make_request
        from pandas import read_csv

        url = (
            "https://www.federalreserve.gov/datadownload/Output.aspx?"
            + "rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=&"
            + "from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package"
        )

        r = make_request(url, **kwargs)

        df = read_csv(BytesIO(r.content), header=5, index_col=None, parse_dates=True)
        df.columns = ["date"] + maturities
        df = df.set_index("date").replace("ND", nan)

        return df.dropna(axis=0, how="all").reset_index()

    @staticmethod
    def transform_data(
        query: FederalReserveTreasuryRatesQueryParams, data: "DataFrame", **kwargs: Any
    ) -> list[FederalReserveTreasuryRatesData]:
        """Return the transformed data."""
        from pandas import to_datetime

        df = data.copy()
        df = df[
            (to_datetime(df.date) >= to_datetime(query.start_date))  # ty: ignore[no-matching-overload]
            & (to_datetime(df.date) <= to_datetime(query.end_date))  # ty: ignore[no-matching-overload]
        ]
        for col in maturities:
            df[col] = df[col].astype(float) / 100
        df = df.fillna("N/A").replace("N/A", None)
        return [
            FederalReserveTreasuryRatesData.model_validate(d)
            for d in df.to_dict("records")
        ]
