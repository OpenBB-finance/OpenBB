"""Utilities for handling PSD report templates by ID.

Ensures all table formats are consistent long/tidy format:

    region | country | commodity | attribute | marketing_year | value | unit
"""

# pylint: disable=unused-argument,C0302

from openbb_government_us.utils.psd_codes import REGION_DISPLAY

# Build KNOWN_REGIONS from REGION_DISPLAY values plus special cases
KNOWN_REGIONS = set(REGION_DISPLAY.values()) | {
    "World Ex-US",
    "Others",
    "Asia",
}

# Aliases for region names that appear differently in CSV reports
REGION_ALIASES = {
    "Total Foreign": "World Ex-US",
    "FSU-12": "Former Soviet Union - 12",
    "Asia (WAP)": "Asia",
    "World Total": "World",
}


def set_region_country(
    entity_name: str, parent_region: str | None = None
) -> tuple[str | None, str]:
    """
    Determine correct region/country values for an entity name.

    Returns (region, country) tuple:
    - If entity_name is a known region -> (normalized_region_name, "--")
    - If entity_name is "European Union" -> ("European Union", "European Union")
    - Otherwise -> (parent_region, entity_name)
    """
    entity_name = entity_name.strip()

    # Apply alias normalization
    normalized = REGION_ALIASES.get(entity_name, entity_name)

    # European Union is both a region and a country (special case per time series)
    if normalized == "European Union":
        return ("European Union", "European Union")

    # Check if it's a known region
    if normalized in KNOWN_REGIONS:
        return (normalized, "--")

    # Regular country - use parent_region if available
    return (parent_region, entity_name)


COMMODITY_GROUP_MAP = {
    "cot": "Cotton",
    "crn": "Corn",
    "wht": "Wheat",
    "ric": "Rice",
    "soy": "Soybeans",
    "bar": "Barley",
    "sor": "Sorghum",
    "oil": "Oilseeds",
    "cof": "Coffee",
    "sug": "Sugar",
    "dai": "Dairy",
    "htp": "Horticultural",
    "juc": "Juice",
    "nut": "Nuts",
    "gra": "Grains",
    "fcr": "Grains",
    "liv": "Livestock",
}

# Known commodities to extract from titles
KNOWN_COMMODITIES = [
    # Grains
    "Cotton",
    "Corn",
    "Wheat",
    "Soybean",
    "Soybeans",
    "Rice",
    "Oats",
    "Barley",
    "Sorghum",
    "Millet",
    "Rye",
    "Coarse Grains",
    # Oilseeds
    "Palm Oil",
    "Rapeseed",
    "Sunflower",
    "Peanut",
    "Copra",
    "Palm Kernel",
    "Oilseeds",
    "Oilseed",
    "Protein Meals",
    "Vegetable Oils",
    # Beverages
    "Coffee",
    "Cocoa",
    "Tea",
    # Sugar
    "Sugar",
    # Dairy
    "Butter",
    "Cheese",
    "Milk",
    "Skim Milk Powder",
    "Whole Milk Powder",
    "Whey",
    "Nonfat Dry Milk",
    "Fluid Milk",
    # Fruits (Horticultural)
    "Apples",
    "Apple",
    "Oranges",
    "Orange",
    "Lemons",
    "Lemon",
    "Limes",
    "Lime",
    "Grapes",
    "Grape",
    "Grapefruit",
    "Tangerines",
    "Tangerine",
    "Mandarins",
    "Mandarin",
    "Cherries",
    "Cherry",
    "Peaches",
    "Peach",
    "Nectarines",
    "Nectarine",
    "Pears",
    "Pear",
    "Raisins",
    "Raisin",
    # Juice
    "Orange Juice",
    # Nuts
    "Almond",
    "Almonds",
    "Walnut",
    "Walnuts",
    "Pistachio",
    "Pistachios",
    "Cashew",
    "Cashews",
    "Hazelnut",
    "Hazelnuts",
    # Livestock
    "Beef",
    "Beef and Veal",
    "Veal",
    "Cattle",
    "Pork",
    "Swine",
    "Chicken",
    "Chicken Meat",
    "Poultry",
    "Turkey",
]


def parse_value(val: str) -> float | None:
    """Parse a value to float, handling special cases."""
    val = val.strip()
    if not val or val.lower() in ("nr", "na", "-", "--", ""):
        return None
    try:
        return float(val.replace(",", ""))
    except ValueError:
        return None


def extract_unit_from_html(html_text: str) -> str | None:
    """Extract unit from HTML rptSubTitle class.

    The subtitle format is often: "Commodity Group  Unit" (double-space separated)
    We want just the unit part.
    """
    # pylint: disable=import-outside-toplevel
    import re

    if not html_text:
        return None
    match = re.search(r"rptSubTitle[^>]*>([^<]+)", html_text)
    if not match:
        return None

    subtitle = match.group(1).strip()

    # Check for double-space separation (commodity group  unit)
    if "  " in subtitle:
        parts = subtitle.split("  ")
        # Unit is typically the last part containing "Million", "Thousand", "Metric", etc.
        for part in reversed(parts):
            stripped_part = part.strip()
            if any(
                u in stripped_part
                for u in [
                    "Million",
                    "Thousand",
                    "Metric",
                    "Tons",
                    "Hectares",
                    "Bales",
                    "Bags",
                ]
            ):
                return stripped_part

    return subtitle


def extract_commodity_from_title(
    title: str, commodity_group: str | None = None
) -> str | None:
    """Extract commodity name from report title or fall back to commodity group."""
    title_lower = title.lower()

    for c in sorted(KNOWN_COMMODITIES, key=len, reverse=True):
        if c.lower() in title_lower:
            if c.endswith("s") and c[:-1] in KNOWN_COMMODITIES:
                return c[:-1]
            return c
    # Fall back to commodity group if provided
    if commodity_group:
        return COMMODITY_GROUP_MAP.get(commodity_group, commodity_group.title())

    return None


def parse_template_1(
    lines: list, html_text: str | None = None, commodity_group: str | None = None
) -> dict:
    """
    Template 1, 20: Area, Yield, and Production tables.
    Used for: Corn/Cotton/Soybean/Wheat Area Yield Production

    These are single-commodity tables. The commodity is in the title.
    Countries are rows, attributes (area/yield/production) are column groups.
    """
    # pylint: disable=import-outside-toplevel
    import re

    report_title = lines[0].strip()
    commodity = extract_commodity_from_title(report_title, commodity_group) or "Unknown"

    # For Oilseed reports (Template 20), check if it's aggregated
    if "Oilseed" in report_title or "Total" in report_title:
        commodity = "Total Oilseeds"

    # Extract units from header line
    header_line = lines[3] if len(lines) > 3 else ""
    unit_matches = re.findall(r"\(([^)]+)\)", header_line)
    units = {
        "area": unit_matches[0] if len(unit_matches) > 0 else "Unknown",
        "yield": unit_matches[1] if len(unit_matches) > 1 else "Unknown",
        "production": unit_matches[2] if len(unit_matches) > 2 else "Unknown",
    }

    # Extract periods from lines 4 and 5
    proj_line = lines[4].split(",") if len(lines) > 4 else []
    period_line = lines[5].split(",") if len(lines) > 5 else []

    periods = []
    current_proj = ""
    for i, p in enumerate(period_line[1:5]):
        _p = p.strip()
        if _p:
            proj_val = proj_line[i + 1].strip() if i + 1 < len(proj_line) else ""
            if "Proj" in proj_val:
                current_proj = proj_val.replace(" Proj.", "")

            if current_proj and _p in (
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ):
                periods.append(f"{current_proj} {_p}")
            else:
                periods.append(_p)

    if not periods:
        return {
            "report": report_title,
            "template": 1,
            "row_count": 0,
            "data": [],
            "error": "Could not extract periods from CSV",
        }

    data = []
    current_region = None
    prev_line_empty = False

    for line in lines[6:]:
        if line and not line.strip():
            if prev_line_empty:
                current_region = None
            continue
        if not line:
            prev_line_empty = True
            continue
        prev_line_empty = False

        parts = line.split(",")
        country = parts[0].strip()
        if not country:
            continue

        values = parts[1:]
        has_data = any(parse_value(v) is not None for v in values)

        if not has_data:
            current_region = country
            continue

        # Determine region/country using helper
        region_val, country_val = set_region_country(country, current_region)

        for i, period in enumerate(periods[:4]):
            # Area
            val = parse_value(values[i]) if i < len(values) else None
            if val is not None:
                data.append(
                    {
                        "region": region_val,
                        "country": country_val,
                        "commodity": commodity,
                        "attribute": "Area",
                        "marketing_year": period,
                        "value": val,
                        "unit": units["area"],
                    }
                )

            # Yield
            val = parse_value(values[4 + i]) if 4 + i < len(values) else None
            if val is not None:
                data.append(
                    {
                        "region": region_val,
                        "country": country_val,
                        "commodity": commodity,
                        "attribute": "Yield",
                        "marketing_year": period,
                        "value": val,
                        "unit": units["yield"],
                    }
                )

            # Production
            val = parse_value(values[8 + i]) if 8 + i < len(values) else None
            if val is not None:
                data.append(
                    {
                        "region": region_val,
                        "country": country_val,
                        "commodity": commodity,
                        "attribute": "Production",
                        "marketing_year": period,
                        "value": val,
                        "unit": units["production"],
                    }
                )

        # Change from last month/year (production change for latest projection period)
        latest_period = periods[-1] if periods else "Unknown"
        if len(values) > 12 and parse_value(values[12]) is not None:
            data.append(
                {
                    "region": region_val,
                    "country": country_val,
                    "commodity": commodity,
                    "attribute": "Production Change from Last Month",
                    "marketing_year": latest_period,
                    "value": parse_value(values[12]),
                    "unit": units["production"],
                }
            )
        if len(values) > 13 and parse_value(values[13]) is not None:
            data.append(
                {
                    "region": region_val,
                    "country": country_val,
                    "commodity": commodity,
                    "attribute": "Production Change from Last Month (%)",
                    "marketing_year": latest_period,
                    "value": parse_value(values[13]),
                    "unit": "%",
                }
            )
        if len(values) > 14 and parse_value(values[14]) is not None:
            data.append(
                {
                    "region": region_val,
                    "country": country_val,
                    "commodity": commodity,
                    "attribute": "Production Change from Last Year",
                    "marketing_year": latest_period,
                    "value": parse_value(values[14]),
                    "unit": units["production"],
                }
            )
        if len(values) > 15 and parse_value(values[15]) is not None:
            data.append(
                {
                    "region": region_val,
                    "country": country_val,
                    "commodity": commodity,
                    "attribute": "Production Change from Last Year (%)",
                    "marketing_year": latest_period,
                    "value": parse_value(values[15]),
                    "unit": "%",
                }
            )

    return {"report": report_title, "template": 1, "row_count": len(data), "data": data}


def parse_template_3(
    lines: list, html_text: str | None = None, commodity_group: str | None = None
) -> dict:
    """
    Template 3, 17: Supply and Distribution by country/year.
    Used for: Cotton Supply, Corn Supply Disappearance

    Single-commodity tables. Countries as section headers, years as rows.
    Attributes are columns (Area Harvested, Production, Imports, etc.)
    """
    report_title = lines[0].strip()
    commodity = extract_commodity_from_title(report_title, commodity_group) or "Unknown"

    # Get column headers from line 2
    header_line = lines[2] if len(lines) > 2 else ""
    columns = [c.strip() for c in header_line.split(",")[1:] if c.strip()]

    unit = extract_unit_from_html(html_text) or "Unknown"  # type: ignore

    data = []
    current_country = None

    for line in lines[3:]:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        parts = line.split(",")
        first_col = parts[0].strip()
        values = parts[1:]

        has_data = any(parse_value(v) is not None for v in values)

        if first_col and not has_data:
            current_country = first_col
            continue

        if not first_col:
            continue

        year = first_col

        # Determine region/country using helper
        if current_country:
            region_val, country_val = set_region_country(current_country, None)
        else:
            region_val, country_val = None, "Unknown"

        for i, col in enumerate(columns):
            if i < len(values):
                val = parse_value(values[i])
                if val is not None:
                    data.append(
                        {
                            "region": region_val,
                            "country": country_val,
                            "commodity": commodity,
                            "attribute": col,
                            "marketing_year": year,
                            "value": val,
                            "unit": unit,
                        }
                    )

    return {"report": report_title, "template": 3, "row_count": len(data), "data": data}


def parse_template_5(
    lines: list, html_text: str | None = None, commodity_group: str | None = None
) -> dict:
    """
    Template 5: World Trade/Production tables - COMMODITY VIEW (Oilseeds).

    Structure (from raw CSV):
    - Attribute (Production, Imports, Exports) is section header
    - Commodity (Oilseed Copra, Oilseed Soybean) is the row identifier
    - Marketing years are columns
    - NO country - this is world-level aggregate data
    """
    report_title = lines[0].strip()

    # Get periods from line 2
    period_line = lines[2] if len(lines) > 2 else ""
    periods = [p.strip() for p in period_line.split(",")[1:] if p.strip()]

    unit = extract_unit_from_html(html_text) or "Unknown"  # type: ignore

    data = []
    current_attribute = None

    for line in lines[3:]:
        if not line.strip():
            continue

        parts = line.split(",")
        first_col = parts[0].strip()
        values = parts[1:]

        has_data = any(parse_value(v) is not None for v in values)

        # Section header = attribute (Production, Imports, etc)
        if first_col and not has_data:
            current_attribute = first_col
            continue

        if not first_col:
            continue

        # first_col = commodity name (Oilseed Copra, etc)
        commodity = first_col

        for i, period in enumerate(periods):
            if i < len(values):
                val = parse_value(values[i])
                if val is not None:
                    data.append(
                        {
                            "region": "World",
                            "country": "--",  # World aggregates
                            "commodity": commodity,
                            "attribute": current_attribute,
                            "marketing_year": period,
                            "value": val,
                            "unit": unit,
                        }
                    )

    return {"report": report_title, "template": 5, "row_count": len(data), "data": data}


def parse_template_7(
    lines: list, html_text: str | None = None, commodity_group: str | None = None
) -> dict:
    """
    Template 7: Production/Consumption summary - COUNTRY VIEW (Dairy).

    Structure (from raw CSV):
    - Attribute (Production, Domestic Consumption) is section header
    - Country (India, EU, US, etc.) is the row identifier
    - Commodity (Butter, Cheese, etc.) is in the TITLE
    - Marketing years are columns
    """
    report_title = lines[0].strip()

    # Extract commodity from title - e.g. "Butter Production and Consumption"
    # Try to find commodity name at the start of title
    commodity = None
    dairy_commodities = [
        "Butter",
        "Cheese",
        "Milk",
        "Skim Milk Powder",
        "Whole Milk Powder",
        "Whey",
        "Nonfat Dry Milk",
        "Fluid Milk",
    ]
    for dc in dairy_commodities:
        if dc.lower() in report_title.lower():
            commodity = dc
            break

    if not commodity:
        commodity = (
            extract_commodity_from_title(report_title, commodity_group) or "Unknown"
        )

    # Get periods from line 2
    period_line = lines[2] if len(lines) > 2 else ""
    periods = [p.strip() for p in period_line.split(",")[1:] if p.strip()]

    unit = extract_unit_from_html(html_text) or "Unknown"  # type: ignore

    data = []
    current_attribute = None

    for line in lines[3:]:
        if not line.strip():
            continue

        parts = line.split(",")
        first_col = parts[0].strip()
        values = parts[1:]

        has_data = any(parse_value(v) is not None for v in values)

        # Section header = attribute (Production, Domestic Consumption, etc)
        if first_col and not has_data:
            current_attribute = first_col
            continue

        if not first_col:
            continue

        # first_col = country name (India, EU, etc)
        country = first_col

        # Determine region/country using helper
        region_val, country_val = set_region_country(country, None)

        for i, period in enumerate(periods):
            if i < len(values):
                val = parse_value(values[i])
                if val is not None:
                    data.append(
                        {
                            "region": region_val,
                            "country": country_val,
                            "commodity": commodity,
                            "attribute": current_attribute,
                            "marketing_year": period,
                            "value": val,
                            "unit": unit,
                        }
                    )

    return {"report": report_title, "template": 7, "row_count": len(data), "data": data}


def parse_template_8(
    lines: list, html_text: str | None = None, commodity_group: str | None = None
) -> dict:
    """
    Template 8: Summary tables (like Coffee, Cotton World Supply).
    Attribute = section header, Country = row, periods = columns
    """
    report_title = lines[0].strip()
    commodity = extract_commodity_from_title(report_title) or "Unknown"

    # Get periods from line 3
    period_line = lines[3] if len(lines) > 3 else ""
    periods = [p.strip() for p in period_line.split(",")[1:] if p.strip()]

    unit = extract_unit_from_html(html_text) or "Unknown"  # type: ignore

    data = []
    current_attribute = None

    for line in lines[4:]:
        if not line.strip():
            continue

        parts = line.split(",")
        first_col = parts[0].strip()
        values = parts[1:]

        if first_col.lower() in ("nr", "") and all(
            v.strip().lower() in ("nr", "") for v in values
        ):
            continue

        has_data = any(parse_value(v) is not None for v in values)

        if first_col and not has_data:
            current_attribute = first_col
            continue

        if not first_col:
            continue

        country = first_col

        # Determine region/country using helper
        region_val, country_val = set_region_country(country, None)

        for i, period in enumerate(periods):
            if i < len(values):
                val = parse_value(values[i])
                if val is not None:
                    data.append(
                        {
                            "region": region_val,
                            "country": country_val,
                            "commodity": commodity,
                            "attribute": current_attribute,
                            "marketing_year": period,
                            "value": val,
                            "unit": unit,
                        }
                    )

    return {"report": report_title, "template": 8, "row_count": len(data), "data": data}


def parse_template_13(
    lines: list, html_text: str | None = None, commodity_group: str | None = None
) -> dict:
    """
    Template 13: Multi-commodity supply/demand tables.
    Used for: China Grain Supply, EU Grain Supply

    Structure (from raw CSV):
    - Row 0: Title (e.g., "China: Grain Supply and Demand")
    - Row 3: Attribute headers (Area Harvested, Yield, Production, Imports, etc.)
    - Row 5+: Commodity sections (Wheat, Coarse Grains, etc.) with year rows

    Country is in the title (China, EU, etc.)
    """
    report_title = lines[0].strip()

    # Extract country from title (e.g., "China: Grain Supply" -> "China")
    country = None
    if ":" in report_title:
        country = report_title.split(":")[0].strip()
    else:
        # Try common patterns
        for c in ["China", "EU", "India", "Brazil", "Russia"]:
            if c in report_title:
                country = c
                break

    if not country:
        country = "Unknown"

    # Determine region/country using helper
    region_val, country_val = set_region_country(country, None)

    # Get column headers from line 3
    header_line = lines[3] if len(lines) > 3 else ""
    columns = [c.strip() for c in header_line.split(",")[1:] if c.strip()]

    unit = extract_unit_from_html(html_text) or "Millions of Metric Tons/Hectares"  # type: ignore

    data = []
    current_commodity = None

    for line in lines[4:]:
        if not line.strip():
            continue

        parts = line.split(",")
        first_col = parts[0].strip()
        values = parts[1:]

        has_data = any(parse_value(v) is not None for v in values)

        # Section header = commodity (Wheat, Coarse Grains, etc.)
        if first_col and not has_data:
            current_commodity = first_col
            continue

        if not first_col:
            continue

        # first_col = marketing year
        year = first_col

        for i, col in enumerate(columns):
            if i < len(values):
                val = parse_value(values[i])
                if val is not None:
                    data.append(
                        {
                            "region": region_val,
                            "country": country_val,
                            "commodity": current_commodity,
                            "attribute": col,
                            "marketing_year": year,
                            "value": val,
                            "unit": unit,
                        }
                    )

    return {
        "report": report_title,
        "template": 13,
        "row_count": len(data),
        "data": data,
    }


def parse_template_2(
    lines: list, html_text: str | None = None, commodity_group: str | None = None
) -> dict:
    """
    Template 2: World Crop Production Summary.

    Structure:
    - Row 3: Regions (World, Total Foreign, North America, FSU-12, Asia (WAP), ...)
    - Row 4: Countries under each region
    - Commodity sections (Wheat, Coarse Grains, Rice, etc.) with marketing year rows

    Attribute is ALWAYS "Production" for this template.
    """
    report_title = lines[0].strip()

    # Get region/country headers from lines 3-4
    region_line = lines[3].split(",") if len(lines) > 3 else []
    country_line = lines[4].split(",") if len(lines) > 4 else []

    columns = []
    current_region = None

    for i, region_value in enumerate(region_line):
        region = region_value.strip()
        country = country_line[i].strip() if i < len(country_line) else ""
        country = country.replace("- ", "").replace(" -", "")

        if region:
            current_region = region

        if i == 0:
            continue

        # Use set_region_country for proper region/country assignment
        if current_region and not country:
            # This is a region-level aggregate (World, Total Foreign, North America, etc.)
            region_val, country_val = set_region_country(current_region, None)
            columns.append((region_val, country_val))
        elif country and current_region:
            # This is a country under a region
            # Apply alias normalization to region name
            normalized_region = REGION_ALIASES.get(current_region, current_region)
            columns.append((normalized_region, country))
        elif country:
            # Country without a region
            columns.append((None, country))

    unit_line = lines[5] if len(lines) > 5 else ""
    unit = unit_line.strip().strip("-").strip() or "Million metric tons"

    data = []
    current_commodity = None
    current_proj_year = None

    def looks_like_year(s: str) -> bool:
        """Heuristic to determine if a string looks like a year or projection indicator."""
        s = s.lower().strip()
        return (
            "/" in s
            or "proj" in s
            or "prel" in s
            or s
            in (
                "nov",
                "dec",
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
            )
        )

    for line in lines[6:]:
        if not line.strip():
            continue

        parts = line.split(",")
        first_col = parts[0].strip()
        values = parts[1:]

        has_data = any(parse_value(v) is not None for v in values)

        if first_col and not has_data:
            if looks_like_year(first_col):
                if "proj" in first_col.lower():
                    current_proj_year = (
                        first_col.replace("proj.", "").replace("Proj.", "").strip()
                    )
                continue
            current_commodity = first_col.strip()
            current_proj_year = None
            continue

        if not first_col and not has_data:
            continue

        if first_col:
            if "proj" in first_col.lower():
                current_proj_year = (
                    first_col.replace("proj.", "").replace("Proj.", "").strip()
                )
                continue
            if first_col.strip() in (
                "Nov",
                "Dec",
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
            ):
                marketing_year = (
                    f"{current_proj_year} {first_col.strip()}"
                    if current_proj_year
                    else first_col.strip()
                )
            else:
                marketing_year = first_col.strip()
                current_proj_year = None
        else:
            continue

        for i, (region, country) in enumerate(columns):
            if i < len(values):
                val = parse_value(values[i])
                if val is not None:
                    data.append(
                        {
                            "region": region,
                            "country": country,
                            "commodity": current_commodity,
                            "attribute": "Production",
                            "marketing_year": marketing_year,
                            "value": val,
                            "unit": unit,
                        }
                    )

    return {"report": report_title, "template": 2, "row_count": len(data), "data": data}


def parse_template_9(
    lines: list, html_text: str | None = None, commodity_group: str | None = None
) -> dict:
    """
    Template 9: Copra, Palm Kernel, Palm Oil Production.

    Multi-commodity table with country rows.
    Commodity is section header, Country is row, periods are columns.
    """
    # pylint: disable=import-outside-toplevel
    import re

    report_title = lines[0].strip()
    unit = extract_unit_from_html(html_text) or "Million metric tons"  # type: ignore

    # Extract periods from line 5 (e.g., "2023/24444" -> "2023/24")
    def clean_period(p):
        """Remove trailing garbage digits from period strings like '2023/24444' -> '2023/24'"""
        p = p.strip()
        if not p:
            return p
        # Match patterns like 2023/24, 2024/25, Nov, Dec, Prel., Proj.
        # Strip any trailing digits that don't belong

        # Handle "2023/24444" -> "2023/24"
        m = re.match(r"^(\d{4}/\d{2})\d*$", p)
        if m:
            return m.group(1)
        # Handle "Prel. 2024/25222" -> "Prel. 2024/25"
        m = re.match(r"^(Prel\.\s*\d{4}/\d{2})\d*$", p)
        if m:
            return m.group(1)
        # Handle "2025/26Proj.111" -> "2025/26 Proj."
        m = re.match(r"^(\d{4}/\d{2})(Proj\.?)\d*$", p)
        if m:
            return f"{m.group(1)} {m.group(2)}"
        # Handle "Nov333" -> "Nov"
        m = re.match(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\d*$", p)
        if m:
            return m.group(1)
        return p

    period_line = lines[5].split(",") if len(lines) > 5 else []
    sub_period_line = lines[6].split(",") if len(lines) > 6 else []

    # Build periods list
    periods = []
    for i, p in enumerate(period_line[1:5]):
        _p = clean_period(p)
        if _p:
            # Check if there's a sub-period (Nov, Dec)
            sub = (
                clean_period(sub_period_line[i + 1])
                if i + 1 < len(sub_period_line)
                else ""
            )
            if sub and sub in ("Nov", "Dec", "Jan", "Feb", "Mar"):
                periods.append(f"{_p} {sub}")
            else:
                periods.append(_p)

    if not periods:
        return {
            "report": report_title,
            "template": 9,
            "row_count": 0,
            "data": [],
            "error": "Could not extract periods from CSV",
        }

    data = []
    current_commodity = None

    for line in lines[9:]:
        if not line.strip():
            continue

        parts = line.split(",")
        first_col = parts[0].strip()
        values = parts[1:]

        has_data = any(parse_value(v) is not None for v in values)

        # Commodity header
        if first_col and not has_data:
            current_commodity = first_col
            continue

        if not first_col:
            continue

        country = first_col

        # Determine region/country using helper
        region_val, country_val = set_region_country(country, None)

        for i, period in enumerate(periods[:4]):
            if i < len(values):
                val = parse_value(values[i])
                if val is not None:
                    data.append(
                        {
                            "region": region_val,
                            "country": country_val,
                            "commodity": current_commodity,
                            "attribute": "Production",
                            "marketing_year": period,
                            "value": val,
                            "unit": unit,
                        }
                    )

        # Change values
        latest_period = periods[-1] if periods else "Unknown"
        if len(values) > 4 and parse_value(values[4]) is not None:
            data.append(
                {
                    "region": region_val,
                    "country": country_val,
                    "commodity": current_commodity,
                    "attribute": "Change from Last Month",
                    "marketing_year": latest_period,
                    "value": parse_value(values[4]),
                    "unit": unit,
                }
            )
        if len(values) > 5 and parse_value(values[5]) is not None:
            data.append(
                {
                    "region": region_val,
                    "country": country_val,
                    "commodity": current_commodity,
                    "attribute": "Change from Last Month (%)",
                    "marketing_year": latest_period,
                    "value": parse_value(values[5]),
                    "unit": "%",
                }
            )

    return {"report": report_title, "template": 9, "row_count": len(data), "data": data}


def parse_template_11(
    lines: list, html_text: str | None = None, commodity_group: str | None = None
) -> dict:
    """
    Template 11: All Grain Summary Comparison.

    Structure (from raw CSV):
    - Row 3: Commodities (Wheat, Rice Milled, Corn, ...)
    - Row 4: Marketing years repeated for each commodity
    - Attribute (Production, Domestic Consumption, etc.) is section header
    - Country (United States, Other, World Total) is row identifier
    """
    report_title = lines[0].strip()

    # Get commodity headers from line 3
    commodity_line = lines[3].split(",") if len(lines) > 3 else []
    commodities = [c.strip() for c in commodity_line if c.strip()]

    # Get periods from line 4 - they repeat for each commodity
    period_line = lines[4].split(",") if len(lines) > 4 else []
    periods = []
    for p in period_line[2:5]:  # First 3 periods for first commodity
        _p = p.strip()
        if _p:
            periods.append(_p)

    unit = extract_unit_from_html(html_text) or "Million Metric Tons"  # type: ignore

    data = []
    current_attribute = None

    for line in lines[5:]:
        if not line.strip():
            continue

        parts = line.split(",")
        first_col = parts[0].strip()
        values = parts[1:]

        has_data = any(parse_value(v) is not None for v in values)

        # Section header = attribute
        if first_col and not has_data:
            current_attribute = first_col
            continue

        if not first_col:
            continue

        country = first_col

        # Determine region/country using helper
        region_val, country_val = set_region_country(country, None)

        # Values are: [note], [c1_y1, c1_y2, c1_y3], [c2_y1, c2_y2, c2_y3], ...
        # Skip the note column (values[0])
        val_idx = 1
        for commodity in commodities:
            for period in periods:
                if val_idx < len(values):
                    val = parse_value(values[val_idx])
                    if val is not None:
                        data.append(
                            {
                                "region": region_val,
                                "country": country_val,
                                "commodity": commodity,
                                "attribute": current_attribute,
                                "marketing_year": period,
                                "value": val,
                                "unit": unit,
                            }
                        )
                    val_idx += 1

    return {
        "report": report_title,
        "template": 11,
        "row_count": len(data),
        "data": data,
    }


def parse_template_20(
    lines: list, html_text: str | None = None, commodity_group: str | None = None
) -> dict:
    """
    Template 20: Total Oilseed Area, Yield, and Production.

    Complex structure with country/commodity sections.
    - Aggregate rows (World Total, Total Foreign, Major OilSeeds, Foreign Oilseeds)
    - Regional subtotals (South America, South Asia, etc. with production value on same row)
    - Individual country rows under regions
    """
    # pylint: disable=import-outside-toplevel
    import re

    report_title = lines[0].strip()
    # Extract units from header line
    header_line = lines[3] if len(lines) > 3 else ""
    unit_matches = re.findall(r"\(([^)]+)\)", header_line)
    units = {
        "area": unit_matches[0] if len(unit_matches) > 0 else "Million hectares",
        "yield": (
            unit_matches[1] if len(unit_matches) > 1 else "Metric tons per hectare"
        ),
        "production": (
            unit_matches[2] if len(unit_matches) > 2 else "Million metric tons"
        ),
    }

    # Extract periods from lines 4 and 5
    proj_line = lines[4].split(",") if len(lines) > 4 else []
    period_line = lines[5].split(",") if len(lines) > 5 else []

    periods = []
    current_proj = ""
    for i, p in enumerate(period_line[1:5]):
        _p = p.strip()
        if p:
            proj_val = proj_line[i + 1].strip() if i + 1 < len(proj_line) else ""
            if "Proj" in proj_val:
                current_proj = proj_val.replace(" Proj.", "")

            if current_proj and p in (
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ):
                periods.append(f"{current_proj} {_p}")
            else:
                periods.append(_p)

    if not periods:
        return {
            "report": report_title,
            "template": 20,
            "row_count": 0,
            "data": [],
            "error": "Could not extract periods from CSV",
        }

    data = []
    current_region = None
    current_commodity = "Total Oilseeds"  # Default commodity for this report

    # Aggregate/commodity names to watch for
    aggregates = ["World Total", "Total Foreign", "Major OilSeeds", "Foreign Oilseeds"]
    special_commodities = ["Oilseed Copra", "Oilseed Palm Kernel"]

    for line in lines[6:]:
        if not line.strip():
            current_region = None
            continue

        parts = line.split(",")
        first_col = parts[0].strip()
        if not first_col:
            continue

        values = parts[1:]
        has_data = any(parse_value(v) is not None for v in values)

        if first_col in special_commodities and not has_data:
            current_commodity = first_col
            continue

        # Check if this is a region subtotal line (region name + values on same line)
        region_match = re.match(r"^([A-Za-z ]+)\s+(\d+\.?\d*)$", first_col)

        if not has_data:
            current_region = first_col
            continue

        # Determine entity type and set appropriate values
        is_aggregate = any(agg.lower() in first_col.lower() for agg in aggregates)
        is_special_commodity = first_col in special_commodities

        if region_match:
            # Region subtotal - extract region name
            entity_name = region_match.group(1).strip()
            current_region = entity_name
            commodity = current_commodity
            # Use helper for region/country assignment
            region_val, country_val = set_region_country(entity_name, None)
        elif is_aggregate:
            # Aggregates like "World Total", "Total Foreign"
            commodity = current_commodity
            region_val, country_val = set_region_country(first_col, None)
        elif is_special_commodity:
            commodity = first_col
            region_val, country_val = ("World", "--")
        else:
            # Regular country row
            commodity = current_commodity
            region_val, country_val = set_region_country(first_col, current_region)

        # Emit data for each period and attribute
        for i, period in enumerate(periods[:4]):
            # Area
            val = parse_value(values[i]) if i < len(values) else None
            if val is not None:
                data.append(
                    {
                        "region": region_val,
                        "country": country_val,
                        "commodity": commodity,
                        "attribute": "Area",
                        "marketing_year": period,
                        "value": val,
                        "unit": units["area"],
                    }
                )

            # Yield
            val = parse_value(values[4 + i]) if 4 + i < len(values) else None
            if val is not None:
                data.append(
                    {
                        "region": region_val,
                        "country": country_val,
                        "commodity": commodity,
                        "attribute": "Yield",
                        "marketing_year": period,
                        "value": val,
                        "unit": units["yield"],
                    }
                )

            # Production
            val = parse_value(values[8 + i]) if 8 + i < len(values) else None
            if val is not None:
                data.append(
                    {
                        "region": region_val,
                        "country": country_val,
                        "commodity": commodity,
                        "attribute": "Production",
                        "marketing_year": period,
                        "value": val,
                        "unit": units["production"],
                    }
                )

        # Change from last month/year
        latest_period = periods[-1] if periods else "Unknown"

        if len(values) > 12 and parse_value(values[12]) is not None:
            data.append(
                {
                    "region": region_val,
                    "country": country_val,
                    "commodity": commodity,
                    "attribute": "Production Change from Last Month",
                    "marketing_year": latest_period,
                    "value": parse_value(values[12]),
                    "unit": units["production"],
                }
            )
        if len(values) > 13 and parse_value(values[13]) is not None:
            data.append(
                {
                    "region": region_val,
                    "country": country_val,
                    "commodity": commodity,
                    "attribute": "Production Change from Last Month (%)",
                    "marketing_year": latest_period,
                    "value": parse_value(values[13]),
                    "unit": "%",
                }
            )
        if len(values) > 14 and parse_value(values[14]) is not None:
            data.append(
                {
                    "region": region_val,
                    "country": country_val,
                    "commodity": commodity,
                    "attribute": "Production Change from Last Year",
                    "marketing_year": latest_period,
                    "value": parse_value(values[14]),
                    "unit": units["production"],
                }
            )
        if len(values) > 15 and parse_value(values[15]) is not None:
            data.append(
                {
                    "region": region_val,
                    "country": country_val,
                    "commodity": commodity,
                    "attribute": "Production Change from Last Year (%)",
                    "marketing_year": latest_period,
                    "value": parse_value(values[15]),
                    "unit": "%",
                }
            )

    return {
        "report": report_title,
        "template": 20,
        "row_count": len(data),
        "data": data,
    }


# Template router
PARSERS = {
    1: parse_template_1,
    2: parse_template_2,
    3: parse_template_3,
    5: parse_template_5,
    7: parse_template_7,
    8: parse_template_8,
    9: parse_template_9,
    11: parse_template_11,
    13: parse_template_13,
    17: parse_template_3,
    20: parse_template_20,
}


def parse_report(
    template_id: int,
    lines: list,
    html_text: str | None = None,
    commodity_group: str | None = None,
) -> dict:
    """Route to appropriate parser based on template ID.

    Args:
        template_id: The template ID for the report
        lines: CSV lines from the report
        html_text: HTML text from the report (for unit extraction)
        commodity_group: The commodity group code (e.g., 'cot', 'crn', 'wht')
    """
    parser = PARSERS.get(template_id)

    if parser:
        return parser(lines, html_text, commodity_group)

    return {"error": f"No parser for template {template_id}", "data": []}
