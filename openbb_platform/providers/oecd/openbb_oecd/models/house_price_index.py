"""OECD House Price Index Model."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.house_price_index import (
    HousePriceIndexData,
    HousePriceIndexQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import check_item
from openbb_oecd.utils.constants import (
    CODE_TO_COUNTRY_RGDP,
    COUNTRY_TO_CODE_RGDP,
)
from pydantic import Field, field_validator

countries = tuple(CODE_TO_COUNTRY_RGDP.values()) + ("all",)
CountriesList = list(countries)  # type: ignore
frequency_dict = {
    "monthly": "M",
    "quarter": "Q",
    "annual": "A",
}
transform_dict = {"yoy": "PA", "period": "PC", "index": "IX"}


class OECDHousePriceIndexQueryParams(HousePriceIndexQueryParams):
    """OECD House Price Index Query.

    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": CountriesList,
        }
    }

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        result: List = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            if v.upper() in CODE_TO_COUNTRY_RGDP:
                result.append(CODE_TO_COUNTRY_RGDP.get(v.upper()))
                continue
            try:
                check_item(v.lower(), CountriesList)
            except Exception as e:
                if len(values) == 1:
                    raise e from e
                warn(f"Invalid country: {v}. Skipping...")
                continue
            result.append(v.lower())
        if result:
            return ",".join(result)
        raise OpenBBError(f"No valid country found. -> {values}")


class OECDHousePriceIndexData(HousePriceIndexData):
    """OECD House Price Index Data."""


class OECDHousePriceIndexFetcher(
    Fetcher[OECDHousePriceIndexQueryParams, List[OECDHousePriceIndexData]]
):
    """OECD House Price Index Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDHousePriceIndexQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                date(2000, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1969, 1, 1)
            )
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return OECDHousePriceIndexQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDHousePriceIndexQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from openbb_oecd.utils.helpers import oecd_date_to_python_date  # noqa
        from openbb_core.provider.utils.helpers import make_request  # noqa
        from pandas import read_csv  # noqa

        frequency = frequency_dict.get(query.frequency, "Q")
        transform = transform_dict.get(query.transform, "PA")

        def country_string(input_str: str):
            if input_str == "all":
                return ""
            _countries = input_str.split(",")
            return "+".join([COUNTRY_TO_CODE_RGDP[country] for country in _countries])

        country = country_string(query.country) if query.country else ""
        start_date = query.start_date.strftime("%Y-%m") if query.start_date else ""
        end_date = query.end_date.strftime("%Y-%m") if query.end_date else ""
        url = (
            "https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_RHPI_TARGET@DF_RHPI_TARGET,1.0/"
            + f"COU.{country}.{frequency}.RHPI.{transform}....?"
            + f"startPeriod={start_date}&endPeriod={end_date}"
            + "&dimensionAtObservation=TIME_PERIOD&detail=dataonly"
        )
        headers = {"Accept": "application/vnd.sdmx.data+csv; charset=utf-8"}
        response = make_request(url, headers=headers, timeout=20)
        if response.status_code == 404 and frequency == "M":
            warn("No monthly data found. Switching to quarterly data.")
            response = make_request(
                url.replace(".M.RHPI.", ".Q.RHPI."), headers=headers
            )
        if response.status_code != 200:
            raise OpenBBError(
                f"Error with the OECD request (HTTP {response.status_code}): `{response.text}`"
            )
        df = read_csv(StringIO(response.text)).get(
            ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]
        )
        if df.empty:
            raise EmptyDataError()
        df = df.rename(
            columns={"REF_AREA": "country", "TIME_PERIOD": "date", "OBS_VALUE": "value"}
        )
        df.country = df.country.map(CODE_TO_COUNTRY_RGDP)
        df.date = df.date.apply(oecd_date_to_python_date)
        df = (
            df.query("value.notnull()")
            .set_index(["date", "country"])
            .sort_index()
            .reset_index()
        )

        return df.to_dict("records")

    @staticmethod
    def transform_data(
        query: OECDHousePriceIndexQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[OECDHousePriceIndexData]:
        """Transform the data from the OECD endpoint."""
        return [OECDHousePriceIndexData.model_validate(d) for d in data]
