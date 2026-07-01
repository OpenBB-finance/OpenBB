"""ECB Currency Reference Rates Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_reference_rates import (
    CurrencyReferenceRatesData,
    CurrencyReferenceRatesQueryParams,
)


class ECBCurrencyReferenceRatesQueryParams(CurrencyReferenceRatesQueryParams):
    """ECB Currency Reference Rates Query."""


class ECBCurrencyReferenceRatesData(CurrencyReferenceRatesData):
    """ECB Currency Reference Rates Data."""


class ECBCurrencyReferenceRatesFetcher(
    Fetcher[ECBCurrencyReferenceRatesQueryParams, ECBCurrencyReferenceRatesData]
):
    """Transform the query, extract and transform the data from the ECB endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBCurrencyReferenceRatesQueryParams:
        """Transform query."""
        return ECBCurrencyReferenceRatesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: ECBCurrencyReferenceRatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the raw daily reference-rate XML from the ECB website."""
        # pylint: disable=import-outside-toplevel
        import xmltodict
        from openbb_core.provider.utils.helpers import make_request

        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        response = make_request(url)
        if response.status_code != 200:
            raise OpenBBError(
                "Failed to fetch data from ECB."
                + f" -> Status Code: {response.status_code}"
            )
        cube = xmltodict.parse(response.content)["gesmes:Envelope"]["Cube"]["Cube"]
        return {
            "time": cube["@time"],
            "rates": {d["@currency"]: d["@rate"] for d in cube["Cube"]},
        }

    @staticmethod
    def transform_data(
        query: ECBCurrencyReferenceRatesQueryParams, data: dict, **kwargs: Any
    ) -> ECBCurrencyReferenceRatesData:
        """Shape the raw rates into the standardized record and validate."""
        record = {"date": data["time"], "EUR": 1, **data["rates"]}
        return ECBCurrencyReferenceRatesData.model_validate(record)
