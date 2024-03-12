"""Intrinio Insider Trading Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional, Union

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.insider_trading import (
    InsiderTradingData,
    InsiderTradingQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import get_data_many
from pydantic import Field, model_validator


class IntrinioInsiderTradingQueryParams(InsiderTradingQueryParams):
    """Intrinio Insider Trading Query.

    Source: https://docs.intrinio.com/documentation/web_api/insider_transaction_filings_by_company_v2
    """

    __alias_dict__ = {"limit": "page_size"}

    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", "")
    )
    ownership_type: Optional[Literal["D", "I"]] = Field(
        default=None,
        description="Type of ownership.",
    )
    sort_by: Optional[Literal["filing_date", "updated_on"]] = Field(
        default="updated_on",
        description="Field to sort by.",
    )


class IntrinioInsiderTradingData(InsiderTradingData):
    """Intrinio Insider Trading Data."""

    __alias_dict__ = {
        "owner_title": "officer_title",
        "transaction_type": "transaction_type_code",
        "acquisition_or_disposition": "acquisition_disposition_code",
        "security_type": "security_title",
        "securities_owned": "total_shares_owned",
        "securities_transacted": "amount_of_shares",
    }

    company_name: str = Field(description="Name of the company.")
    conversion_exercise_price: Optional[float] = Field(
        default=None,
        description="Conversion/Exercise price of the shares.",
    )
    deemed_execution_date: Optional[dateType] = Field(
        default=None,
        description="Deemed execution date of the trade.",
    )
    exercise_date: Optional[dateType] = Field(
        default=None,
        description="Exercise date of the trade.",
    )
    expiration_date: Optional[dateType] = Field(
        default=None,
        description="Expiration date of the derivative.",
    )
    underlying_security_title: Optional[str] = Field(
        default=None,
        description="Name of the underlying non-derivative security related to this derivative transaction.",
    )
    underlying_shares: Optional[Union[int, float]] = Field(
        default=None,
        description="Number of underlying shares related to this derivative transaction.",
    )
    nature_of_ownership: Optional[str] = Field(
        default=None,
        description="Nature of ownership of the insider trading.",
    )
    director: Optional[bool] = Field(
        default=None, description="Whether the owner is a director."
    )
    officer: Optional[bool] = Field(
        default=None, description="Whether the owner is an officer."
    )
    ten_percent_owner: Optional[bool] = Field(
        default=None, description="Whether the owner is a 10% owner."
    )
    other_relation: Optional[bool] = Field(
        default=None, description="Whether the owner is having another relation."
    )
    derivative_transaction: Optional[bool] = Field(
        default=None,
        description="Whether the owner is having a derivative transaction.",
    )
    report_line_number: Optional[int] = Field(
        default=None, description="Report line number of the insider trading."
    )
    filing_url: Optional[str] = Field(default=None, description="URL of the filing.")

    @model_validator(mode="before")
    @classmethod
    def empty_strings(cls, values):  # pylint: disable=no-self-argument
        """Check for empty strings and replace with None."""
        return (
            {k: None if v == "" else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class IntrinioInsiderTradingFetcher(
    Fetcher[
        IntrinioInsiderTradingQueryParams,
        List[IntrinioInsiderTradingData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioInsiderTradingQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=5)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioInsiderTradingQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioInsiderTradingQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com/companies"
        query_str = get_querystring(query.model_dump(by_alias=True), ["symbol"])
        url = f"{base_url}/{query.symbol}/insider_transaction_filings?{query_str}&api_key={api_key}"

        return await get_data_many(url, "transaction_filings", **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioInsiderTradingQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioInsiderTradingData]:
        """Return the transformed data."""
        transformed_data: List[Dict] = []

        for item in data:
            transformed_data.extend(
                [
                    {
                        **sub_item,
                        "filing_date": item["filing_date"],
                        "filing_url": item["filing_url"],
                        "symbol": item["issuer_ticker"],
                        "company_cik": item["issuer_cik"],
                        "company_name": item["issuer_company"],
                        "owner_cik": item["owner"]["owner_cik"],
                        "owner_name": item["owner"]["owner_name"],
                    }
                    for sub_item in item["transactions"]
                ]
            )

        return [IntrinioInsiderTradingData.model_validate(d) for d in transformed_data]
