"""OECD CPI Data."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Dict, List, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.consumer_price_index import (
    ConsumerPriceIndexData,
    ConsumerPriceIndexQueryParams,
)
from openbb_core.provider.utils.helpers import check_item
from openbb_oecd.utils.constants import (
    CODE_TO_COUNTRY_CPI,
    COUNTRY_TO_CODE_CPI,
)
from pydantic import Field, field_validator

countries = tuple(CODE_TO_COUNTRY_CPI.values()) + ("all",)
CountriesList = list(countries)  # type: ignore

expenditure_dict_rev = {
    "_T": "total",
    "CP01": "food_non_alcoholic_beverages",
    "CP02": "alcoholic_beverages_tobacco_narcotics",
    "CP03": "clothing_footwear",
    "CP04": "housing_water_electricity_gas",
    "CP05": "furniture_household_equipment",
    "CP06": "health",
    "CP07": "transport",
    "CP08": "communication",
    "CP09": "recreation_culture",
    "CP10": "education",
    "CP11": "restaurants_hotels",
    "CP12": "miscellaneous_goods_services",
    "CP045_0722": "energy",
    "GD": "goods",
    "CP041T043": "housing",
    "CP041T043X042": "housing_excluding_rentals" "",
    "_TXCP01_NRG": "all_non_food_non_energy",
    "SERVXCP041_042_0432": "services_less_housing",
    "SERVXCP041_0432": "services_less_house_excl_rentals",
    "SERV": "services",
    "_TXNRG_01_02": "overall_excl_energy_food_alcohol_tobacco",
    "CPRES": "residuals",
    "CP0722": "fuels_lubricants_personal",
    "CP041": "actual_rentals",
    "CP042": "imputed_rentals",
    "CP043": "maintenance_repair_dwelling",
    "CP044": "water_supply_other_services",
    "CP045": "electricity_gas_other_fuels",
}
expenditure_dict = {v: k for k, v in expenditure_dict_rev.items()}
expenditures = tuple(expenditure_dict.keys()) + ("all",)
ExpenditureChoices = Literal[
    "total",
    "all",
    "actual_rentals",
    "alcoholic_beverages_tobacco_narcotics",
    "all_non_food_non_energy",
    "clothing_footwear",
    "communication",
    "education",
    "electricity_gas_other_fuels",
    "energy",
    "overall_excl_energy_food_alcohol_tobacco",
    "food_non_alcoholic_beverages",
    "fuels_lubricants_personal",
    "furniture_household_equipment",
    "goods",
    "housing",
    "housing_excluding_rentals",
    "housing_water_electricity_gas",
    "health",
    "imputed_rentals",
    "maintenance_repair_dwelling",
    "miscellaneous_goods_services",
    "recreation_culture",
    "residuals",
    "restaurants_hotels",
    "services_less_housing",
    "services_less_house_excl_rentals",
    "services",
    "transport",
    "water_supply_other_services",
]


class OECDCPIQueryParams(ConsumerPriceIndexQueryParams):
    """OECD CPI Query.

    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": CountriesList,
        },
    }

    country: str = Field(
        description="Country to get CPI for.  This is the list of OECD supported countries",
        default="united_states",
    )
    expenditure: ExpenditureChoices = Field(
        description="Expenditure component of CPI.",
        default="total",
        json_schema_extra={"choices": list(expenditures)},
    )

    @field_validator("country", mode="before", check_fields=False)
    def validate_country(cls, c: str):  # pylint: disable=E0213
        """Validate country."""
        result: List = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            check_item(v.lower(), CountriesList)
            result.append(v.lower())
        return ",".join(result)


class OECDCPIData(ConsumerPriceIndexData):
    """OECD CPI Data."""

    expenditure: str = Field(description="Expenditure component of CPI.")


class OECDCPIFetcher(Fetcher[OECDCPIQueryParams, List[OECDCPIData]]):
    """OECD CPI Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDCPIQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = date(1950, 1, 1)
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return OECDCPIQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDCPIQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from requests.exceptions import HTTPError  # noqa
        from openbb_oecd.utils import helpers  # noqa

        methodology = "HICP" if query.harmonized is True else "N"
        query.units = "mom" if query.transform == "period" else query.transform
        query.frequency = (
            "monthly"
            if query.harmonized is True and query.frequency == "quarter"
            else query.frequency
        )
        frequency = query.frequency[0].upper()
        units = {
            "index": "IX",
            "yoy": "PA",
            "mom": "PC",
        }[query.units]
        expenditure = (
            "" if query.expenditure == "all" else expenditure_dict[query.expenditure]
        )

        def country_string(input_str: str):
            if input_str == "all":
                return ""
            _countries = input_str.split(",")
            return "+".join([COUNTRY_TO_CODE_CPI[country] for country in _countries])

        country = country_string(query.country)
        # For caching, include this in the key
        query_dict = {
            k: v
            for k, v in query.__dict__.items()
            if k not in ["start_date", "end_date"]
        }

        url = (
            f"https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/"
            f"{country}.{frequency}.{methodology}.CPI.{units}.{expenditure}.N."
        )
        try:
            data = helpers.get_possibly_cached_data(
                url, function="economy_cpi", query_dict=query_dict
            )
        except HTTPError as exc:
            raise OpenBBError("No data found for the given query.") from exc
        url_query = f"METHODOLOGY=='{methodology}' & UNIT_MEASURE=='{units}' & FREQ=='{frequency}'"

        if country != "all":
            if "+" in country:
                _countries = country.split("+")
                country_conditions = " or ".join(
                    [f"REF_AREA=='{c}'" for c in _countries]
                )
                url_query += f" & ({country_conditions})"
            else:
                url_query = url_query + f" & REF_AREA=='{country}'"
        url_query = (
            url_query + f" & EXPENDITURE=='{expenditure}'"
            if query.expenditure != "all"
            else url_query
        )
        # Filter down
        data = (
            data.query(url_query)
            .reset_index(drop=True)[["REF_AREA", "TIME_PERIOD", "VALUE", "EXPENDITURE"]]
            .rename(
                columns={
                    "REF_AREA": "country",
                    "TIME_PERIOD": "date",
                    "VALUE": "value",
                    "EXPENDITURE": "expenditure",
                }
            )
        )
        data["country"] = data["country"].map(CODE_TO_COUNTRY_CPI)
        data["expenditure"] = data["expenditure"].map(expenditure_dict_rev)
        data["date"] = data["date"].apply(helpers.oecd_date_to_python_date)
        data = data[
            (data["date"] <= query.end_date) & (data["date"] >= query.start_date)
        ]
        # Normalize the percent value.
        if query.transform in ("yoy", "period"):
            data["value"] = data["value"].astype(float) / 100

        return data.fillna("N/A").replace("N/A", None).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDCPIQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[OECDCPIData]:
        """Transform the data from the OECD endpoint."""
        return [
            OECDCPIData.model_validate(d) for d in sorted(data, key=lambda x: x["date"])
        ]
