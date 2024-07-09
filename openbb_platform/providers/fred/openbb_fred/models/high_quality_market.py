"""FRED High Quality Market Corporate Bond Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.high_quality_market import (
    HighQualityMarketCorporateBondData,
    HighQualityMarketCorporateBondQueryParams,
)
from pydantic import Field, field_validator


class FredHighQualityMarketCorporateBondQueryParams(
    HighQualityMarketCorporateBondQueryParams
):
    """FRED High Quality Market Corporate Bond Query."""

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}

    yield_curve: Literal["spot", "par"] = Field(
        default="spot",
        description="The yield curve type.",
        json_schema_extra={"choices": ["spot", "par"]},
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Validate the dates entered."""
        if v is None:
            return None
        if isinstance(v, (list, dateType)):
            return v
        new_dates: List = []
        date_param = v
        if isinstance(date_param, str):
            new_dates = date_param.split(",")
        elif isinstance(date_param, dateType):
            new_dates.append(date_param.strftime("%Y-%m-%d"))
        elif isinstance(date_param, list) and isinstance(date_param[0], dateType):
            new_dates = [d.strftime("%Y-%m-%d") for d in new_dates]
        else:
            new_dates = date_param
        return ",".join(new_dates) if len(new_dates) > 1 else new_dates[0]


class FredHighQualityMarketCorporateBondData(HighQualityMarketCorporateBondData):
    """FRED High Quality Market Corporate Bond Data."""


class FredHighQualityMarketCorporateBondFetcher(
    Fetcher[
        FredHighQualityMarketCorporateBondQueryParams,
        List[FredHighQualityMarketCorporateBondData],
    ]
):
    """FRED High Quality Market Corporate Bond Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FredHighQualityMarketCorporateBondQueryParams:
        """Transform query."""
        return FredHighQualityMarketCorporateBondQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredHighQualityMarketCorporateBondQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from dateutil import parser  # noqa
        from openbb_core.provider.utils.helpers import amake_request  # noqa

        api_key = credentials.get("fred_api_key") if credentials else ""

        element_id = "219299" if query.yield_curve == "spot" else "219294"
        dates: List = [""]
        if query.date:
            if query.date and isinstance(query.date, dateType):
                query.date = query.date.strftime("%Y-%m-%d")
            dates = query.date.split(",")  # type: ignore
            dates = [d.replace(d[-2:], "01") if len(d) == 10 else d for d in dates]
            dates = list(set(dates))
            dates = (
                [f"&observation_date={date}" for date in dates if date] if dates else ""  # type: ignore
            )
        URLS = [
            f"https://api.stlouisfed.org/fred/release/tables?release_id=402&element_id={element_id}"
            + f"{date}&include_observation_values=true&api_key={api_key}"
            + "&file_type=json"
            for date in dates
        ]
        results = []

        async def get_one(URL):
            """Get the observations for a single date."""
            data = await amake_request(URL)
            if data:
                elements = dict(data.get("elements", {}).items())  # type: ignore
                for k, v in elements.items():  # pylint: disable=W0612
                    value = v.get("observation_value")
                    if not value:
                        continue
                    maturity = v.get("name").lower().split("-")
                    results.append(
                        {
                            "date": parser.parse(
                                v.get("observation_date"),
                            ).date(),
                            "rate": float(value) / 100,
                            "maturity": (maturity[1] + "_" + maturity[0]).replace(
                                " ", ""
                            ),
                        }
                    )

        await asyncio.gather(*[get_one(URL) for URL in URLS])

        return results

    @staticmethod
    def transform_data(
        query: FredHighQualityMarketCorporateBondQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FredHighQualityMarketCorporateBondData]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from pandas import Categorical, DataFrame

        df = DataFrame(data)
        df["maturity_int"] = df["maturity"].str.replace("year_", "").astype(float)
        maturity_categories = sorted(df.maturity_int.unique().tolist())
        df["maturity_int"] = Categorical(
            df["maturity_int"], categories=maturity_categories, ordered=True
        )
        df = df.sort_values(by=["date", "maturity_int"]).reset_index(drop=True)
        df = df.drop(columns=["maturity_int"])
        records = df.to_dict("records")
        return [
            FredHighQualityMarketCorporateBondData.model_validate(d) for d in records
        ]
