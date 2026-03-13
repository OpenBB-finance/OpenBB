"""IMF CPI Data."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.consumer_price_index import (
    ConsumerPriceIndexData,
    ConsumerPriceIndexQueryParams,
)
from openbb_imf.utils.helpers import normalize_country_label
from openbb_imf.utils.query_builder import ImfQueryBuilder
from pydantic import Field, field_validator

CpiCountries = [
    {"label": "Afghanistan", "value": "AFG"},
    {"label": "Albania", "value": "ALB"},
    {"label": "Algeria", "value": "DZA"},
    {"label": "Angola", "value": "AGO"},
    {"label": "Anguilla, United Kingdom-British Overseas Territory", "value": "AIA"},
    {"label": "Antigua and Barbuda", "value": "ATG"},
    {"label": "Argentina", "value": "ARG"},
    {"label": "Armenia, Republic of", "value": "ARM"},
    {"label": "Aruba, Kingdom of the Netherlands", "value": "ABW"},
    {"label": "Australia", "value": "AUS"},
    {"label": "Austria", "value": "AUT"},
    {"label": "Azerbaijan, Republic of", "value": "AZE"},
    {"label": "Bahamas, The", "value": "BHS"},
    {"label": "Bahrain", "value": "BHR"},
    {"label": "Bangladesh", "value": "BGD"},
    {"label": "Barbados", "value": "BRB"},
    {"label": "Belarus, Republic of", "value": "BLR"},
    {"label": "Belgium", "value": "BEL"},
    {"label": "Belize", "value": "BLZ"},
    {"label": "Benin", "value": "BEN"},
    {"label": "Bhutan", "value": "BTN"},
    {"label": "Bolivia", "value": "BOL"},
    {"label": "Bosnia and Herzegovina", "value": "BIH"},
    {"label": "Botswana", "value": "BWA"},
    {"label": "Brazil", "value": "BRA"},
    {"label": "British Virgin Islands", "value": "VGB"},
    {"label": "Brunei Darussalam", "value": "BRN"},
    {"label": "Bulgaria", "value": "BGR"},
    {"label": "Burkina Faso", "value": "BFA"},
    {"label": "Burundi", "value": "BDI"},
    {"label": "Cabo Verde", "value": "CPV"},
    {"label": "Cambodia", "value": "KHM"},
    {"label": "Cameroon", "value": "CMR"},
    {"label": "Canada", "value": "CAN"},
    {"label": "Cayman Islands", "value": "CYM"},
    {"label": "Central African Republic", "value": "CAF"},
    {"label": "Chad", "value": "TCD"},
    {"label": "Chile", "value": "CHL"},
    {"label": "China", "value": "CHN"},
    {"label": "Colombia", "value": "COL"},
    {"label": "Comoros", "value": "COM"},
    {"label": "Congo", "value": "COG"},
    {"label": "Costa Rica", "value": "CRI"},
    {"label": "Croatia, Republic of", "value": "HRV"},
    {"label": "Curacao", "value": "CUW"},
    {"label": "Cyprus", "value": "CYP"},
    {"label": "Czech Republic", "value": "CZE"},
    {"label": "Democratic Republic of the Congo", "value": "COD"},
    {"label": "Denmark", "value": "DNK"},
    {"label": "Djibouti", "value": "DJI"},
    {"label": "Dominica", "value": "DMA"},
    {"label": "Dominican Republic", "value": "DOM"},
    {"label": "Ecuador", "value": "ECU"},
    {"label": "Egypt", "value": "EGY"},
    {"label": "El Salvador", "value": "SLV"},
    {"label": "Equatorial Guinea, Republic of", "value": "GNQ"},
    {"label": "Estonia, Republic of", "value": "EST"},
    {"label": "Eswatini, Kingdom of", "value": "SWZ"},
    {"label": "Ethiopia", "value": "ETH"},
    {"label": "Euro Area (EA)", "value": "G163"},
    {"label": "Fiji, Republic of", "value": "FJI"},
    {"label": "Finland", "value": "FIN"},
    {"label": "France", "value": "FRA"},
    {"label": "Gabon", "value": "GAB"},
    {"label": "Gambia", "value": "GMB"},
    {"label": "Georgia", "value": "GEO"},
    {"label": "Germany", "value": "DEU"},
    {"label": "Ghana", "value": "GHA"},
    {"label": "Greece", "value": "GRC"},
    {"label": "Greenland", "value": "GRL"},
    {"label": "Grenada", "value": "GRD"},
    {"label": "Guadeloupe", "value": "GLP"},
    {"label": "Guatemala", "value": "GTM"},
    {"label": "Guinea", "value": "GIN"},
    {"label": "Guinea-Bissau", "value": "GNB"},
    {"label": "Guyana", "value": "GUY"},
    {"label": "Haiti", "value": "HTI"},
    {"label": "Honduras", "value": "HND"},
    {"label": "Hong Kong", "value": "HKG"},
    {"label": "Hungary", "value": "HUN"},
    {"label": "Iceland", "value": "ISL"},
    {"label": "India", "value": "IND"},
    {"label": "Indonesia", "value": "IDN"},
    {"label": "Iran", "value": "IRN"},
    {"label": "Iraq", "value": "IRQ"},
    {"label": "Ireland", "value": "IRL"},
    {"label": "Israel", "value": "ISR"},
    {"label": "Italy", "value": "ITA"},
    {"label": "Ivory Coast", "value": "CIV"},
    {"label": "Jamaica", "value": "JAM"},
    {"label": "Japan", "value": "JPN"},
    {"label": "Jordan", "value": "JOR"},
    {"label": "Kazakhstan", "value": "KAZ"},
    {"label": "Kenya", "value": "KEN"},
    {"label": "Kiribati", "value": "KIR"},
    {"label": "Kosovo", "value": "KOS"},
    {"label": "Kuwait", "value": "KWT"},
    {"label": "Kyrgyz Republic", "value": "KGZ"},
    {"label": "Lao", "value": "LAO"},
    {"label": "Latvia, Republic of", "value": "LVA"},
    {"label": "Lebanon", "value": "LBN"},
    {"label": "Lesotho", "value": "LSO"},
    {"label": "Liberia", "value": "LBR"},
    {"label": "Libya", "value": "LBY"},
    {"label": "Lithuania, Republic of", "value": "LTU"},
    {"label": "Luxembourg", "value": "LUX"},
    {"label": "Macao", "value": "MAC"},
    {"label": "Madagascar", "value": "MDG"},
    {"label": "Malawi", "value": "MWI"},
    {"label": "Malaysia", "value": "MYS"},
    {"label": "Maldives", "value": "MDV"},
    {"label": "Mali", "value": "MLI"},
    {"label": "Malta", "value": "MLT"},
    {"label": "Martinique", "value": "MTQ"},
    {"label": "Mauritania", "value": "MRT"},
    {"label": "Mauritius", "value": "MUS"},
    {"label": "Mexico", "value": "MEX"},
    {"label": "Micronesia, Federated States of", "value": "FSM"},
    {"label": "Moldova, Republic of", "value": "MDA"},
    {"label": "Mongolia", "value": "MNG"},
    {"label": "Montenegro", "value": "MNE"},
    {"label": "Montserrat", "value": "MSR"},
    {"label": "Morocco", "value": "MAR"},
    {"label": "Mozambique", "value": "MOZ"},
    {"label": "Myanmar", "value": "MMR"},
    {"label": "Namibia", "value": "NAM"},
    {"label": "Nauru, Republic of", "value": "NRU"},
    {"label": "Nepal", "value": "NPL"},
    {"label": "Netherlands", "value": "NLD"},
    {"label": "Netherlands Antilles", "value": "ANT"},
    {"label": "New Caledonia", "value": "NCL"},
    {"label": "New Zealand", "value": "NZL"},
    {"label": "Nicaragua", "value": "NIC"},
    {"label": "Niger", "value": "NER"},
    {"label": "Nigeria", "value": "NGA"},
    {"label": "North Macedonia", "value": "MKD"},
    {"label": "Norway", "value": "NOR"},
    {"label": "Oman", "value": "OMN"},
    {"label": "Pakistan", "value": "PAK"},
    {"label": "Palau", "value": "PLW"},
    {"label": "Palestine", "value": "WBG"},
    {"label": "Panama", "value": "PAN"},
    {"label": "Papua New Guinea", "value": "PNG"},
    {"label": "Paraguay", "value": "PRY"},
    {"label": "Peru", "value": "PER"},
    {"label": "Philippines", "value": "PHL"},
    {"label": "Poland", "value": "POL"},
    {"label": "Portugal", "value": "PRT"},
    {"label": "Qatar", "value": "QAT"},
    {"label": "Romania", "value": "ROU"},
    {"label": "Russia", "value": "RUS"},
    {"label": "Rwanda", "value": "RWA"},
    {"label": "Saint Kitts and Nevis", "value": "KNA"},
    {"label": "Saint Lucia", "value": "LCA"},
    {"label": "Saint Vincent and the Grenadines", "value": "VCT"},
    {"label": "Samoa", "value": "WSM"},
    {"label": "San Marino", "value": "SMR"},
    {"label": "Sao Tome and Principe", "value": "STP"},
    {"label": "Saudi Arabia", "value": "SAU"},
    {"label": "Senegal", "value": "SEN"},
    {"label": "Serbia", "value": "SRB"},
    {"label": "Seychelles", "value": "SYC"},
    {"label": "Sierra Leone", "value": "SLE"},
    {"label": "Singapore", "value": "SGP"},
    {"label": "Sint Maarten (Dutch part)", "value": "SXM"},
    {"label": "Slovak Republic", "value": "SVK"},
    {"label": "Slovenia, Republic of", "value": "SVN"},
    {"label": "Solomon Islands", "value": "SLB"},
    {"label": "Somalia", "value": "SOM"},
    {"label": "South Africa", "value": "ZAF"},
    {"label": "South Korea", "value": "KOR"},
    {"label": "South Sudan", "value": "SSD"},
    {"label": "Spain", "value": "ESP"},
    {"label": "Sri Lanka", "value": "LKA"},
    {"label": "Sudan", "value": "SDN"},
    {"label": "Suriname", "value": "SUR"},
    {"label": "Sweden", "value": "SWE"},
    {"label": "Switzerland", "value": "CHE"},
    {"label": "Syria", "value": "SYR"},
    {"label": "Tajikistan", "value": "TJK"},
    {"label": "Tanzania", "value": "TZA"},
    {"label": "Thailand", "value": "THA"},
    {"label": "Timor-Leste", "value": "TLS"},
    {"label": "Togo", "value": "TGO"},
    {"label": "Tonga", "value": "TON"},
    {"label": "Trinidad and Tobago", "value": "TTO"},
    {"label": "Tunisia", "value": "TUN"},
    {"label": "Turkey", "value": "TUR"},
    {"label": "Tuvalu", "value": "TUV"},
    {"label": "Uganda", "value": "UGA"},
    {"label": "Ukraine", "value": "UKR"},
    {"label": "United Arab Emirates", "value": "ARE"},
    {"label": "United Kingdom", "value": "GBR"},
    {"label": "United States", "value": "USA"},
    {"label": "Uruguay", "value": "URY"},
    {"label": "Uzbekistan", "value": "UZB"},
    {"label": "Vanuatu", "value": "VUT"},
    {"label": "Venezuela", "value": "VEN"},
    {"label": "Viet Nam", "value": "VNM"},
    {"label": "Yemen", "value": "YEM"},
    {"label": "Zambia", "value": "ZMB"},
    {"label": "Zimbabwe", "value": "ZWE"},
    {"label": "All", "value": "*"},
]
CPI_LABEL_TO_CODE: dict[str, str] = {
    normalize_country_label(item["label"]): item["value"] for item in CpiCountries
}
CPI_CODE_TO_LABEL: dict[str, str] = {
    item["value"]: normalize_country_label(item["label"]) for item in CpiCountries
}
CPI_CODE_SET: set[str] = {item["value"] for item in CpiCountries}
transformation_map: dict = {
    "index": "IX",
    "period": "POP_PCH_PA_PT",
    "yoy": "YOY_PCH_PA_PT",
    "ref_index": "SRP_IX",
    "ref_period": "SRP_POP_PCH_PA_PT",
    "ref_yoy": "SRP_YOY_PCH_PA_PT",
    "weight": "WGT",
    "weight_percent": "WGT_PT",
}
transformation_choices = [
    "index",
    "period",
    "yoy",
    "ref_index",
    "ref_period",
    "ref_yoy",
    "weight",
    "weight_percent",
]
expenditure_dict_rev: dict = {
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
    "*": "all",
}
expenditure_dict: dict = {v: k for k, v in expenditure_dict_rev.items()}

# Order mapping for sorting expenditure categories (COICOP codes)
# _T (total) comes first, then CP01-CP12 in numerical order
expenditure_order: dict[str, int] = {
    "_T": 0,
    "CP01": 1,
    "CP02": 2,
    "CP03": 3,
    "CP04": 4,
    "CP05": 5,
    "CP06": 6,
    "CP07": 7,
    "CP08": 8,
    "CP09": 9,
    "CP10": 10,
    "CP11": 11,
    "CP12": 12,
    "CP13": 13,
    "CP14": 14,
}
expenditure_choices = [
    "total",
    "all",
    "food_non_alcoholic_beverages",
    "alcoholic_beverages_tobacco_narcotics",
    "clothing_footwear",
    "housing_water_electricity_gas",
    "furniture_household_equipment",
    "health",
    "transport",
    "communication",
    "recreation_culture",
    "education",
    "restaurants_hotels",
    "miscellaneous_goods_services",
]


class ImfConsumerPriceIndexQueryParams(ConsumerPriceIndexQueryParams):
    """IMF CPI Query Params Model."""

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(CPI_LABEL_TO_CODE),
        },
        "transform": {
            "multiple_items_allowed": False,
            "choices": transformation_choices,
        },
        "expenditure": {
            "multiple_items_allowed": True,
            "choices": expenditure_choices,
        },
    }

    expenditure: str = Field(
        default="total", description="Expenditure component of CPI."
    )

    limit: int | None = Field(
        default=None,
        description="Maximum number of records to retrieve per series and country."
        + " If None, retrieves all available records.",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country.

        Accepts both ISO3 codes (e.g., "USA") and snake_case country names
        (e.g., "united_states"). Converts names to ISO3 codes.
        """
        result: list = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            v_upper = v.upper()
            v_lower = v.lower()
            # Check if it's a valid ISO3 code
            if v_upper in CPI_CODE_SET:
                result.append(v_upper)
            # Check if it's a valid snake_case country name
            elif v_lower in CPI_LABEL_TO_CODE:
                result.append(CPI_LABEL_TO_CODE[v_lower])
            else:
                raise ValueError(
                    f"Country '{v}' is not a valid IMF country code (ISO3) or country name."
                )

        return ",".join(result)

    @field_validator("expenditure", mode="before", check_fields=False)
    @classmethod
    def validate_expenditure(cls, v):
        """Validate expenditure."""
        expenditures = v.replace(" ", "_").split(",")
        new_expenditures: list[str] = []
        for e in expenditures:
            if (
                e.lower() not in expenditure_choices
                and e.upper() not in expenditure_dict_rev
            ):
                raise ValueError(
                    f"Expenditure '{e}' is not a valid choice. Valid choices:\n\n{expenditure_choices}"
                )
            new_expenditures.append(e.lower())
        return ",".join(new_expenditures)


class ImfConsumerPriceIndexData(ConsumerPriceIndexData):
    """IMF CPI Data Model."""

    unit: str = Field(
        description="Unit of measurement.",
    )
    unit_multiplier: int | float = Field(
        description="Unit multiplier for the observation value.",
    )
    country_code: str = Field(
        description="ISO3 country code.",
    )
    series_id: str = Field(
        description="IMF series identifier.",
    )
    expenditure: str = Field(
        description="Expenditure category.",
    )
    title: str = Field(
        description="Complete reference title for the series.",
    )
    order: int | None = Field(
        default=None,
        description="Sort order for expenditure categories and table presentations.",
    )


class ImfConsumerPriceIndexFetcher(
    Fetcher[ImfConsumerPriceIndexQueryParams, list[ImfConsumerPriceIndexData]]
):
    """IMF CPI Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> ImfConsumerPriceIndexQueryParams:
        """Transform query."""
        return ImfConsumerPriceIndexQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfConsumerPriceIndexQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract data."""
        countries = query.country.split(",")
        countries_str = (
            "*" if "*" in countries else "+".join([c.upper() for c in countries])
        )
        index_type = "HICP" if query.harmonized is True else "CPI"
        expenditures = query.expenditure.split(",") if query.expenditure else ["total"]
        expenditures_str = (
            "*"
            if "all" in expenditures
            else "+".join(
                [
                    (
                        e.upper()
                        if e.upper() in expenditure_dict_rev
                        else expenditure_dict[e]
                    )
                    for e in expenditures
                ]
            )
        )
        parameters: dict = {
            "COUNTRY": countries_str,
            "INDEX_TYPE": index_type,
            "COICOP_1999": expenditures_str,
            "TYPE_OF_TRANSFORMATION": transformation_map[query.transform],
            "FREQUENCY": query.frequency[0].upper(),
        }
        query_builder = ImfQueryBuilder()

        # Mappings from IMF dimension codes to user-friendly parameter names
        dim_to_param = {
            "COUNTRY": "country",
            "INDEX_TYPE": "harmonized",
            "COICOP_1999": "expenditure",
            "TYPE_OF_TRANSFORMATION": "transform",
            "FREQUENCY": "frequency",
        }
        # Reverse mappings for values
        transformation_rev = {v: k for k, v in transformation_map.items()}
        frequency_map = {"A": "annual", "Q": "quarter", "M": "monthly"}

        if query.limit is not None:
            parameters["lastNObservations"] = query.limit

        try:
            data = query_builder.fetch_data(
                dataflow="CPI",
                start_date=(
                    query.start_date.strftime("%Y-%m-%d") if query.start_date else None
                ),
                end_date=(
                    query.end_date.strftime("%Y-%m-%d") if query.end_date else None
                ),
                **parameters,
            )
        except ValueError as e:
            # Translate dimension codes to user-friendly parameter names in error message
            error_msg = str(e)
            for dim_code, param_name in dim_to_param.items():
                error_msg = error_msg.replace(f"'{dim_code}'", f"'{param_name}'")
                error_msg = error_msg.replace(f'"{dim_code}"', f'"{param_name}"')
            # Translate transformation values
            for api_val, user_val in transformation_rev.items():
                error_msg = error_msg.replace(f"'{api_val}'", f"'{user_val}'")
            # Translate frequency values
            for api_val, user_val in frequency_map.items():
                error_msg = error_msg.replace(f"'{api_val}'", f"'{user_val}'")
            # Translate expenditure values
            for api_val, user_val in expenditure_dict_rev.items():
                error_msg = error_msg.replace(f"'{api_val}'", f"'{user_val}'")
            # Translate INDEX_TYPE values
            error_msg = error_msg.replace("'CPI'", "'False'")
            error_msg = error_msg.replace("'HICP'", "'True'")
            # Translate country codes back to user-friendly names
            for code, label in CPI_CODE_TO_LABEL.items():
                error_msg = error_msg.replace(f"'{code}'", f"'{label}'")
            raise OpenBBError(error_msg) from e
        except OpenBBError as e:
            raise OpenBBError(e) from e

        return data

    @staticmethod
    def transform_data(
        query: ImfConsumerPriceIndexQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[list[ImfConsumerPriceIndexData]]:
        """Transform data and validate the model."""
        row_data = data.get("data", [])
        result: list[ImfConsumerPriceIndexData] = []
        metadata: dict = data.get("metadata", {})
        dataset_info: dict = metadata.pop("dataset", {})
        table_info: dict = (
            metadata.pop("IMF_STA_CPI_CPI", {})
            or metadata.pop("IMF_STA_CPI_HICP", {})
            or {}
        )
        dataset_info["index_type"] = table_info.get("indicator", "")
        dataset_info["index_description"] = table_info.get("description", "")

        if not row_data:
            raise OpenBBError("No data returned for the given query parameters.")

        for item in row_data:
            # Filter by date range here because IMF API date filtering can be inconsistent
            item_date = item.get("TIME_PERIOD", None)
            if (
                query.start_date
                and item_date
                and item_date < query.start_date.strftime("%Y-%m-%d")
            ):
                continue
            if (
                query.end_date
                and item_date
                and item_date > query.end_date.strftime("%Y-%m-%d")
            ):
                continue

            # Get translated labels (these are now human-readable)
            frequency = (item.get("FREQUENCY") or "").strip()
            index_type = (item.get("INDEX_TYPE") or "").strip()
            expenditure = (item.get("COICOP_1999") or item.get("title") or "").strip()
            expenditure_code = (item.get("COICOP_1999_code") or "").strip()
            transformation = (item.get("TYPE_OF_TRANSFORMATION") or "").strip()
            # Build title from translated values
            title = f"{frequency} {index_type} - {expenditure} - {transformation}"
            # Get unit from transformation (use last part if comma-separated)
            unit = (transformation.rsplit(", ", maxsplit=1)[-1] or "").strip()
            # Get sort order from expenditure code
            order = expenditure_order.get(expenditure_code, 99)
            obs_value = item.get("OBS_VALUE", None)
            multiplier = item.get("UNIT_MULT", 1)

            if "percent" in unit.lower() and obs_value is not None:
                obs_value = obs_value / 100.0
                multiplier = 100
            symbol = item.get("series_id", "").strip().split("IMF_STA_CPI_")[-1]
            symbol = f"CPI::{symbol}"
            new_row = {
                "date": item_date,
                "country": (item.get("COUNTRY") or "").strip() or None,
                "country_code": (item.get("country_code") or "").strip() or None,
                "series_id": symbol,
                "expenditure": expenditure or None,
                "title": title.strip(),
                "unit": unit,
                "unit_multiplier": multiplier,
                "value": obs_value,
                "order": order,
            }
            result.append(ImfConsumerPriceIndexData.model_validate(new_row))

        # Sort by date, then country, then order (expenditure)
        result.sort(
            key=lambda x: (
                x.date,
                x.country or "",
                x.order if x.order is not None else 99,
            )
        )

        return AnnotatedResult(
            result=result, metadata={"dataset": dataset_info, "series": metadata}
        )
