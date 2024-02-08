"""OECD Long Term Interest Rate Rate Data."""

# pylint: disable=unused-argument

import re
from datetime import date, timedelta
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.long_term_interest_rate import (
    LTIRData,
    LTIRQueryParams,
)
from openbb_oecd.utils import helpers
from pydantic import Field, field_validator

ltir_mapping = {
    "BEL": "belgium",
    "IRL": "ireland",
    "MEX": "mexico",
    "IDN": "indonesia",
    "NZL": "new_zealand",
    "JPN": "japan",
    "GBR": "united_kingdom",
    "FRA": "france",
    "CHL": "chile",
    "CAN": "canada",
    "NLD": "netherlands",
    "USA": "united_states",
    "KOR": "south_korea",
    "NOR": "norway",
    "AUT": "austria",
    "ZAF": "south_africa",
    "DNK": "denmark",
    "CHE": "switzerland",
    "HUN": "hungary",
    "LUX": "luxembourg",
    "AUS": "australia",
    "DEU": "germany",
    "SWE": "sweden",
    "ISL": "iceland",
    "TUR": "turkey",
    "GRC": "greece",
    "ISR": "israel",
    "CZE": "czech_republic",
    "LVA": "latvia",
    "SVN": "slovenia",
    "POL": "poland",
    "EST": "estonia",
    "LTU": "lithuania",
    "PRT": "portugal",
    "CRI": "costa_rica",
    "SVK": "slovakia",
    "FIN": "finland",
    "ESP": "spain",
    "RUS": "russia",
    "EA19": "euro_area19",
    "COL": "colombia",
    "ITA": "italy",
    "IND": "india",
    "CHN": "china",
    "HRV": "croatia",
}

countries = tuple(ltir_mapping.values()) + ("all",)
CountriesLiteral = Literal[countries]  # type: ignore
country_to_code = {v: k for k, v in ltir_mapping.items()}


class OECDLTIRQueryParams(LTIRQueryParams):
    """OECD Short Term Interest Rate Query."""

    country: CountriesLiteral = Field(
        description="Country to get GDP for.", default="united_states"
    )

    frequency: Literal["monthly", "quarterly", "annual"] = Field(
        description="Frequency to get interest rate for for.", default="monthly"
    )


class OECDLTIRData(LTIRData):
    """OECD Long Term Interest Rate Data."""

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, in_date: Union[date, str]):  # pylint: disable=E0213
        """Validate value."""
        if isinstance(in_date, str):
            # i.e 2022-Q1
            if re.match(r"\d{4}-Q[1-4]$", in_date):
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
            # Now match if it is monthly, i.e 2022-01
            elif re.match(r"\d{4}-\d{2}$", in_date):
                year, month = map(int, in_date.split("-"))
                if month == 12:
                    return date(year, month, 31)
                next_month = date(year, month + 1, 1)
                return date(next_month.year, next_month.month, 1) - timedelta(days=1)
            # Now match if it is yearly, i.e 2022
            elif re.match(r"\d{4}$", in_date):
                return date(int(in_date), 12, 31)
        # If the input date is a year
        if isinstance(in_date, int):
            return date(in_date, 12, 31)

        return in_date


class OECDLTIRFetcher(Fetcher[OECDLTIRQueryParams, List[OECDLTIRData]]):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDLTIRQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params["start_date"] is None:
            transformed_params["start_date"] = date(1950, 1, 1)
        if transformed_params["end_date"] is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)

        return OECDLTIRQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDLTIRQueryParams,  # pylint: disable=W0613
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the OECD endpoint."""
        frequency = query.frequency[0].upper()
        country = "" if query.country == "all" else country_to_code[query.country]
        url = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_KEI@DF_KEI,4.0/..IRLT...."
        data = helpers.get_possibly_cached_data(
            url, function="economy_long_term_interest_rate"
        )
        query = f"FREQ=='{frequency}'"
        query = query + f" & REF_AREA=='{country}'" if country else query
        # Filter down
        data = (
            data.query(query)
            .reset_index(drop=True)[["REF_AREA", "TIME_PERIOD", "VALUE"]]
            .rename(
                columns={"REF_AREA": "country", "TIME_PERIOD": "date", "VALUE": "value"}
            )
        )
        data["country"] = data["country"].map(ltir_mapping)
        data = data.fillna("N/A").replace("N/A", None)
        return data.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDLTIRQueryParams, data: Dict, **kwargs: Any
    ) -> List[OECDLTIRData]:
        """Transform the data from the OECD endpoint."""
        return [OECDLTIRData.model_validate(d) for d in data]
