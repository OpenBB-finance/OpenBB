"""Federal Reserve FED Model."""

from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fed_rates import (
    FEDData,
    FEDQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from pydantic import field_validator


class FederalReserveFEDQueryParams(FEDQueryParams):
    """FederalReserve FED Query."""


class FederalReserveFEDData(FEDData):
    """FederalReserve FED Data."""

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FederalReserveFEDFetcher(
    Fetcher[FederalReserveFEDQueryParams, List[Dict[str, List[FederalReserveFEDData]]]]
):
    """FederalReserve FED Model."""

    data_type = FederalReserveFEDData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FederalReserveFEDQueryParams:
        """Transform query."""
        transformed_params = params
        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=10 * 365)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FederalReserveFEDQueryParams(**transformed_params)

    # pylint: disable=unused-argument
    @staticmethod
    def extract_data(
        query: FederalReserveFEDQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> dict:
        """Extract data."""
        url = (
            "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=c5025f4bbbed155a6f17c587772ed69e"
            "&lastobs=&from=01/01/1938&to=12/31/3023&filetype=csv&label=include&layout=seriescolumn"
        )
        r = make_request(url, **kwargs)
        df = pd.read_csv(BytesIO(r.content), header=5, index_col=None, parse_dates=True)
        df.columns = ["date", "rate"]
        df = df[
            (pd.to_datetime(df.date) >= pd.to_datetime(query.start_date))
            & (pd.to_datetime(df.date) <= pd.to_datetime(query.end_date))
        ]

        return df.to_dict(orient="records")

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: FederalReserveFEDQueryParams, data: dict, **kwargs: Any
    ) -> List[Dict[str, List[FederalReserveFEDData]]]:
        """Transform data."""

        return [FederalReserveFEDData.model_validate(d) for d in data]
