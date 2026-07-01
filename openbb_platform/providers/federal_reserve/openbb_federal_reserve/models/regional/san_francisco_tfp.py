"""Federal Reserve Bank of San Francisco TFP (Fernald) Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.frbsf.org/wp-content/uploads/quarterly_tfp.xlsx"

# Labels taken from the workbook's own "readme" tab (Fernald growth accounting).
_LABELS = {
    "dY_prod": "Business Output (Product Side)",
    "dY_inc": "Business Output (Income Side)",
    "dY": "Output",
    "dhours": "Hours (Business Sector)",
    "dLP": "Labor Productivity",
    "dk": "Capital Input",
    "dLQ_BLS_interpolated": "Labor Quality (BLS, Interpolated)",
    "dLQ_Aaronson_Sullivan": "Labor Quality (Aaronson-Sullivan)",
    "dLQ": "Labor Quality",
    "alpha": "Capital's Share of Income",
    "dtfp": "TFP",
    "dutil": "Utilization of Capital and Labor",
    "dtfp_util": "Utilization-Adjusted TFP",
    "relativePrice": "Relative Price of Consumption to Equipment",
    "invShare": "Equipment and Consumer Durables Share of Output",
    "dtfp_I": "TFP in Equipment and Consumer Durables",
    "dtfp_C": "TFP in Non-Equipment Output",
    "du_invest": "Utilization in Producing Investment",
    "du_consumption": "Utilization in Producing Consumption",
    "dtfp_I_util": "Utilization-Adjusted TFP (Equipment and Consumer Durables)",
    "dtfp_C_util": "Utilization-Adjusted TFP (Non-Equipment Output)",
}


_SHEETS = {
    "quarterly": ("quarterly", 1),
    "annual": ("annual", 0),
    "capital_input_details": ("Capital-input-details", 1),
}


class FederalReserveSanFranciscoTfpQueryParams(QueryParams):
    """San Francisco Fed TFP (Fernald) Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": "Quarterly", "value": "quarterly"},
                    {"label": "Annual", "value": "annual"},
                    {
                        "label": "Capital Input Details",
                        "value": "capital_input_details",
                    },
                ]
            }
        }
    }

    table: Literal["quarterly", "annual", "capital_input_details"] = Field(
        default="quarterly",
        description="The quarterly growth-accounting series, its annualized"
        " counterpart, or the capital-input composition detail.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveSanFranciscoTfpData(Data):
    """San Francisco Fed Total Factor Productivity (Fernald) Data.

    One row per period-end observation date, with one column per growth-accounting
    series carrying that series' annualized percent-change growth rate. The series
    are pivoted to wide, so the columns vary with the selected table (quarterly,
    annual, or capital-input detail).
    """

    date: dateType = Field(description="The period-end observation date.")


class FederalReserveSanFranciscoTfpFetcher(
    Fetcher[
        FederalReserveSanFranciscoTfpQueryParams,
        list[FederalReserveSanFranciscoTfpData],
    ]
):
    """San Francisco Fed TFP (Fernald) Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveSanFranciscoTfpQueryParams:
        """Transform the query params."""
        return FederalReserveSanFranciscoTfpQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveSanFranciscoTfpQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the TFP workbook from the San Francisco Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw TFP workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "san_francisco_tfp",
            lambda: seconds_until_next_release("quarterly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveSanFranciscoTfpQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveSanFranciscoTfpData]:
        """Parse the selected frequency, decode dates, and label the wide columns."""
        from io import BytesIO

        from pandas import PeriodIndex, isna, read_excel, to_numeric

        sheet, header = _SHEETS[query.table]
        annual = query.table == "annual"
        frame = read_excel(
            BytesIO(data[0]["_raw"]),
            engine="openpyxl",
            sheet_name=sheet,
            header=header,
        )
        frame = frame.rename(columns={frame.columns[0]: "date"})
        frame["date"] = frame["date"].astype(str).str.strip()
        if annual:
            frame = frame[frame["date"].str.match(r"^\d{4}(\.0)?$")]
            dates = [dateType(int(float(year)), 12, 31) for year in frame["date"]]
        else:
            frame = frame[frame["date"].str.match(r"^\d{4}:Q\d$")]
            stamps = PeriodIndex(
                frame["date"].str.replace(":", ""), freq="Q"
            ).to_timestamp(how="end")
            dates = [stamp.date() for stamp in stamps]
        frame["date"] = dates

        # Every value column is kept; section-marker columns hold no numbers.
        value_columns = []
        for column in frame.columns:
            if column == "date":
                continue
            frame[column] = to_numeric(frame[column], errors="coerce")
            if frame[column].notna().any():
                value_columns.append(column)

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        rows = []
        for row in frame.sort_values("date").to_dict(orient="records"):
            values = {
                _LABELS.get(column, column): (
                    None if isna(row[column]) else float(row[column])
                )
                for column in value_columns
            }
            if all(value is None for value in values.values()):
                continue
            rows.append(
                FederalReserveSanFranciscoTfpData.model_validate(
                    {"date": row["date"], **values}
                )
            )
        return rows
