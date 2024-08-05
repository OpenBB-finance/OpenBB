"""FRED Release Table Table Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fred_release_table import (
    ReleaseTableData,
    ReleaseTableQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import field_validator


class FredReleaseTableQueryParams(ReleaseTableQueryParams):
    """FRED Release Table Query Params."""

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}

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


class FredReleaseTableData(ReleaseTableData):
    """FRED Release Table Data."""

    __alias_dict__ = {
        "date": "observation_date",
        "value": "observation_value",
        "symbol": "series_id",
        "element_type": "type",
    }


class FredReleaseTableFetcher(
    Fetcher[
        FredReleaseTableQueryParams,
        List[FredReleaseTableData],
    ]
):
    """FRED Release Table Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredReleaseTableQueryParams:
        """Transform query."""
        return FredReleaseTableQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredReleaseTableQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_fred.models.search import FredSearchFetcher
        from numpy import nan
        from pandas import DataFrame, to_datetime

        api_key = credentials.get("fred_api_key") if credentials else ""
        dates: List = [""]

        # We'll verify that the release_id is valid and check the frequency for monthly/quarterly data.
        release_info = await FredSearchFetcher.fetch_data(
            {"release_id": query.release_id}, credentials
        )

        if not release_info:
            raise OpenBBError(f"No release information found for, {query.release_id}.")

        release_freq = list(set([d.model_dump().get("frequency_short") for d in release_info]))[0]  # type: ignore  # pylint: disable=R1718

        if query.date is not None:
            if isinstance(query.date, dateType):
                query.date = query.date.strftime("%Y-%m-%d")  # type: ignore
            dates = query.date.split(",")  # type: ignore
            # Set the date to the first of the observation frequency for each date.
            # Daily observations should automatically fetch the closest date.
            if release_freq == "M":
                dates = [d.replace(d[-2:], "01") if len(d) == 10 else d for d in dates]
            elif release_freq == "Q":

                def to_quarter_start(d):
                    date_obj = datetime.strptime(d, "%Y-%m-%d")
                    quarter = (date_obj.month - 1) // 3 + 1
                    start_month = (quarter - 1) * 3 + 1
                    return date_obj.replace(month=start_month, day=1).strftime(
                        "%Y-%m-%d"
                    )

                dates = [to_quarter_start(d) for d in dates if len(d) == 10]

            dates = list(set(dates))
            dates = (
                [f"&observation_date={date}" for date in dates if date] if dates else ""  # type: ignore
            )

        element_id = (
            f"&element_id={query.element_id}" if query.element_id is not None else ""
        )

        URLS = [
            f"https://api.stlouisfed.org/fred/release/tables?release_id={query.release_id}"
            + f"{element_id}{date}&include_observation_values=true&api_key={api_key}"
            + "&file_type=json"
            for date in dates
        ]
        results: List = []

        async def get_one(URL):
            """Get the observations for a single date."""
            response = await amake_request(URL)

            # If the response has no elements we return empty and try the next URL.
            # If all URLs return empty, it will raise in `transform_data`.
            if "elements" not in response:
                return

            res: List = []
            data: List = []
            # We use `res` to store the table and section elements
            # and to identify if observation values are returned.
            # We use `data` to store the observation values.
            # Only one scenario should unfold.
            for v in response.get("elements", {}).values():  # type: ignore
                if v and (v.get("type") == "section" or v.get("type") == "table"):
                    v["element_id"] = str(v["element_id"])
                    v["parent_id"] = str(v["parent_id"]) if v.get("parent_id") else None
                    v.pop("children", None)
                    v.pop("release_id", None)
                    res.append(v)
                elif (
                    "observation_value" in v
                    and v.get("observation_value") != "."
                    and v.get("type") != "header"
                ):
                    v["element_id"] = str(v["element_id"])
                    data.append(v)
            # When observation values are returned, we parse and collect the parent elements while flattening the data.
            if data:
                index_cols = ["line", "element_id", "parent_id"]
                df = DataFrame(data).dropna(how="all", axis=1)
                for index_col in index_cols.copy():
                    if index_col not in df.columns:
                        index_cols.remove(index_col)
                df = (
                    df.set_index(index_cols)
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

                if "line" in df.columns:
                    df["line"] = df.line.astype(int)

                # Some dates are in the format 'Jan 2021' and others are '2021-01-01'.
                def apply_date_format(x):
                    """Apply the date format."""
                    x = x.replace(" ", "-")
                    if x.startswith("Q"):
                        new_x = x.split("-")[-1]
                        q_dict = {
                            "Q1": "-03-31",
                            "Q2": "-06-30",
                            "Q3": "-09-30",
                            "Q4": "-12-31",
                        }
                        return new_x + q_dict[x.split("-")[0]]
                    try:
                        return to_datetime(x).date()
                    except ValueError:
                        try:
                            return to_datetime(x, format="%b-%Y").date()
                        except ValueError:
                            return x

                df["observation_date"] = df.observation_date.apply(apply_date_format)
                children = (
                    df.groupby("parent_id")["element_id"]
                    .apply(lambda x: x.sort_values().unique().tolist())
                    .to_dict()
                )
                children = {k: ",".join(v) for k, v in children.items()}
                df["children"] = df.element_id.map(children)
                new_index_cols = [
                    "line",
                    "element_id",
                    "children",
                    "parent_id",
                    "level",
                ]
                for index_col in new_index_cols.copy():
                    if index_col not in df.columns:
                        new_index_cols.remove(index_col)
                df = (
                    df.set_index(new_index_cols)
                    .sort_index()
                    .reset_index()
                    .replace({nan: None})
                )
                results.extend(df.to_dict("records"))
            # If no observation values are returned, we collect the unique element IDs for the user.
            elif res:
                for item in res:
                    if not any(r["element_id"] == item["element_id"] for r in results):
                        results.append(item)

        await asyncio.gather(*[get_one(URL) for URL in URLS])

        return results

    @staticmethod
    def transform_data(
        query: FredReleaseTableQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FredReleaseTableData]:
        """Transform data."""
        if not data:
            raise EmptyDataError(
                f"No tables were found for the release, {query.release_id}."
                + " Use `fred_search()` to list all release IDs."
                + "\n\nReleases without tables will not return data,"
                + " nor will this endpoint return individual line items."
                + "\n\nTry a different 'element_id' and/or 'date'."
                + "\n\nExclude 'date' for the most recent observations."
                + "\n\nExclude 'element_id' to reveal the top-level element IDs."
                + "\n\nUse `fred_series` for single series data."
            )

        return [
            FredReleaseTableData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: (
                    x.get("observation_date", float("inf")),
                    x.get("line", float("inf")),
                ),
            )
        ]
