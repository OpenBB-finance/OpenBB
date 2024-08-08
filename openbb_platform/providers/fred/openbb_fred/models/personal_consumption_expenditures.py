"""FRED Personal Consumption Expenditures Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.personal_consumption_expenditures import (
    PersonalConsumptionExpendituresData,
    PersonalConsumptionExpendituresQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

PCE_CATEGORY_TO_EID = {
    "personal_income": "155443",
    "wages_by_industry": "3151",
    "real_pce_percent_change": "3160",
    "real_pce_quantity_index": "3196",
    "pce_price_index": "3208",
    "pce_dollars": "3220",
    "real_pce_chained_dollars": "3232",
    "pce_price_percent_change": "3172",
}


class FredPersonalConsumptionExpendituresQueryParams(
    PersonalConsumptionExpendituresQueryParams
):
    """FRED Personal Consumption Expenditures Query."""

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}

    category: Literal[
        "personal_income",
        "wages_by_industry",
        "real_pce_percent_change",
        "real_pce_quantity_index",
        "pce_price_index",
        "pce_dollars",
        "real_pce_chained_dollars",
        "pce_price_percent_change",
    ] = Field(
        default="personal_income",
        description="The category to query.",
        json_schema_extra={"choices": list(PCE_CATEGORY_TO_EID)},
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


class FredPersonalConsumptionExpendituresData(PersonalConsumptionExpendituresData):
    """FRED Personal Consumption Expenditures Data."""

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
    line: int = Field(
        description="The line number of the series in the table.",
    )


class FredPersonalConsumptionExpendituresFetcher(
    Fetcher[
        FredPersonalConsumptionExpendituresQueryParams,
        List[FredPersonalConsumptionExpendituresData],
    ]
):
    """FRED Personal Consumption Expenditures Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FredPersonalConsumptionExpendituresQueryParams:
        """Transform query."""
        return FredPersonalConsumptionExpendituresQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredPersonalConsumptionExpendituresQueryParams,
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
        element_id = PCE_CATEGORY_TO_EID[query.category]
        dates: List = [""]

        if query.date:
            if isinstance(query.date, dateType):
                query.date = query.date.strftime("%Y-%m-%d")
            dates = query.date.split(",")  # type: ignore
            dates = [d.replace(d[-2:], "01") if len(d) == 10 else d for d in dates]
            dates = list(set(dates))
            dates = (
                [f"&observation_date={date}" for date in dates if date] if dates else ""  # type: ignore
            )

        URLS = [
            f"https://api.stlouisfed.org/fred/release/tables?release_id=54&element_id={element_id}"
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
                if v.get("observation_value") != "." and v.get("type") != "header"
            ]
            if data:
                df = (
                    DataFrame(data)
                    .set_index(["line", "element_id", "parent_id"])
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
                df["line"] = df.line.astype(int)
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
                    df.set_index(
                        ["line", "element_id", "children", "parent_id", "level"]
                    )
                    .sort_index()
                    .reset_index()
                    .replace({nan: None})
                )
                if query.category == "personal_income":
                    df = df.set_index("line").sort_index()
                    df["units"] = "Bil. of $"
                    df.loc[35, "units"] = "%"
                    df.loc[36:37, "units"] = "Bil. of Chn. 2017 $"
                    df.loc[38, "units"] = "$"
                    df.loc[39, "units"] = "Chn. 2017"
                    df.loc[40, "units"] = "Thous."
                    df = df.reset_index()
                elif query.category in ["wages_by_industry", "pce_dollars"]:
                    df["units"] = "Bil. of $"
                elif query.category in [
                    "real_pce_percent_change",
                    "pce_price_percent_change",
                ]:
                    df["units"] = "%"
                elif query.category in ["real_pce_quantity_index", "pce_price_index"]:
                    df["units"] = "Index 2017=100"
                elif query.category == "real_pce_chained_dollars":
                    df["units"] = "Bil. of Chn. 2017 $"
                else:
                    pass

                results.extend(df.to_dict("records"))

        await asyncio.gather(*[get_one(URL) for URL in URLS])

        return results

    @staticmethod
    def transform_data(
        query: FredPersonalConsumptionExpendituresQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FredPersonalConsumptionExpendituresData]:
        """Transform data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")

        return [
            FredPersonalConsumptionExpendituresData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: (
                    x["observation_date"],
                    x["line"],
                ),
            )
        ]
