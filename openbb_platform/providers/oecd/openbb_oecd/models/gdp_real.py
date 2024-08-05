"""OECD Real GDP Model."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.gdp_real import (
    GdpRealData,
    GdpRealQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_oecd.utils.constants import CODE_TO_COUNTRY_GDP, COUNTRY_TO_CODE_GDP
from pydantic import Field, field_validator

COUNTRIES = list(COUNTRY_TO_CODE_GDP) + ["all"]


class OECDGdpRealQueryParams(GdpRealQueryParams):
    """OECD Real GDP Query.

    Source: https://www.oecd.org/en/data/datasets/gdp-and-non-financial-accounts.html

    This table presents Gross Domestic Product (GDP) and its main components according to the expenditure approach.
    Data is presented in US dollars. In the expenditure approach, the components of GDP are:
    final consumption expenditure of households and non-profit institutions serving households (NPISH)
    plus final consumption expenditure of General Government plus gross fixed capital formation (or investment)
    plus net trade (exports minus imports).
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": COUNTRIES,
        }
    }

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", "")
        + " Use 'all' to get data for all available countries.",
        default="united_states",
    )
    frequency: Literal["quarter", "annual"] = Field(
        description="Frequency of the data.",
        default="quarter",
        json_schema_extra={"choices": ["quarter", "annual"]},
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import check_item

        result: List = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            if v.upper() in CODE_TO_COUNTRY_GDP:
                result.append(CODE_TO_COUNTRY_GDP.get(v.upper()))
                continue
            try:
                check_item(v.lower(), COUNTRIES)
            except Exception as e:
                if len(values) == 1:
                    raise e from e
                warn(f"Invalid country: {v}. Skipping...")
                continue
            result.append(v.lower())
        if result:
            return ",".join(result)
        raise OpenBBError(f"No valid country found. -> {values}")


class OECDGdpRealData(GdpRealData):
    """OECD Real GDP Data."""


class OECDGdpRealFetcher(Fetcher[OECDGdpRealQueryParams, List[OECDGdpRealData]]):
    """OECD GDP Real Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDGdpRealQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                date(2020, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1947, 1, 1)
            )
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return OECDGdpRealQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: OECDGdpRealQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from openbb_oecd.utils.helpers import oecd_date_to_python_date
        from numpy import nan
        from pandas import read_csv
        from openbb_core.provider.utils.helpers import amake_request

        frequency = "Q" if query.frequency == "quarter" else "A"

        def country_string(input_str: str):
            """Convert the list of countries to an abbreviated string."""
            if input_str == "all":
                return ""
            _countries = input_str.split(",")

            return "+".join([COUNTRY_TO_CODE_GDP[country] for country in _countries])

        country = country_string(query.country) if query.country else ""

        url = (
            "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,1.1"
            + f"/{frequency}..{country}.S1..B1GQ._Z...USD_PPP.LR.LA.T0102?"
            + f"&startPeriod={query.start_date}&endPeriod={query.end_date}"
            + "&dimensionAtObservation=TIME_PERIOD&detail=dataonly&format=csvfile"
        )

        async def response_callback(response, _):
            """Response callback."""
            if response.status != 200:
                raise OpenBBError(f"Error with the OECD request: {response.status}")
            return await response.text()

        response = await amake_request(
            url, timeout=30, response_callback=response_callback
        )

        df = read_csv(StringIO(response)).get(  # type: ignore
            ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]
        )
        if df.empty:  # type: ignore
            raise EmptyDataError()
        df = df.rename(  # type: ignore
            columns={"REF_AREA": "country", "TIME_PERIOD": "date", "OBS_VALUE": "value"}
        )

        def apply_map(x):
            """Apply the country map."""
            v = CODE_TO_COUNTRY_GDP.get(x, x)
            v = v.replace("_", " ").title()
            return v

        df["country"] = df["country"].apply(apply_map).str.replace("Oecd", "OECD")
        df["date"] = df["date"].apply(oecd_date_to_python_date)
        df = df[(df["date"] <= query.end_date) & (df["date"] >= query.start_date)]
        df["value"] = (df["value"].astype(float) * 1_000_000).astype("int64")

        df = df.sort_values(by=["date", "value"], ascending=[True, False])

        return df.replace({nan: None}).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDGdpRealQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[OECDGdpRealData]:
        """Transform the data from the OECD endpoint."""
        return [OECDGdpRealData.model_validate(d) for d in data]
