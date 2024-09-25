"""BLS Helpers."""

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from pandas import DataFrame


# We need to wrap this as a helper to accommodate requests for historical data
# greater than 20 years in length, or containing more than 50 symbols.
async def get_bls_timeseries(  # pylint: disable=too-many-branches,too-many-positional-arguments  # noqa: PLR0912
    api_key: str,
    series_ids: Union[str, List[str]],
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    calculations: bool = True,
    catalog: bool = True,
    annual_average: bool = True,
    aspects: bool = False,
) -> Dict:
    """Get BLS timeseries data. Max 50 symbols per request, and a 20 year historical window.

    Parameters
    ----------
    api_key : str
        BLS API key.
    series_ids : List[str]
        List of BLS series IDs. Max 50 symbols per request.
    start_year : Optional[int]
        Start year for the data. Max history per-request may span 20 years.
    end_year : Optional[int]
        End year for the data.  Max history per-request may span 20 years.
    calculations : bool
        Include calculations in the response, if available. Default is True.
    catalog : bool
        Include catalog information in the response. Default is True.
    annual_average : bool
        Include annual averages in the response, if available. Default is True.
    aspects : bool
        Include aspects in the response, if available. Default is False.

    Returns
    -------
    Dict
        Returns a dictionary with the following keys: data, metadata, messages.
    EmptyDataError
        If no data is found, an EmptyDataError is returned and not raised.
    """
    # pylint: disable=import-outside-toplevel
    import json  # noqa
    from warnings import warn
    from openbb_core.provider.utils.errors import EmptyDataError
    from openbb_core.provider.utils.helpers import amake_request

    symbols = series_ids.split(",") if isinstance(series_ids, str) else series_ids
    if len(symbols) > 50:
        warn(
            "Max 50 symbols per request. Truncating to 50 symbols."
            "Break the request into multiple queries to get more data."
        )
        symbols = symbols[:50]

    headers = {"Content-type": "application/json"}
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = json.dumps(
        {
            k: v
            for k, v in {
                "seriesid": symbols,
                "startyear": start_year,
                "endyear": end_year,
                "catalog": catalog,
                "calculations": calculations,
                "annualaverage": annual_average,
                "aspects": aspects,
                "registrationkey": api_key,
            }.items()
            if v
        }
    )
    res = await amake_request(url=url, method="POST", headers=headers, data=payload)
    results = res.get("Results", {}).get("series", [])  # type: ignore
    messages = res.get("message", [])  # type: ignore
    if messages:
        messages = [
            (
                f"The key provided by the User is invalid. {m.split(' provided by the User is invalid.')[1].strip()}"
                if m.startswith("The key:")
                else m
            )
            for m in messages
            if m
        ]

    metadata: Dict = {}
    data: List = []
    for result in results:
        seriesID = result.get("seriesID")
        if not seriesID:
            continue
        catalog = result.get("catalog")
        if catalog:
            metadata.update({seriesID: catalog})
        _data = result.get("data", [])
        for _d in _data:
            new_d: Dict = {}
            year = _d.get("year", "")
            month = _d.get("period", "").replace("M", "")
            if month.startswith("A") or month in ("S01", "Q01"):
                _date = year + "-01-01"
            elif month == "S02":
                _date = year + "-07-01"
            elif month in ("S03", "Q05"):
                _date = year + "-12-31"
                month = "13"
            elif month == "Q02":
                _date = year + "-04-01"
            elif month == "Q03":
                _date = year + "-07-01"
            elif month == "Q04":
                _date = year + "-10-01"
            else:
                _date = year + "-12-31" if month == "13" else year + "-" + month + "-01"
            new_d["symbol"] = seriesID
            title = metadata[seriesID].get("series_title") if catalog else None
            title = (
                title + (" (Annual Average)" if month == "13" else "")
                if title
                else None
            )
            if title:
                new_d["title"] = title
            new_d["date"] = _date
            value = _d.get("value")
            if value and value != "-":
                new_d["value"] = float(value)
            else:
                new_d["value"] = None
            new_d["latest"] = _d.get("latest") == "true"
            footnotes = _d.get("footnotes")
            if footnotes:
                new_d["footnotes"] = "; ".join(
                    [
                        f.get("text") if isinstance(f, dict) else str(f)  # type: ignore
                        for f in footnotes
                        if f
                    ]
                )
                if not new_d.get("footnotes"):
                    new_d.pop("footnotes")

            calcs = _d.get("calculations")
            if calcs:
                changes = calcs.get("net_changes")
                pct_changes = calcs.get("pct_changes")
                if changes:
                    new_d["change_1M"] = (
                        float(changes.get("1")) if changes.get("1") else None
                    )
                    new_d["change_3M"] = (
                        float(changes.get("3")) if changes.get("3") else None
                    )
                    new_d["change_6M"] = (
                        float(changes.get("6")) if changes.get("6") else None
                    )
                    new_d["change_12M"] = (
                        float(changes.get("12")) if changes.get("12") else None
                    )

                if pct_changes:
                    new_d["change_percent_1M"] = (
                        float(pct_changes.get("1")) / 100
                        if pct_changes.get("1")
                        else None
                    )
                    new_d["change_percent_3M"] = (
                        float(pct_changes.get("3")) / 100
                        if pct_changes.get("3")
                        else None
                    )
                    new_d["change_percent_6M"] = (
                        float(pct_changes.get("6")) / 100
                        if pct_changes.get("6")
                        else None
                    )
                    new_d["change_percent_12M"] = (
                        float(pct_changes.get("12")) / 100
                        if pct_changes.get("12")
                        else None
                    )
            if aspects is True:
                # If there are aspects returned, we want to separate them from the main data.
                # We will store the aspects in the metadata dictionary.
                _aspects = _d.get("aspects")
                if _aspects:
                    for aspect in _aspects:
                        aspect.update(
                            {
                                "date": _date,
                                "footnotes": " ".join(
                                    [f.get("text", "") for f in footnotes]  # type: ignore
                                    if footnotes
                                    else None
                                ).strip(),
                            }
                        )
                    new_aspects = [
                        d for d in _aspects if d.get("value") and d.get("value") != "-"
                    ]
                    if new_aspects:
                        metadata[seriesID]["aspects"] = new_aspects
                    else:
                        messages.append(f"No Aspect Available for Series {seriesID}")

            if new_d:
                data.append(new_d)

    if not data:
        # Return EmptyDataError if no data is found instead of raising.
        # If we raise here, the API key can be exposed in the traceback.
        return EmptyDataError(f"No data found -> {messages}")  # type: ignore

    return {"data": data, "metadata": metadata, "messages": messages}


async def get_survey_asset(survey: str, asset: str) -> "DataFrame":
    """Get an asset in the FTP download folder of the two-letter survey code."""
    # pylint: disable=import-outside-toplevel
    from io import StringIO  # noqa
    from openbb_core.provider.utils.helpers import make_request
    from numpy import nan
    from pandas import read_csv, NA

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 4.0.4; en-us; Glass 1 Build/IMM76L; XE16.2) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"  # noqa  # pylint: disable=line-too-long
    }
    url = f"https://download.bls.gov/pub/time.series/{survey.lower()}/{survey.lower()}.{asset.lower()}"
    res = make_request(url=url, method="GET", headers=headers)
    if res.status_code != 200:
        return
    df = read_csv(StringIO(res.text), sep="\t", low_memory=False, dtype="object")
    df.columns = [d.strip() for d in df.columns]
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    return df.replace({"''": None, '""': None, NA: None, "nan": None, nan: None})


async def download_category_series_ids(category) -> Tuple[List, Dict]:
    """Download all series ids for a category of survey, along with the code maps.
    This should only be required for updating static files.
    """
    # pylint: disable=import-outside-toplevel
    from numpy import nan  # noqa
    from openbb_core.provider.utils.errors import EmptyDataError
    from openbb_bls.utils.constants import SURVEY_CATEGORY_MAP, SURVEY_NAMES

    series_ids: List = []
    series_codes: Dict = {}

    if category not in SURVEY_CATEGORY_MAP:
        raise EmptyDataError(
            f"Category {category} is not a supported choice. Choose from {list(SURVEY_CATEGORY_MAP)}"
        )

    async def get_all_series_ids(survey):
        """Get an asset in the FTP download folder of the two-letter survey code."""
        if survey in ["ch", "cs", "fw", "is", "nw", "oe", "yy"]:
            return
        data = await get_survey_asset(survey, "series")
        for col in ["series_title", "survey_name"]:
            if col not in data.columns:
                data.loc[:, col] = None
        codes = [d for d in data.columns if "code" in d and "periodicity" not in d]
        ids = data.get(["series_id", "series_title"] + codes).copy()

        if ids is None or ids.empty:
            return

        ids = ids.rename(columns={"footnote_codes": "footnote_code"})
        ids = ids.astype(str).replace({"nan": None, "''": None, "": None})

        ids.loc[:, "survey_name"] = SURVEY_NAMES.get(survey.upper(), None)
        ids = ids[ids.series_id.astype(str).str.startswith(survey.upper())]

        if ids is None or ids.empty:
            return

        # Get the code maps for the survey and convert the codes in the series table.
        code_map: Dict = {}
        new_codes = [d.split("_")[0] for d in codes]

        for code in new_codes:
            code = "datatype" if code == "data" else code  # noqa
            code_dict: Dict = {}
            code_data = await get_survey_asset(survey, code)
            if code_data is None or code_data.empty:
                continue
            code = (  # noqa
                "data_type" if code == "datatype" and survey == "ce" else code
            )
            code_data = code_data.rename(
                columns={
                    col: f"{code}_name"
                    for col in code_data.columns
                    if col in [f"{code}_text", f"{code}_title"]
                }
            )
            if f"{code}_code" in code_data.columns:
                if (
                    code_data.index.dtype == "object"
                    and code_data.get(f"{code}_name").isnull().all()
                ):
                    code_data.loc[:, f"{code}_name"] = code_data.loc[
                        :, f"{code}_code"
                    ].copy()
                    code_data.loc[:, f"{code}_code"] = code_data.index.copy()
                    code_data = code_data.reset_index(drop=True)
                code_dict = (
                    code_data.set_index(f"{code}_code")[[f"{code}_name"]]
                    .to_dict()
                    .get(f"{code}_name", code_dict)
                )
            else:
                code_dict = code_data.to_dict(orient="series")

            code_map[f"{code}_code"] = code_dict
            ids[f"{code}_code"] = [code_dict.get(d, d) for d in ids[f"{code}_code"]]

        # Footnotes may be comma-separated, so we need to expand them.
        if "footnote_code" in ids.columns:
            expanded_data = []
            for item in ids["footnote_code"]:
                if (
                    item
                    and isinstance(item, str)
                    and "," in item
                    and any(char.isdigit() for char in item)
                ):
                    expanded_data.append(
                        " ".join(
                            [
                                code_map["footnote_code"].get(sub_item, sub_item)
                                for sub_item in item.split(",")
                                if code_map["footnote_code"].get(sub_item) is not None
                            ]
                        )
                    )
                else:
                    expanded_data.append(item)
            ids["footnote_code"] = expanded_data

        ids = ids.replace({nan: None, "nan": None, "''": None}).to_dict(
            orient="records"
        )
        series_ids.extend(ids)
        series_codes.update({survey: code_map})

    # Iterate over the all the surveys in the category and generate the tables and code maps.
    # The FTP doesn't seem to like a flood of requests, so we do this operation in series.
    for survey in SURVEY_CATEGORY_MAP[category]:
        await get_all_series_ids(survey.lower())

    return series_ids, series_codes


def open_asset(asset: str) -> Union["DataFrame", Dict]:
    """Open a static file asset for series IDs or code maps."""
    # pylint: disable=import-outside-toplevel
    import os  # noqa
    import json
    from importlib.resources import files
    from pathlib import Path
    from numpy import nan
    from openbb_core.app.model.abstract.error import OpenBBError
    from pandas import read_csv

    if ".xz" not in asset and "series" in asset:
        asset = asset + ".xz"
    elif ".json" not in asset and "codes" in asset:
        asset = asset + ".json"
    elif ".json" in asset or ".xz" in asset:
        pass
    else:
        raise OpenBBError(f"Asset '{asset}' not supported. Expected .json or .xz file.")

    assets_path = Path(str(files("openbb_bls").joinpath("assets")))

    if not os.path.exists(assets_path.joinpath(asset)):
        raise OpenBBError(f"Asset '{asset}' not found.")

    if asset.endswith(".json"):
        with open(assets_path.joinpath(asset)) as f:
            return json.load(f)
    else:
        with open(assets_path.joinpath(asset), "rb") as f:
            df = read_csv(f, compression="xz", low_memory=False, dtype="str")
        return df.replace({nan: None, "nan": None, "''": None}).dropna(
            how="all", axis=1
        )


async def update_static_asset(category: str) -> None:
    """Update a static file assets with series IDs and code maps for a given category.
    Do not use unless the static files in the assets folder require updating.
    """
    # pylint: disable=import-outside-toplevel
    import json  # noqa
    from importlib.resources import files
    from pathlib import Path
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_bls.utils.constants import SURVEY_CATEGORY_NAMES
    from numpy import nan
    from pandas import DataFrame

    if category not in SURVEY_CATEGORY_NAMES:
        raise OpenBBError(
            f"Category '{category}' not found. Choose from {list(SURVEY_CATEGORY_NAMES)}"
        )

    try:
        ids, codes = await download_category_series_ids(category)
    except Exception as e:  # pylint: disable=broad-except
        raise OpenBBError(f"Failed to download {category} -> {e}") from e

    assets_path = Path(str(files("openbb_bls").joinpath("assets")))

    # Save the code map to a JSON file.
    if codes:
        with open(assets_path.joinpath(f"{category}_codes.json"), "w") as f:
            json.dump(codes, f, indent=4)

    # Save the series IDs to a CSV file.
    if ids:
        df = DataFrame(ids)
        df = df.replace({nan: None, "nan": None, "''": None}).dropna(how="all", axis=1)
        df.to_csv(
            assets_path.joinpath(f"{category}_series.xz"), index=False, compression="xz"
        )
