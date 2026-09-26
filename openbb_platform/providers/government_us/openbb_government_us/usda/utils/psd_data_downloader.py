"""PSD Data Downloader Utils"""

from typing import Literal

from openbb_government_us.usda.utils.psd_codes import (
    ATTRIBUTES,
    COMMODITIES,
    COUNTRIES,
    COUNTRY_TO_REGION,
    PSD_REPORTS_METADATA,
    REGION_DISPLAY,
    REGIONS,
)

REPORT_HANDLER_URL = "https://apps.fas.usda.gov/psdonline/reportHandler.ashx"


def get_report_url(
    report_id: int,
    file_format: Literal["csv", "html"] = "csv",
) -> str:
    """Get the download URL for a PSD report.

    Parameters
    ----------
    report_id : int
        The report ID from list_reports()
    file_format : str
        Output format: 'csv' or 'html' (default: 'csv')

    Returns
    -------
    str
        Direct download URL for the report

    Examples
    --------
    >>> url = get_report_url(2109)
    >>> print(url)
    'https://apps.fas.usda.gov/psdonline/reportHandler.ashx?reportId=2109&templateId=8&format=csv&fileName=Coffee_Summary'
    """
    for group_data in PSD_REPORTS_METADATA.values():
        if report_id in group_data["reports"]:
            report = group_data["reports"][report_id]
            title = report["title"]
            template_id = report["templateId"]

            filename = (
                title.replace(" ", "_")
                .replace(":", "")
                .replace(",", "")
                .replace("/", "_")
            )

            return (
                f"{REPORT_HANDLER_URL}?"
                f"reportId={report_id}&"
                f"templateId={template_id}&"
                f"format={file_format}&"
                f"fileName={filename}"
            )

    raise ValueError(
        f"Report ID {report_id} not found. Use list_reports() to see available reports."
    )


async def get_psd_report_data(report_id: int) -> dict:
    """Download and parse a PSD report into structured data ready for pandas DataFrame.

    Parameters
    ----------
    report_id : int
        The report ID from list_reports()

    Returns
    -------
    dict
        Parsed report with flat structure for DataFrame compatibility, with keys:
        'report' (str) report title, 'template' (int) template ID used for parsing,
        'template_description' (str) human-readable template description,
        'units' (dict) column name -> unit mapping, 'columns' (list[str]) all
        column names in order, 'row_count' (int) number of data rows, and
        'data' (list[dict]) flat row data ready for DataFrame().

    Examples
    --------
    >>> import pandas as pd
    >>> result = await get_psd_report_data(2109)
    >>> df = DataFrame(result['data'])
    >>> df.attrs['units'] = result['units']
    >>> print(df.head())

    >>> result = await get_psd_report_data(884)
    >>> df = DataFrame(result['data'])
    >>> print(df.dtypes)
    """
    from aiohttp import ClientError  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import get_async_requests_session
    from openbb_government_us.usda.utils.psd_template_parser import parse_report

    template_id = None
    for group_data in PSD_REPORTS_METADATA.values():
        if report_id in group_data["reports"]:
            template_id = group_data["reports"][report_id]["templateId"]
            break

    if template_id is None:
        raise OpenBBError(f"Invalid report ID -> {report_id} was not found.")

    html_url = get_report_url(report_id, "html")
    csv_url = get_report_url(report_id, "csv")
    session = await get_async_requests_session()

    try:
        html_resp = await session.get(html_url)
        html = await html_resp.text()
        csv_resp = await session.get(csv_url)
        csv_text = await csv_resp.text()
    except ClientError as e:
        raise OpenBBError(f"Error fetching report {report_id} -> {e}") from e
    finally:
        await session.close()

    if "error" in csv_text.lower():
        raise OpenBBError(f"Server error fetching report {report_id} -> {csv_text}")

    lines = csv_text.replace("\r", "").strip().split("\n")

    return parse_report(template_id, lines, html)


def _get_commodity_attributes(commodity_code: str) -> list[str]:
    """Fetch valid attribute names for a commodity using the metadata API."""
    from openbb_core.provider.utils.helpers import make_request

    try:
        resp = make_request(
            f"https://apps.fas.usda.gov/PSDOnlineApi/api/query/GetMultiCommodityAttributes?commodityCodes={commodity_code},"
        )
        if resp.status_code == 200:
            data = resp.json()
            id_to_key = {v: k for k, v in ATTRIBUTES.items()}
            valid_keys = set()

            for item in data:
                attr_id = item.get("attributeId")
                if attr_id and attr_id in id_to_key:
                    valid_keys.add(id_to_key[attr_id])
            if valid_keys:
                return sorted(list(valid_keys))
    except Exception:  # noqa
        pass
    return list(ATTRIBUTES.keys())


def _get_commodity_countries(commodity_code: str) -> dict[str, str]:
    """Fetch valid country names for a commodity using the metadata API.

    Parameters
    ----------
    commodity_code : str
        Commodity code (e.g., '0440000' for corn)

    Returns
    -------
    dict[str, str]
        Mapping of country name -> country code
    """
    from openbb_core.provider.utils.helpers import make_request

    base_url = "https://apps.fas.usda.gov/PSDOnlineApi/api/CompositeVisualization/GetCountries?regionCode=R00&commodityCode="

    try:
        resp = make_request(
            f"{base_url}{commodity_code}",
        )
        if resp.status_code == 200:
            data = resp.json()
            name_to_code = {}
            for item in data:
                code = item.get("value")
                name = item.get("text", "").strip()
                if code and name and code != "00":
                    name_to_code[name] = code
            if name_to_code:
                return name_to_code
    except Exception:  # noqa
        pass
    return {}


def _year_columns(columns) -> list[str]:
    """Return the year-value columns of a query result.

    Parameters
    ----------
    columns : iterable of str
        The result frame's column names.

    Returns
    -------
    list[str]
        Columns whose first four characters are digits, covering both the
        marketing-year headers such as '2023/2024' and the calendar-year
        headers such as '2023' that livestock and meat commodities publish.
    """
    return [c for c in columns if c[0:4].isdigit()]


def get_timeseries(  # noqa: PLR0912
    commodity: str,
    attribute: str | list[str] | None = None,
    country: str | list[str] | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    aggregate_region: bool = False,
) -> list:
    """Get time series for a commodity/attribute using ASYNC parallel requests.

    Parameters
    ----------
    commodity : str
        Commodity name (e.g., 'cotton', 'wheat', 'corn', 'cattle')
    attribute : str | list[str] | None
        Attribute name(s). Can be:
        - Single string: 'production', 'exports'
        - Comma-separated: 'production, exports, ending_stocks'
        - List: ['production', 'exports', 'ending_stocks']
        If None, returns ALL attributes for this commodity.
    country : str | list[str] | None
        Country/region name(s). Can be:
        - Single string: 'United States', 'Brazil', 'EU', 'world'
        - Comma-separated: 'US, China, Brazil'
        - List: ['US', 'China', 'Brazil']
        If None, returns ALL countries.
    start_year : int | None
        First marketing year to include.
    end_year : int | None
        Last marketing year to include.
    aggregate_region : bool, optional
        If True, also include World + regional aggregates.
        Default False.

    Returns
    -------
    DataFrame
        Columns: region, country, commodity, attribute, marketing_year, value, unit
        Sorted by marketing_year, then value descending.

    Examples
    --------
    >>> get_timeseries('wheat', 'production')
    >>> get_timeseries('corn', 'exports', start_year=2020, end_year=2025)
    >>> get_timeseries('wheat', 'production', country='United States')
    >>> get_timeseries('wheat', 'production', country=['US', 'China', 'Brazil'])
    >>> get_timeseries('wheat', 'production', country='US, China, Brazil')
    >>> get_timeseries('wheat', 'production, exports, ending_stocks')
    >>> get_timeseries('wheat', ['production', 'exports'])
    >>> get_timeseries('wheat', 'production', aggregate_region=True)
    >>> get_timeseries('wheat')
    """
    import asyncio  # noqa
    from datetime import datetime
    from aiohttp import ClientError, ClientSession
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import get_async_requests_session, run_async
    from pandas import DataFrame, notna

    QUERY_URL = "https://apps.fas.usda.gov/PSDOnlineApi/api/query/RunQuery"
    key = commodity.lower().replace(" ", "_").replace("-", "_")

    if key not in COMMODITIES:
        raise ValueError(
            f"Unknown commodity: {commodity} -> Valid choices: {list(COMMODITIES.keys())}"
        )

    commodity_code = COMMODITIES[key]
    valid_attrs = _get_commodity_attributes(commodity_code)
    if attribute is None:
        attr_ids = [ATTRIBUTES[a] for a in valid_attrs]
    else:
        if isinstance(attribute, str):
            attr_list = [a.strip() for a in attribute.split(",") if a.strip()]
        else:
            attr_list = list(attribute)

        attr_ids = []
        for attr in attr_list:
            attr_key = attr.lower().replace(" ", "_").replace("-", "_")
            if attr_key not in ATTRIBUTES:
                raise ValueError(
                    f"Unknown attribute: '{attr}' for {commodity}. Valid attributes: {valid_attrs}"
                )
            if attr_key not in valid_attrs:
                raise ValueError(
                    f"Attribute '{attr}' is not available for {commodity}. Valid attributes: {valid_attrs}"
                )
            attr_ids.append(ATTRIBUTES[attr_key])

    selected_region_codes: list[str] = []
    selected_country_codes: list[str] = []
    valid_countries_map = _get_commodity_countries(commodity_code)
    valid_country_codes = set(valid_countries_map.values())
    code_to_key = {}

    for key, code in COUNTRIES.items():
        if code not in code_to_key:
            code_to_key[code] = key

    def get_valid_country_keys() -> list[str]:
        """Get sorted list of valid country keys from our COUNTRIES dict."""
        return sorted(
            [code_to_key.get(c, c) for c in valid_country_codes if c in code_to_key]
        )

    if country is None:
        country_codes = list(valid_country_codes) if valid_country_codes else ["ALL"]
    else:
        country_list = (
            [c.strip() for c in country.split(",") if c.strip()]
            if isinstance(country, str)
            else [
                c.strip()
                for c in country[0].split(",")
                if isinstance(country, list)
                and len(country) == 1
                and isinstance(c, str)
                and c.strip()
            ]
        )
        country_codes = []

        for c in country_list:
            country_key = c.lower().replace(" ", "_").replace("-", "_")
            if c.upper() in REGION_DISPLAY:
                selected_region_codes.append(c.upper())
                country_codes.append(c.upper())
            elif country_key in REGIONS:
                region_code = REGIONS[country_key]
                selected_region_codes.append(region_code)
                country_codes.append(region_code)
            elif country_key == "eu":
                selected_region_codes.append("R05")
                country_codes.append("R05")
            elif c.upper() in COUNTRY_TO_REGION:
                code = c.upper()
                if valid_country_codes and code not in valid_country_codes:
                    valid_keys = get_valid_country_keys()
                    raise ValueError(
                        f"Country '{c}' is not available for {commodity}. Valid countries: {valid_keys}"
                    )
                selected_country_codes.append(code)
                country_codes.append(code)
            elif country_key in COUNTRIES:
                code = COUNTRIES[country_key]
                if valid_country_codes and code not in valid_country_codes:
                    valid_keys = get_valid_country_keys()
                    raise ValueError(
                        f"Country '{c}' is not available for {commodity}. Valid countries: {valid_keys}"
                    )
                selected_country_codes.append(code)
                country_codes.append(code)
            else:
                valid_keys = sorted(
                    [k.lower().replace(" ", "_") for k in valid_countries_map]
                )
                valid_regions = list(REGIONS.keys())
                raise ValueError(
                    f"Unknown country/region: '{c}' for {commodity}. "
                    + f"Valid countries: {valid_keys}. Valid regions: {valid_regions}"
                )

    if aggregate_region:
        if "R00" in selected_region_codes:
            country_codes = list(REGIONS.values()) + selected_country_codes
            country_codes = list(set(country_codes))
        elif selected_region_codes:
            country_codes = ["R00"] + selected_region_codes + selected_country_codes
            country_codes = list(set(country_codes))
        elif selected_country_codes:
            regions_for_countries = set()
            for cc in selected_country_codes:
                if cc in COUNTRY_TO_REGION:
                    regions_for_countries.add(COUNTRY_TO_REGION[cc])
            country_codes = (
                ["R00"] + list(regions_for_countries) + selected_country_codes
            )
            country_codes = list(set(country_codes))
        elif country is None:
            region_codes = set(REGIONS.values())
            country_only_codes = [
                c for c in valid_country_codes if c not in region_codes and c != "E4"
            ]
            country_codes = list(REGIONS.values()) + country_only_codes
            country_codes = list(set(country_codes))

    current_year = datetime.now().year
    years = list(range(start_year or 1960, (end_year or current_year + 1) + 1))

    BATCH_SIZE = 20
    attr_batches = [
        attr_ids[i : i + BATCH_SIZE] for i in range(0, len(attr_ids), BATCH_SIZE)
    ]

    async def fetch_batch(session: ClientSession, batch_attrs: list) -> list:
        """Fetch one batch of attributes."""
        payload = {
            "queryId": 0,
            "commodityGroupCode": None,
            "commodities": [commodity_code],
            "attributes": batch_attrs,
            "countries": country_codes,
            "marketYears": years,
            "chkCommoditySummary": False,
            "chkAttribSummary": False,
            "chkCountrySummary": False,
            "commoditySummaryText": "",
            "attribSummaryText": "",
            "countrySummaryText": "",
            "optionColumn": "year",
            "chkTopCountry": False,
            "topCountryCount": "",
            "chkfileFormat": False,
            "chkPrevMonth": False,
            "chkMonthChange": False,
            "chkCodes": False,
            "chkYearChange": False,
            "queryName": "",
            "sortOrder": "Commodity/Attribute/Country",
            "topCountryState": False,
        }
        try:
            async with await session.post(QUERY_URL, json=payload) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                return data.get("queryResult", [])
        except ClientError as e:
            raise OpenBBError(e) from e
        except Exception:
            return []

    async def fetch_all_batches():
        """Fetch all batches concurrently."""
        async with await get_async_requests_session() as session:
            tasks = [fetch_batch(session, batch) for batch in attr_batches]
            results = await asyncio.gather(*tasks)
            all_results = []
            for r in results:
                all_results.extend(r)
            return all_results

    result = run_async(fetch_all_batches)

    if not result:
        raise OpenBBError(
            "No data available for the given parameters. -> "
            + f"{commodity} | {attribute} | {country} | {start_year}-{end_year}"
        )

    df = DataFrame(result)

    df["commodity"] = df["commodity"].ffill()
    df["attribute"] = df["attribute"].ffill()

    year_cols = _year_columns(df.columns)
    name_to_code = {name.strip(): code for name, code in valid_countries_map.items()}
    for region_code, region_name in REGION_DISPLAY.items():
        name_to_code[region_name] = region_code

    region_names = {v: k for k, v in REGION_DISPLAY.items()}

    def get_region(country_name: str) -> str:
        """Resolve the region a country belongs to."""
        if country_name == "European Union":
            return "European Union"
        code = name_to_code.get(country_name)
        if code and code in COUNTRY_TO_REGION:
            return REGION_DISPLAY.get(COUNTRY_TO_REGION[code], "Other")
        return "Other"

    def is_region(country_name: str) -> bool:
        """Check if the country name is actually a region aggregate."""
        if aggregate_region and country_name == "European Union":
            return True
        if country_name == "European Union":
            return False
        if country_name == "Other":
            return True
        return country_name in region_names

    rows = []
    for _, row in df.iterrows():
        country_name = row["country"]
        if not notna(country_name) or not country_name:
            continue
        commodity_display = row["commodity"] if row["commodity"] else commodity.title()
        attr_display = row["attribute"] if row["attribute"] else ""
        unit = row.get("unit Description", "") or ""
        for yr_col in year_cols:
            val = row[yr_col]
            if notna(val):
                if is_region(country_name):
                    region_val = country_name
                    country_val = "--"
                else:
                    region_val = get_region(country_name)
                    country_val = country_name
                rows.append(
                    {
                        "region": region_val,
                        "country": country_val,
                        "commodity": commodity_display,
                        "attribute": attr_display,
                        "marketing_year": yr_col,
                        "value": val,
                        "unit": unit.strip().strip("()"),
                    }
                )

    df_long = DataFrame(rows)

    if df_long.empty:
        raise OpenBBError(
            "No data available for the given parameters. -> "
            + f"{commodity} | {attribute} | {country} | {start_year}-{end_year}"
        )

    if start_year is not None or end_year is not None:
        df_long["_year"] = df_long["marketing_year"].str.split("/").str[0].astype(int)

        if start_year is not None:
            df_long = df_long[df_long["_year"] >= start_year]
        if end_year is not None:
            df_long = df_long[df_long["_year"] <= end_year]

        df_long = df_long.drop(columns=["_year"])

    df_long = df_long[
        [
            "region",
            "country",
            "commodity",
            "attribute",
            "marketing_year",
            "value",
            "unit",
        ]
    ]

    if not df_long[df_long["country"] == "--"].empty:
        region_totals = (
            df_long[df_long["country"] == "--"]
            .groupby(["region", "attribute", "marketing_year"])["value"]
            .first()
            .reset_index()
        )
        region_totals = region_totals.rename(columns={"value": "_region_value"})
        df_long = df_long.merge(
            region_totals, on=["region", "attribute", "marketing_year"], how="left"
        )
        df_long.loc[df_long["region"] == "World", "_region_value"] = float("inf")

        df_long["_is_aggregate"] = (df_long["country"] == "--").astype(int)
        df_long = (
            df_long.sort_values(
                by=[
                    "commodity",
                    "attribute",
                    "marketing_year",
                    "_region_value",
                    "_is_aggregate",
                    "value",
                ],
                ascending=[True, True, True, False, False, False],
            )
            .drop(columns=["_region_value", "_is_aggregate"])
            .reset_index(drop=True)
        )
    else:
        df_long = df_long.sort_values(
            by=["commodity", "attribute", "marketing_year", "value"],
            ascending=[True, True, True, False],
        ).reset_index(drop=True)

    return df_long.to_dict(orient="records")
