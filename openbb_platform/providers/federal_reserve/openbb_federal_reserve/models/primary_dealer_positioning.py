"""Federal Reserve Primary Dealer Positioning Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.primary_dealer_positioning import (
    PrimaryDealerPositioningData,
    PrimaryDealerPositioningQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

PdsCategories = Literal[
    "treasuries",
    "bills",
    "coupons",
    "notes",
    "tips",
    "mbs",
    "cmbs",
    "municipal",
    "corporate",
    "commercial_paper",
    "corporate_ig",
    "corporate_junk",
    "abs",
]

PDS_CATEGORY_CHOICES = [
    "treasuries",
    "bills",
    "coupons",
    "notes",
    "tips",
    "mbs",
    "cmbs",
    "municipal",
    "corporate",
    "commercial_paper",
    "corporate_ig",
    "corporate_junk",
    "abs",
]


class FederalReservePrimaryDealerPositioningQueryParams(
    PrimaryDealerPositioningQueryParams
):
    """Federal Reserve Primary Dealer Positioning Query Params."""

    category: PdsCategories = Field(
        default="treasuries",
        description="The category of asset to return, defaults to 'treasuries'.",
        json_schema_extra={"choices": PDS_CATEGORY_CHOICES},  # type: ignore
    )


class FederalReservePrimaryDealerPositioningData(PrimaryDealerPositioningData):
    """Federal Reserve Primary Dealer Positioning Data."""

    value: int = Field(
        description="The reported value of the net position (long - short), in millions of $USD.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-frontend_multiply": 1e6,
        },
    )
    name: str = Field(
        description="Short name for the series.",
    )
    title: str = Field(
        description="Title of the series.",
    )


class FederalReservePrimaryDealerPositioningFetcher(
    Fetcher[
        FederalReservePrimaryDealerPositioningQueryParams,
        List[FederalReservePrimaryDealerPositioningData],
    ]
):
    """Federal Reserve Primary Dealer Positioning Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FederalReservePrimaryDealerPositioningQueryParams:
        """Transform the query params."""
        return FederalReservePrimaryDealerPositioningQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FederalReservePrimaryDealerPositioningQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FederalReserve endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_federal_reserve.utils.primary_dealer_statistics import (
            POSITION_GROUPS_TO_SERIES,
        )

        symbols = POSITION_GROUPS_TO_SERIES.get(query.category, [])
        results: List[Dict] = []

        base_url = "https://markets.newyorkfed.org/api/pd/get/"
        urls = [base_url + symbol + ".json" for symbol in symbols]

        async def get_one(url):
            """Get data for a single URL."""
            result = await amake_request(url)
            if isinstance(result, dict):
                data = result.get("pd", {}).get("timeseries")
                if data:
                    results.extend(data)

        await asyncio.gather(*[get_one(url) for url in urls])

        if not results:
            raise EmptyDataError("The request was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: FederalReservePrimaryDealerPositioningQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FederalReservePrimaryDealerPositioningData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from openbb_federal_reserve.utils.primary_dealer_statistics import (
            POSITION_SERIES_TO_FIELD,
            POSITION_SERIES_TO_TITLE,
        )
        from pandas import DataFrame

        df = DataFrame(data)
        df = df.rename(columns={"keyid": "symbol", "asofdate": "date"})
        df["name"] = df.symbol.map(
            lambda x: POSITION_SERIES_TO_FIELD["dealer_position"].get(x)
        )
        df["title"] = df.symbol.map(lambda x: POSITION_SERIES_TO_TITLE.get(x))

        return [
            FederalReservePrimaryDealerPositioningData.model_validate(d)
            for d in df.to_dict(orient="records")
        ]
