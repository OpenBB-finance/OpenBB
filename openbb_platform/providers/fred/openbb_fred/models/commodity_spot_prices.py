"""FRED Commodity Spot Prices Model."""

# pylint: disable=unused-argument

from typing import Any, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.commodity_spot_prices import (
    CommoditySpotPricesData,
    CommoditySpotPricesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

SERIES_MAP = {
    "wti": "DCOILWTICO",
    "brent": "DCOILBRENTEU",
    "natural_gas": "DHHNGSP",
    "jet_fuel": "DJFUELUSGULF",
    "propane": "DPROPANEMBTX",
    "heating_oil": "DHOILNYH",
    "diesel_gulf_coast": "DDFUELUSGULF",
    "diesel_ny_harbor": "DDFUELNYH",
    "diesel_la": "DDFUELLA",
    "gasoline_ny_harbor": "DGASNYH",
    "gasoline_gulf_coast": "DGASUSGULF",
    "rbob": "DRGASLA",
    "all": "DCOILWTICO,DCOILBRENTEU,DHHNGSP,DJFUELUSGULF,"
    "DPROPANEMBTX,DHOILNYH,DDFUELUSGULF,DDFUELNYH,"
    "DDFUELLA,DGASNYH,DGASUSGULF,DRGASLA",
}


class FredCommoditySpotPricesQueryParams(CommoditySpotPricesQueryParams):
    """FRED Commodity Spot Prices Query Params."""

    __json_schema_extra__ = {
        "commodity": {"multiple_items_allowed": False, "choices": list(SERIES_MAP)},
        "frequency": {
            "multiple_items_allowed": False,
            "choices": [
                "a",
                "q",
                "m",
                "w",
                "d",
                "wef",
                "weth",
                "wew",
                "wetu",
                "wem",
                "wesu",
                "wesa",
                "bwew",
                "bwem",
            ],
        },
        "aggregation_method": {
            "multiple_items_allowed": False,
            "choices": ["avg", "sum", "eop"],
        },
        "transform": {
            "multiple_items_allowed": False,
            "choices": [
                "chg",
                "ch1",
                "pch",
                "pc1",
                "pca",
                "cch",
                "cca",
                "log",
            ],
        },
    }

    commodity: Literal[
        "wti",
        "brent",
        "natural_gas",
        "jet_fuel",
        "propane",
        "heating_oil",
        "diesel_gulf_coast",
        "diesel_ny_harbor",
        "diesel_la",
        "gasoline_ny_harbor",
        "gasoline_gulf_coast",
        "rbob",
        "all",
    ] = Field(
        default="all",
        description="Commodity name associated with the EIA spot price commodity data, default is 'all'.",
    )

    frequency: Optional[
        Literal[
            "a",
            "q",
            "m",
            "w",
            "d",
            "wef",
            "weth",
            "wew",
            "wetu",
            "wem",
            "wesu",
            "wesa",
            "bwew",
            "bwem",
        ]
    ] = Field(
        default=None,
        description="""Frequency aggregation to convert high frequency data to lower frequency.
        None = No change
        a = Annual
        q = Quarterly
        m = Monthly
        w = Weekly
        d = Daily
        wef = Weekly, Ending Friday
        weth = Weekly, Ending Thursday
        wew = Weekly, Ending Wednesday
        wetu = Weekly, Ending Tuesday
        wem = Weekly, Ending Monday
        wesu = Weekly, Ending Sunday
        wesa = Weekly, Ending Saturday
        bwew = Biweekly, Ending Wednesday
        bwem = Biweekly, Ending Monday
        """,
    )
    aggregation_method: Literal["avg", "sum", "eop"] = Field(
        default="eop",
        description="""A key that indicates the aggregation method used for frequency aggregation.
        This parameter has no affect if the frequency parameter is not set.
        avg = Average
        sum = Sum
        eop = End of Period
        """,
    )
    transform: Optional[
        Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
    ] = Field(
        default=None,
        description="""Transformation type
        None = No transformation
        chg = Change
        ch1 = Change from Year Ago
        pch = Percent Change
        pc1 = Percent Change from Year Ago
        pca = Compounded Annual Rate of Change
        cch = Continuously Compounded Rate of Change
        cca = Continuously Compounded Annual Rate of Change
        log = Natural Log
        """,
    )


class FredCommoditySpotPricesData(CommoditySpotPricesData):
    """FRED Commodity Spot Prices Data."""


class FredCommoditySpotPricesFetcher(
    Fetcher[FredCommoditySpotPricesQueryParams, list[FredCommoditySpotPricesData]]
):
    """FRED Commodity Spot Prices Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FredCommoditySpotPricesQueryParams:
        """Transform query."""
        return FredCommoditySpotPricesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredCommoditySpotPricesQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the FRED API."""
        # pylint: disable=import-outside-toplevel
        from datetime import datetime, timedelta  # noqa
        from openbb_fred.models.series import FredSeriesFetcher

        symbols = SERIES_MAP[query.commodity]

        series_query = {
            "symbol": symbols,
            "start_date": (
                query.start_date
                if query.start_date is not None
                else (datetime.now() - timedelta(weeks=156)).date()
            ),
            "end_date": (
                query.end_date if query.end_date is not None else datetime.now().date()
            ),
            "frequency": query.frequency,
            "aggregation_method": query.aggregation_method,
            "transform": query.transform,
        }

        try:
            results = await FredSeriesFetcher.fetch_data(series_query, credentials)

            return {
                "result": results.result,
                "metadata": results.metadata,
            }
        except Exception as e:
            raise OpenBBError(f"Failed to fetch data from FRED API: {e}") from e

    @staticmethod
    def transform_data(
        query: FredCommoditySpotPricesQueryParams, data: dict, **kwargs: Any
    ) -> AnnotatedResult[list[FredCommoditySpotPricesData]]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        results = data.get("result", [])

        if not results:
            raise EmptyDataError("The request was returned with no data.")

        metadata = data.get("metadata", {})
        title_map = {k: v.get("title") for k, v in metadata.items()}
        units_map = {k: v.get("units") for k, v in metadata.items()}
        df = DataFrame([d.model_dump() for d in results])
        df = (
            df.melt(
                id_vars="date",
                value_vars=[d for d in df.columns if d != "date"],
                value_name="price",
                var_name="symbol",
            )
            .dropna()
            .sort_values(by="date")
        )
        df = df.reset_index(drop=True)
        df.loc[:, "commodity"] = df.symbol.map(title_map)
        df.loc[:, "unit"] = df.symbol.map(units_map)
        records = df.to_dict(orient="records")

        return AnnotatedResult(
            result=[FredCommoditySpotPricesData.model_validate(r) for r in records],
            metadata=metadata,
        )
