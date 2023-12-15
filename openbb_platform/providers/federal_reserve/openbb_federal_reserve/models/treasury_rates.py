"""FederalReserve Treasury Rates Model."""

from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_rates import (
    TreasuryRatesData,
    TreasuryRatesQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from pydantic import field_validator

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
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FederalReserveTreasuryRatesFetcher(
    Fetcher[
        FederalReserveTreasuryRatesQueryParams,
        List[FederalReserveTreasuryRatesData],
    ]
):
    """Transform the query, extract and transform the data from the FederalReserve endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FederalReserveTreasuryRatesQueryParams:
        """Transform the query params. Start and end dates are set to a 90 day interval."""
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
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FederalReserve endpoint."""
        url = (
            "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78"
            "&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn"
        )
        r = make_request(url, **kwargs)
        df = pd.read_csv(BytesIO(r.content), header=5, index_col=None, parse_dates=True)
        df.columns = ["date"] + maturities
        df = df.replace("ND", None)
        df = df[
            (pd.to_datetime(df.date) >= pd.to_datetime(query.start_date))
            & (pd.to_datetime(df.date) <= pd.to_datetime(query.end_date))
        ]
        df[maturities] = df[maturities].applymap(
            lambda x: float(x) if x != "-" and x is not None else x
        )
        df = df.reset_index(drop=True)

        return df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: FederalReserveTreasuryRatesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FederalReserveTreasuryRatesData]:
        """Return the transformed data."""
        treasury_data = []
        for d in data:
            for k, v in d.items():
                if pd.isna(v) and not isinstance(v, str):
                    d[k] = None
            treasury_data.append(FederalReserveTreasuryRatesData.model_validate(d))
        return treasury_data
