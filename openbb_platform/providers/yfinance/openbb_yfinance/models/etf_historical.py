"""Yahoo Finance ETF Historical Price Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_historical import (
    EtfHistoricalData,
    EtfHistoricalQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pandas import Timestamp
from pydantic import Field, field_validator

from ..utils.helpers import yf_download


class YFinanceEtfHistoricalQueryParams(EtfHistoricalQueryParams):
    """Yahoo Finance ETF Historical Price Query.

    Source: https://finance.yahoo.com/
    """


class YFinanceEtfHistoricalData(EtfHistoricalData):
    """Yahoo Finance ETF Historical Price Data."""

    __alias_dict__ = {
        "adj_close": "adj close",
    }

    adj_close: Optional[float] = Field(
        default=None,
        description="The adjusted closing price of the ETF.",
    )

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        if isinstance(v, Timestamp):
            return v.to_pydatetime()
        return v


class YFinanceEtfHistoricalFetcher(
    Fetcher[
        YFinanceEtfHistoricalQueryParams,
        List[YFinanceEtfHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceEtfHistoricalQueryParams:
        """Transform the query."""
        transformed_params = params
        now = datetime.now().date()

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return YFinanceEtfHistoricalQueryParams(**params)

    # pylint: disable=unused-argument
    @staticmethod
    def extract_data(
        query: YFinanceEtfHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        data = yf_download(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            keep_adjusted=True,
        )

        if data.empty:
            raise EmptyDataError()

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: YFinanceEtfHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceEtfHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceEtfHistoricalData.model_validate(d) for d in data]
