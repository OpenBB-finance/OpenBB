"""OECD Forecast GDP Model."""

import re
from datetime import date
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.gdp_forecast import (
    GdpForecastData,
    GdpForecastQueryParams,
)
from openbb_oecd.utils import constants, helpers
from pydantic import Field, field_validator

gdp_countries = tuple(constants.COUNTRY_TO_CODE_GDP_FORECAST.keys())
GDPCountriesLiteral = Literal[gdp_countries]  # type: ignore


class OECDGdpForecastQueryParams(GdpForecastQueryParams):
    """OECD GDP Forecast Query."""

    country: GDPCountriesLiteral = Field(
        description="Country to get GDP for.", default="united_states"
    )


class OECDGdpForecastData(GdpForecastData):
    """OECD GDP Forecast Data."""

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(
        cls, in_date: Union[date, Union[str, int]]
    ):  # pylint: disable=E0213
        """Validate date."""
        # OECD Returns dates like 2022-Q2, so we map that to the end of the quarter.
        if isinstance(in_date, str):
            if re.match(r"\d{4}-Q[1-4]$", in_date):
                year, quarter = in_date.split("-")
                quarter = int(quarter[1])
                month = quarter * 3
                return date(int(year), month, 1)
            raise ValueError("Date string does not match the format YYYY-QN")
        if isinstance(in_date, int):
            return date(in_date, 12, 31)
        return date


class OECDGdpForecastFetcher(
    Fetcher[OECDGdpForecastQueryParams, List[OECDGdpForecastData]]
):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDGdpForecastQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params["start_date"] is None:
            transformed_params["start_date"] = date(1990, 1, 1)
        if transformed_params["end_date"] is None:
            transformed_params["end_date"] = date(date.today().year + 10, 12, 31)

        return OECDGdpForecastQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDGdpForecastQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the OECD endpoint."""
        units = query.period[0].upper()
        _type = "REAL" if query.type == "real" else "NOM"

        base_url = "https://stats.oecd.org/sdmx-json/data/DP_LIVE"
        url = (
            f"{base_url}/.{_type}GDPFORECAST.TOT.AGRWTH.{units}"
            "/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en"
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
        data_df["country"] = data_df["country"].map(
            constants.CODE_TO_COUNTRY_GDP_FORECAST
        )
        data_df = data_df[data_df["country"] == query.country]
        data_df = data_df[["country", "date", "value"]]
        return data_df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDGdpForecastQueryParams, data: Dict, **kwargs: Any
    ) -> List[OECDGdpForecastData]:
        """Transform the data from the OECD endpoint."""
        return [OECDGdpForecastData.model_validate(d) for d in data]
