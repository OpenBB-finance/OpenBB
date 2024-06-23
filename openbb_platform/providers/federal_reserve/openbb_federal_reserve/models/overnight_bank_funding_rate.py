"""Federal Reserve Federal Funds Rate Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.overnight_bank_funding_rate import (
    OvernightBankFundingRateData,
    OvernightBankFundingRateQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class FederalReserveOvernightBankFundingRateQueryParams(
    OvernightBankFundingRateQueryParams
):
    """FederalReserve Overnight Bank Funding Rate Query."""


class FederalReserveOvernightBankFundingRateData(OvernightBankFundingRateData):
    """FederalReserve Overnight Bank Funding Rate Data."""

    __alias_dict__ = {
        "date": "effectiveDate",
        "rate": "percentRate",
        "percentile_1": "percentPercentile1",
        "percentile_25": "percentPercentile25",
        "percentile_75": "percentPercentile75",
        "percentile_99": "percentPercentile99",
        "volume": "volumeInBillions",
    }

    revision_indicator: Optional[str] = Field(
        default=None,
        description="Indicates a revision of the data for that date.",
    )

    @field_validator("revision_indicator", mode="before", check_fields=False)
    @classmethod
    def validate_revision_indicator(cls, v):
        """Validate revision indicator."""
        return None if v in ("", "''") else v

    @field_validator(
        "rate",
        "percentile_1",
        "percentile_25",
        "percentile_75",
        "percentile_99",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent."""
        if v is not None:
            return v / 100 if v != 0 else 0
        return None


class FederalReserveOvernightBankFundingRateFetcher(
    Fetcher[
        FederalReserveOvernightBankFundingRateQueryParams,
        List[FederalReserveOvernightBankFundingRateData],
    ]
):
    """Federal Reserve Federal Funds Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FederalReserveOvernightBankFundingRateQueryParams:
        """Transform query."""
        transformed_params = params.copy()
        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = datetime(2016, 3, 1).date()
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FederalReserveOvernightBankFundingRateQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FederalReserveOvernightBankFundingRateQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request

        url = (
            "https://markets.newyorkfed.org/api/rates/unsecured/obfr/search.json?"
            + f"startDate={query.start_date}&endDate={query.end_date}"
        )
        results: List[Dict] = []
        response = await amake_request(url, **kwargs)
        if response.get("refRates", []):  # type: ignore
            results = response["refRates"]  # type: ignore
        if not results:
            raise EmptyDataError()
        return results

    @staticmethod
    def transform_data(
        query: FederalReserveOvernightBankFundingRateQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FederalReserveOvernightBankFundingRateData]:
        """Transform data."""
        results: List[FederalReserveOvernightBankFundingRateData] = []
        for d in data.copy():
            _ = d.pop("type", None)
            _ = d.pop("revisionIndicator", None)
            _ = d.pop("footnoteId", None)
            results.append(FederalReserveOvernightBankFundingRateData.model_validate(d))

        return results
