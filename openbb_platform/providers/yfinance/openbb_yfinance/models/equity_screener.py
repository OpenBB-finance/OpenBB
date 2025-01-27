"""YFinance Equity Screener Model."""

# pylint: disable=unused-argument, too-many-statements, too-many-branches

from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_screener import (
    EquityScreenerData,
    EquityScreenerQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.references import (
    COUNTRIES,
    EXCHANGES,
    INDUSTRIES,
    INDUSTRY_MAP,
    PEER_GROUPS,
    SECTOR_MAP,
    SECTORS,
    Exchanges,
    YFPredefinedScreenerData,
    get_industry_sector,
)
from pydantic import Field


class YFinanceEquityScreenerQueryParams(EquityScreenerQueryParams):
    """YFinance Equity Screener Query."""

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": False,
            "choices": COUNTRIES,
        },
        "exchange": {
            "multiple_items_allowed": False,
            "choices": EXCHANGES,
        },
        "sector": {
            "multiple_items_allowed": False,
            "choices": list(SECTOR_MAP),
        },
        "industry": {
            "multiple_items_allowed": False,
            "choices": INDUSTRIES,
        },
    }

    country: Optional[str] = Field(
        default="us",
        description="Filter by country, as a two-letter country code. Default is, 'us'. Use, 'all', for all countries.",
    )
    exchange: Optional[Exchanges] = Field(
        default=None,
        description="Filter by exchange.",
    )
    sector: Optional[SECTORS] = Field(default=None, description="Filter by sector.")
    industry: Optional[str] = Field(
        default=None,
        description="Filter by industry.",
    )
    mktcap_min: Optional[int] = Field(
        default=500000000,
        description="Filter by market cap greater than this value. Default is 500M.",
    )
    mktcap_max: Optional[int] = Field(
        default=None,
        description="Filter by market cap less than this value.",
    )
    price_min: Optional[float] = Field(
        default=5,
        description="Filter by price greater than this value. Default is, 5",
    )
    price_max: Optional[float] = Field(
        default=None,
        description="Filter by price less than this value.",
    )
    volume_min: Optional[int] = Field(
        default=10000,
        description="Filter by volume greater than this value. Default is, 10K",
    )
    volume_max: Optional[int] = Field(
        default=None,
        description="Filter by volume less than this value.",
    )
    beta_min: Optional[float] = Field(
        default=None,
        description="Filter by a beta greater than this value.",
    )
    beta_max: Optional[float] = Field(
        default=None,
        description="Filter by a beta less than this value.",
    )
    limit: Optional[int] = Field(
        default=200,
        description="Limit the number of results returned. Default is, 200. Set to, 0, for all results.",
    )


class YFinanceEquityScreenerData(EquityScreenerData, YFPredefinedScreenerData):
    """YFinance Equity Screener Data."""


class YFinanceEquityScreenerFetcher(
    Fetcher[YFinanceEquityScreenerQueryParams, list[YFinanceEquityScreenerData]]
):
    """YFinance Equity Screener Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceEquityScreenerQueryParams:
        """Transform query."""
        sector = params.get("sector")
        industry = params.get("industry")

        if industry and sector:
            sec = get_industry_sector(industry)
            if sec and sec != sector:
                choices = "\n    ".join(sorted(INDUSTRY_MAP[sector]))
                raise OpenBBError(
                    ValueError(
                        f"Industry {industry} does not belong to sector {sector}."
                        " Valid choices are:" + "\n\n    " + f"{choices}"
                    )
                )
        elif industry and not sector:
            choices = "\n".join(INDUSTRIES)
            sector = get_industry_sector(industry)
            if not sector:
                raise OpenBBError(
                    ValueError(
                        f"Industry {industry} not found. Valid choices are:"
                        "\n" + f"{choices}"
                    )
                )
            _industry = INDUSTRY_MAP[sector][industry]

            if _industry not in PEER_GROUPS:
                params["sector"] = get_industry_sector(industry)

        return YFinanceEquityScreenerQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceEquityScreenerQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the raw data."""
        # pylint: disable=import-outside-toplevel
        from openbb_yfinance.utils.helpers import get_custom_screener

        operands: list = []

        if query.exchange is not None:
            operands.append(
                {"operator": "eq", "operands": ["exchange", query.exchange.upper()]}
            )
            query.country = "all"

        if query.country and query.country != "all":
            operands.append({"operator": "EQ", "operands": ["region", query.country]})

        if query.sector is not None:
            sector = SECTOR_MAP[query.sector]
            operands.append({"operator": "EQ", "operands": ["sector", sector]})

        if query.industry is not None:
            sector = (
                query.sector
                if query.sector is not None
                else get_industry_sector(query.industry)
            )
            industry = INDUSTRY_MAP[sector][query.industry]
            if industry in PEER_GROUPS:
                operands.append(
                    {"operator": "EQ", "operands": ["peer_group", industry]}
                )
            else:
                operands.append({"operator": "EQ", "operands": ["industry", industry]})

        if query.mktcap_min is not None:
            operands.append(
                {"operator": "gt", "operands": ["intradaymarketcap", query.mktcap_min]}
            )

        if query.mktcap_max is not None:
            operands.append(
                {"operator": "lt", "operands": ["intradaymarketcap", query.mktcap_max]}
            )

        if query.price_min is not None:
            operands.append(
                {"operator": "gt", "operands": ["intradayprice", query.price_min]}
            )

        if query.price_max is not None:
            operands.append(
                {"operator": "lt", "operands": ["intradayprice", query.price_max]}
            )

        if query.volume_min is not None:
            operands.append(
                {"operator": "gt", "operands": ["dayvolume", query.volume_min]}
            )

        if query.volume_max is not None:
            operands.append(
                {"operator": "lt", "operands": ["dayvolume", query.volume_max]}
            )

        if query.beta_min is not None:
            operands.append({"operator": "gt", "operands": ["beta", query.beta_min]})

        if query.beta_max is not None:
            operands.append({"operator": "lt", "operands": ["beta", query.beta_max]})

        payload = {
            "offset": 0,
            "size": 100,
            "sortField": "percentchange",
            "sortType": "DESC",
            "quoteType": "EQUITY",
            "query": {
                "operands": operands,
                "operator": "AND",
            },
            "userId": "",
            "userIdType": "guid",
        }

        response = await get_custom_screener(
            body=payload,
            limit=query.limit if query.limit and query.limit not in (0, None) else None,
        )

        if not response:
            raise EmptyDataError("No results found for the combination of filters.")

        return response

    @staticmethod
    def transform_data(
        query: YFinanceEquityScreenerQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceEquityScreenerData]:
        """Transform the data."""
        return [YFinanceEquityScreenerData(**d) for d in data]
