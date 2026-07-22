"""USDA ERS Food-at-Home Monthly Area Prices catalog, fetch, and CSV parser."""

import csv
import io
import zipfile
from collections import OrderedDict
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/food-at-home-monthly-area-prices"

FMAP_TABLES: "OrderedDict[str, dict]" = OrderedDict(
    [
        (
            "monthly_area_prices",
            {
                "media_path": (
                    "/media/5400/food-at-home-monthly-area-prices-2012-to-2018.zip"
                ),
                "member": "FMAP-Data.csv",
                "label": "Monthly area prices (2012-2018)",
            },
        ),
        (
            "supplemental_price_indexes",
            {
                "media_path": (
                    "/media/5402/food-at-home-monthly-area-prices"
                    "-supplemental-price-indexes-2016-to-2018.zip"
                ),
                "member": "FMAP-SupIndex-Data.csv",
                "label": "Supplemental price indexes (2016-2018)",
            },
        ),
    ]
)

DEFAULT_TABLE = "monthly_area_prices"

AREAS: "OrderedDict[str, tuple[str, str]]" = OrderedDict(
    [
        ("0", ("national", "National")),
        ("1", ("northeast", "Northeast")),
        ("2", ("midwest", "Midwest")),
        ("3", ("south", "South")),
        ("4", ("west", "West")),
        ("12060", ("atlanta", "Atlanta, GA")),
        ("14460", ("boston", "Boston, MA-NH")),
        ("16980", ("chicago", "Chicago, IL-IN-WI")),
        ("19100", ("dallas", "Dallas-Fort Worth, TX")),
        ("19820", ("detroit", "Detroit, MI")),
        ("26420", ("houston", "Houston, TX")),
        ("31080", ("los_angeles", "Los Angeles, CA")),
        ("33100", ("miami", "Miami, FL")),
        ("35620", ("new_york", "New York, NY-NJ-PA")),
        ("37980", ("philadelphia", "Philadelphia, PA-NJ-DE-MD")),
    ]
)

AREA_FIELDS: tuple[str, ...] = tuple(field for field, _ in AREAS.values())

MEASURES: "OrderedDict[str, dict]" = OrderedDict(
    [
        (
            "unit_value_mean_wtd",
            {
                "source": "Unit_value_mean_wtd",
                "label": "Weighted mean unit value (dollars per 100 grams)",
                "unit": "dollars per 100 grams",
                "tables": ("monthly_area_prices",),
            },
        ),
        (
            "unit_value_mean_unwtd",
            {
                "source": "Unit_value_mean_unwtd",
                "label": "Unweighted mean unit value (dollars per 100 grams)",
                "unit": "dollars per 100 grams",
                "tables": ("monthly_area_prices",),
            },
        ),
        (
            "unit_value_se_wtd",
            {
                "source": "Unit_value_se_wtd",
                "label": "Std. error of weighted mean unit value (dollars per 100 g)",
                "unit": "dollars per 100 grams",
                "tables": ("monthly_area_prices",),
            },
        ),
        (
            "price_index_geks",
            {
                "source": "Price_index_GEKS",
                "label": "GEKS price index",
                "unit": "index",
                "tables": ("monthly_area_prices", "supplemental_price_indexes"),
            },
        ),
        (
            "purchase_dollars_wtd",
            {
                "source": "Purchase_dollars_wtd",
                "label": "Weighted purchases (U.S. dollars)",
                "unit": "U.S. dollars",
                "tables": ("monthly_area_prices", "supplemental_price_indexes"),
            },
        ),
        (
            "purchase_dollars_unwtd",
            {
                "source": "Purchase_dollars_unwtd",
                "label": "Unweighted purchases (U.S. dollars)",
                "unit": "U.S. dollars",
                "tables": ("monthly_area_prices", "supplemental_price_indexes"),
            },
        ),
        (
            "purchase_grams_wtd",
            {
                "source": "Purchase_grams_wtd",
                "label": "Weighted purchases (grams)",
                "unit": "grams",
                "tables": ("monthly_area_prices", "supplemental_price_indexes"),
            },
        ),
        (
            "purchase_grams_unwtd",
            {
                "source": "Purchase_grams_unwtd",
                "label": "Unweighted purchases (grams)",
                "unit": "grams",
                "tables": ("monthly_area_prices", "supplemental_price_indexes"),
            },
        ),
        (
            "number_stores",
            {
                "source": "Number_stores",
                "label": "Number of stores",
                "unit": "count",
                "tables": ("monthly_area_prices", "supplemental_price_indexes"),
            },
        ),
        (
            "price_index_laspeyres",
            {
                "source": "Price_index_Laspeyres",
                "label": "Laspeyres price index",
                "unit": "index",
                "tables": ("supplemental_price_indexes",),
            },
        ),
        (
            "price_index_paasche",
            {
                "source": "Price_index_Paasche",
                "label": "Paasche price index",
                "unit": "index",
                "tables": ("supplemental_price_indexes",),
            },
        ),
        (
            "price_index_tornqvist",
            {
                "source": "Price_index_Tornqvist",
                "label": "Tornqvist price index",
                "unit": "index",
                "tables": ("supplemental_price_indexes",),
            },
        ),
        (
            "price_index_fisher_ideal",
            {
                "source": "Price_index_Fisher_Ideal",
                "label": "Fisher Ideal price index",
                "unit": "index",
                "tables": ("supplemental_price_indexes",),
            },
        ),
        (
            "price_index_ccd",
            {
                "source": "Price_index_CCD",
                "label": "Caves-Christensen-Diewert (CCD) price index",
                "unit": "index",
                "tables": ("supplemental_price_indexes",),
            },
        ),
    ]
)

DEFAULT_MEASURE = "unit_value_mean_wtd"

DEFAULT_MEASURE_BY_TABLE: dict[str, str] = {
    "monthly_area_prices": "unit_value_mean_wtd",
    "supplemental_price_indexes": "price_index_geks",
}

SOURCE_TO_MEASURE: dict[str, str] = {
    meta["source"]: key for key, meta in MEASURES.items()
}

GROUPS: tuple[str, ...] = (
    "Grains",
    "Vegetables",
    "Fruit",
    "Dairy",
    "Meat and Protein Foods",
    "Prepared meals, sides, and salads",
    "Other foods",
)

DEFAULT_GROUP = "Dairy"
DEFAULT_ITEM = "40000"

EFPG: "OrderedDict[str, dict]" = OrderedDict(
    [
        ("10000", {"name": "Whole-grain breads", "group": "Grains"}),
        ("10025", {"name": "Whole-grain rice and pasta", "group": "Grains"}),
        ("10050", {"name": "Whole-grain breakfast grains", "group": "Grains"}),
        (
            "10075",
            {
                "name": "Whole-grain flour, bread mixes, and frozen dough",
                "group": "Grains",
            },
        ),
        ("15000", {"name": "Non-whole-grain breads", "group": "Grains"}),
        ("15025", {"name": "Non-whole-grain rice and pasta", "group": "Grains"}),
        ("15050", {"name": "Non-whole-grain breakfast grains", "group": "Grains"}),
        (
            "15075",
            {
                "name": "Non-whole-grain flour, bread mixes, and frozen dough",
                "group": "Grains",
            },
        ),
        ("20000", {"name": "Potatoes, fresh", "group": "Vegetables"}),
        ("20075", {"name": "Potatoes, canned", "group": "Vegetables"}),
        ("21500", {"name": "Other starchy vegetables, fresh", "group": "Vegetables"}),
        (
            "21525",
            {"name": "Other starchy vegetables, fresh cut", "group": "Vegetables"},
        ),
        ("21550", {"name": "Other starchy vegetables, frozen", "group": "Vegetables"}),
        ("21575", {"name": "Other starchy vegetables, canned", "group": "Vegetables"}),
        ("23000", {"name": "Tomatoes, fresh", "group": "Vegetables"}),
        ("23075", {"name": "Tomatoes, canned", "group": "Vegetables"}),
        (
            "24500",
            {"name": "Other red and orange vegetables, fresh", "group": "Vegetables"},
        ),
        (
            "24525",
            {
                "name": "Other red and orange vegetables, fresh cut",
                "group": "Vegetables",
            },
        ),
        (
            "24550",
            {"name": "Other red and orange vegetables, frozen", "group": "Vegetables"},
        ),
        (
            "24575",
            {"name": "Other red and orange vegetables, canned", "group": "Vegetables"},
        ),
        ("26000", {"name": "Dark green vegetables, fresh", "group": "Vegetables"}),
        ("26525", {"name": "Dark green vegetables, fresh cut", "group": "Vegetables"}),
        ("26550", {"name": "Dark green vegetables, frozen", "group": "Vegetables"}),
        ("26575", {"name": "Dark green vegetables, canned", "group": "Vegetables"}),
        (
            "27500",
            {"name": "Beans, lentils, and peas, fresh/dried", "group": "Vegetables"},
        ),
        ("27550", {"name": "Beans, lentils, and peas, frozen", "group": "Vegetables"}),
        ("27575", {"name": "Beans, lentils, and peas, canned", "group": "Vegetables"}),
        ("29000", {"name": "Other/mixed vegetables, fresh", "group": "Vegetables"}),
        ("29025", {"name": "Other/mixed vegetables, fresh cut", "group": "Vegetables"}),
        ("29050", {"name": "Other/mixed vegetables, frozen", "group": "Vegetables"}),
        ("29075", {"name": "Other/mixed vegetables, canned", "group": "Vegetables"}),
        ("30000", {"name": "Whole fruit, fresh", "group": "Fruit"}),
        ("30025", {"name": "Whole fruit, fresh cut", "group": "Fruit"}),
        ("30050", {"name": "Whole fruit, frozen", "group": "Fruit"}),
        ("30075", {"name": "Whole fruit, canned", "group": "Fruit"}),
        ("30090", {"name": "Whole fruit, dried", "group": "Fruit"}),
        (
            "35000",
            {"name": "100-percent fruit and vegetable juices, fresh", "group": "Fruit"},
        ),
        (
            "35050",
            {
                "name": "100-percent fruit and vegetable juices, frozen",
                "group": "Fruit",
            },
        ),
        (
            "35075",
            {
                "name": "100-percent fruit and vegetable juices, canned and "
                "shelf-stable",
                "group": "Fruit",
            },
        ),
        ("40000", {"name": "Whole milk", "group": "Dairy"}),
        ("40030", {"name": "Whole cream and sour cream", "group": "Dairy"}),
        ("40060", {"name": "Whole yogurt", "group": "Dairy"}),
        ("43000", {"name": "Reduced-fat, low-fat, and skim milk", "group": "Dairy"}),
        (
            "43030",
            {
                "name": "Reduced-fat, low-fat, and skim cream and sour cream",
                "group": "Dairy",
            },
        ),
        (
            "43060",
            {"name": "Reduced-fat, low-fat, and skim yogurt", "group": "Dairy"},
        ),
        ("46000", {"name": "Cheese and cream cheese", "group": "Dairy"}),
        ("46050", {"name": "Processed cheese", "group": "Dairy"}),
        (
            "50000",
            {
                "name": "Beef, pork, lamb, veal and game, fresh",
                "group": "Meat and Protein Foods",
            },
        ),
        (
            "50050",
            {
                "name": "Beef, pork, lamb, veal and game, frozen",
                "group": "Meat and Protein Foods",
            },
        ),
        (
            "50075",
            {
                "name": "Beef, pork, lamb, veal and game, canned",
                "group": "Meat and Protein Foods",
            },
        ),
        (
            "51500",
            {
                "name": "Chicken, turkey, and game birds, fresh",
                "group": "Meat and Protein Foods",
            },
        ),
        (
            "51550",
            {
                "name": "Chicken, turkey, and game birds, frozen",
                "group": "Meat and Protein Foods",
            },
        ),
        (
            "51575",
            {
                "name": "Chicken, turkey, and game birds, canned",
                "group": "Meat and Protein Foods",
            },
        ),
        (
            "53000",
            {"name": "Fish and seafood, fresh", "group": "Meat and Protein Foods"},
        ),
        (
            "53050",
            {"name": "Fish and seafood, frozen", "group": "Meat and Protein Foods"},
        ),
        (
            "53075",
            {"name": "Fish and seafood, canned", "group": "Meat and Protein Foods"},
        ),
        ("54500", {"name": "Nuts and seeds", "group": "Meat and Protein Foods"}),
        (
            "54550",
            {
                "name": "Nut and seed butters and spreads",
                "group": "Meat and Protein Foods",
            },
        ),
        (
            "56000",
            {
                "name": "Bacon, sausage, and lunch meats",
                "group": "Meat and Protein Foods",
            },
        ),
        (
            "57500",
            {"name": "Egg and egg substitutes", "group": "Meat and Protein Foods"},
        ),
        (
            "59000",
            {"name": "Tofu and meat substitutes", "group": "Meat and Protein Foods"},
        ),
        (
            "60000",
            {
                "name": "Ready-to-eat foods",
                "group": "Prepared meals, sides, and salads",
            },
        ),
        (
            "62500",
            {
                "name": "Frozen and refrigerated ready-to-heat foods",
                "group": "Prepared meals, sides, and salads",
            },
        ),
        (
            "65000",
            {
                "name": "Shelf-stable, ready-to-heat foods and soups",
                "group": "Prepared meals, sides, and salads",
            },
        ),
        (
            "67500",
            {
                "name": "Shelf-stable meal kits",
                "group": "Prepared meals, sides, and salads",
            },
        ),
        ("70000", {"name": "Fats and oils", "group": "Other foods"}),
        ("70050", {"name": "Salad dressing", "group": "Other foods"}),
        ("71000", {"name": "Condiments, gravies, and sauces", "group": "Other foods"}),
        ("71050", {"name": "Dry spices", "group": "Other foods"}),
        ("72000", {"name": "Sweetened coffee and tea", "group": "Other foods"}),
        ("72010", {"name": "Unsweetened coffee and tea", "group": "Other foods"}),
        (
            "72020",
            {
                "name": "Flavored milk and other sweetened milk-based beverages",
                "group": "Other foods",
            },
        ),
        ("72030", {"name": "Low-calorie beverages", "group": "Other foods"}),
        ("72040", {"name": "All other caloric beverages", "group": "Other foods"}),
        ("72050", {"name": "Alcohol", "group": "Other foods"}),
        ("72060", {"name": "Water", "group": "Other foods"}),
        ("73000", {"name": "Sweeteners", "group": "Other foods"}),
        ("73010", {"name": "Jellies and jams", "group": "Other foods"}),
        ("73020", {"name": "Candy", "group": "Other foods"}),
        ("73030", {"name": "Baked goods", "group": "Other foods"}),
        ("73040", {"name": "Cake and cookie mixes", "group": "Other foods"}),
        (
            "73050",
            {
                "name": "Ice cream and other milk-based desserts",
                "group": "Other foods",
            },
        ),
        ("73060", {"name": "All other desserts", "group": "Other foods"}),
        ("74000", {"name": "Whole-grain breakfast cereal", "group": "Other foods"}),
        ("74050", {"name": "All other breakfast cereal", "group": "Other foods"}),
        (
            "75000",
            {"name": "Savory snacks, whole-grain snacks", "group": "Other foods"},
        ),
        ("75050", {"name": "Savory snacks, all other snacks", "group": "Other foods"}),
        ("76000", {"name": "Vitamins and meal supplements", "group": "Other foods"}),
        ("77000", {"name": "Baby food", "group": "Other foods"}),
        ("78000", {"name": "Infant formula", "group": "Other foods"}),
    ]
)


def media_path(table: str) -> str:
    """Return a table's zip media path.

    Parameters
    ----------
    table : str
        Table key from FMAP_TABLES.

    Returns
    -------
    str
        The '/media/{id}/{name}.zip' path of the table's archive.
    """
    return FMAP_TABLES[table]["media_path"]


def build_url(table: str) -> str:
    """Return a table's full download URL."""
    return f"{BASE_URL}{media_path(table)}"


def table_measures(table: str) -> list[str]:
    """List the measure keys a table publishes, in canonical order.

    Parameters
    ----------
    table : str
        Table key from FMAP_TABLES.

    Returns
    -------
    list[str]
        Measure keys whose source attribute is present in the table.
    """
    return [key for key, meta in MEASURES.items() if table in meta["tables"]]


def measure_options(table: str) -> list[dict]:
    """Build the labeled measure options a table publishes."""
    return [
        {"label": MEASURES[key]["label"], "value": key} for key in table_measures(table)
    ]


def group_options() -> list[dict]:
    """Build the labeled Tier-1 food-group options."""
    return [{"label": group, "value": group} for group in GROUPS]


def item_options(group: str) -> list[dict]:
    """List a food group's items as labeled EFPG-code options.

    Parameters
    ----------
    group : str
        Tier-1 food group from GROUPS.

    Returns
    -------
    list[dict]
        Label/value options with the EFPG name as label and the EFPG code
        string as value, in published order.
    """
    return [
        {"label": meta["name"], "value": code}
        for code, meta in EFPG.items()
        if meta["group"] == group
    ]


def resolve_measure(table: str, measure: str) -> str:
    """Resolve a measure to one the table publishes, falling back per table.

    Parameters
    ----------
    table : str
        Table key from FMAP_TABLES.
    measure : str
        Requested measure key.

    Returns
    -------
    str
        The requested measure when the table publishes it, otherwise the
        table's default measure.
    """
    meta = MEASURES.get(measure)
    if meta is not None and table in meta["tables"]:
        return measure
    return DEFAULT_MEASURE_BY_TABLE[table]


def parse_series(text: str, item_code: str, measure_source: str) -> list[dict]:
    """Parse one table's CSV, keeping one item and one measure's observations.

    Parameters
    ----------
    text : str
        Decoded CSV text of the table's member file.
    item_code : str
        EFPG code to keep, as a string.
    measure_source : str
        Source Attribute name to keep, e.g. 'Unit_value_mean_wtd'.

    Returns
    -------
    list[dict]
        Records with year, month, area_code, and value keys, one per area
        and month.
    """
    reader = csv.reader(StringIO(text))
    header = next(reader)
    idx = {name: position for position, name in enumerate(header)}
    year_i = idx["Year"]
    month_i = idx["Month"]
    efpg_i = idx["EFPG_code"]
    area_i = idx["Metroregion_code"]
    attribute_i = idx["Attribute"]
    value_i = idx["Value"]
    item = str(item_code)
    records: list[dict] = []
    for row in reader:
        if row[efpg_i] != item or row[attribute_i] != measure_source:
            continue
        records.append(
            {
                "year": int(row[year_i]),
                "month": int(row[month_i]),
                "area_code": row[area_i],
                "value": float(row[value_i]),
            }
        )
    return records


def extract_csv_text(zip_bytes: bytes, member: str) -> str:
    """Extract and decode one CSV member from a table's zip archive.

    Parameters
    ----------
    zip_bytes : bytes
        Raw bytes of the table's zip archive.
    member : str
        Member CSV file name to read.

    Returns
    -------
    str
        The decoded CSV text of the member.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        raw = archive.read(member)
    return raw.decode("utf-8-sig", errors="replace")


async def afetch_series(table: str, item_code: str, measure_source: str) -> list[dict]:
    """Download a table and parse one item and measure through the disk cache.

    Parameters
    ----------
    table : str
        Table key from FMAP_TABLES.
    item_code : str
        EFPG code to keep, as a string.
    measure_source : str
        Source Attribute name to keep.

    Returns
    -------
    list[dict]
        Records from parse_series for the selected item and measure.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = FMAP_TABLES[table]
    content = await afetch_ers_file(config["media_path"], product=PRODUCT_PAGE)
    text = extract_csv_text(content, config["member"])
    return parse_series(text, item_code, measure_source)
