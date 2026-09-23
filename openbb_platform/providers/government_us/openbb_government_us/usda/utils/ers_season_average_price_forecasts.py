"""USDA ERS Season-Average Price Forecasts file catalog and CSV parser."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/season-average-price-forecasts"

SEASON_AVERAGE_FILES: dict[str, str] = {
    "output_forecast": "/media/6497/output-forecast-csv-file.csv",
    "input_data": "/media/6498/input-data-csv-file.csv",
}

COMMODITIES: tuple[str, ...] = ("Corn", "Cotton", "Soybeans", "Wheat")

OUTPUT_FORECAST_COLUMNS: tuple[str, ...] = (
    "model_forecast_date",
    "commodity",
    "futures_model_type",
    "futures_exchange",
    "marketing_year",
    "mya_price_model_forecast",
    "mya_price_wasde_forecast",
    "wasde_forecast_date",
    "target_price",
    "national_loan_rate",
    "direct_payment_rate",
    "reference_price",
    "ccp_effective_price_model_forecast",
    "ccp_rate_model_forecast",
    "ccp_effective_price_wasde_forecast",
    "ccp_rate_wasde_forecast",
    "historical_mya_price_year1",
    "historical_mya_price_year2",
    "historical_mya_price_year3",
    "historical_mya_price_year4",
    "historical_mya_price_year5",
    "historical_mya_5year_range",
    "historical_mya_price_5year_olympic_average",
    "effective_reference_price",
    "effective_price_model_forecast",
    "plc_payment_rate_model_forecast",
    "effective_price_wasde_forecast",
    "plc_payment_rate_wasde_forecast",
    "maximum_plc_payment_rate",
    "arc_annual_benchmark_price_year1",
    "arc_annual_benchmark_price_year2",
    "arc_annual_benchmark_price_year3",
    "arc_annual_benchmark_price_year4",
    "arc_annual_benchmark_price_year5",
    "arc_annual_benchmark_price_5year_range",
    "arc_co_benchmark_price",
    "arc_co_price_model_forecast",
    "arc_co_price_wasde_forecast",
    "arc_ic_price_model_forecast",
    "arc_ic_price_wasde_forecast",
    "actual_mya_price",
    "price_unit",
)


def parse_output_forecast(text: str) -> list[dict]:
    """Parse the output-forecast CSV text into wide observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the output-forecast file. Each row is one
        already-wide observation keyed by model forecast date, commodity,
        futures model type, futures exchange, and marketing year, with the
        forecast measures spread across a fixed set of columns.

    Returns
    -------
    list[dict]
        One record per row, values stripped of surrounding whitespace, with
        rows lacking a commodity skipped.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        record = {
            key.lower(): (value.strip() if isinstance(value, str) else value)
            for key, value in row.items()
        }
        if not record.get("commodity"):
            continue
        records.append(record)
    return records


async def afetch_output_forecast() -> list[dict]:
    """Download and parse the output-forecast CSV through the ERS disk cache.

    Returns
    -------
    list[dict]
        Wide observation records from parse_output_forecast.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(
        SEASON_AVERAGE_FILES["output_forecast"], product=PRODUCT_PAGE
    )
    return parse_output_forecast(content.decode("utf-8-sig", errors="replace"))
