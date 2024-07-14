"""ECB Currency Reference Rates Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, Optional

from openbb_core.app.model.abstract.error import OpenBBError
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
        # pylint: disable=import-outside-toplevel
        import xmltodict
        from openbb_core.provider.utils.helpers import make_request

        results = {}
        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        response = make_request(url)
        if response.status_code != 200:
            raise OpenBBError(
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
