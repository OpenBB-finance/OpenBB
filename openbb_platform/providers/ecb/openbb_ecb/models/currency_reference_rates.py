"""ECB Currency Reference Rates Model."""

from typing import Any, Dict, Optional

import requests
import xmltodict
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_reference_rates import (
    CurrencyReferenceRatesData,
    CurrencyReferenceRatesQueryParams,
)


class ECBCurrencyReferenceRatesQueryParams(CurrencyReferenceRatesQueryParams):
    """
    ECB Currency Reference Rates Query.

    source: https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/
    """


class ECBCurrencyReferenceRatesData(CurrencyReferenceRatesData):
    """ECB Currency Reference Rates Data."""


class ECBCurrencyReferenceRatesFetcher(
    Fetcher[ECBCurrencyReferenceRatesQueryParams, ECBCurrencyReferenceRatesData]
):
    """Transform the query, extract and transform the data from the ECB endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> ECBCurrencyReferenceRatesQueryParams:
        """Transform query."""
        return ECBCurrencyReferenceRatesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: ECBCurrencyReferenceRatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract the raw data from the ECB website."""
        results = {}
        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            raise RuntimeError(
                "Failed to fetch data from ECB."
                + f" -> Status Code: {response.status_code}"
            )
        data = xmltodict.parse(response.content)
        rates_data = data["gesmes:Envelope"]["Cube"]["Cube"]["Cube"]
        rates = {d["@currency"]: d["@rate"] for d in rates_data}
        results["date"] = data["gesmes:Envelope"]["Cube"]["Cube"]["@time"]
        results["EUR"] = 1
        results.update(rates)

        return results

    @staticmethod
    def transform_data(
        query: ECBCurrencyReferenceRatesQueryParams, data: Dict, **kwargs: Any
    ) -> ECBCurrencyReferenceRatesData:
        """Transform data."""
        return ECBCurrencyReferenceRatesData.model_validate(data)
