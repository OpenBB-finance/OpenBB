"""Nasdaq Equity Screener Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_screener import (
    EquityScreenerData,
    EquityScreenerQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

EXCHANGE_CHOICES = ["all", "nasdaq", "nyse", "amex"]
EXSUBCATEGORY_CHOICES = ["all", "ngs", "ngm", "ncm", "adr"]
MKT_CAP_CHOICES = ["all", "mega", "large", "mid", "small", "micro"]
RECOMMENDATION_CHOICES = ["all", "strong_buy", "buy", "hold", "sell", "strong_sell"]
SECTOR_CHOICES = [
    "all",
    "energy",
    "basic_materials",
    "industrials",
    "consumer_staples",
    "consumer_discretionary",
    "health_care",
    "financial_services",
    "technology",
    "communication_services",
    "utilities",
    "real_estate",
]
REGION_CHOICES = [
    "all",
    "africa",
    "asia",
    "australia_and_south_pacific",
    "caribbean",
    "europe",
    "middle_east",
    "north_america",
    "south_america",
]
COUNTRY_CHOICES = [
    "all",
    "argentina",
    "armenia",
    "australia",
    "austria",
    "belgium",
    "bermuda",
    "brazil",
    "canada",
    "cayman_islands",
    "chile",
    "colombia",
    "costa_rica",
    "curacao",
    "cyprus",
    "denmark",
    "finland",
    "france",
    "germany",
    "greece",
    "guernsey",
    "hong_kong",
    "india",
    "indonesia",
    "ireland",
    "isle_of_man",
    "israel",
    "italy",
    "japan",
    "jersey",
    "luxembourg",
    "macau",
    "mexico",
    "monaco",
    "netherlands",
    "norway",
    "panama",
    "peru",
    "philippines",
    "puerto_rico",
    "russia",
    "singapore",
    "south_africa",
    "south_korea",
    "spain",
    "sweden",
    "switzerland",
    "taiwan",
    "turkey",
    "united_kingdom",
    "united_states",
    "usa",
]


class NasdaqEquityScreenerQueryParams(EquityScreenerQueryParams):
    """Nasdaq Equity Screener Query Params."""

    __alias_dict__ = {
        "mktcap": "marketcap",
    }
    __json_schema_extra__ = {
        "exchange": {"multiple_items_allowed": True},
        "exsubcategory": {"multiple_items_allowed": True},
        "mktcap": {"multiple_items_allowed": True},
        "recommendation": {"multiple_items_allowed": True},
        "sector": {"multiple_items_allowed": True},
        "region": {"multiple_items_allowed": True},
        "country": {"multiple_items_allowed": True},
    }

    exchange: Union[Literal["all", "nasdaq", "nyse", "amex"], str] = Field(
        default="all",
        description="Filter by exchange.",
        json_schema_extra={"choices": EXCHANGE_CHOICES},
    )
    exsubcategory: Union[Literal["all", "ngs", "ngm", "ncm", "adr"], str] = Field(
        default="all",
        description="Filter by exchange subcategory."
        "\n    NGS - Nasdaq Global Select Market"
        "\n    NGM - Nasdaq Global Market"
        "\n    NCM - Nasdaq Capital Market"
        "\n    ADR - American Depository Receipt\n",
        json_schema_extra={"choices": EXSUBCATEGORY_CHOICES},
    )
    mktcap: Union[Literal["all", "mega", "large", "mid", "small", "micro"], str] = (
        Field(
            default="all",
            description="Filter by market cap."
            "\n    Mega - > 200B"
            "\n    Large - 10B - 200B"
            "\n    Mid - 2B - 10B"
            "\n    Small - 300M - 2B"
            "\n    Micro - 50M - 300M\n",
            json_schema_extra={"choices": MKT_CAP_CHOICES},
        )
    )
    recommendation: Union[
        Literal["all", "strong_buy", "buy", "hold", "sell", "strong_sell"], str
    ] = Field(
        default="all",
        description="Filter by consensus analyst action.",
        json_schema_extra={"choices": RECOMMENDATION_CHOICES},
    )
    sector: Union[
        Literal[
            "all",
            "energy",
            "basic_materials",
            "industrials",
            "consumer_staples",
            "consumer_discretionary",
            "health_care",
            "financial_services",
            "technology",
            "communication_services",
            "utilities",
            "real_estate",
        ],
        str,
    ] = Field(
        default="all",
        description="Filter by sector.",
        json_schema_extra={"choices": SECTOR_CHOICES},
    )
    region: Union[
        Literal[
            "all",
            "africa",
            "asia",
            "australia_and_south_pacific",
            "caribbean",
            "europe",
            "middle_east",
            "north_america",
            "south_america",
        ],
        str,
    ] = Field(
        default="all",
        description="Filter by region.",
        json_schema_extra={"choices": REGION_CHOICES},
    )
    country: Union[
        Literal[
            "all",
            "argentina",
            "armenia",
            "australia",
            "austria",
            "belgium",
            "bermuda",
            "brazil",
            "canada",
            "cayman_islands",
            "chile",
            "colombia",
            "costa_rica",
            "curacao",
            "cyprus",
            "denmark",
            "finland",
            "france",
            "germany",
            "greece",
            "guernsey",
            "hong_kong",
            "india",
            "indonesia",
            "ireland",
            "isle_of_man",
            "israel",
            "italy",
            "japan",
            "jersey",
            "luxembourg",
            "macau",
            "mexico",
            "monaco",
            "netherlands",
            "norway",
            "panama",
            "peru",
            "philippines",
            "puerto_rico",
            "russia",
            "singapore",
            "south_africa",
            "south_korea",
            "spain",
            "sweden",
            "switzerland",
            "taiwan",
            "turkey",
            "united_kingdom",
            "united_states",
            "usa",
        ],
        str,
    ] = Field(
        default="all",
        description="Filter by country.",
        json_schema_extra={"choices": COUNTRY_CHOICES},
    )
    limit: Optional[int] = Field(
        default=None,
        description="Limit the number of results to return.",
    )

    @field_validator("exchange", mode="before", check_fields=False)
    @classmethod
    def validate_exchange(cls, v):
        """Validate exchange."""
        v = v.split(",")
        new_items = []
        for item in v:
            if item == "all":
                continue
            if item in EXCHANGE_CHOICES:
                new_items.append(item)
            else:
                warn(f"Invalid exchange: {item}")
        return ",".join(new_items) if new_items else "all"

    @field_validator("exsubcategory", mode="before", check_fields=False)
    @classmethod
    def validate_exsubcategory(cls, v):
        """Validate exsubcategory."""
        v = v.split(",")
        new_items = []
        for item in v:
            if item == "all":
                continue
            if item in EXSUBCATEGORY_CHOICES:
                new_items.append(item)
            else:
                warn(f"Invalid exsubcategory: {item}")
        return ",".join(new_items) if new_items else "all"

    @field_validator("mktcap", mode="before", check_fields=False)
    @classmethod
    def validate_mktcap(cls, v):
        """Validate market cap."""
        v = v.split(",")
        new_items = []
        for item in v:
            if item == "all":
                continue
            if item in MKT_CAP_CHOICES:
                new_items.append(item)
            else:
                warn(f"Invalid market cap: {item}")
        return ",".join(new_items) if new_items else "all"

    @field_validator("recommendation", mode="before", check_fields=False)
    @classmethod
    def validate_recommendation(cls, v):
        """Validate recommendation."""
        v = v.split(",")
        new_items = []
        for item in v:
            if item == "all":
                continue
            if item in RECOMMENDATION_CHOICES:
                new_items.append(item)
            else:
                warn(f"Invalid recommendation: {item}")
        return ",".join(new_items) if new_items else "all"

    @field_validator("sector", mode="before", check_fields=False)
    @classmethod
    def validate_sector(cls, v):
        """Validate sector."""
        v = v.split(",")
        new_items = []
        for item in v:
            if item == "all":
                continue
            if item in SECTOR_CHOICES:
                new_items.append(item)
            else:
                warn(f"Invalid sector: {item}")
        return ",".join(new_items) if new_items else "all"

    @field_validator("region", mode="before", check_fields=False)
    @classmethod
    def validate_region(cls, v):
        """Validate region."""
        v = v.split(",")
        new_items = []
        for item in v:
            if item == "all":
                continue
            if item in REGION_CHOICES:
                new_items.append(item)
            else:
                warn(f"Invalid region: {item}")
        return ",".join(new_items) if new_items else "all"

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, v):
        """Validate country."""
        v = v.split(",")
        new_items = []
        for item in v:
            if item == "all":
                continue
            if item in COUNTRY_CHOICES:
                new_items.append(item)
            else:
                warn(f"Invalid country: {item}")
        return ",".join(new_items) if new_items else "all"


class NasdaqEquityScreenerData(EquityScreenerData):
    """Nasdaq Equity Screener Data."""

    __alias_dict__ = {
        "last_price": "lastsale",
        "change": "netchange",
        "change_percent": "pctchange",
        "market_cap": "marketCap",
    }

    last_price: float = Field(
        description="Last sale price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    change: Optional[float] = Field(
        default=None,
        description="1-day change in price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="1-day percent change in price.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    market_cap: Optional[int] = Field(
        default=None,
        description="Market cap.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )

    @field_validator(
        "last_price",
        "change",
        "change_percent",
        "market_cap",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_numbers(cls, v):
        """Validate numbers."""
        if "%" in v:
            v = v.replace("%", "")
            return float(v) / 100
        v = (
            v.replace("$", "")
            .replace(",", "")
            .replace("UNCH", "")
            .replace("--", "")
            .replace("NA", "")
        )
        return v if v else None


class NasdaqEquityScreenerFetcher(
    Fetcher[
        NasdaqEquityScreenerQueryParams,
        List[NasdaqEquityScreenerData],
    ]
):
    """Nasdaq Equity Screener Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqEquityScreenerQueryParams:
        """Transform query."""
        return NasdaqEquityScreenerQueryParams(**params)

    @staticmethod
    def extract_data(
        query: NasdaqEquityScreenerQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data from the Nasdaq Equity Screener."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import get_querystring, make_request
        from openbb_nasdaq.utils.helpers import get_headers

        HEADERS = get_headers(accept_type="text")
        base_url = (
            "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit="
            + f"{query.limit if query.limit else 10000}&"
        )
        exchange = query.exchange.split(",")
        exsubcategory = query.exsubcategory.split(",")
        marketcap = query.mktcap.split(",")
        recommendation = query.recommendation.split(",")
        sector = (
            query.sector.replace("communications_services", "telecommunications")
            .replace("financial_services", "finance")
            .split(",")
        )
        region = query.region.split(",")
        country = query.country.split(",")
        params = dict(
            exchange=None if "all" in exchange else "|".join(exchange).upper(),
            exsubcategory=(
                None if "all" in exsubcategory else "|".join(exsubcategory).upper()
            ),
            marketcap=None if "all" in marketcap else "|".join(marketcap),
            recommendation=(
                None if "all" in recommendation else "|".join(recommendation)
            ),
            sector=None if "all" in sector else "|".join(sector),
            region=None if "all" in region else "|".join(region),
            country=None if "all" in country else "|".join(country),
        )
        querystring = get_querystring(params, [])
        querystring = "&" + querystring if querystring else ""
        url = f"{base_url}{querystring}"
        try:
            response = make_request(url, headers=HEADERS)
            return response.json()
        except Exception as error:
            raise OpenBBError(f"Failed to get data from Nasdaq -> {error}") from error

    @staticmethod
    def transform_data(
        query: NasdaqEquityScreenerQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[NasdaqEquityScreenerData]:
        """Transform data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        rows = data.get("data", {}).get("table", {}).get("rows")
        if not rows:
            raise EmptyDataError("No results were found.")
        results: List[NasdaqEquityScreenerData] = []
        for row in sorted(rows, key=lambda x: x["pctchange"], reverse=True):
            row.pop("url", None)
            results.append(NasdaqEquityScreenerData.model_validate(row))

        return results
