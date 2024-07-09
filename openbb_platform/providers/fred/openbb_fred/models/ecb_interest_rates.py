"""FRED European Central Bank Interest Rates Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.ecb_interest_rates import (
    EuropeanCentralBankInterestRatesData,
    EuropeanCentralBankInterestRatesParams,
)
from pydantic import field_validator

NAME_TO_ID_ECB = {"deposit": "ECBDFR", "lending": "ECBMLFR", "refinancing": "ECBMRRFR"}


class FREDEuropeanCentralBankInterestRatesParams(
    EuropeanCentralBankInterestRatesParams
):
    """FRED European Central Bank Interest Rates Query."""


class FREDEuropeanCentralBankInterestRatesData(EuropeanCentralBankInterestRatesData):
    """FRED European Central Bank Interest Rates Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDEuropeanCentralBankInterestRatesFetcher(
    Fetcher[
        FREDEuropeanCentralBankInterestRatesParams,
        List[FREDEuropeanCentralBankInterestRatesData],
    ]
):
    """FRED ECB Interest Rates Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FREDEuropeanCentralBankInterestRatesParams:
        """Transform query."""
        return FREDEuropeanCentralBankInterestRatesParams(**params)

    @staticmethod
    def extract_data(
        query: FREDEuropeanCentralBankInterestRatesParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        from openbb_fred.utils.fred_base import Fred

        key = credentials.get("fred_api_key") if credentials else ""
        fred = Fred(key)

        data = fred.get_series(
            series_id=NAME_TO_ID_ECB[query.interest_rate_type],
            start_date=query.start_date,
            end_date=query.end_date,
            **kwargs,
        )

        return data

    @staticmethod
    def transform_data(
        query: FREDEuropeanCentralBankInterestRatesParams, data: List, **kwargs: Any
    ) -> List[FREDEuropeanCentralBankInterestRatesData]:
        """Transform data."""
        return [
            FREDEuropeanCentralBankInterestRatesData.model_validate(d) for d in data
        ]
