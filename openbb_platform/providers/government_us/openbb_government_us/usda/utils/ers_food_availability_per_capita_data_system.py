"""USDA ERS Food Availability (Per Capita) Data System catalog, fetch, and parsers."""

import csv
from collections import OrderedDict
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/food-availability-per-capita-data-system"

DATA_SYSTEMS = ("food_availability", "loss_adjusted", "nutrient")

DATA_SYSTEM_LABELS: dict[str, str] = {
    "food_availability": "Food availability",
    "loss_adjusted": "Loss-adjusted food availability",
    "nutrient": "Nutrient availability",
}

NULL_TOKENS = frozenset({"", "-", "--", "---", "----", "n/a", "na", "null", "nan"})

NUTRIENT_TOTALS_COLUMNS: tuple[tuple[int, str], ...] = (
    (1, "Food energy - Kilocalories"),
    (2, "Carbohydrates - Grams"),
    (3, "Protein - Grams"),
    (4, "Total fat - Grams"),
    (5, "Saturated fat - Grams"),
    (6, "Monounsaturated fat - Grams"),
    (7, "Polyunsaturated fat - Grams"),
    (8, "Cholesterol - Milligrams"),
    (9, "Dietary fiber - Grams"),
    (10, "Vitamin A (RE) - Micrograms RE"),
    (11, "Vitamin A (RAE) - Micrograms RAE"),
    (12, "Carotene - Micrograms"),
    (13, "Vitamin E - Milligrams Alpha-TE"),
    (14, "Vitamin C - Milligrams"),
    (15, "Thiamin - Milligrams"),
    (16, "Riboflavin - Milligrams"),
    (17, "Niacin - Milligrams"),
    (18, "Vitamin B6 - Milligrams"),
    (19, "Folate (DFE) - Micrograms"),
    (20, "Vitamin B12 - Micrograms"),
    (21, "Calcium - Milligrams"),
    (22, "Phosphorus - Milligrams"),
    (23, "Magnesium - Milligrams"),
    (24, "Iron - Milligrams"),
    (25, "Zinc - Milligrams"),
    (26, "Copper - Milligrams"),
    (27, "Potassium - Milligrams"),
    (28, "Selenium - Micrograms"),
    (29, "Sodium - Milligrams"),
)

NUTRIENT_FOODGROUP_NUTRIENTS: tuple[tuple[str, str], ...] = (
    ("Food energy", "Kilocalories"),
    ("Carbohydrates", "Grams"),
    ("Protein", "Grams"),
    ("Total fat", "Grams"),
    ("Saturated fat", "Grams"),
    ("Monounsaturated fat", "Grams"),
    ("Polyunsaturated fat", "Grams"),
    ("Cholesterol", "Milligrams"),
    ("Dietary fiber", "Grams"),
    ("Vitamin A (RAE)", "Micrograms RAE"),
    ("Carotene", "Micrograms"),
    ("Vitamin E", "Milligrams ATE"),
    ("Vitamin C", "Milligrams"),
    ("Thiamin", "Milligrams"),
    ("Riboflavin", "Milligrams"),
    ("Niacin", "Milligrams"),
    ("Vitamin B6", "Milligrams"),
    ("Folate (DFE)", "Micrograms"),
    ("Vitamin B12", "Micrograms"),
    ("Calcium", "Milligrams"),
    ("Phosphorus", "Milligrams"),
    ("Magnesium", "Milligrams"),
    ("Iron", "Milligrams"),
    ("Zinc", "Milligrams"),
    ("Copper", "Milligrams"),
    ("Potassium", "Milligrams"),
    ("Selenium", "Micrograms"),
    ("Sodium", "Milligrams"),
)

CATALOG: dict[str, "OrderedDict[str, dict]"] = {
    "food_availability": OrderedDict(
        [
            (
                "coffee_tea_cocoa",
                {
                    "label": "Coffee, tea, cocoa, and spices",
                    "media": "/media/5327/coffee-tea-cocoa-and-spices-availability.csv",
                    "format": "wide_columnar",
                    "year_col": 0,
                    "block_col": 3,
                    "id_cols": (0, 1, 2, 3),
                    "header_row": 0,
                    "data_start": 1,
                },
            ),
            (
                "dairy_fluid_milk",
                {
                    "label": "Dairy (fluid milk)",
                    "media": "/media/5329/dairy-fluid-milk.csv",
                    "format": "long",
                },
            ),
            (
                "dairy_products",
                {
                    "label": "Dairy products",
                    "media": "/media/5331/dairy-products.csv",
                    "format": "long",
                },
            ),
            (
                "eggs",
                {
                    "label": "Eggs",
                    "media": "/media/5333/eggs.csv",
                    "format": "long",
                },
            ),
            (
                "fats_and_oils_added",
                {
                    "label": "Fats and oils (added)",
                    "media": "/media/5335/fats-and-oils-added.csv",
                    "format": "wide_fixed",
                    "block": "Added fats and oils (product weight): Per capita food availability",
                    "year_col": 0,
                    "data_start": 5,
                    "columns": (
                        (1, "U.S. total population, July 1 - Millions"),
                        (2, "Butter - Pounds"),
                        (3, "Margarine - Pounds"),
                        (4, "Lard - Pounds"),
                        (5, "Edible tallow - Pounds"),
                        (6, "Shortening - Pounds"),
                        (7, "Salad and cooking oils - Pounds"),
                        (8, "Other edible fats and oils - Pounds"),
                        (9, "Total - Pounds"),
                    ),
                },
            ),
            (
                "fish_and_shellfish",
                {
                    "label": "Fish and shellfish",
                    "media": "/media/5337/fish-and-shellfish.csv",
                    "format": "long",
                },
            ),
            (
                "fruit_all_uses",
                {
                    "label": "Fruit (all uses)",
                    "media": "/media/5339/fruit-all-uses.csv",
                    "format": "long",
                },
            ),
            (
                "fruit_canned",
                {
                    "label": "Fruit (canned)",
                    "media": "/media/5341/fruit-canned.csv",
                    "format": "long",
                },
            ),
            (
                "fruit_dried",
                {
                    "label": "Fruit (dried)",
                    "media": "/media/5343/fruit-dried.csv",
                    "format": "long",
                },
            ),
            (
                "fruit_fresh",
                {
                    "label": "Fruit (fresh)",
                    "media": "/media/5345/fruit-fresh.csv",
                    "format": "long",
                },
            ),
            (
                "fruit_frozen",
                {
                    "label": "Fruit (frozen)",
                    "media": "/media/5347/fruit-frozen.csv",
                    "format": "long",
                },
            ),
            (
                "fruit_juices",
                {
                    "label": "Fruit juices",
                    "media": "/media/5349/fruit-juices.csv",
                    "format": "long",
                },
            ),
            (
                "fruit_and_vegetables",
                {
                    "label": "Fruit and vegetables",
                    "media": "/media/5351/fruit-and-vegetables.csv",
                    "format": "long",
                },
            ),
            (
                "grains",
                {
                    "label": "Grains",
                    "media": "/media/5353/grains.csv",
                    "format": "long",
                },
            ),
            (
                "peanuts_and_tree_nuts",
                {
                    "label": "Peanuts and tree nuts",
                    "media": "/media/5355/peanuts-and-tree-nuts.csv",
                    "format": "long",
                },
            ),
            (
                "population",
                {
                    "label": "Population",
                    "media": "/media/5357/population.csv",
                    "format": "wide_fixed",
                    "block": "Population: Resident and resident plus Armed Forces overseas",
                    "year_col": 0,
                    "data_start": 8,
                    "columns": (
                        (
                            1,
                            "Resident population plus Armed Forces overseas - January 1 - Millions",
                        ),
                        (
                            2,
                            "Resident population plus Armed Forces overseas - July 1 - Millions",
                        ),
                        (3, "Resident - January 1 - Millions"),
                        (4, "Resident - July 1 - Millions"),
                        (
                            5,
                            "ERS estimate of resident plus Armed Forces overseas - July 1 - Millions",
                        ),
                    ),
                },
            ),
            (
                "poultry_chicken_and_turkey",
                {
                    "label": "Poultry (chicken and turkey)",
                    "media": "/media/5359/poultry-chicken-and-turkey.csv",
                    "format": "long",
                },
            ),
            (
                "red_meat",
                {
                    "label": "Red meat (beef, veal, pork, lamb, and mutton)",
                    "media": "/media/5361/red-meat-beef-veal-pork-lamb-and-mutton.csv",
                    "format": "long",
                },
            ),
            (
                "red_meat_poultry_and_fish",
                {
                    "label": "Red meat, poultry, and fish",
                    "media": "/media/5363/red-meat-poultry-and-fish.csv",
                    "format": "long",
                },
            ),
            (
                "sugar_and_sweeteners_added",
                {
                    "label": "Sugar and sweeteners (added)",
                    "media": "/media/5365/sugar-and-sweeteners-added.csv",
                    "format": "long",
                },
            ),
            (
                "vegetables_all_uses",
                {
                    "label": "Vegetables (all uses)",
                    "media": "/media/5367/vegetables-all-uses.csv",
                    "format": "long",
                },
            ),
            (
                "vegetables_canned",
                {
                    "label": "Vegetables (canned)",
                    "media": "/media/5369/vegetables-canned.csv",
                    "format": "long",
                },
            ),
            (
                "vegetables_fresh",
                {
                    "label": "Vegetables (fresh)",
                    "media": "/media/5371/vegetables-fresh.csv",
                    "format": "long",
                },
            ),
            (
                "vegetables_frozen",
                {
                    "label": "Vegetables (frozen)",
                    "media": "/media/5373/vegetables-frozen.csv",
                    "format": "long",
                },
            ),
            (
                "vegetables_potatoes",
                {
                    "label": "Vegetables (potatoes)",
                    "media": "/media/5375/vegetables-potatoes.csv",
                    "format": "long",
                },
            ),
            (
                "vegetables_processed",
                {
                    "label": "Vegetables (processed)",
                    "media": "/media/5377/vegetables-processed.csv",
                    "format": "long",
                },
            ),
            (
                "vegetables_pulses",
                {
                    "label": "Vegetables (pulses)",
                    "media": "/media/5379/vegetables-pulses.csv",
                    "format": "long",
                },
            ),
        ]
    ),
    "loss_adjusted": OrderedDict(
        [
            (
                "calories",
                {
                    "label": "Calories",
                    "media": "/media/5381/calories.csv",
                    "format": "wide_fixed",
                    "block": "Average daily per capita calories from the U.S. food availability, adjusted for spoilage and other waste",
                    "year_col": 0,
                    "data_start": 5,
                    "columns": (
                        (1, "Meat, eggs, and nuts"),
                        (2, "Dairy"),
                        (3, "Fruit"),
                        (4, "Vegetables"),
                        (5, "Flour and cereal products"),
                        (6, "Added fats and oils and dairy fats"),
                        (7, "Sugar and sweeteners (added)"),
                        (8, "Total"),
                    ),
                },
            ),
            (
                "dairy",
                {
                    "label": "Dairy (fluid milk, cream, and other products)",
                    "media": "/media/5383/dairy-fluid-milk-cream-and-other-products.csv",
                    "format": "long",
                },
            ),
            (
                "fats_and_oils_added",
                {
                    "label": "Fats and oils (added) - butter",
                    "media": "/media/5385/fats-and-oils-added.csv",
                    "format": "wide_fixed",
                    "block": "Butter: Per capita availability adjusted for loss",
                    "year_col": 0,
                    "data_start": 6,
                    "columns": (
                        (1, "Primary weight - Lbs/year"),
                        (2, "Loss from primary to retail weight - Percent"),
                        (3, "Retail weight - Lbs/year"),
                        (
                            4,
                            "Loss from retail/institutional to consumer level - Percent",
                        ),
                        (5, "Consumer weight - Lbs/year"),
                        (6, "Loss at consumer level - Nonedible share - Percent"),
                        (7, "Loss at consumer level - Edible weight - Lbs/year"),
                        (
                            8,
                            "Loss at consumer level - Other (cooking loss and uneaten food) - Percent",
                        ),
                        (9, "Total loss, all levels - Percent"),
                        (10, "Per capita availability adjusted for loss - Lbs/year"),
                        (11, "Per capita availability adjusted for loss - Oz/day"),
                        (12, "Per capita availability adjusted for loss - G/day"),
                        (13, "Calories per fat gram - Number"),
                    ),
                },
            ),
            (
                "food_pattern_equivalents",
                {
                    "label": "Food pattern equivalents",
                    "media": "/media/5387/food-pattern-equivalents.csv",
                    "format": "wide_fixed",
                    "block": "Average daily per capita food pattern equivalents from the U.S. food availability, adjusted for spoilage and other waste",
                    "year_col": 0,
                    "data_start": 7,
                    "columns": (
                        (1, "Meat, eggs, and nuts - Ounces"),
                        (2, "Dairy - Cups"),
                        (3, "Fruit - Cups"),
                        (4, "Vegetables - Cups"),
                        (5, "Flour and cereal products - Ounces"),
                        (6, "Added fats and oils and dairy fats - Grams"),
                        (7, "Added sugars - Teaspoons"),
                    ),
                },
            ),
            (
                "fruit",
                {
                    "label": "Fruit",
                    "media": "/media/5389/fruit.csv",
                    "format": "long",
                },
            ),
            (
                "grains",
                {
                    "label": "Grains",
                    "media": "/media/5391/grains.csv",
                    "format": "long",
                },
            ),
            (
                "meat_poultry_fish_eggs_and_nuts",
                {
                    "label": "Meat, poultry, fish, eggs, and nuts",
                    "media": "/media/5393/meat-poultry-fish-eggs-and-nuts.csv",
                    "format": "long",
                },
            ),
            (
                "sugar_and_sweeteners_added",
                {
                    "label": "Sugar and sweeteners (added)",
                    "media": "/media/5395/sugar-and-sweeteners-added.csv",
                    "format": "long",
                },
            ),
            (
                "vegetables",
                {
                    "label": "Vegetables",
                    "media": "/media/5397/vegetables.csv",
                    "format": "long",
                },
            ),
        ]
    ),
    "nutrient": OrderedDict(
        [
            (
                "totals",
                {
                    "label": "Totals",
                    "media": "/media/5325/nutrient-availability-food-energy-nutrients-and-dietary-components.xls",
                    "format": "nutrient_totals",
                    "sheet": "Totals",
                    "block": "Totals",
                    "year_col": 0,
                    "data_start": 6,
                    "columns": NUTRIENT_TOTALS_COLUMNS,
                },
            ),
            (
                "food_group",
                {
                    "label": "By food group",
                    "media": "/media/5325/nutrient-availability-food-energy-nutrients-and-dietary-components.xls",
                    "format": "nutrient_foodgroups",
                    "sheet": "Foodgroups",
                    "block_col": 0,
                    "data_start": 4,
                },
            ),
        ]
    ),
}


def parse_value(raw: object) -> float | None:
    """Parse a source cell into a float, keeping full precision.

    Parameters
    ----------
    raw : object
        A raw CSV string or a spreadsheet cell value.

    Returns
    -------
    float | None
        The numeric value with thousands separators removed, or None when the
        cell is blank, a null placeholder, or non-numeric.
    """
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(raw or "").strip()
    if text.casefold() in NULL_TOKENS:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def is_year_token(token: str) -> bool:
    """Return whether a string is a four-digit calendar year."""
    token = token.strip()
    return len(token) == 4 and token.isdigit()


def clean_block_label(raw: str) -> str:
    """Strip surrounding whitespace and trailing footnote digits from a label."""
    return raw.strip().rstrip("0123456789").strip()


def parse_long(text: str) -> list[dict]:
    """Parse a tidy [Commodity, Year, Attribute, Value] file into records.

    Parameters
    ----------
    text : str
        Decoded CSV text whose header begins with Commodity, Year, Attribute,
        and Value, optionally followed by a Notes column.

    Returns
    -------
    list[dict]
        Records with block, year, attribute, and value keys. Rows whose year
        token is not a four-digit calendar year are skipped.
    """
    records: list[dict] = []
    reader = csv.reader(StringIO(text))
    next(reader, None)
    for row in reader:
        if len(row) < 4:
            continue
        year_token = row[1].strip()
        if not is_year_token(year_token):
            continue
        records.append(
            {
                "block": row[0].strip(),
                "year": int(year_token),
                "attribute": row[2].strip(),
                "value": parse_value(row[3]),
            }
        )
    return records


def parse_wide_columnar(text: str, config: dict) -> list[dict]:
    """Parse a columnar wide file with a single header row into records.

    Parameters
    ----------
    text : str
        Decoded CSV text whose first row is a header of measure columns.
    config : dict
        The catalog entry, carrying header_row, year_col, block_col, id_cols,
        and data_start.

    Returns
    -------
    list[dict]
        Records with block, year, attribute, and value keys, one per measure
        column and data row.
    """
    rows = list(csv.reader(StringIO(text)))
    header = rows[config["header_row"]]
    year_col = config["year_col"]
    block_col = config["block_col"]
    id_cols = set(config["id_cols"])
    measure_cols = [i for i in range(len(header)) if i not in id_cols]
    records: list[dict] = []
    for row in rows[config["data_start"] :]:
        if len(row) <= year_col or not is_year_token(row[year_col]):
            continue
        block = row[block_col].strip() if len(row) > block_col else ""
        year = int(row[year_col].strip())
        for col in measure_cols:
            records.append(
                {
                    "block": block,
                    "year": year,
                    "attribute": header[col].strip(),
                    "value": parse_value(row[col] if col < len(row) else ""),
                }
            )
    return records


def parse_wide_fixed(text: str, config: dict) -> list[dict]:
    """Parse a single-block wide file with a hardcoded column map into records.

    Parameters
    ----------
    text : str
        Decoded CSV text of a titled wide file with year rows.
    config : dict
        The catalog entry, carrying block, year_col, data_start, and a columns
        tuple of (index, attribute-name) pairs.

    Returns
    -------
    list[dict]
        Records with block, year, attribute, and value keys, one per mapped
        column and data row.
    """
    rows = list(csv.reader(StringIO(text)))
    year_col = config["year_col"]
    block = config["block"]
    records: list[dict] = []
    for row in rows[config["data_start"] :]:
        if len(row) <= year_col or not is_year_token(row[year_col]):
            continue
        year = int(row[year_col].strip())
        for col, name in config["columns"]:
            records.append(
                {
                    "block": block,
                    "year": year,
                    "attribute": name,
                    "value": parse_value(row[col] if col < len(row) else ""),
                }
            )
    return records


def parse_nutrient_totals(content: bytes, config: dict) -> list[dict]:
    """Parse the nutrient workbook Totals sheet into records.

    Parameters
    ----------
    content : bytes
        Raw bytes of the nutrient .xls workbook.
    config : dict
        The catalog entry, carrying sheet, block, data_start, and a columns
        tuple of (index, nutrient-name) pairs.

    Returns
    -------
    list[dict]
        Records with block, year, attribute, and value keys, one per nutrient
        column and year row.
    """
    import xlrd

    sheet = xlrd.open_workbook(file_contents=content).sheet_by_name(config["sheet"])
    block = config["block"]
    records: list[dict] = []
    for row in range(config["data_start"], sheet.nrows):
        year = _year_from_cell(sheet.cell_value(row, 0))
        if year is None:
            continue
        for col, name in config["columns"]:
            records.append(
                {
                    "block": block,
                    "year": year,
                    "attribute": name,
                    "value": parse_value(sheet.cell_value(row, col)),
                }
            )
    return records


def parse_nutrient_foodgroups(content: bytes, config: dict) -> list[dict]:
    """Parse the nutrient workbook Foodgroups sheet into records.

    Parameters
    ----------
    content : bytes
        Raw bytes of the nutrient .xls workbook.
    config : dict
        The catalog entry, carrying sheet and data_start.

    Returns
    -------
    list[dict]
        Records with block, year, attribute, and value keys. Each food group is
        a block with 1970 and 2010 year rows and paired value and percent-of-
        total nutrient columns.
    """
    import xlrd

    sheet = xlrd.open_workbook(file_contents=content).sheet_by_name(config["sheet"])
    columns = foodgroup_columns()
    records: list[dict] = []
    block: str | None = None
    for row in range(config["data_start"], sheet.nrows):
        first = sheet.cell_value(row, 0)
        year = _year_from_cell(first)
        if year is None:
            if isinstance(first, str) and first.strip():
                block = clean_block_label(first)
            continue
        if block is None:
            continue
        for col, name in columns:
            records.append(
                {
                    "block": block,
                    "year": year,
                    "attribute": name,
                    "value": parse_value(sheet.cell_value(row, col)),
                }
            )
    return records


def foodgroup_columns() -> list[tuple[int, str]]:
    """Build the Foodgroups sheet value and percent-of-total column map.

    Returns
    -------
    list[tuple[int, str]]
        (index, attribute-name) pairs: a value column then a percent-of-total
        column for each nutrient, in sheet order.
    """
    columns: list[tuple[int, str]] = []
    for index, (nutrient, unit) in enumerate(NUTRIENT_FOODGROUP_NUTRIENTS):
        value_col = index * 2 + 1
        columns.append((value_col, f"{nutrient} - {unit}"))
        columns.append((value_col + 1, f"{nutrient} - Percent of total"))
    return columns


def _year_from_cell(value: object) -> int | None:
    """Return the integer calendar year of a cell, or None when it is not one."""
    if isinstance(value, (int, float)):
        year = int(value)
        return year if 1500 <= year <= 2100 else None
    text = str(value or "").strip()
    return int(text) if is_year_token(text) else None


def parse_records(content: bytes, config: dict) -> list[dict]:
    """Dispatch a file's raw bytes to the parser for its format.

    Parameters
    ----------
    content : bytes
        Raw bytes of the downloaded file.
    config : dict
        The catalog entry for the file.

    Returns
    -------
    list[dict]
        Long-format records with block, year, attribute, and value keys.
    """
    fmt = config["format"]
    if fmt == "long":
        return parse_long(content.decode("utf-8-sig", errors="replace"))
    if fmt == "wide_columnar":
        return parse_wide_columnar(
            content.decode("utf-8-sig", errors="replace"), config
        )
    if fmt == "wide_fixed":
        return parse_wide_fixed(content.decode("utf-8-sig", errors="replace"), config)
    if fmt == "nutrient_totals":
        return parse_nutrient_totals(content, config)
    return parse_nutrient_foodgroups(content, config)


def group_options(data_system: str) -> list[dict]:
    """Build the labeled food-group (file) options for a data system.

    Parameters
    ----------
    data_system : str
        Data system key from DATA_SYSTEMS.

    Returns
    -------
    list[dict]
        Label/value option dictionaries for the widget's food-group selector.
    """
    return [
        {"label": config["label"], "value": slug}
        for slug, config in CATALOG[data_system].items()
    ]


def distinct_blocks(records: list[dict]) -> list[str]:
    """List the distinct block names in first-seen order."""
    seen: OrderedDict[str, None] = OrderedDict()
    for record in records:
        seen.setdefault(record["block"], None)
    return list(seen)


async def afetch_records(data_system: str, food_group: str) -> list[dict]:
    """Download and parse one file into long-format records through the cache.

    Parameters
    ----------
    data_system : str
        Data system key from DATA_SYSTEMS.
    food_group : str
        Food-group (file) slug within the data system.

    Returns
    -------
    list[dict]
        Long-format records with block, year, attribute, and value keys.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = CATALOG[data_system][food_group]
    content = await afetch_ers_file(config["media"], product=PRODUCT_PAGE)
    return parse_records(content, config)


async def afetch_blocks(data_system: str, food_group: str) -> list[str]:
    """List the block (commodity) options for a file in first-seen order.

    Parameters
    ----------
    data_system : str
        Data system key from DATA_SYSTEMS.
    food_group : str
        Food-group (file) slug within the data system.

    Returns
    -------
    list[str]
        Distinct block names; a single hardcoded block for the wide single-block
        files, otherwise the blocks parsed from the file.
    """
    config = CATALOG[data_system][food_group]
    if config["format"] in ("wide_fixed", "nutrient_totals"):
        return [config["block"]]
    return distinct_blocks(await afetch_records(data_system, food_group))
