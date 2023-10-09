from datetime import date
from typing import Any, Dict, List, Literal, Optional

from openbb_oecd.utils import constants, helpers
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.gdpforecast import (
    GDPForecastData,
    GDPForecastQueryParams,
)
from pydantic import Field

gdp_countries = tuple(constants.COUNTRY_TO_CODE_GDP_FORECAST.keys())


class OECDGDPForecastQueryParams(GDPForecastQueryParams):
    """GDP Forecast query."""

    country: Literal[*gdp_countries] = Field(
        description="Country to get GDP for.", default="united_states"
    )


class OECDGDPForecastData(GDPForecastData):
    """GDP Forecast data from OECD."""


class OECDGDPForecastFetcher(
    Fetcher[OECDGDPForecastQueryParams, List[OECDGDPForecastData]]
):
    """OECD GDP Forecast Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDGDPForecastQueryParams:
        transformed_params = params.copy()
        if transformed_params["start_date"] is None:
            transformed_params["start_date"] = date(1990, 1, 1)
        if transformed_params["end_date"] is None:
            transformed_params["end_date"] = date(date.today().year + 10, 12, 31)

        return OECDGDPForecastQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDGDPForecastQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        units = query.period[0].upper()
        if query.type == "real":
            url = f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.REALGDPFORECAST.TOT.AGRWTH.{units}/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en&startPeriod={query.start_date}&endPeriod={query.end_date}"
        elif query.type == "nominal":
            url = f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.NOMGDPFORECAST.TOT.AGRWTH.{units}/OECD?contentType=csv&detail=code&separator=comma&csv-lang=en&startPeriod={query.start_date}&endPeriod={query.end_date}"

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
    def transform_data(data: dict) -> List[OECDGDPForecastData]:
        return [OECDGDPForecastData.model_validate(d) for d in data]
