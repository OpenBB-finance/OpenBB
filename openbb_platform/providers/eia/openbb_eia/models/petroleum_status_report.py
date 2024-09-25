"""EIA Weekly Petroleum Status Report model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.petroleum_status_report import (
    PetroleumStatusReportData,
    PetroleumStatusReportQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_eia.utils.constants import (
    WpsrCategoryChoices,
    WpsrCategoryType,
    WpsrFileMap,
    WpsrTableChoices,
    WpsrTableMap,
    WpsrTableType,
)


class EiaPetroleumStatusReportQueryParams(PetroleumStatusReportQueryParams):
    """EIA Petroleum Status Report Query Parameters.

    Source: https://www.eia.gov/petroleum/supply/weekly/
    """

    __json_schema_extra__ = {
        "category": {
            "multiiple_items_allowed": False,
            "choices": WpsrCategoryChoices,
        },
        "table": {
            "multiple_items_allowed": False,
            "choices": WpsrTableChoices,
        },
    }

    category: WpsrCategoryType = Field(
        default="balance_sheet",
        description="The group of data to be returned. The default is the balance sheet.",
    )
    table: WpsrTableType = Field(
        default="stocks",
        description="The specific table element within the category to be returned, default is 'stocks'."
        + "\n    Note: Choices represent all available tables from the entire collection and are not all"
        + " available for every category. Invalid choices will raise a ValidationError with a message"
        + " indicating the valid choices for the selected category.",
    )
    use_cache: bool = Field(
        default=True,
        description="Subsequent requests for the same source data are cached for the session using ALRU cache.",
    )


class EiaPetroleumStatusReportData(PetroleumStatusReportData):
    """EIA Petroleum Status Report Data Model."""


class EiaPetroleumStatusReportFetcher(
    Fetcher[EiaPetroleumStatusReportQueryParams, list[EiaPetroleumStatusReportData]]
):
    """EIA Petroleum Status Report Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaPetroleumStatusReportQueryParams:
        """Transform the query parameters."""
        category = params.get("category", "balance_sheet")
        tables = WpsrTableMap.get(category, {})
        table = params.get("table")
        if table and table != "all" and table not in tables:
            raise OpenBBError(
                ValueError(
                    f"Invalid table choice: {table}. Valid choices: {list(tables)}"
                )
            )

        return EiaPetroleumStatusReportQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumStatusReportQueryParams,
        credentials: Optional[dict[str, Any]],
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA website."""
        # pylint: disable=import-outside-toplevel
        from openbb_eia.utils.helpers import download_excel_file

        url = WpsrFileMap.get(query.category, "balance_sheet")

        try:
            results = await download_excel_file(url, query.use_cache)
        except OpenBBError as e:
            raise OpenBBError(f"Error extracting data -> {e}") from e

        return {"file": results}

    @staticmethod
    def transform_data(
        query: EiaPetroleumStatusReportQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumStatusReportData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        import re  # noqa
        from warnings import warn
        from pandas import Categorical, ExcelFile, concat, read_excel

        category = query.category
        tables = (
            list(WpsrTableMap[category])
            if query.table == "all" or not query.table
            else [query.table]
        )

        file = data.get("file")

        if not isinstance(file, ExcelFile):
            raise OpenBBError(
                TypeError(f"Expected an ExcelFile object, got {type(file)} instead.")
            )

        dfs: list = []

        def replace_data_strings(text):
            """Replace the table strings with sortable numbers."""
            pattern = r"Data (\d):"

            def replacer(match):
                """Replace the matched string with a sortable number."""
                return f"Data 0{match.group(1)}:"

            return re.sub(pattern, replacer, text)

        def read_excel_file(file, category, table):
            """Read the ExcelFile for the sheet name and flatten the table."""
            sheet_name = WpsrTableMap[category][table]
            table_name = read_excel(file, sheet_name, header=None, nrows=1).iloc[0, 1]
            table_name = replace_data_strings(table_name)
            df = read_excel(file, sheet_name, header=[1, 2], nrows=3)
            symbols = df.columns.get_level_values(0).tolist()
            titles = [
                d.replace(".1", "") for d in df.columns.get_level_values(1).tolist()
            ]
            title_map = dict(zip(symbols, titles))
            df = read_excel(file, sheet_name, header=None, skiprows=3)
            df.columns = [d.replace("Sourcekey", "date") for d in symbols]
            df = df.melt(
                id_vars="date",
                value_vars=[d for d in df.columns if d != "date"],
                var_name="symbol",
            ).dropna()
            df = df.reset_index(drop=True)
            df.loc[:, "title"] = df.symbol.map(title_map)
            df.loc[:, "unit"] = df.title.map(lambda x: x.split(" (")[-1].split(")")[0])
            units = [f"({d})" for d in df.unit.unique().tolist()]
            for unit in units:
                df.title = df.title.str.replace(unit, "", regex=False).str.strip()
            df.loc[:, "table"] = table_name
            df["order"] = df.groupby("date").cumcount() + 1
            df = df[["date", "table", "symbol", "order", "title", "value", "unit"]]
            df.symbol = Categorical(df.symbol, categories=symbols, ordered=True)
            df = df.sort_values(["date", "symbol"])
            df.date = df.date.dt.date

            if query.start_date:
                df = df[df.date >= query.start_date]

            if query.end_date:
                df = df[df.date <= query.end_date]

            df = df.reset_index(drop=True)

            if len(df) > 0:
                dfs.append(df)
            else:
                warn(f"No data for table: {table}")

        try:
            for table in tables:
                read_excel_file(file, category, table)
            results = concat(dfs)
            results = results.sort_values(by=["date", "table", "order"])

            if len(results) < 1:
                raise EmptyDataError("The data is empty.")

            return [
                EiaPetroleumStatusReportData.model_validate(d)
                for d in results.to_dict(orient="records")
            ]
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(f"Error transforming the data -> {e}") from e
