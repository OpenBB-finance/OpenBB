"""yfinance Major Indices End of Day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.major_indices_eod import (
    MajorIndicesEODData,
    MajorIndicesEODQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, validator
from yfinance import Ticker

from openbb_yfinance.utils.references import INTERVALS, PERIODS


class YFinanceMajorIndicesEODQueryParams(MajorIndicesEODQueryParams):
    """YFinance Major Indices End of Day Query.

    Source: https://finance.yahoo.com/world-indices
    """

    interval: Optional[INTERVALS] = Field(default="1d", description="Data granularity.")
    period: Optional[PERIODS] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("period", "")
    )
    prepost: bool = Field(
        default=False, description="Include Pre and Post market data."
    )
    adjust: bool = Field(default=True, description="Adjust all the data automatically.")
    back_adjust: bool = Field(
        default=False, description="Back-adjusted data to mimic true historical prices."
    )


class YFinanceMajorIndicesEODData(MajorIndicesEODData):
    """YFinance Major Indices End of Day Data."""

    @validator("Date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")


class YFinanceMajorIndicesEODFetcher(
    Fetcher[
        YFinanceMajorIndicesEODQueryParams,
        List[YFinanceMajorIndicesEODData],
    ]
):
    """Transform the query, extract and transform the data from the yfinance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceMajorIndicesEODQueryParams:
        """Transform the query. Setting the start and end dates for a 1 year period."""
        if params.get("period") is None:
            transformed_params = params

            now = datetime.now().date()
            if params.get("start_date") is None:
                transformed_params["start_date"] = now - relativedelta(years=1)

            if params.get("end_date") is None:
                transformed_params["end_date"] = now
            return YFinanceMajorIndicesEODQueryParams(**transformed_params)

        return YFinanceMajorIndicesEODQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceMajorIndicesEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the yfinance endpoint."""
        query.symbol = f"^{query.symbol}"

        if query.period:
            data = Ticker(query.symbol).history(
                interval=query.interval,
                period=query.period,
                prepost=query.prepost,
                auto_adjust=query.adjust,
                back_adjust=query.back_adjust,
                actions=False,
                raise_errors=True,
            )
        else:
            data = Ticker(query.symbol).history(
                interval=query.interval,
                start=query.start_date,
                end=query.end_date,
                prepost=query.prepost,
                auto_adjust=query.adjust,
                back_adjust=query.back_adjust,
                actions=False,
                raise_errors=True,
            )

        data = data.reset_index()
        data["Date"] = (
            data["Date"].dt.tz_localize(None).dt.strftime("%Y-%m-%dT%H:%M:%S")
        )
        return data.to_dict("records")

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[YFinanceMajorIndicesEODData]:
        """Transform the data to the standard format."""
        return [YFinanceMajorIndicesEODData.parse_obj(d) for d in data]
