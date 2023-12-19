"""OECD Nominal GDP Model."""

from datetime import date
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.gdp_nominal import (
    GdpNominalData,
    GdpNominalQueryParams,
)
from openbb_oecd.utils import constants, helpers
from pydantic import Field, field_validator

gdp_countries = tuple(constants.COUNTRY_TO_CODE_GDP.keys())
GDPCountriesLiteral = Literal[gdp_countries]  # type: ignore


class OECDGdpNominalQueryParams(GdpNominalQueryParams):
    """OECD Nominal GDP Query."""

    country: GDPCountriesLiteral = Field(
        description="Country to get GDP for.", default="united_states"
    )


class OECDGdpNominalData(GdpNominalData):
    """OECD Nominal GDP Data."""

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, in_date: Union[date, int]):  # pylint: disable=E0213
        """Validate value."""
        if isinstance(in_date, int):
            return date(in_date, 12, 31)
        return date


class OECDGdpNominalFetcher(
    Fetcher[OECDGdpNominalQueryParams, List[OECDGdpNominalData]]
):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDGdpNominalQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params["start_date"] is None:
            transformed_params["start_date"] = date(1950, 1, 1)
        if transformed_params["end_date"] is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)

        return OECDGdpNominalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDGdpNominalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the OECD endpoint."""
        unit = "MLN_USD" if query.units == "usd" else "USD_CAP"
        url = (
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.GDP.TOT.{unit}.A/OECD"
            "?contentType=csv&detail=code&separator=comma&csv-lang=en"
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
        data_df["country"] = data_df["country"].map(constants.CODE_TO_COUNTRY_GDP)
        data_df = data_df[data_df["country"] == query.country]
        data_df = data_df[["country", "date", "value"]]
        return data_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDGdpNominalQueryParams, data: Dict, **kwargs: Any
    ) -> List[OECDGdpNominalData]:
        """Transform the data from the OECD endpoint."""
        return [OECDGdpNominalData.model_validate(d) for d in data]
