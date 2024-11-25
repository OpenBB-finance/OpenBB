"""OECD Forecast GDP Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.gdp_forecast import (
    GdpForecastData,
    GdpForecastQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_oecd.utils.constants import (
    CODE_TO_COUNTRY_GDP_FORECAST,
    COUNTRY_TO_CODE_GDP_FORECAST,
)
from pydantic import Field

COUNTRIES = list(COUNTRY_TO_CODE_GDP_FORECAST) + ["all"]

COUNTRIES_QUARTER = [
    "australia",
    "austria",
    "belgium",
    "canada",
    "chile",
    "colombia",
    "costa_rica",
    "czechia",
    "denmark",
    "estonia",
    "finland",
    "france",
    "germany",
    "greece",
    "iceland",
    "ireland",
    "israel",
    "italy",
    "japan",
    "korea",
    "lithuania",
    "luxembourg",
    "netherlands",
    "new_zealand",
    "norway",
    "poland",
    "portugal",
    "slovak_republic",
    "spain",
    "sweden",
    "switzerland",
    "turkey",
    "united_kingdom",
    "united_states",
]


class OECDGdpForecastQueryParams(GdpForecastQueryParams):
    """OECD GDP Forecast Query.

    The OECD Economic Outlook presents the OECD's analysis of the major
    global economic trends and prospects for the next two years.
    The Outlook puts forward a consistent set of projections for output, employment, government spending,
    prices and current balances based on a review of each member country
    and of the induced effect on each of them on international developments.

    https://www.oecd.org/economic-outlook/
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": COUNTRIES,
        },
    }

    country: str = Field(
        description="Country, or countries, to get forward GDP projections for. Default is all.",
        default="all",
    )
    frequency: Literal["annual", "quarter"] = Field(
        default="annual",
        description="Frequency of the data, default is annual.",
    )
    units: Literal["current_prices", "volume", "capita", "growth", "deflator"] = Field(
        default="volume",
        description="Units of the data, default is volume (chain linked volume, 2015)."
        + "\n'current_prices', 'volume', and 'capita' are expressed in USD; 'growth' as a percent;"
        + " 'deflator' as an index.",
        json_schema_extra={
            "choices": ["current_prices", "volume", "capita", "growth", "deflator"]
        },
    )


class OECDGdpForecastData(GdpForecastData):
    """OECD GDP Forecast Data."""


class OECDGdpForecastFetcher(
    Fetcher[OECDGdpForecastQueryParams, List[OECDGdpForecastData]]
):
    """OECD GDP Forecast Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDGdpForecastQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        countries = transformed_params.get("country")
        new_countries: List = []
        freq = transformed_params.get("frequency")
        if not countries:
            new_countries.append("all")
        if countries:
            countries = (
                countries.split(",") if isinstance(countries, str) else countries
            )
            if "all" in countries:
                new_countries = ["all"]
            else:
                for country in countries:
                    if freq == "quarter":
                        if country.lower() in COUNTRIES_QUARTER:
                            new_countries.append(country.lower())
                        else:
                            warn(f"{country} is not available for quarterly data.")
                    else:  # noqa
                        if country.lower() in COUNTRIES:
                            new_countries.append(country.lower())
                        else:
                            warn(f"{country} is not available for annual data.")

        if not new_countries:
            raise OpenBBError(
                "No valid countries were found for the supplied parameters."
            )

        transformed_params["country"] = ",".join(new_countries)

        if not transformed_params.get("start_date"):
            transformed_params["start_date"] = datetime(
                datetime.today().year, 1, 1
            ).date()

        if not transformed_params.get("end_date"):
            transformed_params["end_date"] = datetime(
                datetime.today().year + 2, 12, 31
            ).date()

        return OECDGdpForecastQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: OECDGdpForecastQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from openbb_oecd.utils.helpers import oecd_date_to_python_date
        from pandas import read_csv
        from openbb_core.provider.utils.helpers import amake_request

        freq = "Q" if query.frequency == "quarter" else "A"

        measure_dict = {
            "current_prices": "GDP_USD",  # This gives questionable results.
            "volume": "GDPV_USD",
            "capita": "GDPVD_CAP",
            "growth": "GDPV_ANNPCT",
            "deflator": "PGDP",
        }
        measure = measure_dict[query.units]  # type: ignore

        if query.units == "capita" and freq == "Q":
            warn(
                "Capita data is not available for quarterly data, using annual data instead."
            )
            freq = "A"

        def country_string(input_str: str):
            """Convert the list of countries to an abbreviated string."""
            if input_str == "all":
                return ""
            _countries = input_str.split(",")

            return "+".join(
                [
                    COUNTRY_TO_CODE_GDP_FORECAST[country.lower()]
                    for country in _countries
                ]
            )

        country = country_string(query.country)

        url = (
            "https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,1.1"
            + f"/{country}.{measure}.{freq}?"
            + f"startPeriod={query.start_date}&endPeriod={query.end_date}"
            + "&dimensionAtObservation=TIME_PERIOD&detail=dataonly&format=csvfile"
        )

        async def response_callback(response, _):
            """Response callback."""
            if response.status != 200:
                raise OpenBBError(f"Error with the OECD request: {response.status}")
            return await response.text()

        headers = {"Accept": "application/vnd.sdmx.data+csv; charset=utf-8"}
        response = await amake_request(
            url, timeout=30, headers=headers, response_callback=response_callback
        )
        df = read_csv(StringIO(response)).get(  # type: ignore
            ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]
        )
        if df.empty:  # type: ignore
            raise EmptyDataError("No data was found.")

        df = df.rename(  # type: ignore
            columns={"REF_AREA": "country", "TIME_PERIOD": "date", "OBS_VALUE": "value"}
        )
        df.country = [
            (
                CODE_TO_COUNTRY_GDP_FORECAST.get(d, d)
                .replace("_", " ")
                .replace("asia", "Dynamic Asian Economies")
                .title()
            )
            for d in df.country
        ]
        df.date = df.date.apply(oecd_date_to_python_date)
        df = df[df["value"].notnull()]

        if query.units != "growth":
            df["value"] = df.value.astype("int64")
            df = df[df["value"] > 0]

        if query.units == "growth":
            df["value"] = df.value.astype("float64") / 100

        df = df[df["value"] > 0]
        df = df.sort_values(by=["date", "value"], ascending=[True, False])

        return df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDGdpForecastQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[OECDGdpForecastData]:
        """Transform the data from the OECD endpoint."""
        return [OECDGdpForecastData.model_validate(d) for d in data]
