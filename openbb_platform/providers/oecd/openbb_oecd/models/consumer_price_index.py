"""OECD CPI Data."""

import re
from datetime import date, timedelta
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.consumer_price_index import (
    ConsumerPriceIndexData,
    ConsumerPriceIndexQueryParams,
)
from openbb_oecd.utils import helpers
from openbb_oecd.utils.constants import (
    CODE_TO_COUNTRY_CPI,
    COUNTRY_TO_CODE_CPI,
)
from pydantic import Field, field_validator

countries = tuple(CODE_TO_COUNTRY_CPI.values()) + ("all",)
CountriesLiteral = Literal[countries]  # type: ignore

expendature_dict = {
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
    "CP014T043": "housing",
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
expendature_dict = {v: k for k, v in expendature_dict.items()}
ExpendatureLiteral = Literal[tuple(expendature_dict.values())]  # type: ignore


class OECDCPIQueryParams(ConsumerPriceIndexQueryParams):
    """OECD CPI Query.

    Source: https://data-explorer.oecd.org/?lc=en
    """

    country: CountriesLiteral = Field(
        description="Country to get CPI for.", default="united_states"
    )

    seasonal_adjustment: bool = Field(
        description="Whether to get seasonally adjusted CPI. Defaults to False.",
        default=False,
    )

    units: Literal["index", "yoy", "mom"] = Field(
        description="Units to get CPI for. Either index, month over month or year over year. Defaults to year over year.",
        default="yoy",
    )

    expendature: ExpendatureLiteral = Field(
        description="Expendature component of CPI.",
        default="total",
    )


class OECDCPIData(ConsumerPriceIndexData):
    """OECD CPI Data."""

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
                year, month = map(int, in_date.split("-"))  # type: ignore
                if month == 12:
                    return date(year, month, 31)  # type: ignore
                next_month = date(year, month + 1, 1)  # type: ignore
                return date(next_month.year, next_month.month, 1) - timedelta(days=1)
            # Now match if it is yearly, i.e 2022
            elif re.match(r"\d{4}$", in_date):
                return date(int(in_date), 12, 31)
        # If the input date is a year
        if isinstance(in_date, int):
            return date(in_date, 12, 31)

        return in_date


class OECDCPIFetcher(Fetcher[OECDCPIQueryParams, List[OECDCPIData]]):
    """Transform the query, extract and transform the data from the OECD endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> OECDCPIQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params["start_date"] is None:
            transformed_params["start_date"] = date(1950, 1, 1)
        if transformed_params["end_date"] is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params["country"] is None:
            transformed_params["country"] = "united_states"

        return OECDCPIQueryParams(**transformed_params)

    # pylint: disable=unused-argument
    @staticmethod
    def extract_data(
        query: OECDCPIQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the OECD endpoint."""
        methodology = ["N", "HICP"][query.harmonized]
        frequency = query.frequency[0].upper()
        units = {
            "index": "IX",
            "yoy": "PA",
            "mom": "PC",
        }[query.units]
        expendature = expendature_dict[query.expendature]
        # transform = {"mom": "G1", "yoy": "GY", "na": "_Z", "none": ""}[
        #     query.transformation
        # ]
        seasonal_adjustment = "Y" if query.seasonal_adjustment else "N"
        country = "" if query.country == "all" else COUNTRY_TO_CODE_CPI[query.country]
        # For caching, include this in the key
        query_dict = {
            k: v
            for k, v in query.__dict__.items()
            if k not in ["start_date", "end_date"]
        }

        url = (
            f"https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/"
            f"{country}.{frequency}.{methodology}.CPI.{units}.{expendature}.{seasonal_adjustment}."
        )
        data = helpers.get_possibly_cached_data(
            url, function="economy_cpi", query_dict=query_dict
        )
        url_query = (
            f"METHODOLOGY=='{methodology}' & UNIT_MEASURE=='{units}' & FREQ=='{frequency}' & "
            f"ADJUSTMENT=='{seasonal_adjustment}' & EXPENDITURE=='{expendature}'"
        )
        url_query = url_query + f" & REF_AREA=='{country}'" if country else url_query

        # Filter down
        data = (
            data.query(url_query)
            .reset_index(drop=True)[["REF_AREA", "TIME_PERIOD", "VALUE"]]
            .rename(
                columns={"REF_AREA": "country", "TIME_PERIOD": "date", "VALUE": "value"}
            )
        )
        data["country"] = data["country"].map(CODE_TO_COUNTRY_CPI)

        data["date"] = data["date"].apply(helpers.oecd_date_to_python_date)
        data = data[
            (data["date"] <= query.end_date) & (data["date"] >= query.start_date)
        ]

        return data.to_dict(orient="records")

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: OECDCPIQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[OECDCPIData]:
        """Transform the data from the OECD endpoint."""
        return [OECDCPIData.model_validate(d) for d in data]
