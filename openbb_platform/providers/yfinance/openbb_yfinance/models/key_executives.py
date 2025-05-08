"""YFinance Key Executives Model."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_executives import (
    KeyExecutivesData,
    KeyExecutivesQueryParams,
)
from pydantic import Field


class YFinanceKeyExecutivesQueryParams(KeyExecutivesQueryParams):
    """YFinance Key Executives Query."""


class YFinanceKeyExecutivesData(KeyExecutivesData):
    """YFinance Key Executives Data."""

    __alias_dict__ = {
        "year_born": "yearBorn",
        "fiscal_year": "fiscalYear",
        "pay": "totalPay",
        "exercised_value": "exercisedValue",
        "unexercised_value": "unexercisedValue",
    }

    exercised_value: Optional[int] = Field(
        default=None,
        description="Value of shares exercised.",
    )
    unexercised_value: Optional[int] = Field(
        default=None,
        description="Value of shares not exercised.",
    )
    fiscal_year: Optional[int] = Field(
        default=None,
        description="Fiscal year of the pay.",
    )


class YFinanceKeyExecutivesFetcher(
    Fetcher[YFinanceKeyExecutivesQueryParams, List[YFinanceKeyExecutivesData]]
):
    """YFinance Key Executives Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceKeyExecutivesQueryParams:
        """Transform the query."""
        return YFinanceKeyExecutivesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceKeyExecutivesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance."""
        # pylint: disable=import-outside-toplevel
        from curl_adapter import CurlCffiAdapter  # noqa
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.helpers import get_requests_session
        from yfinance import Ticker

        session = get_requests_session()
        session.mount("https://", CurlCffiAdapter())
        session.mount("http://", CurlCffiAdapter())

        try:
            ticker = Ticker(
                query.symbol,
                session=session,
            ).get_info()
        except Exception as e:
            raise OpenBBError(
                f"Error getting data for {query.symbol} -> {e.__class__.__name__}: {e}"
            ) from e

        if ticker.get("companyOfficers") is None:
            raise OpenBBError(f"No executive data found for {query.symbol}")

        officers_data = ticker.get("companyOfficers", [])
        _ = [d.pop("maxAge", None) for d in officers_data]

        return officers_data

    @staticmethod
    def transform_data(
        query: YFinanceKeyExecutivesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceKeyExecutivesData]:
        """Transform the data."""
        return [YFinanceKeyExecutivesData.model_validate(d) for d in data]
