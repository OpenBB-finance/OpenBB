"""OECD Composite Leading Indicator Data."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Dict, List, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.composite_leading_indicator import (
    CompositeLeadingIndicatorData,
    CompositeLeadingIndicatorQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

COUNTRIES = {
    "g20": "G20",
    "g7": "G7",
    "asia5": "A5M",
    "north_america": "NAFTA",
    "europe4": "G4E",
    "australia": "AUS",
    "brazil": "BRA",
    "canada": "CAN",
    "china": "CHN",
    "france": "FRA",
    "germany": "DEU",
    "india": "IND",
    "indonesia": "IDN",
    "italy": "ITA",
    "japan": "JPN",
    "mexico": "MEX",
    "spain": "ESP",
    "south_africa": "ZAF",
    "south_korea": "KOR",
    "turkey": "TUR",
    "united_states": "USA",
    "united_kingdom": "GBR",
}
COUNTRY_CHOICES = list(COUNTRIES) + ["all"]
Countries = Literal[
    "g20",
    "g7",
    "asia5",
    "north_america",
    "europe4",
    "australia",
    "brazil",
    "canada",
    "china",
    "france",
    "germany",
    "india",
    "indonesia",
    "italy",
    "japan",
    "mexico",
    "south_africa",
    "south_korea",
    "spain",
    "turkey",
    "united_kingdom",
    "united_states",
    "all",
]


class OECDCompositeLeadingIndicatorQueryParams(CompositeLeadingIndicatorQueryParams):
    """OECD Composite Leading Indicator Query."""

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": COUNTRY_CHOICES,
        },
    }

    country: Union[Countries, str] = Field(
        description="Country to get the CLI for, default is G20.",
        default="g20",
    )
    adjustment: Literal["amplitude", "normalized"] = Field(
        default="amplitude",
        description="Adjustment of the data, either 'amplitude' or 'normalized'."
        + " Default is amplitude.",
    )
    growth_rate: bool = Field(
        default=False,
        description="Return the 1-year growth rate (%) of the CLI, default is False.",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def country_validate(cls, v):
        """Validate countries."""
        if v is None:
            return "g20"
        new_countries: List = []
        if isinstance(v, str):
            countries = v.split(",")
        elif isinstance(v, list):
            countries = v
        if "all" in countries:
            return "all"
        for country in countries:
            if country.lower() not in COUNTRY_CHOICES:
                warn(f"Country {country} not supported, skipping...")
            else:
                new_countries.append(country)
        if not new_countries:
            raise OpenBBError("No valid countries found.")
        return ",".join(new_countries)


class OECDCompositeLeadingIndicatorData(CompositeLeadingIndicatorData):
    """OECD Composite Leading Indicator Data."""


class OECDCompositeLeadingIndicatorFetcher(
    Fetcher[
        OECDCompositeLeadingIndicatorQueryParams,
        List[OECDCompositeLeadingIndicatorData],
    ]
):
    """OECD Composite Leading Indicator Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> OECDCompositeLeadingIndicatorQueryParams:
        """Transform the query."""
        transformed_params = params.copy()

        if not transformed_params.get("start_date"):
            transformed_params["start_date"] = (
                date(2020, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1947, 1, 1)
            )

        if not transformed_params.get("end_date"):
            transformed_params["end_date"] = date(date.today().year, 12, 31)

        if not transformed_params.get("country"):
            transformed_params["country"] = "g20"

        return OECDCompositeLeadingIndicatorQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: OECDCompositeLeadingIndicatorQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from openbb_oecd.utils.helpers import oecd_date_to_python_date
        from pandas import read_csv
        from openbb_core.provider.utils.helpers import amake_request

        COUNTRY_MAP = {v: k.replace("_", " ").title() for k, v in COUNTRIES.items()}

        growth_rate = "GY" if query.growth_rate is True else "IX"
        adjustment = "AA" if query.adjustment == "amplitude" else "NOR"

        if growth_rate == "GY":
            adjustment = ""

        def country_string(input_str: str):
            if input_str == "all":
                return ""
            _countries = input_str.split(",")
            return "+".join([COUNTRIES[country.lower()] for country in _countries])

        country = country_string(query.country) if query.country else ""
        url = (
            "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI,4.1"
            + f"/{country}.M.LI...{adjustment}.{growth_rate}..H"
            + f"?startPeriod={query.start_date}&endPeriod={query.end_date}"
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
                COUNTRY_MAP.get(d, d)
                .replace("Asia5", "Major 5 Asian Economies")
                .replace("Europe4", "Major 4 European Economies")
            )
            for d in df.country
        ]
        df.date = df.date.apply(oecd_date_to_python_date)

        if query.growth_rate is True:
            df.value = df.value.astype(float) / 100

        df = (
            df.query("value.notnull()")
            .set_index(["date", "country"])
            .sort_index()
            .reset_index()
        )

        return df.to_dict("records")

    @staticmethod
    def transform_data(
        query: OECDCompositeLeadingIndicatorQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[OECDCompositeLeadingIndicatorData]:
        """Transform the data from the OECD endpoint."""
        return [OECDCompositeLeadingIndicatorData.model_validate(d) for d in data]
