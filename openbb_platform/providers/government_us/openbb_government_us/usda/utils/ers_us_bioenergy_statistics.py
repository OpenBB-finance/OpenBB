"""USDA ERS U.S. Bioenergy Statistics file catalog and long-format parser."""

import csv
from io import StringIO

from openbb_government_us.utils.serializers import is_null_token

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/us-bioenergy-statistics"
MEDIA_PATH = "/media/6478/us-bioenergy-statistics.csv"

BIOENERGY_TABLES: dict[str, dict] = {
    "ethanol_supply_marketing_year": {
        "csv_table_key": "1",
        "label": "Fuel ethanol supply and disappearance and grain crushings"
        + " for fuel ethanol by marketing year and quarter",
        "series_fields": ("commodity", "data_item"),
        "row_location": False,
        "cadence": "Marketing year and quarter",
    },
    "ethanol_supply_calendar_year": {
        "csv_table_key": "2",
        "label": "Fuel ethanol supply and disappearance and grain crushings"
        + " for fuel ethanol by calendar year",
        "series_fields": ("commodity", "data_item"),
        "row_location": False,
        "cadence": "Calendar year",
    },
    "ethanol_supply_monthly": {
        "csv_table_key": "3",
        "label": "Fuel ethanol supply and disappearance and grain crushings"
        + " for fuel ethanol by month",
        "series_fields": ("commodity", "data_item"),
        "row_location": False,
        "cadence": "Monthly",
    },
    "biodiesel_supply_marketing_year": {
        "csv_table_key": "4.1",
        "label": "Biodiesel supply and disappearance by soybean oil marketing year",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Marketing year",
    },
    "biodiesel_supply_calendar_year": {
        "csv_table_key": "4.2",
        "label": "Biodiesel supply and disappearance by calendar year",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Calendar year",
    },
    "renewable_diesel_supply_marketing_year": {
        "csv_table_key": "4.3",
        "label": "Renewable diesel supply and disappearance by soybean oil"
        + " marketing year",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Marketing year",
    },
    "renewable_diesel_supply_calendar_year": {
        "csv_table_key": "4.4",
        "label": "Renewable diesel supply and disappearance by calendar year",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Calendar year",
    },
    "corn_supply_and_ethanol_share": {
        "csv_table_key": "5",
        "label": "Corn supply, disappearance, and share of total corn used"
        + " for ethanol",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Marketing year and quarter",
    },
    "soybean_oil_supply_and_biofuel_share": {
        "csv_table_key": "6",
        "label": "Soybean oil supply, disappearance, and share used for biofuel",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Marketing year",
    },
    "oils_and_fats_supply_and_prices": {
        "csv_table_key": "7",
        "label": "Oils and fats supply and prices",
        "series_fields": ("commodity", "data_item", "data_item_desc"),
        "row_location": False,
        "cadence": "Annual",
    },
    "distillers_grains_supply": {
        "csv_table_key": "8.1",
        "label": "Distillers grains supply and disappearance",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Marketing year",
    },
    "corn_gluten_meal_supply": {
        "csv_table_key": "8.2",
        "label": "Corn gluten meal supply and disappearance",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Marketing year",
    },
    "corn_gluten_feed_supply": {
        "csv_table_key": "8.3",
        "label": "Corn gluten feed supply and disappearance",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Marketing year",
    },
    "distillers_dried_grains_price": {
        "csv_table_key": "9",
        "label": "Distillers dried grains price",
        "series_fields": ("data_item",),
        "row_location": True,
        "cadence": "Monthly",
    },
    "ethanol_capacity_and_utilization": {
        "csv_table_key": "10",
        "label": "Fuel ethanol production facilities capacity, production,"
        + " and utilization ratios",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Annual",
    },
    "ethanol_capacity_by_state": {
        "csv_table_key": "11",
        "label": "Fuel ethanol production facilities capacity, by State",
        "series_fields": ("data_item",),
        "row_location": True,
        "cadence": "Annual snapshot",
    },
    "biodiesel_renewable_diesel_plants_by_state": {
        "csv_table_key": "12",
        "label": "Biodiesel and renewable diesel production: Number of plants"
        + " and capacity by State",
        "series_fields": ("commodity", "data_item"),
        "row_location": True,
        "cadence": "Annual snapshot",
    },
    "alternative_fuel_stations": {
        "csv_table_key": "13",
        "label": "Alternative fuel stations",
        "series_fields": ("commodity",),
        "row_location": False,
        "cadence": "Calendar year",
    },
    "corn_ethanol_gasoline_prices_monthly": {
        "csv_table_key": "14",
        "label": "Monthly prices for corn, fuel ethanol, and gasoline",
        "series_fields": ("commodity", "data_item", "data_item_desc"),
        "row_location": False,
        "cadence": "Monthly",
    },
    "ethanol_gasoline_consumption_and_share": {
        "csv_table_key": "15",
        "label": "Fuel ethanol and finished motor gasoline consumption and"
        + " fuel ethanol market share",
        "series_fields": ("commodity", "data_item"),
        "row_location": False,
        "cadence": "Calendar year",
    },
    "biodiesel_and_diesel_prices": {
        "csv_table_key": "16",
        "label": "Biodiesel and diesel prices",
        "series_fields": ("commodity",),
        "row_location": False,
        "cadence": "Monthly",
    },
    "retail_diesel_prices_monthly": {
        "csv_table_key": "17",
        "label": "Monthly average retail diesel prices",
        "series_fields": ("data_item",),
        "row_location": False,
        "cadence": "Monthly",
    },
}


def series_label(components: list[str], units: str) -> str:
    """Build a wide-column header from series-key components and the unit.

    Parameters
    ----------
    components : list[str]
        Ordered series-key values, e.g. ['Fuel ethanol', 'Production'].
        Placeholder and empty values are dropped, and an immediately
        repeated value is collapsed.
    units : str
        Unit of the value, appended in parentheses unless it is a
        placeholder or already appears as a component.

    Returns
    -------
    str
        The column header, e.g. 'Fuel ethanol - Production (1,000 gallons)'.
    """
    parts: list[str] = []
    for component in components:
        value = (component or "").strip()
        if not value or is_null_token(value):
            continue
        if parts and parts[-1] == value:
            continue
        parts.append(value)
    label = " - ".join(parts)
    unit = (units or "").strip()
    if unit and not is_null_token(unit) and unit != label and unit not in parts:
        label = f"{label} ({unit})" if label else unit
    return label


def parse_table(text: str, table: str) -> list[dict]:
    """Parse the tidy CSV into one table's long-format observation records.

    Parameters
    ----------
    text : str
        Decoded text of the whole us-bioenergy-statistics CSV.
    table : str
        Table slug from BIOENERGY_TABLES.

    Returns
    -------
    list[dict]
        Records carrying the table slug, integer year, period label and
        ordinal, the row location (only for state and city tables), the
        wide-column series header, the numeric value, and source order.
        Rows outside the table or with a blank year or non-numeric value
        are skipped.
    """
    config = BIOENERGY_TABLES[table]
    key = config["csv_table_key"]
    series_fields = config["series_fields"]
    row_location = config["row_location"]
    records: list[dict] = []
    for order, row in enumerate(csv.DictReader(StringIO(text))):
        if (row.get("table") or "").strip() != key:
            continue
        raw_value = (row.get("value") or "").strip()
        try:
            value = float(raw_value)
        except ValueError:
            continue
        year_raw = (row.get("year") or "").strip()
        if not (len(year_raw) == 4 and year_raw.isdigit()):
            continue
        try:
            period_ord = int((row.get("period") or "").strip())
        except ValueError:
            period_ord = 0
        location = (row.get("location") or "").strip()
        records.append(
            {
                "table": table,
                "year": int(year_raw),
                "period": (row.get("period_desc") or "").strip() or None,
                "period_ord": period_ord,
                "location": (location or None) if row_location else None,
                "series": series_label(
                    [row.get(field, "") for field in series_fields],
                    row.get("units", ""),
                ),
                "value": value,
            }
        )
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one bioenergy table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table slug from BIOENERGY_TABLES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    return parse_table(content.decode("utf-8-sig", errors="replace"), table)
