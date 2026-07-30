"""Cboe Futures Settlements Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class CboeFuturesSettlementsQueryParams(QueryParams):
    """Cboe Futures Settlements Query.

    Source: https://www.cboe.com/
    """

    date: dateType | None = Field(
        default=None,
        description="The settlement date. Sessions that settled nothing, such as"
        + " weekends and holidays, fall back to the most recent session that did.",
    )
    options: bool = Field(
        default=False,
        description="When True, returns options on futures.",
    )
    archives: bool = Field(
        default=False,
        description="Settlement price archives for select years and products."
        + " Overridden by the other parameters.",
    )
    final_settlement: bool = Field(
        default=False,
        description="Final settlement prices for expired contracts."
        + " Overrides archives.",
    )


class CboeFuturesSettlementsData(Data):
    """Cboe Futures Settlements Data."""

    product: str | None = Field(
        default=None, description="The product family of the contract."
    )
    symbol: str | None = Field(default=None, description="The contract symbol.")
    expiration: str | None = Field(
        default=None, description="The expiration date of the contract."
    )
    price: float | None = Field(
        default=None,
        description="The settlement price of the contract.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    duration_type: str | None = Field(
        default=None, description="The duration classification of the contract."
    )
    settlement_date: dateType | None = Field(
        default=None, description="The session the prices settled on."
    )
    settlement_price: float | None = Field(
        default=None,
        description="The final settlement price, for archived contracts.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    settlement_month: int | None = Field(
        default=None, description="The settlement month, for archived contracts."
    )
    settlement_year: int | None = Field(
        default=None, description="The settlement year, for archived contracts."
    )
    product_type: str | None = Field(
        default=None, description="The product type, for archived contracts."
    )
    product_description: str | None = Field(
        default=None, description="The product description, for archived contracts."
    )

    @field_validator("settlement_date", mode="before", check_fields=False)
    @classmethod
    def validate_settlement_date(cls, v):
        """Parse the settlement date from either ISO or US formatting."""
        from pandas import to_datetime

        return to_datetime(v).date() if v else None


class CboeFuturesSettlementsFetcher(
    Fetcher[
        CboeFuturesSettlementsQueryParams,
        list[CboeFuturesSettlementsData],
    ]
):
    """Transform the query, extract and transform the data from the Cboe endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CboeFuturesSettlementsQueryParams:
        """Transform the query."""
        return CboeFuturesSettlementsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeFuturesSettlementsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Cboe endpoint.

        Raises
        ------
        EmptyDataError
            If no session within the lookback published settlement prices.
        """
        from openbb_cboe.utils.helpers import get_settlement_prices

        data = await get_settlement_prices(
            settlement_date=query.date,
            options=query.options,
            archives=query.archives,
            final_settlement=query.final_settlement,
        )

        if data.empty:
            raise EmptyDataError("No settlement prices were published.")

        data = data.astype(object).where(data.notna(), None)

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: CboeFuturesSettlementsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CboeFuturesSettlementsData]:
        """Transform the data to the model."""
        return [CboeFuturesSettlementsData.model_validate(record) for record in data]
