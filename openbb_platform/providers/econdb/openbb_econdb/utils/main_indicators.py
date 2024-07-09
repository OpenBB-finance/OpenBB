"""Main Indicators."""

from datetime import datetime, timedelta
from typing import Dict, List, Literal, Union

from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from numpy import arange
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.utils import get_user_cache_directory
from openbb_core.provider.utils.helpers import amake_request
from openbb_econdb.utils.helpers import COUNTRY_MAP, THREE_LETTER_ISO_MAP
from pandas import Categorical, DataFrame, Series, concat, to_datetime

trends_transform_labels_dict = {
    1: "Change from previous period.",
    2: "Change from one year ago.",
    3: "Level",
    9: "Level (USD)",
}
trends_freq_dict = {
    "annual": "Y",
    "quarter": "Q",
    "month": "M",
}
trends_transform_dict = {
    "tpop": 1,
    "toya": 2,
    "level": 3,
    "tusd": 9,
    None: 3,
}

main_indicators_order = [
    "RGDP",
    "RPRC",
    "RPUC",
    "RGFCF",
    "REXP",
    "RIMP",
    "GDP",
    "PRC",
    "PUC",
    "GFCF",
    "EXP",
    "IMP",
    "CPI",
    "PPI",
    "CORE",
    "URATE",
    "EMP",
    "ACPOP",
    "RETA",
    "CONF",
    "IP",
    "CP",
    "GBAL",
    "GREV",
    "GSPE",
    "GDEBT",
    "CA",
    "TB",
    "NIIP",
    "IIPA",
    "IIPL",
    "Y10YD",
    "M3YD",
    "HOU",
    "OILPROD",
    "POP",
]


async def fetch_data(url, use_cache: bool = True):
    """Fetch the data with or without the cached session object."""
    response: Union[dict, List[dict]] = {}
    if use_cache is True:
        cache_dir = f"{get_user_cache_directory()}/http/econdb_main_indicators"
        async with CachedSession(
            cache=SQLiteBackend(cache_dir, expire_after=3600 * 24)
        ) as session:
            try:
                response = await amake_request(url, session=session)
            finally:
                await session.close()
    else:
        response = await amake_request(url)

    return response


async def get_main_indicators(  # pylint: disable=R0913,R0914,R0915
    country: str = "US",
    start_date: str = (datetime.now() - timedelta(weeks=52 * 3)).strftime("%Y-%m-%d"),
    end_date: str = datetime.now().strftime("%Y-%m-%d"),
    frequency: Literal["annual", "quarter", "month"] = "quarter",
    transform: Literal["tpop", "toya", "level", "tusd", None] = "toya",
    use_cache: bool = True,
) -> List[Dict]:
    """Get the main indicators for a given country."""
    freq = trends_freq_dict.get(frequency)
    transform = trends_transform_dict.get(transform)  # type: ignore
    if len(country) == 3:
        country = THREE_LETTER_ISO_MAP.get(country.upper())
        if not country:
            raise OpenBBError(f"Error: Invalid country code -> {country}")
    if country in COUNTRY_MAP:
        country = COUNTRY_MAP.get(country)
    if len(country) != 2:
        raise OpenBBError(
            f"Error: Please supply a 2-Letter ISO Country Code -> {country}"
        )
    if country not in COUNTRY_MAP.values():
        raise OpenBBError(f"Error: Invalid country code -> {country}")
    parents_url = (
        "https://www.econdb.com/trends/country_forecast/"
        + f"?country={country}&freq={freq}&transform={transform}"
        + f"&dateStart={start_date}&dateEnd={end_date}"
    )
    r = await fetch_data(parents_url, use_cache)
    row_names = r.get("row_names")
    row_symbols = []
    row_is_parent = []
    row_symbols = [d["code"] for d in row_names]
    row_is_parent = [d["is_parent"] for d in row_names]
    parent_map = {d["code"]: d["is_parent"] for d in row_names}
    units_col = r.get("units_col")
    metadata = r.get("footnote")
    row_names = r.get("row_names")
    row_name_map = {d["code"]: d["verbose"].title() for d in row_names}
    row_units_dict = dict(zip(row_symbols, units_col))
    units_df = concat([Series(units_col), Series(row_is_parent)], axis=1)
    units_df.columns = ["units", "is_parent"]
    df = DataFrame(r["data"]).set_index("indicator")
    df = df.pivot(columns="obs_time", values="obs_value").filter(
        items=row_symbols, axis=0
    )
    df["units"] = df.index.map(row_units_dict.get)
    df["is_parent"] = df.index.map(parent_map.get)
    df = df.set_index("is_parent", append=True)

    async def get_children(  # pylint: disable=R0913
        parent, country, freq, transform, start_date, end_date, use_cache
    ) -> DataFrame:
        """Get the child elements for the main indicator symbols."""
        children_url = (
            "https://www.econdb.com/trends/get_topic_children/"
            + f"?country={country}&agency=3&freq={freq}&transform={transform}"
            + f"&parent_id={parent}&dateStart={start_date}&dateEnd={end_date}"
        )
        child_r = await fetch_data(children_url, use_cache)
        row_names = child_r.get("row_names")
        row_symbols = []
        row_symbols = [d["code"] for d in row_names]
        units_col = child_r.get("units_col")
        metadata.extend(child_r.get("footnote"))
        row_names = child_r.get("row_names")
        row_name_map.update({d["code"]: d["verbose"].title() for d in row_names})
        row_units_dict = dict(zip(row_symbols, units_col))
        child_df = DataFrame(child_r["data"]).set_index("indicator")
        child_df = child_df.pivot(columns="obs_time", values="obs_value").filter(
            items=row_symbols, axis=0
        )
        child_df["units"] = child_df.index.map(row_units_dict.get)
        # Set 'units' to 'Index' when the index is 'CONF'
        if "CONF" in child_df.index and child_df.loc["CONF", "units"] == "..":
            child_df.loc["CONF", "units"] = "Index"
        child_df["is_parent"] = parent
        child_df = child_df.reset_index().rename(columns={"index": "indicator"})
        child_df["name"] = child_df["indicator"].map(row_name_map)
        return child_df

    new_df = df.copy()
    new_df = new_df.reset_index().rename(columns={"level_0": "indicator"})

    has_children = new_df[
        new_df["is_parent"] == True  # noqa pylint: disable=C0121
    ].indicator.tolist()

    async def append_children(  # pylint: disable=R0913
        parent_df, parent, country, freq, transform, start_date, end_date, use_cache
    ):
        """Get the child element and insert it below the parent row."""
        temp = DataFrame()
        try:
            children = await get_children(
                parent, country, freq, transform, start_date, end_date, use_cache
            )
        except Exception as _:  # pylint: disable=W0718
            return parent_df

        idx = parent_df[parent_df["indicator"] == parent].index[0]
        df1 = parent_df[parent_df.index <= idx]
        df2 = parent_df[parent_df.index > idx]
        temp = concat([df1, children, df2])
        return temp

    # Get the child elements for each parent.
    for parent in has_children:
        new_df = await append_children(
            new_df, parent, country, freq, transform, start_date, end_date, use_cache
        )

    # Cast the shape, specify the order and flatten for output.
    new_df["name"] = new_df["indicator"].map(row_name_map)
    new_df.set_index(["indicator", "is_parent", "name", "units"], inplace=True)
    new_df.columns = new_df.columns
    new_df.columns = [to_datetime(d).strftime("%Y-%m-%d") for d in new_df.columns]
    for col in new_df.columns:
        new_df[col] = new_df[col].astype(str).str.replace(" ", "").astype(float)
    new_df = new_df.apply(lambda row: row / 100 if "%" in row.name[3] else row, axis=1)
    new_df = new_df.iloc[:, ::-1]
    new_df = new_df.fillna("N/A").replace("N/A", None)
    output = new_df.copy()
    output.columns.name = "date"
    output = output.reset_index()
    filtered_df = output[output["indicator"].isin(main_indicators_order)].copy()
    filtered_df["indicator"] = Categorical(
        filtered_df["indicator"], categories=main_indicators_order, ordered=True
    )
    filtered_df.sort_values("indicator", inplace=True)
    output = filtered_df
    output.set_index(["indicator", "is_parent", "name", "units"], inplace=True)
    output["index_order"] = arange(len(output))
    output = output.reset_index().melt(
        id_vars=["index_order", "indicator", "is_parent", "name", "units"],
        var_name="date",
        value_name="value",
    )
    output = output.rename(columns={"indicator": "symbol_root"})
    results = {"records": output.to_dict(orient="records"), "metadata": metadata}
    return [results]
