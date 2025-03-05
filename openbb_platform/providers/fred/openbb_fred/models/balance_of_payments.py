"""FRED Balance Of Payments Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_of_payments import (
    BalanceOfPaymentsQueryParams,
    BP6BopUsdData,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fred.models.series import (
    FredSeriesFetcher,
    FredSeriesQueryParams,
)
from openbb_fred.utils.fred_helpers import (
    BOP_COUNTRIES,
    BOP_COUNTRY_CHOICES,
    get_bop_series,
)
from pydantic import Field, field_validator


class FredBalanceOfPaymentsQueryParams(BalanceOfPaymentsQueryParams):
    """FRED Balance Of Payments Query Parameters."""

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": False,
            "choices": list(BOP_COUNTRIES),
        }
    }

    country: BOP_COUNTRY_CHOICES = Field(
        default="united_states",
        description=QUERY_DESCRIPTIONS.get("country", "")
        + " Enter as a 3-letter ISO country code, default is USA.",
    )
    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class FredBalanceOfPaymentsData(BP6BopUsdData):
    """FRED Balance Of Payments Data."""

    __alias_dict__ = {"period": "date"}

    @field_validator(
        "balance_percent_of_gdp",
        "credits_services_percent_of_goods_and_services",
        "credits_services_percent_of_current_account",
        "debits_services_percent_of_goods_and_services",
        "debits_services_percent_of_current_account",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Normalize the percent value."""
        return float(v) / 100 if v else None


class FredBalanceOfPaymentsFetcher(
    Fetcher[FredBalanceOfPaymentsQueryParams, List[FredBalanceOfPaymentsData]]
):
    """FRED Balance Of Payments Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredBalanceOfPaymentsQueryParams:
        """Transform query."""
        return FredBalanceOfPaymentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredBalanceOfPaymentsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data."""
        fred_fetcher = FredSeriesFetcher()
        country = BOP_COUNTRIES.get(query.country) if query.country else "USA"
        query_dict = query.model_dump(exclude_none=True)
        query_dict["symbol"] = ",".join(list(get_bop_series(country).values()))
        fred_query = FredSeriesQueryParams(**query_dict)
        data = await fred_fetcher.aextract_data(fred_query, credentials)
        return data

    @staticmethod
    def transform_data(
        query: FredBalanceOfPaymentsQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[FredBalanceOfPaymentsData]]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        if not data:
            raise EmptyDataError(f"No data was found for, {query.country}.")
        fred_fetcher = FredSeriesFetcher()
        country = BOP_COUNTRIES.get(query.country) if query.country else "USA"
        query_dict = query.model_dump(exclude_none=True)
        query_dict["symbol"] = ",".join(list(get_bop_series(country).values()))
        fred_query = FredSeriesQueryParams(**query_dict)
        data = fred_fetcher.transform_data(fred_query, data)
        series_ids = get_bop_series(country)
        col_map = {v: k for k, v in series_ids.items()}
        result = data.result  # type: ignore
        df = (
            DataFrame([d.model_dump() for d in result])
            .set_index("date")
            .sort_index(ascending=False)
        )
        df = df.rename(columns=col_map)
        records = df.reset_index().fillna("N/A").replace("N/A", None).to_dict("records")

        return AnnotatedResult(
            result=[FredBalanceOfPaymentsData.model_validate(r) for r in records],
            metadata=data.metadata,  # type: ignore
        )
