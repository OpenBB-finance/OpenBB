"""FRED Release Table Table Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fred_release_table import (
    ReleaseTableData,
    ReleaseTableQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_fred.utils.query import UseCacheQueryParams
from openbb_fred.utils.release_tables import get_units, shown, tree


def _quarter_start(value: str) -> str:
    """Return the first day of the quarter one date falls in.

    Parameters
    ----------
    value : str
        A date, as ``YYYY-MM-DD``.

    Returns
    -------
    str
        The quarter's first day, as ``YYYY-MM-DD``.
    """
    read = datetime.strptime(value, "%Y-%m-%d")

    return read.replace(month=(read.month - 1) // 3 * 3 + 1, day=1).strftime("%Y-%m-%d")


class FredReleaseTableQueryParams(UseCacheQueryParams, ReleaseTableQueryParams):
    """FRED Release Table Query Params."""

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}


class FredReleaseTableData(ReleaseTableData):
    """FRED Release Table Data."""

    __alias_dict__ = {
        "date": "observation_date",
        "value": "observation_value",
        "symbol": "series_id",
        "element_type": "type",
    }

    date: dateType | None = Field(
        default=None,
        description="The date of the observation.",
        json_schema_extra=shown("date"),
    )
    symbol: str | None = Field(
        default=None,
        description="The series id of the observation.",
        json_schema_extra=shown("symbol"),
    )
    name: str | None = Field(
        default=None,
        description="The name of the series.",
        json_schema_extra=shown("name"),
    )
    units: str | None = Field(
        default=None,
        description="The unit of measure the series is published in.",
        json_schema_extra=shown("units"),
    )
    value: float | None = Field(
        default=None,
        description="The observed value.",
        json_schema_extra=shown("value"),
    )
    element_type: str | None = Field(
        default=None,
        description="The type of the element.",
        json_schema_extra=tree(),
    )
    element_id: str | None = Field(
        default=None,
        description="The element id in the parent/child relationship.",
        json_schema_extra=tree(),
    )
    parent_id: str | None = Field(
        default=None,
        description="The parent id in the parent/child relationship.",
        json_schema_extra=tree(),
    )
    children: str | None = Field(
        default=None,
        description="The element_id of each child, as a comma-separated string.",
        json_schema_extra=tree(),
    )
    level: int | None = Field(
        default=None,
        description="The indentation level of the element.",
        json_schema_extra=tree(),
    )
    line: int | None = Field(
        default=None,
        description="The line number of the series in the table.",
        json_schema_extra=tree(),
    )


class FredReleaseTableFetcher(
    Fetcher[
        FredReleaseTableQueryParams,
        list[FredReleaseTableData],
    ]
):
    """FRED Release Table Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FredReleaseTableQueryParams:
        """Transform query."""
        return FredReleaseTableQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredReleaseTableQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract data."""
        import asyncio  # noqa
        from openbb_fred.utils.api import release_tables_url
        from openbb_fred.utils.query import join_dates
        from openbb_fred.utils.rate_limiter import fred_get
        from openbb_fred.models.search import FredSearchFetcher
        from numpy import nan
        from pandas import DataFrame, to_datetime, to_numeric
        from pandas.api.types import is_numeric_dtype

        api_key = credentials.get("fred_api_key") if credentials else ""

        release_info = await FredSearchFetcher.fetch_data(
            {"release_id": query.release_id, "use_cache": query.use_cache}, credentials
        )

        if not release_info:
            raise OpenBBError(f"No release information found for, {query.release_id}.")

        release_freq = next(
            iter({getattr(d, "frequency_short", None) for d in release_info})
        )
        joined = join_dates(query.date)
        dates: list = [None]

        if joined:
            requested = joined.split(",")

            if release_freq == "M":
                requested = [f"{d[:-2]}01" for d in requested]
            elif release_freq == "Q":
                requested = [_quarter_start(d) for d in requested]

            dates = sorted(set(requested))

        URLS = [
            release_tables_url(query.release_id, query.element_id, api_key, date)
            for date in dates
        ]
        results: list = []

        async def get_one(URL):
            """Get the observations for a single date."""
            response = await fred_get(URL, use_cache=query.use_cache)

            if "elements" not in response:
                return

            res: list = []
            data: list = []
            for v in response.get("elements", {}).values():
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
            if data:
                index_cols = ["line", "element_id", "parent_id"]
                df = DataFrame(data).dropna(how="all", axis=1)
                for index_col in index_cols.copy():
                    if index_col not in df.columns:
                        index_cols.remove(index_col)
                df = df[
                    index_cols
                    + [
                        "level",
                        "series_id",
                        "name",
                        "observation_date",
                        "observation_value",
                    ]
                ]
                df["parent_id"] = df.parent_id.astype(str)
                df["element_id"] = df.element_id.astype(str)
                df["observation_value"] = df.observation_value.str.replace(
                    ",", ""
                ).astype(float)

                if "line" in df.columns:
                    df["line"] = to_numeric(df.line, errors="coerce").astype("Int64")

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
                order = [c for c in new_index_cols if c in df.columns]
                keys = [f"_sort_{c}" for c in order]

                for column, key in zip(order, keys):
                    df[key] = df[column].fillna(
                        -1 if is_numeric_dtype(df[column]) else ""
                    )

                df = (
                    df.sort_values(by=keys)
                    .drop(columns=keys)
                    .reset_index(drop=True)
                    .replace({nan: None})
                )
                results.extend(df.to_dict("records"))
            elif res:
                for item in res:
                    if not any(r["element_id"] == item["element_id"] for r in results):
                        results.append(item)

        await asyncio.gather(*[get_one(URL) for URL in URLS])

        units = await get_units(query.release_id, credentials)

        for row in results:
            row["units"] = units.get(row.get("series_id"))

        return results

    @staticmethod
    def transform_data(
        query: FredReleaseTableQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FredReleaseTableData]:
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
                    str(x.get("observation_date") or ""),
                    x.get("line") if x.get("line") is not None else float("inf"),
                ),
            )
        ]
