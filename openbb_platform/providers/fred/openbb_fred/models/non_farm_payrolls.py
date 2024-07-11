"""FRED Nonfarm Payrolls Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.non_farm_payrolls import (
    NonFarmPayrollsData,
    NonFarmPayrollsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

EstablishmentData = {
    "employees_nsa": "5645",
    "employees_sa": "4881",
    "employees_production_and_nonsupervisory": "6411",
    "employees_women": "6304",
    "employees_women_percent": "6433",
    "avg_hours": "6462",
    "avg_hours_production_and_nonsupervisory": "5923",
    "avg_hours_overtime": "6466",
    "avg_hours_overtime_production_and_nonsupervisory": "6442",
    "avg_earnings_hourly": "6471",
    "avg_earnings_hourly_production_and_nonsupervisory": "5943",
    "avg_earnings_weekly": "6490",
    "avg_earnings_weekly_production_and_nonsupervisory": "6020",
    "index_weekly_hours": "6637",
    "index_weekly_hours_production_and_nonsupervisory": "6095",
    "index_weekly_payrolls": "6654",
    "index_weekly_payrolls_production_and_nonsupervisory": "6280",
}

NFP_SECTOR_ORDER = [
    "Total nonfarm",
    "Total private",
    "Goods-producing",
    "Mining and logging",
    "Logging",
    "Mining",
    "Oil and gas extraction",
    "Mining, except oil and gas",
    "Coal mining",
    "Support activities for mining",
    "Construction",
    "Construction of buildings",
    "Residential building",
    "Nonresidential building",
    "Heavy and civil engineering construction",
    "Specialty trade contractors",
    "Residential specialty trade contractors",
    "Nonresidential specialty trade contractors",
    "Manufacturing",
    "Durable goods",
    "Wood products",
    "Nonmetallic mineral products",
    "Primary metals",
    "Fabricated metal products",
    "Machinery",
    "Computer and electronic products",
    "Computer and peripheral equipment",
    "Communication equipment",
    "Semiconductors and electronic components",
    "Electronic instruments",
    "Electrical equipment and appliances",
    "Transportation equipment",
    "Motor vehicles and parts",
    "Furniture and related products",
    "Miscellaneous durable goods manufacturing",
    "Nondurable goods",
    "Food manufacturing",
    "Textile mills",
    "Textile product mills",
    "Apparel",
    "Paper and paper products",
    "Printing and related support activities",
    "Petroleum and coal products",
    "Chemicals",
    "Plastics and rubber products",
    "Miscellaneous nondurable goods manufacturing",
    "Private service-providing",
    "Trade, transportation, and utilities",
    "Wholesale trade",
    "Durable goods",
    "Nondurable goods",
    "Electronic markets and agents and brokers",
    "Retail trade",
    "Motor vehicles and parts dealers",
    "Automobile dealers",
    "Furniture and home furnishings stores",
    "Electronics and appliance stores",
    "Building material and garden supply stores",
    "Food and beverage stores",
    "Health and personal care stores",
    "Gasoline stations",
    "Clothing and clothing accessories stores",
    "Sporting goods, hobby, book, and music stores",
    "General merchandise stores",
    "Transportation and warehousing",
    "Air transportation",
    "Rail transportation",
    "Water transportation",
    "Truck transportation",
    "Transit and ground passenger transportation",
    "Pipeline transportation",
    "Scenic and sightseeing transportation",
    "Support activities for transportation",
    "Couriers and messengers",
    "Warehousing and storage",
    "Utilities",
    "Information",
    "Publishing industries, except Internet",
    "Motion picture and sound recording industries",
    "Broadcasting, except Internet",
    "Telecommunications",
    "Data processing, hosting and related services",
    "Other information services",
    "Financial activities",
    "Finance and insurance",
    "Monetary authorities - central bank",
    "Credit intermediation and related activities",
    "Depository credit intermediation",
    "Commercial banking",
    "Securities, commodity contracts, investments, and funds and trusts",
    "Insurance carriers and related activities",
    "Real estate and rental and leasing",
    "Real estate",
    "Rental and leasing services",
    "Lessors of nonfinancial intangible assets",
    "Professional and business services",
    "Professional and technical services",
    "Legal services",
    "Accounting and bookkeeping services",
    "Architectural and engineering services",
    "Computer systems design and related services",
    "Management and technical consulting services",
    "Management of companies and enterprises",
    "Administrative and waste services",
    "Administrative and support services",
    "Employment services",
    "Temporary help services",
    "Business support services",
    "Services to buildings and dwellings",
    "Waste management and remediation services",
    "Education and health services",
    "Educational services",
    "Health care and social assistance",
    "Health care",
    "Ambulatory health care services",
    "Offices of physicians",
    "Outpatient care centers",
    "Home health care services",
    "Hospitals",
    "Nursing and residential care facilities",
    "Nursing care facilities",
    "Social assistance",
    "Child day care services",
    "Leisure and hospitality",
    "Arts, entertainment, and recreation",
    "Performing arts and spectator sports",
    "Museums, historical sites, and similar institutions",
    "Amusements, gambling, and recreation",
    "Accommodation and food services",
    "Accommodation",
    "Food services and drinking places",
    "Other services",
    "Repair and maintenance",
    "Personal and laundry services",
    "Membership associations and organizations",
    "Government",
    "Federal",
    "Federal, except U.S. Postal Service",
    "U.S. Postal Service",
    "State government",
    "State government education",
    "State government, excluding education",
    "Local government",
    "Local government education",
    "Local government, excluding education",
]


class FredNonFarmPayrollsQueryParams(NonFarmPayrollsQueryParams):
    """FRED NonFarm Payrolls Query."""

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}

    category: Literal[
        "employees_nsa",
        "employees_sa",
        "employees_production_and_nonsupervisory",
        "employees_women",
        "employees_women_percent",
        "avg_hours",
        "avg_hours_production_and_nonsupervisory",
        "avg_hours_overtime",
        "avg_hours_overtime_production_and_nonsupervisory",
        "avg_earnings_hourly",
        "avg_earnings_hourly_production_and_nonsupervisory",
        "avg_earnings_weekly",
        "avg_earnings_weekly_production_and_nonsupervisory",
        "index_weekly_hours",
        "index_weekly_hours_production_and_nonsupervisory",
        "index_weekly_payrolls",
        "index_weekly_payrolls_production_and_nonsupervisory",
    ] = Field(
        default="employees_nsa",
        description="The category to query.",
        json_schema_extra={"choices": list(EstablishmentData)},
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Validate the dates entered."""
        if v is None:
            return None
        if isinstance(v, (list, dateType)):
            return v
        new_dates: List = []
        date_param = v
        if isinstance(date_param, str):
            new_dates = date_param.split(",")
        elif isinstance(date_param, dateType):
            new_dates.append(date_param.strftime("%Y-%m-%d"))
        elif isinstance(date_param, list) and isinstance(date_param[0], dateType):
            new_dates = [d.strftime("%Y-%m-%d") for d in new_dates]
        else:
            new_dates = date_param
        return ",".join(new_dates) if len(new_dates) > 1 else new_dates[0]


class FredNonFarmPayrollsData(NonFarmPayrollsData):
    """FRED NonFarm Payrolls Data."""

    __alias_dict__ = {
        "date": "observation_date",
        "value": "observation_value",
        "symbol": "series_id",
    }

    name: str = Field(
        description="The name of the series.",
    )
    element_id: str = Field(
        description="The element id in the parent/child relationship.",
    )
    parent_id: str = Field(
        description="The parent id in the parent/child relationship.",
    )
    children: Optional[str] = Field(
        default=None,
        description="The element_id of each child, as a comma-separated string.",
    )
    level: int = Field(
        description="The indentation level of the element.",
    )


class FredNonFarmPayrollsFetcher(
    Fetcher[FredNonFarmPayrollsQueryParams, List[FredNonFarmPayrollsData]]
):
    """FRED NonFarm Payrolls Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredNonFarmPayrollsQueryParams:
        """Transform query."""
        return FredNonFarmPayrollsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredNonFarmPayrollsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import amake_request
        from numpy import nan
        from pandas import DataFrame, to_datetime

        api_key = credentials.get("fred_api_key") if credentials else ""
        element_id = EstablishmentData[query.category]
        dates: List = [""]

        if query.date:
            if query.date and isinstance(query.date, dateType):
                query.date = query.date.strftime("%Y-%m-%d")
            dates = query.date.split(",")  # type: ignore
            dates = [d.replace(d[-2:], "01") if len(d) == 10 else d for d in dates]
            dates = list(set(dates))
            dates = (
                [f"&observation_date={date}" for date in dates if date] if dates else ""  # type: ignore
            )

        URLS = [
            f"https://api.stlouisfed.org/fred/release/tables?release_id=50&element_id={element_id}"
            + f"{date}&include_observation_values=true&api_key={api_key}"
            + "&file_type=json"
            for date in dates
        ]
        results: List = []

        async def get_one(URL):
            """Get the observations for a single date."""
            response = await amake_request(URL)
            data = [
                v
                for v in response.get("elements", {}).values()  # type: ignore
                if v.get("observation_value") != "."
            ]
            if data:
                df = (
                    DataFrame(data)
                    .set_index(["element_id", "parent_id"])
                    .sort_index()[
                        [
                            "level",
                            "series_id",
                            "name",
                            "observation_date",
                            "observation_value",
                        ]
                    ]
                    .reset_index()
                )
                df["parent_id"] = df.parent_id.astype(str)
                df["element_id"] = df.element_id.astype(str)
                df["observation_value"] = df.observation_value.str.replace(
                    ",", ""
                ).astype(float)
                if query.category.startswith(
                    "employees"
                ) and not query.category.endswith("percent"):
                    df["observation_value"] = df.observation_value * 1000
                elif query.category.endswith("percent"):
                    df["observation_value"] = df.observation_value / 100

                df["observation_date"] = to_datetime(
                    df["observation_date"], format="%b %Y"
                ).dt.date
                children = (
                    df.groupby("parent_id")["element_id"]
                    .apply(lambda x: x.sort_values().unique().tolist())
                    .to_dict()
                )
                children = {k: ",".join(v) for k, v in children.items()}
                df["children"] = df.element_id.map(children)
                df = (
                    df.set_index(["element_id", "children", "parent_id", "level"])
                    .sort_index()
                    .reset_index()
                    .replace({nan: None})
                )
                results.extend(df.to_dict("records"))

        await asyncio.gather(*[get_one(URL) for URL in URLS])

        return results

    @staticmethod
    def transform_data(
        query: FredNonFarmPayrollsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FredNonFarmPayrollsData]:
        """Transform data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        unique_order_index = {
            name: index for index, name in enumerate(NFP_SECTOR_ORDER)
        }

        return [
            FredNonFarmPayrollsData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: (
                    x["observation_date"],
                    unique_order_index.get(x["name"], len(NFP_SECTOR_ORDER)),
                ),
            )
        ]
