"""TMX Treasury Prices Fetcher."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_prices import (
    TreasuryPricesData,
    TreasuryPricesQueryParams,
)
from pydantic import Field, field_validator

if TYPE_CHECKING:
    from pandas import DataFrame


class TmxTreasuryPricesQueryParams(TreasuryPricesQueryParams):
    """TMX Treasury Prices Query Params.

    Data will be made available by 5:00 EST on T+1

    Source: https://bondtradedata.iiroc.ca/#/
    """

    govt_type: Literal["federal", "provincial", "municipal"] = Field(
        default="federal",
        description="The level of government issuer.",
    )
    issue_date_min: Optional[dateType] = Field(
        default=None,
        description="Filter by the minimum original issue date.",
    )
    issue_date_max: Optional[dateType] = Field(
        default=None,
        description="Filter by the maximum original issue date.",
    )
    last_traded_min: Optional[dateType] = Field(
        default=None,
        description="Filter by the minimum last trade date.",
    )
    maturity_date_min: Optional[dateType] = Field(
        default=None,
        description="Filter by the minimum maturity date.",
    )
    maturity_date_max: Optional[dateType] = Field(
        default=None,
        description="Filter by the maximum maturity date.",
    )
    use_cache: bool = Field(
        default=True,
        description="All bond data is sourced from a single JSON file that is updated daily."
        + " The file is cached for one day to eliminate downloading more than once."
        + " Caching will significantly speed up subsequent queries. To bypass, set to False.",
    )


class TmxTreasuryPricesData(TreasuryPricesData):
    """TMX Treasury Prices Data."""

    __alias_dict__ = {
        "rate": "couponRate",
        "ytm": "lastYield",
        "last_price": "lastPrice",
        "highest_price": "highestPrice",
        "lowest_price": "lowestPrice",
        "total_trades": "totalTrades",
        "last_traded_date": "lastTradedDate",
        "maturity_date": "maturityDate",
        "issue_date": "originalIssueDate",
        "issuer_name": "issuer",
    }

    @field_validator(
        "ytm",
        "rate",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else None


class TmxTreasuryPricesFetcher(
    Fetcher[
        TmxTreasuryPricesQueryParams,
        List[TmxTreasuryPricesData],
    ]
):
    """Tmx Bond Reference Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxTreasuryPricesQueryParams:
        """Transform query params."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta

        transformed_params = params.copy()
        yesterday = dateType.today() - timedelta(days=1)
        last_bd = (
            yesterday - timedelta(yesterday.weekday() - 4)
            if yesterday.weekday() > 4
            else yesterday
        )
        if "maturity_date_min" not in transformed_params:
            transformed_params["maturity_date_min"] = last_bd
        return TmxTreasuryPricesQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: TmxTreasuryPricesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> "DataFrame":
        """Get the raw data containing all bond data."""
        # pylint: disable=import-outside-toplevel
        from openbb_tmx.utils.helpers import get_all_bonds

        bonds = await get_all_bonds(use_cache=query.use_cache)

        return bonds

    @staticmethod
    def transform_data(
        query: TmxTreasuryPricesQueryParams,
        data: "DataFrame",
        **kwargs: Any,
    ) -> List[TmxTreasuryPricesData]:
        """Transform data."""
        bonds = data.copy()
        results = []
        govt_type_dict = {
            "provincial": "prov",
            "federal": "government of canada",
            "municipal": "municipal",
        }
        govt_type = govt_type_dict[query.govt_type]  # noqa  # pylint: disable=W0612
        data = bonds.query(
            "maturityDate >= @query.maturity_date_min.strftime('%Y-%m-%d')"
            + " & bondType == 'Govt'"
            + " & issuer.str.contains(@govt_type, case=False)"
        ).sort_values(by=["maturityDate"])
        data.issuer = data.loc[:, "issuer"].str.strip()
        if query.maturity_date_max:
            data = data.query(
                "maturityDate <= @query.maturity_date_max.strftime('%Y-%m-%d')"
            )
        if query.last_traded_min:
            data = data.query(
                "lastTradedDate >= @query.last_traded_min.strftime('%Y-%m-%d')"
            )

        if len(data) > 0:
            data = data.drop(columns=["bondType", "securityId", "secKey"])
            data = data.fillna("N/A").replace("N/A", None)
            results = data.to_dict("records")

        return [TmxTreasuryPricesData.model_validate(d) for d in results]
