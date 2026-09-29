"""FINRA Equity List Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FinraEquityListQueryParams(QueryParams):
    """FINRA Equity List Query."""

    security_type: Literal["all", "stock", "etf", "closed_end_fund", "other"] = Field(
        default="all",
        description="The type of security to list. Other is every symbol without a"
        + " stock, ETF, or closed-end fund type - warrants, rights, units, and"
        + " securities the Market Data Center does not classify.",
    )


class FinraEquityListData(Data):
    """FINRA Equity List Data."""

    symbol: str = Field(description="The FINRA symbol.")
    name: str | None = Field(
        default=None, description="The Morningstar name of the security."
    )
    issue_name: str | None = Field(
        default=None, description="The FINRA name of the issue."
    )
    security_type: str | None = Field(
        default=None,
        description="The Morningstar security type - Stock, ETF, Closed-End Fund,"
        + " or Open-End Fund.",
    )
    security_description: str | None = Field(
        default=None,
        description="The share class, or the Morningstar category of a fund.",
    )
    tier: str | None = Field(
        default=None,
        description="The FINRA tier - NMS Tier 1, NMS Tier 2, or OTC equities.",
    )
    product_type: str | None = Field(
        default=None,
        description="The FINRA product type - Nasdaq-listed, NYSE and regional"
        + " exchange-listed, or OTC equity.",
    )
    exchange: str | None = Field(
        default=None, description="The Market Identifier Code of the listing venue."
    )
    listing_market: str | None = Field(
        default=None, description="The Market Data Center name of the listing exchange."
    )
    composite_market: str | None = Field(
        default=None, description="The Market Data Center name of the composite market."
    )
    country: str | None = Field(
        default=None, description="The ISO 3166 alpha-3 code of the listing region."
    )
    domicile: str | None = Field(
        default=None, description="The ISO 3166 alpha-3 code of the domicile."
    )
    currency: str | None = Field(default=None, description="The trading currency.")
    security_id: str | None = Field(
        default=None, description="The Morningstar security id."
    )
    performance_id: str | None = Field(
        default=None, description="The Morningstar performance id."
    )
    quote_symbol: str | None = Field(
        default=None,
        description="The real-time quote key - composite market, type, and symbol.",
    )
    url: str | None = Field(
        default=None, description="The security's page on the FINRA Market Data Center."
    )


class FinraEquityListFetcher(
    Fetcher[FinraEquityListQueryParams, list[FinraEquityListData]]
):
    """Transform the query, extract and transform the data from FINRA."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinraEquityListQueryParams:
        """Transform the query."""
        return FinraEquityListQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FinraEquityListQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return every traded security of one type.

        Raises
        ------
        EmptyDataError
            If no security of the type was found.
        """
        from openbb_finra.utils.constants import SECURITY_LIST_TYPES
        from openbb_finra.utils.directory import list_securities

        rows = await list_securities()
        typed = set(SECURITY_LIST_TYPES.values())

        if query.security_type == "other":
            rows = [row for row in rows if row.get("security_type") not in typed]
        elif query.security_type != "all":
            code = SECURITY_LIST_TYPES[query.security_type]
            rows = [row for row in rows if row.get("security_type") == code]

        if not rows:
            raise EmptyDataError(f"No {query.security_type} securities were found.")

        return rows

    @staticmethod
    def transform_data(
        query: FinraEquityListQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FinraEquityListData]:
        """Transform the data to the model."""
        from openbb_finra.utils.constants import EQUITY_PRODUCT_TYPES, SECURITY_TYPES
        from openbb_finra.utils.helpers import decode, market_names

        rows = []

        for row in data:
            values = {
                key: value
                for key, value in row.items()
                if key not in ("listing_market_id", "composite_exchange_id")
            }
            rows.append(
                FinraEquityListData.model_validate(
                    {
                        **values,
                        "security_type": decode(
                            SECURITY_TYPES, row.get("security_type")
                        ),
                        "product_type": decode(
                            EQUITY_PRODUCT_TYPES, row.get("product_type")
                        ),
                        "listing_market": decode(
                            market_names(), row.get("listing_market_id")
                        ),
                        "composite_market": decode(
                            market_names(), row.get("composite_exchange_id")
                        ),
                    }
                )
            )

        return rows
