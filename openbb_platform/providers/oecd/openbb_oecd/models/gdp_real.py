"""OECD Real GDP Model."""

from datetime import date
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.gdp_real import (
    GdpRealData,
    GdpRealQueryParams,
)
from openbb_oecd.utils import constants, helpers
from pydantic import Field, field_validator

rgdp_countries = tuple(constants.COUNTRY_TO_CODE_RGDP.keys()) + ("all",)
RGDPCountriesLiteral = Literal[rgdp_countries]  # type: ignore


# pylint: disable=unused-argument
class OECDGdpRealQueryParams(GdpRealQueryParams):
    """OECD Real GDP Query."""

    country: RGDPCountriesLiteral = Field(
        description="Country to get GDP for.", default="united_states"
    )


class OECDGdpRealData(GdpRealData):
    """OECD Real GDP Data."""

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, in_date: Union[date, str]):  # pylint: disable=E0213
        """Validate value."""
        if isinstance(in_date, str):
            year, quarter = in_date.split("-")
            _year = int(year)
            if quarter == "Q1":
                return date(_year, 3, 31)
            if quarter == "Q2":
                return date(_year, 6, 30)
            if quarter == "Q3":
                return date(_year, 9, 30)
            if quarter == "Q4":
                return date(_year, 12, 31)
        return in_date


class OECDGdpRealFetcher(Fetcher[OECDGdpRealQueryParams, List[OECDGdpRealData]]):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDGdpRealQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params["start_date"] is None:
            transformed_params["start_date"] = date(1950, 1, 1)
        if transformed_params["end_date"] is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)

        return OECDGdpRealQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDGdpRealQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the OECD endpoint."""
        units = {"qoq": "PC_CHGPP", "yoy": "PC_CHGPY", "idx": "IDX"}[query.units]
        url = (
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.QGDP.{'VOLIDX' if units == 'IDX' else 'TOT'}"
            f".{units}.Q/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en"
            f"&startPeriod={query.start_date}&endPeriod={query.end_date}"
        )
        data_df = helpers.fetch_data(url, csv_kwargs={"encoding": "utf-8"}, **kwargs)
        # Sometimes there is weird unicode characters in the column names, so we need to rename them.
        # Even changing the encoding on the fetch doesn't seem to help.
        data_df = data_df.rename(
            columns={
                'ï»¿"LOCATION"': "country",
                "TIME": "date",
                "Value": "value",
                "Location": "country",
            }
        )
        data_df["country"] = data_df["country"].map(constants.CODE_TO_COUNTRY_RGDP)
        if query.country != "all":
            data_df = data_df[data_df["country"] == query.country]
        data_df = data_df[["country", "date", "value"]]

        data_df["date"] = data_df["date"].apply(helpers.oecd_date_to_python_date)
        data_df = data_df[
            (data_df["date"] <= query.end_date) & (data_df["date"] >= query.start_date)
        ]
        return data_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDGdpRealQueryParams, data: Dict, **kwargs: Any
    ) -> List[OECDGdpRealData]:
        """Transform the data from the OECD endpoint."""
        return [OECDGdpRealData.model_validate(d) for d in data]
