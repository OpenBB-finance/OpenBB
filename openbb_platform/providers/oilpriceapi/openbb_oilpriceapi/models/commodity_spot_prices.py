"""OilPriceAPI Commodity Spot Prices Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.commodity_spot_prices import (
    CommoditySpotPricesData,
    CommoditySpotPricesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_oilpriceapi.utils.constants import BASE_URL, COMMODITY_CHOICES


class OilPriceAPICommoditySpotPricesQueryParams(CommoditySpotPricesQueryParams):
    """OilPriceAPI Commodity Spot Prices Query.

    Source: https://docs.oilpriceapi.com
    """

    __json_schema_extra__ = {
        "commodity": {"multiple_items_allowed": False, "choices": COMMODITY_CHOICES},
    }

    commodity: str = Field(
        default="brent",
        description="Commodity to get the spot price for. Any code accepted by"
        + " OilPriceAPI's /v1/commodities catalogue is valid; the listed choices are"
        + " the most commonly used subset.",
    )

    @field_validator("commodity", mode="before", check_fields=False)
    @classmethod
    def _normalize_commodity(cls, v):
        """Accept friendly aliases and raw OilPriceAPI codes interchangeably."""
        if not v:
            return "brent"
        return str(v).strip().lower()


class OilPriceAPICommoditySpotPricesData(CommoditySpotPricesData):
    """OilPriceAPI Commodity Spot Prices Data."""

    currency: Optional[str] = Field(
        default=None,
        description="Currency the price is denominated in.",
    )


class OilPriceAPICommoditySpotPricesFetcher(
    Fetcher[
        OilPriceAPICommoditySpotPricesQueryParams,
        list[OilPriceAPICommoditySpotPricesData],
    ]
):
    """OilPriceAPI Commodity Spot Prices Fetcher."""

    require_credentials = True

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> OilPriceAPICommoditySpotPricesQueryParams:
        """Transform the query parameters."""
        return OilPriceAPICommoditySpotPricesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: OilPriceAPICommoditySpotPricesQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from OilPriceAPI."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.helpers import amake_request

        api_key = (credentials or {}).get("oilpriceapi_api_key")
        headers = {"Authorization": f"Token {api_key}"}
        code = COMMODITY_CHOICES.get(query.commodity, query.commodity.upper())

        if query.start_date or query.end_date:
            url = f"{BASE_URL}/prices/historical?by_code={code}&by_period=day"
        else:
            url = f"{BASE_URL}/prices/latest?by_code={code}"

        response = await amake_request(url, headers=headers, **kwargs)

        if not isinstance(response, dict):
            raise OpenBBError(f"Unexpected response from OilPriceAPI -> {response}")

        # The API self-documents its failures: the error envelope carries a code,
        # a request_id and a docs deep-link. Surface them rather than a bare status.
        if error := response.get("error"):
            raise OpenBBError(
                f"OilPriceAPI error -> {error.get('code')}: {error.get('message')}"
                + f" (request_id {error.get('request_id')})"
            )

        data = response.get("data")
        if not data:
            raise EmptyDataError(f"No data found for commodity '{query.commodity}'.")

        records = data.get("prices") if isinstance(data, dict) else None
        if records is None:
            records = [data] if isinstance(data, dict) else list(data)

        if not records:
            raise EmptyDataError(f"No data found for commodity '{query.commodity}'.")

        return records

    @staticmethod
    def transform_data(
        query: OilPriceAPICommoditySpotPricesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[OilPriceAPICommoditySpotPricesData]:
        """Transform the raw records into the standard model."""
        results: list[OilPriceAPICommoditySpotPricesData] = []
        parsed = 0

        for row in data:
            price = row.get("price")
            if price is None:
                continue

            # `created_at` is the observation timestamp on both endpoints.
            stamp = row.get("created_at") or row.get("as_of") or row.get("updated_at")
            if not stamp:
                continue
            observed = dateType.fromisoformat(str(stamp)[:10])
            parsed += 1

            if query.start_date and observed < query.start_date:
                continue
            if query.end_date and observed > query.end_date:
                continue

            results.append(
                OilPriceAPICommoditySpotPricesData.model_validate(
                    {
                        "date": observed,
                        "symbol": row.get("code"),
                        "commodity": query.commodity,
                        "price": float(price),
                        "unit": row.get("unit"),
                        "currency": row.get("currency"),
                    }
                )
            )

        if not results:
            # Distinguish "that commodity returned nothing usable" from "the
            # commodity is fine but your window is empty" — they need different fixes.
            if parsed == 0:
                raise EmptyDataError(
                    f"No usable records for commodity '{query.commodity}'."
                    + " Check the code against GET /v1/commodities."
                )
            raise EmptyDataError(
                f"'{query.commodity}' returned {parsed} record(s), none within"
                + f" {query.start_date} to {query.end_date}."
            )

        return sorted(results, key=lambda r: r.date)
