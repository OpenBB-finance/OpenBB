"""Federal Reserve Total Factor Productivity Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.lru import ttl_cache
from pydantic import ConfigDict, Field, model_serializer

TFP_URL = "http://www.frbsf.org/economic-research/files/quarterly_tfp.xlsx"

EXCEL_TO_FIELD = {
    "dY_prod": "d_y_prod",
    "dY_inc": "d_y_inc",
    "dY": "d_y",
    "dhours": "d_hours",
    "dLP": "d_lp",
    "dk": "d_k",
    "dLQ_BLS_interpolated": "d_lq_bls_interpolated",
    "dLQ_Aaronson_Sullivan": "d_lq_aaronson_sullivan",
    "dLQ": "d_lq",
    "alpha": "alpha",
    "dtfp": "d_tfp",
    "dutil": "d_util",
    "dtfp_util": "d_tfp_util",
    "relativePrice": "relative_price",
    "invShare": "inv_share",
    "dtfp_I": "d_tfp_i",
    "dtfp_C": "d_tfp_c",
    "du_invest": "d_u_invest",
    "du_consumption": "d_u_consumption",
    "dtfp_I_util": "d_tfp_i_util",
    "dtfp_C_util": "d_tfp_c_util",
}

NUMERIC_FIELDS = tuple(EXCEL_TO_FIELD.values())

SUMMARY_FIELDS = (
    "full_sample_mean",
    "past_4_quarters",
    "past_8_quarters",
    "since_2019",
    "period_2004_2019",
    "period_1995_2004",
    "period_1973_1995",
    "period_1947_1973",
)

ALL_FLOAT_FIELDS = NUMERIC_FIELDS + SUMMARY_FIELDS

PERIOD_COLUMN_MAP = {
    "Full sample mean": "full_sample_mean",
    "1947:1-1973:1": "period_1947_1973",
    "1973:1-1995:4": "period_1973_1995",
    "1995:4-2004:4": "period_1995_2004",
    "2004:4-2019:4": "period_2004_2019",
    "Since 2019:4": "since_2019",
    "Past 8 qtrs": "past_8_quarters",
    "Past 4 qtrs": "past_4_quarters",
}

VARIABLE_TITLES = {
    "d_y_prod": "Output (Product Side)",
    "d_y_inc": "Output (Income Side)",
    "d_y": "Output",
    "d_hours": "Hours",
    "d_lp": "Labor Productivity",
    "d_k": "Capital Input",
    "d_lq_bls_interpolated": "Labor Quality (BLS Interpolated)",
    "d_lq_aaronson_sullivan": "Labor Quality (Aaronson-Sullivan)",
    "d_lq": "Labor Quality",
    "alpha": "Capital Share",
    "d_tfp": "TFP",
    "d_util": "Utilization",
    "d_tfp_util": "Utilization-Adjusted TFP",
    "relative_price": "Relative Price",
    "inv_share": "Investment Share",
    "d_tfp_i": "TFP (Investment)",
    "d_tfp_c": "TFP (Consumption)",
    "d_u_invest": "Utilization (Investment)",
    "d_u_consumption": "Utilization (Consumption)",
    "d_tfp_i_util": "Utilization-Adjusted TFP (Investment)",
    "d_tfp_c_util": "Utilization-Adjusted TFP (Consumption)",
}

TIME_SERIES_FIELDS = {"date", *NUMERIC_FIELDS}

SUMMARY_RECORD_FIELDS = {"variable", "variable_title", *SUMMARY_FIELDS}


@ttl_cache(ttl=86400)
def download_tfp_excel() -> bytes:
    """Download the TFP Excel file from the San Francisco Federal Reserve.

    Returns:
        bytes: The Excel file content.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import make_request

    response = make_request(TFP_URL)
    response.raise_for_status()

    return response.content


class FederalReserveTfpQueryParams(QueryParams):
    """Federal Reserve Total Factor Productivity Query Parameters.

    This data contains Total Factor Productivity estimates from the
    San Francisco Federal Reserve, including quarterly and annual time series
    as well as summary statistics across different time periods.

    Source: http://www.frbsf.org/economic-research/indicators-data/total-factor-productivity-tfp/
    """

    frequency: Literal["quarter", "annual", "summary"] = Field(
        default="quarter",
        description="Type of data to return. "
        "'quarter' for quarterly time series, "
        "'annual' for annual time series, "
        "'summary' for summary statistics (period means).",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Only applicable for time series data (quarter/annual).",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " Only applicable for time series data (quarter/annual).",
    )


class FederalReserveTfpTimeSeriesData(Data):
    """Federal Reserve Total Factor Productivity time series fields.

    Base class containing time series specific fields.
    """

    model_config = ConfigDict(populate_by_name=True)

    date: dateType | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    d_y_prod: float | None = Field(
        default=None,
        title="Output (Product Side)",
        description=(
            "Business output, expenditure (product) side. "
            "From NIPA tables, Gross Value Added: Total Business: Quantity Index."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_y_inc: float | None = Field(
        default=None,
        title="Output (Income Side)",
        description=(
            "Business output, measured from income side. "
            "Nominal business output is GDI less nominal non-business output. "
            "Real business income uses expenditure-side deflator."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_y: float | None = Field(
        default=None,
        title="Output",
        description=(
            "Output. Average of d_y_prod and d_y_inc (weighted equally). "
            "If d_y_inc not yet available, equals d_y_prod."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_hours: float | None = Field(
        default=None,
        title="Hours",
        description="Hours worked in the business sector. From BLS productivity and cost release.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_lp: float | None = Field(
        default=None,
        title="Labor Productivity",
        description=(
            "Business-sector labor productivity, defined as d_y - d_hours. "
            "Note: Labor productivity in the BLS productivity-and-cost release equals d_y_prod - d_hours."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_k: float | None = Field(
        default=None,
        title="Capital Input",
        description=(
            "Capital input. Perpetual inventory stocks calculated from disaggregated quarterly NIPA "
            "investment data, then growth rates are weighted by estimated rental prices."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_lq_bls_interpolated: float | None = Field(
        default=None,
        title="Labor Quality (BLS Interpolated)",
        description=(
            "Labor composition/quality from BLS. Pre-1979 is interpolated annual BLS MFP estimate "
            "of labor composition (interpolated using Denton (1971) relative to changes in hours)."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_lq_aaronson_sullivan: float | None = Field(
        default=None,
        title="Labor Quality (Aaronson-Sullivan)",
        description=(
            "Labor composition/quality following Aaronson-Sullivan. 1979:Q1 - present follows "
            "Aaronson and Sullivan (2001), as extended by Bart Hobijn and Joyce Kwok (FRBSF)."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_lq: float | None = Field(
        default=None,
        title="Labor Quality",
        description=(
            "Labor composition/quality actually used. Pre-1979 is d_lq_bls_interpolated, "
            "1979:Q1 onward uses d_lq_aaronson_sullivan."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    alpha: float | None = Field(
        default=None,
        title="Capital Share",
        description=(
            "Capital's share of income (ratio between 0 and 1). Based primarily on NIPA data for "
            "the corporate sector, assuming private noncorporate factor shares match corporate shares."
        ),
    )
    d_tfp: float | None = Field(
        default=None,
        title="TFP",
        description=(
            "Business sector Total Factor Productivity. Calculated as d_y - alpha*d_k - "
            "(1-alpha)*(d_hours+d_lq), i.e., output growth less the contribution of capital and labor."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_util: float | None = Field(
        default=None,
        title="Utilization",
        description=(
            "Utilization adjustment for capital and labor. Uses Basu, Fernald, Fisher, and Kimball "
            "(2013) estimates applied to quarterly data."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_tfp_util: float | None = Field(
        default=None,
        title="Utilization-Adjusted TFP",
        description=(
            "Utilization-adjusted Total Factor Productivity. Calculated as d_tfp - d_util, "
            "adjusting for variations in factor utilization."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    relative_price: float | None = Field(
        default=None,
        title="Relative Price",
        description=(
            "Relative price growth of 'consumption' to price of 'equipment'. Measures the relative "
            "price of non-equipment goods and services to price of equipment (with consumer durables "
            "classified as equipment)."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    inv_share: float | None = Field(
        default=None,
        title="Investment Share",
        description=(
            "Equipment and consumer durables share of business output (ratio between 0 and 1). "
            "Represents the proportion of output devoted to equipment investment and consumer durables."
        ),
    )
    d_tfp_i: float | None = Field(
        default=None,
        title="TFP (Investment)",
        description=(
            "TFP in equipment and consumer durables sector. Calculated from d_tfp assuming that "
            "relative price growth reflects relative TFP growth."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_tfp_c: float | None = Field(
        default=None,
        title="TFP (Consumption)",
        description=(
            "TFP in non-equipment business output ('consumption' goods and services). Calculated from "
            "d_tfp assuming that relative price growth reflects relative TFP growth."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_u_invest: float | None = Field(
        default=None,
        title="Utilization (Investment)",
        description=(
            "Utilization adjustment in producing investment goods. Uses estimates from Basu, Fernald, "
            "Fisher, and Kimball to calculate utilization for producing equipment and consumer durables."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_u_consumption: float | None = Field(
        default=None,
        title="Utilization (Consumption)",
        description=(
            "Utilization adjustment in producing non-investment business output ('consumption'). Uses "
            "estimates from Basu, Fernald, Fisher, and Kimball to calculate utilization for producing "
            "non-investment goods and services."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_tfp_i_util: float | None = Field(
        default=None,
        title="Utilization-Adjusted TFP (Investment)",
        description=(
            "Utilization-adjusted TFP in producing equipment and consumer durables. "
            "Calculated as d_tfp_i - d_u_invest."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    d_tfp_c_util: float | None = Field(
        default=None,
        title="Utilization-Adjusted TFP (Consumption)",
        description=(
            "Utilization-adjusted TFP in producing non-equipment business output ('consumption'). "
            "Calculated as d_tfp_c - d_u_consumption."
        ),
        json_schema_extra={"x-unit_measurement": "percent"},
    )


class FederalReserveTfpSummaryData(Data):
    """Federal Reserve Total Factor Productivity summary fields.

    Base class containing summary statistics specific fields.
    """

    model_config = ConfigDict(populate_by_name=True)

    variable: str | None = Field(
        default=None,
        title="Variable",
        description="The variable name (e.g., 'd_y', 'd_tfp', 'd_tfp_util').",
    )
    variable_title: str | None = Field(
        default=None,
        title="Variable Title",
        description="Human-readable title for the variable.",
    )
    full_sample_mean: float | None = Field(
        default=None,
        title="Full Sample Mean",
        description="Mean value over the full sample period.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    past_4_quarters: float | None = Field(
        default=None,
        title="Past 4 Quarters",
        description="Mean value over the past 4 quarters.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    past_8_quarters: float | None = Field(
        default=None,
        title="Past 8 Quarters",
        description="Mean value over the past 8 quarters.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    since_2019: float | None = Field(
        default=None,
        title="Since 2019:4",
        description="Mean value since 2019:Q4.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    period_2004_2019: float | None = Field(
        default=None,
        title="2004:4-2019:4",
        description="Mean value for the period 2004:Q4 to 2019:Q4.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    period_1995_2004: float | None = Field(
        default=None,
        title="1995:4-2004:4",
        description="Mean value for the period 1995:Q4 to 2004:Q4.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    period_1973_1995: float | None = Field(
        default=None,
        title="1973:1-1995:4",
        description="Mean value for the period 1973:Q1 to 1995:Q4.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    period_1947_1973: float | None = Field(
        default=None,
        title="1947:1-1973:1",
        description="Mean value for the period 1947:Q1 to 1973:Q1.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )


class FederalReserveTfpData(
    FederalReserveTfpTimeSeriesData, FederalReserveTfpSummaryData
):
    """Federal Reserve Total Factor Productivity data.

    Combined model containing both time series and summary fields.

    For time series data (frequency='quarter' or 'annual'):
        - date: Date of the observation
        - d_y_prod, d_y_inc, d_y: Output measures
        - d_hours, d_lp, d_k: Labor and capital inputs
        - d_tfp, d_tfp_util: TFP measures
        - And other productivity variables

    For summary data (frequency='summary'):
        - variable: The variable name
        - full_sample_mean: Mean over full sample
        - period_*: Means for specific time periods
        - past_*_quarters: Recent period means

    Source: http://www.frbsf.org/economic-research/indicators-data/total-factor-productivity-tfp/
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.description": "A Quarterly, Utilization-Adjusted Series on Total Factor Productivity (SF Fed)",
                "$.refetchInterval": False,
            }
        },
        populate_by_name=True,
    )

    @classmethod
    def __get_pydantic_json_schema__(  # pylint: disable=W0221
        cls, core_schema, handler
    ) -> dict[str, Any]:
        """Override JSON schema generation to preserve all inherited field properties.

        This method ensures all fields are included in the OpenAPI schema.
        """
        json_schema = handler(core_schema)

        if "properties" not in json_schema or not json_schema["properties"]:
            json_schema["properties"] = {}

            for field_name, field_info in cls.model_fields.items():
                field_schema: dict[str, Any] = {}
                annotation = field_info.annotation

                if hasattr(annotation, "__origin__"):
                    args = getattr(annotation, "__args__", ())

                    if type(None) in args:
                        inner_type = next((a for a in args if a is not type(None)), str)

                        if inner_type is float:
                            field_schema["anyOf"] = [
                                {"type": "number"},
                                {"type": "null"},
                            ]
                        elif inner_type is str:
                            field_schema["anyOf"] = [
                                {"type": "string"},
                                {"type": "null"},
                            ]
                        else:
                            field_schema["anyOf"] = [
                                {"type": "string", "format": "date"},
                                {"type": "null"},
                            ]
                else:
                    field_schema["type"] = "string"

                field_schema["default"] = field_info.default
                field_schema["title"] = (
                    field_info.title or field_name.replace("_", " ").title()
                )

                if field_info.description:
                    field_schema["description"] = field_info.description

                if field_info.json_schema_extra:
                    field_schema.update(field_info.json_schema_extra)  # type: ignore[arg-type]

                json_schema["properties"][field_name] = field_schema

        # Preserve x-widget_config from model_config.json_schema_extra
        config_extra = cls.model_config.get("json_schema_extra", {})
        if "x-widget_config" in config_extra:  # type: ignore[operator]
            json_schema["x-widget_config"] = config_extra["x-widget_config"]  # type: ignore[index]

        return json_schema

    @model_serializer(mode="wrap")
    def _serialize(self, handler) -> dict[str, Any]:
        """Serialize only relevant fields based on record type."""
        data = handler(self)

        if self.variable is not None:
            return {k: v for k, v in data.items() if k in SUMMARY_RECORD_FIELDS}

        return {k: v for k, v in data.items() if k in TIME_SERIES_FIELDS}


class FederalReserveTfpFetcher(
    Fetcher[FederalReserveTfpQueryParams, list[FederalReserveTfpData]]
):
    """Federal Reserve Total Factor Productivity Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FederalReserveTfpQueryParams:
        """Transform input parameters into FederalReserveTfpQueryParams."""
        return FederalReserveTfpQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveTfpQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Download the Excel data from the San Francisco Federal Reserve."""
        try:
            return {"file": download_tfp_excel()}
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: FederalReserveTfpQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[FederalReserveTfpData]:
        """Transform the Excel data into validated Pydantic models."""
        # pylint: disable=import-outside-toplevel
        from io import BytesIO  # noqa
        import numpy as np
        import pandas as pd

        excel_file = pd.ExcelFile(BytesIO(data["file"]))
        frequency = query.frequency
        sheet_name = "quarterly" if frequency in ("quarter", "summary") else "annual"
        skiprows = 1 if sheet_name == "quarterly" else None
        df = pd.read_excel(excel_file, sheet_name=sheet_name, skiprows=skiprows)
        date_col = df.columns[0]

        # Rename Excel columns to snake_case field names
        df = df.rename(columns=EXCEL_TO_FIELD)

        if sheet_name == "quarterly":
            valid_mask = df[date_col].astype(str).str.match(r"^\d{4}:Q[1-4]$")
        else:
            valid_mask = df[date_col].apply(
                lambda x: np.issubdtype(type(x), np.integer)
                or (isinstance(x, float) and x == int(x))
            )

        if frequency == "summary":
            # Summary rows are those that don't match the date pattern
            summary_df = df[~valid_mask].copy()
            summary_df = summary_df.rename(columns={date_col: "period"})
            summary_df = summary_df[summary_df["period"].isin(PERIOD_COLUMN_MAP.keys())]
            summary_df = summary_df.set_index("period").T.reset_index()
            summary_df = summary_df.rename(
                columns={"index": "variable", **PERIOD_COLUMN_MAP}
            )
            summary_df["variable_title"] = summary_df["variable"].map(VARIABLE_TITLES)
            summary_df = summary_df.replace({np.nan: None})

            results: list[FederalReserveTfpData] = [
                FederalReserveTfpData.model_validate(row.to_dict())
                for _, row in summary_df.iterrows()
            ]

            if not results:
                raise OpenBBError(
                    "No summary data found. The data source may have changed."
                )

            return results

        # Time series data
        data_df = df[valid_mask].copy()

        if frequency == "quarter":
            # Convert "YYYY:QN" to proper dates
            date_series = pd.PeriodIndex(
                data_df[date_col].str.replace(":", ""), freq="Q"
            ).to_timestamp()
            data_df[date_col] = date_series.date
        else:
            # Annual: convert year to January 1 of that year
            data_df[date_col] = pd.to_datetime(
                data_df[date_col].astype(int), format="%Y"
            ).dt.date

        data_df = data_df.rename(columns={date_col: "date"})

        # Apply date filters
        if query.start_date:
            data_df = data_df[data_df["date"] >= query.start_date]

        if query.end_date:
            data_df = data_df[data_df["date"] <= query.end_date]

        data_df = data_df.replace({np.nan: None})

        results = [
            FederalReserveTfpData.model_validate(row.to_dict())
            for _, row in data_df.iterrows()
        ]

        if not results:
            raise OpenBBError(
                "The query filters resulted in no data. "
                "Try again with different date parameters."
            )

        return results
