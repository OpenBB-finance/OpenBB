"""CME contract specifications model."""

import asyncio
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, model_validator

from openbb_cme.utils.catalog import (
    fetch_contract_specifications,
    search_products,
)
from openbb_cme.utils.client import CMEHttpClient


class CMEContractSpecsQueryParams(QueryParams):
    """Identify CME products by product ID or published product code."""

    product_id: int | None = Field(
        default=None, description="Exact CME website product identifier."
    )
    symbol: str | None = Field(
        default=None,
        description="Exact Globex, clearing, ClearPort, floor, or product code.",
    )
    product_type: Literal["Futures", "Options"] | None = Field(
        default=None,
        description="Optional disambiguation for a product code.",
    )

    @model_validator(mode="after")
    def require_identifier(self):
        """Require a product ID or symbol."""
        if self.product_id is None and not self.symbol:
            raise ValueError("Either product_id or symbol must be supplied.")
        if self.symbol:
            self.symbol = self.symbol.strip().upper()
        return self


class CMEContractSpecsData(Data):
    """Complete exchange-published contract specifications for one CME product."""

    product_id: int = Field(description="CME website product identifier.")
    symbol: str = Field(description="Preferred Globex or clearing product code.")
    name: str = Field(description="Exchange-published product name.")
    product_type: str = Field(description="Futures or Options.")
    asset_class: str = Field(description="CME product group or asset class.")
    subgroup: str | None = Field(default=None, description="CME product subgroup.")
    exchange: str = Field(description="Listing exchange.")
    specification_url: str | None = Field(
        default=None, description="Official CME contract-specification URL."
    )
    contract_unit: str | None = Field(default=None, description="Contract unit.")
    price_quotation: str | None = Field(default=None, description="Price quotation.")
    minimum_price_fluctuation: dict | str | None = Field(
        default=None, description="Minimum tick rules."
    )
    product_codes: dict | str | None = Field(
        default=None, description="Product codes by venue or trade type."
    )
    listed_contracts: dict | str | None = Field(
        default=None, description="Contract listing cycle."
    )
    trading_hours: dict | str | None = Field(
        default=None, description="Trading hours by venue."
    )
    settlement_method: str | None = Field(
        default=None, description="Settlement method."
    )
    termination_of_trading: dict | str | None = Field(
        default=None, description="Termination-of-trading rules."
    )
    exercise_style: str | None = Field(
        default=None, description="Option exercise style."
    )
    exercise_procedure: str | None = Field(
        default=None, description="Option exercise procedure."
    )
    settlement_at_expiration: str | None = Field(
        default=None, description="Option settlement at expiration."
    )
    underlying: str | None = Field(
        default=None, description="Underlying futures contract."
    )
    specifications: dict[str, Any] = Field(
        description="Complete normalized CME specification payload."
    )


class CMEContractSpecsFetcher(
    Fetcher[CMEContractSpecsQueryParams, list[CMEContractSpecsData]]
):
    """Fetch complete contract specifications for CME products."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CMEContractSpecsQueryParams:
        """Transform query parameters."""
        return CMEContractSpecsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CMEContractSpecsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Resolve products and fetch their public specifications."""
        async with CMEHttpClient() as client:
            if query.product_id is not None:
                all_products = await search_products(
                    product_type=query.product_type,
                    client=client,
                )
                products = [
                    row for row in all_products if row["product_id"] == query.product_id
                ]
            else:
                products = await search_products(
                    symbol=query.symbol,
                    product_type=query.product_type,
                    client=client,
                )
            if not products:
                raise EmptyDataError("No CME product matched the supplied identifier.")

            specs = await asyncio.gather(
                *[
                    fetch_contract_specifications(product["product_id"], client)
                    for product in products
                ]
            )
        results = []
        for product, specification in zip(products, specs):
            if not specification:
                continue
            results.append(
                {
                    **product,
                    "contract_unit": specification.get("ContractUnit"),
                    "price_quotation": specification.get("PriceQuotation"),
                    "minimum_price_fluctuation": specification.get(
                        "MinimumPriceFluctuation"
                    ),
                    "product_codes": specification.get("ProductCode"),
                    "listed_contracts": specification.get("ListedContracts"),
                    "trading_hours": specification.get("TradingHours"),
                    "settlement_method": specification.get("SettlementMethod"),
                    "termination_of_trading": specification.get("TerminationOfTrading"),
                    "exercise_style": specification.get("ExerciseStyle"),
                    "exercise_procedure": specification.get("ExerciseProcedure"),
                    "settlement_at_expiration": specification.get(
                        "SettlementAtExpiration"
                    ),
                    "underlying": specification.get("Underlying"),
                    "specifications": specification,
                }
            )
        if not results:
            raise EmptyDataError("No contract specifications were returned by CME.")
        return results

    @staticmethod
    def transform_data(
        query: CMEContractSpecsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CMEContractSpecsData]:
        """Validate contract specification rows."""
        return [CMEContractSpecsData.model_validate(row) for row in data]
