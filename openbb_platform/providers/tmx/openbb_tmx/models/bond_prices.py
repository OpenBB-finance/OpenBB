"""TMX Bond Prices Fetcher"""

# pylint: disable=unused-argument
from datetime import (
    date as dateType,
    datetime,
)
from typing import TYPE_CHECKING, Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.bond_reference import (
    BondReferenceData,
    BondReferenceQueryParams,
)
from pydantic import Field, field_validator

if TYPE_CHECKING:
    from pandas import DataFrame


class TmxBondPricesQueryParams(BondReferenceQueryParams):
    """
    TMX Bond Prices Query Params.

    Data will be made available by 5:00 EST on T+1

    Source: https://bondtradedata.iiroc.ca/#/
    """

    __json_schema_extra__ = {"isin": {"multiple_items_allowed": True}}

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
        "ytm": "lastYield",
        "price": "lastPrice",
        "highest_price": "highestPrice",
        "lowest_price": "lowestPrice",
        "total_trades": "totalTrades",
        "last_traded_date": "lastTradedDate",
        "maturity_date": "maturityDate",
        "issue_date": "originalIssueDate",
        "issuer_name": "issuer",
    }

    ytm: Optional[float] = Field(
        default=None,
        description="Yield to maturity (YTM) is the rate of return anticipated on a bond"
        + " if it is held until the maturity date. It takes into account"
        + " the current market price, par value, coupon rate and time to maturity. It is assumed that all"
        + " coupons are reinvested at the same rate."
        + " Values are returned as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    price: Optional[float] = Field(
        default=None,
        description="The last price for the bond.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    highest_price: Optional[float] = Field(
        default=None,
        description="The highest price for the bond on the last traded date.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    lowest_price: Optional[float] = Field(
        default=None,
        description="The lowest price for the bond on the last traded date.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    total_trades: Optional[int] = Field(
        default=None,
        description="Total number of trades on the last traded date.",
    )
    last_traded_date: Optional[dateType] = Field(
        default=None,
        description="Last traded date of the bond.",
    )
    maturity_date: Optional[dateType] = Field(
        default=None,
        description="Maturity date of the bond.",
    )
    issue_date: Optional[dateType] = Field(
        default=None,
        description="Issue date of the bond. This is the date when the bond first accrues interest.",
    )
    issuer_name: Optional[str] = Field(
        default=None,
        description="Name of the issuing entity.",
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
        list[TmxBondPricesData],
    ]
):
    """Tmx Bond Reference Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxBondPricesQueryParams:
        """Transform query params."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta

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
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> "DataFrame":
        """Get the raw data containing all bond data."""
        # pylint: disable=import-outside-toplevel
        from openbb_tmx.utils.helpers import get_all_bonds

        bonds = await get_all_bonds(use_cache=query.use_cache)
        return bonds

    @staticmethod
    def transform_data(
        query: TmxBondPricesQueryParams,
        data: "DataFrame",
        **kwargs: Any,
    ) -> list[TmxBondPricesData]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from numpy import nan

        bonds = data.copy()

        if query.isin is not None:
            isin_list = (
                query.isin.split(",") if isinstance(query.isin, str) else query.isin
            )

            data = bonds[
                bonds["isin"].str.contains("|".join(isin_list), na=False, case=False)
            ].query("bondType == 'Corp'")

            if data.empty or len(data) == 0:
                raise OpenBBError(
                    f"No bonds found for the provided ISIN(s) -> {', '.join(isin_list)}",
                )
        else:
            data = bonds.query(
                "bondType == 'Corp'"
                "& maturityDate >= @query.maturity_date_min.strftime('%Y-%m-%d')"
            ).sort_values(by=["maturityDate"])

        data.loc[:, "issuer"] = data.issuer.str.strip()

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
            data = data.replace({nan: None})
        else:
            raise OpenBBError(
                "No bonds found for the provided query parameters.",
            )

        return [TmxBondPricesData.model_validate(d) for d in data.to_dict("records")]
