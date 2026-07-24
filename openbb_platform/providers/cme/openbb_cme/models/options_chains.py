"""CME options-on-futures chains model."""

import asyncio
import re
from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_cme.utils.catalog import (
    fetch_contract_specifications,
    resolve_product,
    search_products,
)
from openbb_cme.utils.client import CMEHttpClient
from openbb_cme.utils.helpers import (
    fetch_option_expirations,
    fetch_option_settlements,
    parse_cme_value,
)

_REQUEST_SEMAPHORE_LIMIT = 10


class CMEOptionsChainsQueryParams(OptionsChainsQueryParams):
    """CME options-on-futures settlement chain query."""

    product_id: int | None = Field(
        default=None,
        description=(
            "Exact CME option product ID. Use cme.products to disambiguate "
            "product codes with multiple option families."
        ),
    )
    expiration: dateType | None = Field(
        default=None,
        description="Filter to an exact option expiration date.",
    )
    date: dateType | None = Field(
        default=None,
        description="Historical settlement date; defaults to the latest available.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        """Normalize the option product code."""
        result = str(value).strip().upper()
        if not result:
            raise ValueError("Symbol cannot be empty.")
        return result


class CMEOptionsChainsData(OptionsChainsData):
    """End-of-day CME options-on-futures chain."""

    settlement_price: list[float | None] = Field(
        default_factory=list,
        description="Official CME option settlement price.",
    )
    change: list[float | None] = Field(
        default_factory=list,
        description="Change from the previous settlement.",
    )
    product_id: list[int] = Field(description="CME option product identifier.")
    product_name: list[str] = Field(description="CME option product name.")


class CMEOptionsChainsFetcher(
    Fetcher[CMEOptionsChainsQueryParams, CMEOptionsChainsData]
):
    """Fetch CME options-on-futures settlement chains."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CMEOptionsChainsQueryParams:
        """Transform query parameters."""
        return CMEOptionsChainsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CMEOptionsChainsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch every selected expiration concurrently."""
        async with CMEHttpClient() as client:
            if query.product_id is not None:
                products = await search_products(
                    symbol=query.symbol,
                    product_type="Options",
                    client=client,
                )
                product = next(
                    (row for row in products if row["product_id"] == query.product_id),
                    None,
                )
            else:
                product = await resolve_product(query.symbol, "Options", client=client)

            if not product:
                raise ValueError(
                    f"Symbol '{query.symbol}' was not found in the CME options catalog."
                )

            expirations, specs = await asyncio.gather(
                fetch_option_expirations(product["product_id"], client),
                fetch_contract_specifications(product["product_id"], client),
            )
            if query.expiration:
                expirations = [
                    row
                    for row in expirations
                    if row.get("expiration_date") == query.expiration
                ]
            expirations = [
                row
                for row in expirations
                if row.get("expiration_date")
                and row.get("month_year")
                and row.get("contract_id")
                and row.get("trade_dates")
            ]
            if not expirations:
                raise EmptyDataError("No CME option expirations matched the query.")

            contract_unit = str(specs.get("ContractUnit") or "")
            size_match = re.search(r"\d+(?:,\d{3})*(?:\.\d+)?", contract_unit)
            contract_size = (
                float(size_match.group().replace(",", "")) if size_match else None
            )
            semaphore = asyncio.Semaphore(_REQUEST_SEMAPHORE_LIMIT)

            async def fetch_one(expiration: dict) -> list[dict]:
                available_dates = expiration["trade_dates"]
                if query.date:
                    formatted = query.date.strftime("%m/%d/%Y")
                    if formatted not in available_dates:
                        return []
                    trade_date = query.date
                else:
                    month, day, year = available_dates[0].split("/")
                    trade_date = dateType(int(year), int(month), int(day))

                async with semaphore:
                    settlements = await fetch_option_settlements(
                        expiration["product_id"],
                        expiration["month_year"],
                        expiration["contract_id"],
                        trade_date,
                        client,
                    )

                expiration_date = expiration["expiration_date"]
                results = []
                for row in settlements:
                    strike = parse_cme_value(row.get("strike"))
                    option_type = str(row.get("type", "")).lower()
                    if strike is None or option_type not in {"call", "put"}:
                        continue
                    suffix = "C" if option_type == "call" else "P"
                    results.append(
                        {
                            "underlying_symbol": query.symbol,
                            "underlying_price": None,
                            "contract_symbol": (
                                f"{expiration['contract_id']}-{strike:g}-{suffix}"
                            ),
                            "eod_date": trade_date,
                            "expiration": expiration_date,
                            "dte": (expiration_date - trade_date).days,
                            "strike": strike,
                            "option_type": option_type,
                            "contract_size": contract_size,
                            "open_interest": parse_cme_value(row.get("openInterest")),
                            "volume": parse_cme_value(row.get("volume")),
                            "last_trade_price": parse_cme_value(row.get("last")),
                            "open": parse_cme_value(row.get("open")),
                            "high": parse_cme_value(row.get("high")),
                            "low": parse_cme_value(row.get("low")),
                            "settlement_price": parse_cme_value(row.get("settle")),
                            "change": parse_cme_value(row.get("change")),
                            "product_id": expiration["product_id"],
                            "product_name": product["name"],
                        }
                    )
                return results

            nested = await asyncio.gather(
                *(fetch_one(expiration) for expiration in expirations)
            )
            rows = [row for result in nested for row in result]
        if not rows:
            raise EmptyDataError("No CME option settlements matched the query.")
        return sorted(
            rows,
            key=lambda row: (
                row["expiration"],
                row["strike"],
                row["option_type"],
            ),
        )

    @staticmethod
    def transform_data(
        query: CMEOptionsChainsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> CMEOptionsChainsData:
        """Convert row-oriented CME settlements to the standard columnar model."""
        columns = {key: [row.get(key) for row in data] for key in data[0]}
        return CMEOptionsChainsData.model_validate(columns)
