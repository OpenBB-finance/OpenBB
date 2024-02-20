"""TMX Bond Prices Fetcher"""

# pylint: disable=unused-argument
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.bond_reference import (
    BondReferenceData,
    BondReferenceQueryParams,
)
from openbb_tmx.utils.helpers import get_all_bonds
from pandas import DataFrame
from pydantic import Field, field_validator


class TmxBondPricesQueryParams(BondReferenceQueryParams):
    """
    TMX Bond Prices Query Params.

    Data will be made available by 5:00 EST on T+1

    Source: https://bondtradedata.iiroc.ca/#/
    """

    __alias_dict__ = {
        # "isin": "isins",
    }
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
    use_cache: bool = Field(
        default=True,
        description="All bond data is sourced from a single JSON file that is updated daily."
        + " The file is cached for one day to eliminate downloading more than once."
        + " Caching will significantly speed up subsequent queries. To bypass, set to False.",
    )


class TmxBondPricesData(BondReferenceData):
    """TMX Bond Prices Data."""

    __alias_dict__ = {
        "coupon_rate": "couponRate",
    }

    ytm: Optional[float] = Field(
        default=None,
        description="Yield to maturity (YTM) is the rate of return anticipated on a bond"
        + " if it is held until the maturity date. It takes into account"
        + " the current market price, par value, coupon rate and time to maturity. It is assumed that all"
        + " coupons are reinvested at the same rate."
        + " Values are returned as a normalized percent.",
        alias="lastYield",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    price: Optional[float] = Field(
        default=None,
        description="The last price for the bond.",
        alias="lastPrice",
    )
    highest_price: Optional[float] = Field(
        default=None,
        description="The highest price for the bond on the last traded date.",
        alias="highestPrice",
    )
    lowest_price: Optional[float] = Field(
        default=None,
        description="The lowest price for the bond on the last traded date.",
        alias="lowestPrice",
    )
    total_trades: Optional[int] = Field(
        default=None,
        description="Total number of trades on the last traded date.",
        alias="totalTrades",
    )
    last_traded_date: Optional[dateType] = Field(
        default=None,
        description="Last traded date of the bond.",
        alias="lastTradedDate",
    )
    maturity_date: Optional[dateType] = Field(
        default=None,
        description="Maturity date of the bond.",
        alias="maturityDate",
    )
    issue_date: Optional[dateType] = Field(
        default=None,
        description="Issue date of the bond. This is the date when the bond first accrues interest.",
        alias="originalIssueDate",
    )
    issuer_name: Optional[str] = Field(
        default=None,
        description="Name of the issuing entity.",
        alias="issuer",
    )

    @field_validator(
        "ytm",
        "coupon_rate",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else None


class TmxBondPricesFetcher(
    Fetcher[
        TmxBondPricesQueryParams,
        List[TmxBondPricesData],
    ]
):
    """Tmx Bond Reference Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxBondPricesQueryParams:
        """Transform query params."""
        transformed_params = params.copy()
        now = datetime.now()
        if now.date().weekday() > 4:
            now = now - timedelta(now.date().weekday() - 4)
        if transformed_params.get("maturity_date_min") is None:
            transformed_params["maturity_date_min"] = (
                now - timedelta(days=1)
            ).strftime("%Y-%m-%d")
        return TmxBondPricesQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: TmxBondPricesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> DataFrame:
        """Get the raw data containing all bond data."""
        bonds = await get_all_bonds(use_cache=query.use_cache)
        return bonds

    @staticmethod
    def transform_data(
        query: TmxBondPricesQueryParams,
        data: DataFrame,
        **kwargs: Any,
    ) -> List[TmxBondPricesData]:
        """Transform data."""
        bonds = data.copy()
        results = []
        data = data[data["bondType"] == "Corp"]

        data = bonds.query(
            "bondType == 'Corp'"
            "& maturityDate >= @query.maturity_date_min.strftime('%Y-%m-%d')"
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
        if query.coupon_min:
            data = data.query("couponRate >= @query.coupon_min")
        if query.coupon_max:
            data = data.query("couponRate <= @query.coupon_max")
        if query.issuer_name:
            data = data.query("issuer.str.contains(@query.issuer_name, case=False)")
        if len(data) > 0:
            data = data.drop(columns=["bondType", "securityId", "secKey"])
            data = data.fillna("N/A").replace("N/A", None)
            results = data.to_dict("records")

        return [TmxBondPricesData.model_validate(d) for d in results]
