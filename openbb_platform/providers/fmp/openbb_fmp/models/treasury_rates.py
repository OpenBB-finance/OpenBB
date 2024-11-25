"""FMP Treasury Rates Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_rates import (
    TreasuryRatesData,
    TreasuryRatesQueryParams,
)
from openbb_core.provider.utils.helpers import amake_requests
from pydantic import field_validator, model_validator


class FMPTreasuryRatesQueryParams(TreasuryRatesQueryParams):
    """FMP Treasury Rates Query.

    Source: https://site.financialmodelingprep.com/developer/docs/treasury-rates-api/
    """


class FMPTreasuryRatesData(TreasuryRatesData):
    """FMP Treasury Rates Data."""

    __alias_dict__ = {
        "month_1": "month1",
        "month_2": "month2",
        "month_3": "month3",
        "month_6": "month6",
        "year_1": "year1",
        "year_2": "year2",
        "year_3": "year3",
        "year_5": "year5",
        "year_7": "year7",
        "year_10": "year10",
        "year_20": "year20",
        "year_30": "year30",
    }

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")

    @model_validator(mode="before")
    @classmethod
    def normalize_percent(cls, values):
        """Normalize the percent values."""
        for k, v in values.items():
            if k != "date" and v:
                values[k] = float(v) / 100
        return values


class FMPTreasuryRatesFetcher(
    Fetcher[
        FMPTreasuryRatesQueryParams,
        List[FMPTreasuryRatesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPTreasuryRatesQueryParams:
        """Transform the query params. Start and end dates are set to a 90 day interval."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPTreasuryRatesQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPTreasuryRatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""

        api_key = credentials.get("fmp_api_key") if credentials else ""

        def generate_urls(start_date, end_date):
            """Generate URLs for each 3-month interval between start_date and end_date."""
            base_url = "https://financialmodelingprep.com/api/v4/treasury?from={}&to={}"
            urls = []
            while start_date <= end_date:
                next_date = start_date + relativedelta(months=3)
                url = base_url.format(
                    start_date.strftime("%Y-%m-%d"),
                    min(next_date, end_date).strftime("%Y-%m-%d"),
                )
                url = url + f"&apikey={api_key}"
                urls.append(url)
                start_date = next_date
            return urls

        urls = generate_urls(query.start_date, query.end_date)
        return await amake_requests(urls, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPTreasuryRatesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPTreasuryRatesData]:
        """Return the transformed data."""
        return [
            FMPTreasuryRatesData.model_validate(d)
            for d in sorted(data, key=lambda x: x["date"], reverse=False)
        ]
