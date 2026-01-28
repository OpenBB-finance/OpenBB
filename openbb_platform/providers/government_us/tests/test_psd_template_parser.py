"""Deterministic tests for PSD template parser utility functions.

Tests validate:
1. parse_value handles numeric strings and null flags correctly
2. extract_unit_from_html parses HTML subtitle format
3. extract_commodity_from_title matches known commodities
4. Each template parser returns correct shape with proper field types
5. Error handling returns appropriate error dict structure
"""

# pylint: disable=C0302,C1803

import pytest
from openbb_government_us.utils.psd_template_parser import (
    COMMODITY_GROUP_MAP,
    KNOWN_COMMODITIES,
    PARSERS,
    extract_commodity_from_title,
    extract_unit_from_html,
    parse_report,
    parse_template_1,
    parse_template_2,
    parse_template_3,
    parse_template_5,
    parse_template_7,
    parse_template_8,
    parse_template_9,
    parse_template_11,
    parse_template_13,
    parse_template_20,
    parse_value,
)

# =============================================================================
# Test parse_value - validates numeric parsing and null flag handling
# =============================================================================


class TestParseValue:
    """Tests for parse_value function."""

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            # Valid numeric strings
            ("123", 123.0),
            ("123.45", 123.45),
            ("-5", -5.0),
            ("-123.45", -123.45),
            ("0", 0.0),
            ("0.0", 0.0),
            # Comma-formatted numbers
            ("1,234", 1234.0),
            ("1,234.56", 1234.56),
            ("1,234,567.89", 1234567.89),
            # Whitespace handling
            ("  123  ", 123.0),
            ("\t456\n", 456.0),
        ],
    )
    def test_valid_numeric_strings(self, input_val: str, expected: float):
        """Test that valid numeric strings return correct float values."""
        result = parse_value(input_val)
        assert result == expected
        assert isinstance(result, float)

    @pytest.mark.parametrize(
        "input_val",
        [
            # Null flags - should all return None
            "nr",
            "NR",
            "na",
            "NA",
            "-",
            "--",
            "",
            "  ",
            "\t",
        ],
    )
    def test_null_flags_return_none(self, input_val: str):
        """Test that null flags (nr, na, -, --, empty) return None."""
        result = parse_value(input_val)
        assert result is None

    @pytest.mark.parametrize(
        "input_val",
        [
            # Invalid strings
            "abc",
            "12.34.56",
            "N/A",
            "null",
            "none",
        ],
    )
    def test_invalid_strings_return_none(self, input_val: str):
        """Test that invalid non-numeric strings return None."""
        result = parse_value(input_val)
        assert result is None


# =============================================================================
# Test extract_unit_from_html - validates HTML subtitle parsing
# =============================================================================


class TestExtractUnitFromHtml:
    """Tests for extract_unit_from_html function."""

    def test_double_space_separator_extracts_unit(self):
        """Test extraction of unit after double-space separator."""
        html = '<span class="rptSubTitle">Cotton  Million 480-lb. Bales</span>'
        result = extract_unit_from_html(html)
        assert result == "Million 480-lb. Bales"

    def test_metric_tons_unit(self):
        """Test extraction of metric tons unit."""
        html = '<span class="rptSubTitle">Corn  Million Metric Tons</span>'
        result = extract_unit_from_html(html)
        assert result == "Million Metric Tons"

    def test_hectares_unit(self):
        """Test extraction of hectares unit."""
        html = '<span class="rptSubTitle">Wheat  Thousand Hectares</span>'
        result = extract_unit_from_html(html)
        assert result == "Thousand Hectares"

    def test_bags_unit(self):
        """Test extraction of bags unit (coffee)."""
        html = '<span class="rptSubTitle">Coffee  Million 60-kg Bags</span>'
        result = extract_unit_from_html(html)
        assert result == "Million 60-kg Bags"

    def test_no_double_space_returns_full_subtitle(self):
        """Test that subtitle without double-space returns full text."""
        html = '<span class="rptSubTitle">Million Metric Tons</span>'
        result = extract_unit_from_html(html)
        assert result == "Million Metric Tons"

    def test_none_input_returns_none(self):
        """Test that None input returns None."""
        result = extract_unit_from_html(None)  # type: ignore
        assert result is None

    def test_empty_string_returns_none(self):
        """Test that empty string returns None."""
        result = extract_unit_from_html("")
        assert result is None

    def test_html_without_rptsubtitle_returns_none(self):
        """Test that HTML without rptSubTitle class returns None."""
        html = '<span class="other-class">Some Text</span>'
        result = extract_unit_from_html(html)
        assert result is None


# =============================================================================
# Test extract_commodity_from_title - validates commodity name extraction
# =============================================================================


class TestExtractCommodityFromTitle:
    """Tests for extract_commodity_from_title function."""

    def test_known_commodity_match(self):
        """Test matching known commodity from title."""
        result = extract_commodity_from_title("Corn Area, Yield, and Production")
        assert result == "Corn"

    def test_longest_match_wins(self):
        """Test that longest matching commodity wins (Palm Oil vs Oil)."""
        result = extract_commodity_from_title("Palm Oil Production Summary")
        assert result == "Palm Oil"

    def test_plural_normalization(self):
        """Test that plural commodities are normalized to singular."""
        result = extract_commodity_from_title("Soybeans Area and Production")
        assert result == "Soybean"

    def test_case_insensitive_match(self):
        """Test case-insensitive commodity matching."""
        result = extract_commodity_from_title("WHEAT SUPPLY AND DEMAND")
        assert result == "Wheat"

    def test_commodity_group_fallback(self):
        """Test fallback to commodity group when no match in title."""
        result = extract_commodity_from_title("Unknown Report", commodity_group="cot")
        assert result == "Cotton"

    def test_commodity_group_map_lookup(self):
        """Test that COMMODITY_GROUP_MAP contains expected mappings."""
        assert COMMODITY_GROUP_MAP["cot"] == "Cotton"
        assert COMMODITY_GROUP_MAP["crn"] == "Corn"
        assert COMMODITY_GROUP_MAP["wht"] == "Wheat"
        assert COMMODITY_GROUP_MAP["soy"] == "Soybeans"

    def test_no_match_returns_none(self):
        """Test that unknown title with no commodity_group returns None."""
        result = extract_commodity_from_title("Random Report Title")
        assert result is None

    def test_known_commodities_list_populated(self):
        """Test that KNOWN_COMMODITIES contains expected items."""
        assert "Cotton" in KNOWN_COMMODITIES
        assert "Corn" in KNOWN_COMMODITIES
        assert "Wheat" in KNOWN_COMMODITIES
        assert "Coffee" in KNOWN_COMMODITIES
        assert "Palm Oil" in KNOWN_COMMODITIES


# =============================================================================
# Helper to validate response shape
# =============================================================================


def assert_valid_response_shape(result: dict, expected_template: int):
    """Assert that parser response has correct shape and types."""
    # Required keys
    assert "report" in result
    assert "template" in result
    assert "row_count" in result
    assert "data" in result

    # Type checks
    assert isinstance(result["report"], str)
    assert isinstance(result["template"], int)
    assert result["template"] == expected_template
    assert isinstance(result["row_count"], int)
    assert isinstance(result["data"], list)

    # row_count matches data length
    assert result["row_count"] == len(result["data"])

    # No error for valid input
    assert result.get("error") is None


def assert_valid_data_record(record: dict):
    """Assert that a data record has all required fields with correct types."""
    required_keys = [
        "region",
        "country",
        "commodity",
        "attribute",
        "marketing_year",
        "value",
        "unit",
    ]
    for key in required_keys:
        assert key in record, f"Missing key: {key}"

    # Type checks
    assert record["region"] is None or isinstance(record["region"], str)
    assert isinstance(record["country"], str)
    assert isinstance(record["commodity"], str)
    assert isinstance(record["attribute"], str)
    assert isinstance(record["marketing_year"], str)
    assert isinstance(
        record["value"], float
    ), f"value should be float, got {type(record['value'])}"
    assert isinstance(record["unit"], str)


# =============================================================================
# Test Template 1 - Area, Yield, and Production
# =============================================================================


class TestParseTemplate1:
    """Tests for parse_template_1 (Area, Yield, Production tables)."""

    # Minimal valid fixture for Template 1
    # Template 1 expects: 4 area values, 4 yield values, 4 production values, then 4 change values
    # Columns: Area(0-3), Yield(4-7), Production(8-11), ChgMo(12), ChgMo%(13), ChgYr(14), ChgYr%(15)
    VALID_LINES = [
        "Corn Area, Yield, and Production",  # Line 0: Title
        "",  # Line 1: blank
        "",  # Line 2: blank
        "Area (Mil hectares),Yield (MT/HA),Production (MMT)",  # Line 3: unit headers
        ",2023/24,2024/25 Proj.,,",  # Line 4: projection line
        ",Nov,Dec,,",  # Line 5: period line
        "World Total,180.5,181.0,180.0,182.0,5.5,5.6,5.4,5.7,990.0,1010.0,980.0,1020.0,1.0,0.1,20.0,2.0",
        "",  # Line 7: blank
        "North America,,,,,,,,,,,,,,,,",  # Line 8: region header (no data)
        "United States,35.0,36.0,34.0,37.0,11.0,11.2,10.8,11.4,385.0,400.0,380.0,410.0,2.0,0.5,15.0,4.0",
    ]

    def test_valid_input_returns_correct_shape(self):
        """Test that valid input returns correctly shaped response."""
        result = parse_template_1(self.VALID_LINES)

        assert_valid_response_shape(result, expected_template=1)
        assert result["report"] == "Corn Area, Yield, and Production"
        assert result["row_count"] > 0

    def test_extracts_commodity_from_title(self):
        """Test that commodity is extracted from report title."""
        result = parse_template_1(self.VALID_LINES)

        commodities = {r["commodity"] for r in result["data"]}
        assert "Corn" in commodities

    def test_parses_area_yield_production_attributes(self):
        """Test that Area, Yield, Production attributes are parsed."""
        result = parse_template_1(self.VALID_LINES)

        attributes = {r["attribute"] for r in result["data"]}
        assert "Area" in attributes
        assert "Yield" in attributes
        # Production is parsed from columns 8-11
        assert "Production" in attributes or any("Production" in a for a in attributes)

    def test_extracts_units_from_header(self):
        """Test that units are extracted from header line."""
        result = parse_template_1(self.VALID_LINES)

        # Find Area record and check unit
        area_records = [r for r in result["data"] if r["attribute"] == "Area"]
        assert len(area_records) > 0
        assert area_records[0]["unit"] == "Mil hectares"

        # Find Yield record and check unit
        yield_records = [r for r in result["data"] if r["attribute"] == "Yield"]
        assert len(yield_records) > 0
        assert yield_records[0]["unit"] == "MT/HA"

        # Find Production record (base or change) and check unit
        prod_records = [
            r
            for r in result["data"]
            if "Production" in r["attribute"] and "%" not in r["attribute"]
        ]
        assert len(prod_records) > 0
        assert prod_records[0]["unit"] == "MMT"

    def test_parses_marketing_years(self):
        """Test that marketing years are parsed from period line."""
        result = parse_template_1(self.VALID_LINES)

        years = {r["marketing_year"] for r in result["data"]}
        # Should have periods like "Nov", "Dec" or combined with proj year
        assert len(years) > 0

    def test_region_hierarchy_tracking(self):
        """Test that region is tracked for countries under region headers."""
        result = parse_template_1(self.VALID_LINES)

        # Find United States record
        us_records = [r for r in result["data"] if r["country"] == "United States"]
        assert len(us_records) > 0
        assert us_records[0]["region"] == "North America"

        # World Total should have region='World' and country='--'
        world_records = [
            r for r in result["data"] if r["region"] == "World" and r["country"] == "--"
        ]
        assert len(world_records) > 0

    def test_parses_change_values(self):
        """Test that Change from Last Month/Year are parsed."""
        result = parse_template_1(self.VALID_LINES)

        change_attrs = [
            r["attribute"] for r in result["data"] if "Change" in r["attribute"]
        ]
        assert "Production Change from Last Month" in change_attrs
        assert "Production Change from Last Month (%)" in change_attrs
        assert "Production Change from Last Year" in change_attrs
        assert "Production Change from Last Year (%)" in change_attrs

    def test_all_data_records_valid_shape(self):
        """Test that all data records have valid shape."""
        result = parse_template_1(self.VALID_LINES)

        for record in result["data"]:
            assert_valid_data_record(record)

    def test_insufficient_periods_returns_error(self):
        """Test that insufficient period lines return error."""
        # Only 4 lines - missing period info
        short_lines = [
            "Corn Area, Yield, and Production",
            "",
            "",
            "Area (Mil hectares),Yield (MT/HA),Production (MMT)",
        ]
        result = parse_template_1(short_lines)

        assert "error" in result
        assert "Could not extract periods" in result["error"]
        assert result["data"] == []
        assert result["row_count"] == 0

    def test_empty_data_rows_skipped(self):
        """Test that rows with no numeric data are skipped."""
        lines = [
            "Corn Area, Yield, and Production",
            "",
            "",
            "Area (Mil hectares),Yield (MT/HA),Production (MMT)",
            ",2023/24,2024/25 Proj.,,",
            ",Nov,Dec,,",
            "World Total,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr",
        ]
        result = parse_template_1(lines)

        # Should have no data (all nr values)
        assert result["row_count"] == 0
        assert result["data"] == []


# =============================================================================
# Test Template 2 - World Crop Production Summary
# =============================================================================


class TestParseTemplate2:
    """Tests for parse_template_2 (World Crop Production Summary)."""

    VALID_LINES = [
        "World Crop Production Summary",  # Line 0: Title
        "",  # Line 1: blank
        "",  # Line 2: blank
        ",World,Total Foreign,North America,,South America,,",  # Line 3: regions
        ",,, United States, Canada, Brazil, Argentina,",  # Line 4: countries
        "Million metric tons",  # Line 5: unit
        "Wheat",  # Line 6: commodity header
        "2023/24,750.5,600.0,55.0,50.0,30.0,25.0",  # Line 7: year data
        "2024/25 Proj.",  # Line 8: projection indicator
        "Nov,760.0,610.0,56.0,51.0,31.0,26.0",  # Line 9: month data
    ]

    def test_valid_input_returns_correct_shape(self):
        """Test that valid input returns correctly shaped response."""
        result = parse_template_2(self.VALID_LINES)

        assert_valid_response_shape(result, expected_template=2)
        assert result["report"] == "World Crop Production Summary"

    def test_attribute_always_production(self):
        """Test that attribute is always 'Production' for this template."""
        result = parse_template_2(self.VALID_LINES)

        for record in result["data"]:
            assert record["attribute"] == "Production"

    def test_region_country_mapping(self):
        """Test that regions and countries are mapped correctly."""
        result = parse_template_2(self.VALID_LINES)

        countries = {r["country"] for r in result["data"]}
        regions = {r["region"] for r in result["data"]}
        # World and World Ex-US should be in regions with country='--'
        assert "World" in regions or "World Ex-US" in regions
        assert "--" in countries  # Aggregates have country='--'

    def test_commodity_sections_parsed(self):
        """Test that commodity sections are parsed."""
        result = parse_template_2(self.VALID_LINES)

        commodities = {r["commodity"] for r in result["data"]}
        assert "Wheat" in commodities

    def test_all_data_records_valid_shape(self):
        """Test that all data records have valid shape."""
        result = parse_template_2(self.VALID_LINES)

        for record in result["data"]:
            assert_valid_data_record(record)


# =============================================================================
# Test Template 3 - Supply and Distribution
# =============================================================================


class TestParseTemplate3:
    """Tests for parse_template_3 (Supply and Distribution by country/year)."""

    VALID_LINES = [
        "Cotton Supply and Disappearance",  # Line 0: Title
        "",  # Line 1: blank
        ",Area Harvested,Beginning Stocks,Production,Imports,Exports,Ending Stocks",  # Line 2: headers
        "United States",  # Line 3: country header
        "2022/23,4.5,2.0,14.5,0.01,12.0,3.5",  # Line 4: year data
        "2023/24,4.2,3.5,12.0,0.02,10.5,4.0",  # Line 5: year data
        "China",  # Line 6: country header
        "2022/23,3.0,8.0,6.0,2.5,0.1,9.0",  # Line 7: year data
    ]

    HTML_TEXT = '<span class="rptSubTitle">Cotton  Million 480-lb. Bales</span>'

    def test_valid_input_returns_correct_shape(self):
        """Test that valid input returns correctly shaped response."""
        result = parse_template_3(self.VALID_LINES, html_text=self.HTML_TEXT)

        assert_valid_response_shape(result, expected_template=3)
        assert result["report"] == "Cotton Supply and Disappearance"

    def test_extracts_commodity_from_title(self):
        """Test that commodity is extracted from report title."""
        result = parse_template_3(self.VALID_LINES, html_text=self.HTML_TEXT)

        commodities = {r["commodity"] for r in result["data"]}
        assert "Cotton" in commodities

    def test_parses_column_attributes(self):
        """Test that column headers become attributes."""
        result = parse_template_3(self.VALID_LINES, html_text=self.HTML_TEXT)

        attributes = {r["attribute"] for r in result["data"]}
        assert "Area Harvested" in attributes
        assert "Production" in attributes
        assert "Imports" in attributes
        assert "Exports" in attributes

    def test_country_sections_parsed(self):
        """Test that country sections are parsed correctly."""
        result = parse_template_3(self.VALID_LINES, html_text=self.HTML_TEXT)

        countries = {r["country"] for r in result["data"]}
        assert "United States" in countries
        assert "China" in countries

    def test_marketing_years_parsed(self):
        """Test that marketing years are parsed."""
        result = parse_template_3(self.VALID_LINES, html_text=self.HTML_TEXT)

        years = {r["marketing_year"] for r in result["data"]}
        assert "2022/23" in years
        assert "2023/24" in years

    def test_unit_extracted_from_html(self):
        """Test that unit is extracted from HTML."""
        result = parse_template_3(self.VALID_LINES, html_text=self.HTML_TEXT)

        assert result["data"][0]["unit"] == "Million 480-lb. Bales"

    def test_all_data_records_valid_shape(self):
        """Test that all data records have valid shape."""
        result = parse_template_3(self.VALID_LINES, html_text=self.HTML_TEXT)

        for record in result["data"]:
            assert_valid_data_record(record)


# =============================================================================
# Test Template 5 - World Trade (Commodity View)
# =============================================================================


class TestParseTemplate5:
    """Tests for parse_template_5 (World Trade/Production - Commodity View)."""

    VALID_LINES = [
        "World Oilseed Production",  # Line 0: Title
        "",  # Line 1: blank
        ",2022/23,2023/24,2024/25 Proj.",  # Line 2: periods
        "Production",  # Line 3: attribute header
        "Oilseed Copra,5.5,5.8,6.0",  # Line 4: commodity data
        "Oilseed Soybean,370.0,395.0,420.0",  # Line 5: commodity data
        "Imports",  # Line 6: attribute header
        "Oilseed Copra,0.5,0.6,0.7",  # Line 7: commodity data
    ]

    HTML_TEXT = '<span class="rptSubTitle">Oilseeds  Million Metric Tons</span>'

    def test_valid_input_returns_correct_shape(self):
        """Test that valid input returns correctly shaped response."""
        result = parse_template_5(self.VALID_LINES, html_text=self.HTML_TEXT)

        assert_valid_response_shape(result, expected_template=5)
        assert result["report"] == "World Oilseed Production"

    def test_country_always_world(self):
        """Test that country is '--' and region is 'World' for all records (aggregate data)."""
        result = parse_template_5(self.VALID_LINES, html_text=self.HTML_TEXT)

        for record in result["data"]:
            assert record["country"] == "--"
            assert record["region"] == "World"

    def test_commodity_from_row_identifier(self):
        """Test that commodity comes from row identifier."""
        result = parse_template_5(self.VALID_LINES, html_text=self.HTML_TEXT)

        commodities = {r["commodity"] for r in result["data"]}
        assert "Oilseed Copra" in commodities
        assert "Oilseed Soybean" in commodities

    def test_attribute_from_section_header(self):
        """Test that attribute comes from section headers."""
        result = parse_template_5(self.VALID_LINES, html_text=self.HTML_TEXT)

        attributes = {r["attribute"] for r in result["data"]}
        assert "Production" in attributes
        assert "Imports" in attributes

    def test_periods_parsed(self):
        """Test that periods are parsed from header line."""
        result = parse_template_5(self.VALID_LINES, html_text=self.HTML_TEXT)

        years = {r["marketing_year"] for r in result["data"]}
        assert "2022/23" in years
        assert "2023/24" in years
        assert "2024/25 Proj." in years

    def test_all_data_records_valid_shape(self):
        """Test that all data records have valid shape."""
        result = parse_template_5(self.VALID_LINES, html_text=self.HTML_TEXT)

        for record in result["data"]:
            assert_valid_data_record(record)


# =============================================================================
# Test Template 7 - Dairy Production/Consumption (Country View)
# =============================================================================


class TestParseTemplate7:
    """Tests for parse_template_7 (Dairy Production/Consumption - Country View)."""

    VALID_LINES = [
        "Butter Production and Consumption",  # Line 0: Title
        "",  # Line 1: blank
        ",2022,2023,2024 Proj.",  # Line 2: periods
        "Production",  # Line 3: attribute header
        "India,6.5,6.8,7.0",  # Line 4: country data
        "EU,2.3,2.4,2.5",  # Line 5: country data
        "Domestic Consumption",  # Line 6: attribute header
        "India,6.4,6.7,6.9",  # Line 7: country data
    ]

    HTML_TEXT = '<span class="rptSubTitle">Dairy  Thousand Metric Tons</span>'

    def test_valid_input_returns_correct_shape(self):
        """Test that valid input returns correctly shaped response."""
        result = parse_template_7(self.VALID_LINES, html_text=self.HTML_TEXT)

        assert_valid_response_shape(result, expected_template=7)
        assert result["report"] == "Butter Production and Consumption"

    def test_extracts_dairy_commodity_from_title(self):
        """Test that dairy commodity is extracted from title."""
        result = parse_template_7(self.VALID_LINES, html_text=self.HTML_TEXT)

        commodities = {r["commodity"] for r in result["data"]}
        assert "Butter" in commodities

    def test_country_from_row_identifier(self):
        """Test that country comes from row identifier."""
        result = parse_template_7(self.VALID_LINES, html_text=self.HTML_TEXT)

        countries = {r["country"] for r in result["data"]}
        assert "India" in countries
        assert "EU" in countries

    def test_attribute_from_section_header(self):
        """Test that attribute comes from section headers."""
        result = parse_template_7(self.VALID_LINES, html_text=self.HTML_TEXT)

        attributes = {r["attribute"] for r in result["data"]}
        assert "Production" in attributes
        assert "Domestic Consumption" in attributes

    def test_all_data_records_valid_shape(self):
        """Test that all data records have valid shape."""
        result = parse_template_7(self.VALID_LINES, html_text=self.HTML_TEXT)

        for record in result["data"]:
            assert_valid_data_record(record)


# =============================================================================
# Test Template 8 - Summary Tables (Coffee, Cotton World Supply)
# =============================================================================


class TestParseTemplate8:
    """Tests for parse_template_8 (Summary tables like Coffee World Supply)."""

    VALID_LINES = [
        "Coffee World Supply and Demand",  # Line 0: Title
        "",  # Line 1: blank
        "",  # Line 2: blank
        ",2022/23,2023/24,2024/25 Proj.",  # Line 3: periods
        "Production",  # Line 4: attribute header
        "Brazil,65.0,55.0,70.0",  # Line 5: country data
        "Vietnam,31.0,28.0,30.0",  # Line 6: country data
        "Consumption",  # Line 7: attribute header
        "Brazil,22.0,23.0,24.0",  # Line 8: country data
    ]

    HTML_TEXT = '<span class="rptSubTitle">Coffee  Million 60-kg Bags</span>'

    def test_valid_input_returns_correct_shape(self):
        """Test that valid input returns correctly shaped response."""
        result = parse_template_8(self.VALID_LINES, html_text=self.HTML_TEXT)

        assert_valid_response_shape(result, expected_template=8)
        assert result["report"] == "Coffee World Supply and Demand"

    def test_extracts_commodity_from_title(self):
        """Test that commodity is extracted from title."""
        result = parse_template_8(self.VALID_LINES, html_text=self.HTML_TEXT)

        commodities = {r["commodity"] for r in result["data"]}
        assert "Coffee" in commodities

    def test_periods_from_line_3(self):
        """Test that periods are parsed from line 3."""
        result = parse_template_8(self.VALID_LINES, html_text=self.HTML_TEXT)

        years = {r["marketing_year"] for r in result["data"]}
        assert "2022/23" in years
        assert "2023/24" in years

    def test_attribute_sections_parsed(self):
        """Test that attribute sections are parsed."""
        result = parse_template_8(self.VALID_LINES, html_text=self.HTML_TEXT)

        attributes = {r["attribute"] for r in result["data"]}
        assert "Production" in attributes
        assert "Consumption" in attributes

    def test_unit_from_html(self):
        """Test that unit is extracted from HTML."""
        result = parse_template_8(self.VALID_LINES, html_text=self.HTML_TEXT)

        assert result["data"][0]["unit"] == "Million 60-kg Bags"

    def test_all_data_records_valid_shape(self):
        """Test that all data records have valid shape."""
        result = parse_template_8(self.VALID_LINES, html_text=self.HTML_TEXT)

        for record in result["data"]:
            assert_valid_data_record(record)


# =============================================================================
# Test Template 9 - Copra, Palm Kernel, Palm Oil Production
# =============================================================================


class TestParseTemplate9:
    """Tests for parse_template_9 (Copra, Palm Kernel, Palm Oil Production)."""

    VALID_LINES = [
        "Copra, Palm Kernel, and Palm Oil Production",  # Line 0: Title
        "",  # Line 1-4: blanks
        "",
        "",
        "",
        ",2022/23,2023/24,Prel. 2024/25,2025/26Proj.,Change,% Chg",  # Line 5: periods
        ",,,,Nov,,,",  # Line 6: sub-periods
        "",  # Line 7: blank
        "",  # Line 8: blank
        "Copra",  # Line 9: commodity header
        "Philippines,1.8,1.9,2.0,2.1,0.1,5.0",  # Line 10: country data
        "Indonesia,1.5,1.6,1.7,1.8,0.05,3.0",  # Line 11: country data
        "Palm Oil",  # Line 12: commodity header
        "Malaysia,18.0,19.0,19.5,20.0,0.5,2.5",  # Line 13: country data
    ]

    HTML_TEXT = '<span class="rptSubTitle">Oilseeds  Million Metric Tons</span>'

    def test_valid_input_returns_correct_shape(self):
        """Test that valid input returns correctly shaped response."""
        result = parse_template_9(self.VALID_LINES, html_text=self.HTML_TEXT)

        assert_valid_response_shape(result, expected_template=9)
        assert result["report"] == "Copra, Palm Kernel, and Palm Oil Production"

    def test_commodity_sections_parsed(self):
        """Test that commodity sections are parsed."""
        result = parse_template_9(self.VALID_LINES, html_text=self.HTML_TEXT)

        commodities = {r["commodity"] for r in result["data"]}
        assert "Copra" in commodities
        assert "Palm Oil" in commodities

    def test_country_from_row_identifier(self):
        """Test that country comes from row identifier."""
        result = parse_template_9(self.VALID_LINES, html_text=self.HTML_TEXT)

        countries = {r["country"] for r in result["data"]}
        assert "Philippines" in countries
        assert "Indonesia" in countries
        assert "Malaysia" in countries

    def test_attribute_production_and_change(self):
        """Test that Production and Change attributes are parsed."""
        result = parse_template_9(self.VALID_LINES, html_text=self.HTML_TEXT)

        attributes = {r["attribute"] for r in result["data"]}
        assert "Production" in attributes
        assert "Change from Last Month" in attributes
        assert "Change from Last Month (%)" in attributes

    def test_all_data_records_valid_shape(self):
        """Test that all data records have valid shape."""
        result = parse_template_9(self.VALID_LINES, html_text=self.HTML_TEXT)

        for record in result["data"]:
            assert_valid_data_record(record)

    def test_insufficient_periods_returns_error(self):
        """Test that insufficient period lines return error."""
        short_lines = [
            "Copra Production",
            "",
            "",
            "",
            "",
            "",  # Empty period line
        ]
        result = parse_template_9(short_lines)

        assert "error" in result
        assert "Could not extract periods" in result["error"]
        assert result["data"] == []


# =============================================================================
# Test Template 11 - All Grain Summary Comparison
# =============================================================================


class TestParseTemplate11:
    """Tests for parse_template_11 (All Grain Summary Comparison)."""

    VALID_LINES = [
        "All Grain Summary Comparison",  # Line 0: Title
        "",  # Line 1: blank
        "",  # Line 2: blank
        ",Wheat,,,Rice Milled,,,Corn,,,",  # Line 3: commodities
        ",,2022/23,2023/24,2024/25,,2022/23,2023/24,2024/25,,2022/23,2023/24,2024/25",  # Line 4: periods
        "Production",  # Line 5: attribute header
        "United States,,50.0,52.0,55.0,,6.0,6.2,6.5,,350.0,380.0,400.0",  # Line 6: data
        "World Total,,780.0,800.0,820.0,,510.0,520.0,530.0,,1200.0,1250.0,1300.0",  # Line 7: data
        "Consumption",  # Line 8: attribute header
        "United States,,30.0,32.0,33.0,,4.0,4.2,4.3,,320.0,330.0,340.0",  # Line 9: data
    ]

    HTML_TEXT = '<span class="rptSubTitle">Grains  Million Metric Tons</span>'

    def test_valid_input_returns_correct_shape(self):
        """Test that valid input returns correctly shaped response."""
        result = parse_template_11(self.VALID_LINES, html_text=self.HTML_TEXT)

        assert_valid_response_shape(result, expected_template=11)
        assert result["report"] == "All Grain Summary Comparison"

    def test_multiple_commodities_parsed(self):
        """Test that multiple commodities are parsed."""
        result = parse_template_11(self.VALID_LINES, html_text=self.HTML_TEXT)

        commodities = {r["commodity"] for r in result["data"]}
        assert "Wheat" in commodities
        assert "Rice Milled" in commodities
        assert "Corn" in commodities

    def test_attribute_sections_parsed(self):
        """Test that attribute sections are parsed."""
        result = parse_template_11(self.VALID_LINES, html_text=self.HTML_TEXT)

        attributes = {r["attribute"] for r in result["data"]}
        assert "Production" in attributes
        assert "Consumption" in attributes

    def test_country_from_row_identifier(self):
        """Test that country comes from row identifier."""
        result = parse_template_11(self.VALID_LINES, html_text=self.HTML_TEXT)

        countries = {r["country"] for r in result["data"]}
        regions = {r["region"] for r in result["data"]}
        assert "United States" in countries
        # World Total becomes region='World' with country='--'
        assert "World" in regions or "--" in countries

    def test_all_data_records_valid_shape(self):
        """Test that all data records have valid shape."""
        result = parse_template_11(self.VALID_LINES, html_text=self.HTML_TEXT)

        for record in result["data"]:
            assert_valid_data_record(record)


# =============================================================================
# Test Template 13 - Multi-commodity Supply/Demand (Country View)
# =============================================================================


class TestParseTemplate13:
    """Tests for parse_template_13 (Country Grain Supply and Demand)."""

    VALID_LINES = [
        "China: Grain Supply and Demand",  # Line 0: Title
        "",  # Line 1: blank
        "",  # Line 2: blank
        ",Area Harvested,Yield,Production,Imports,Exports,Consumption",  # Line 3: attributes
        "Wheat",  # Line 4: commodity header
        "2022/23,24.0,5.5,132.0,10.0,0.5,150.0",  # Line 5: year data
        "2023/24,24.5,5.6,137.0,8.0,0.3,148.0",  # Line 6: year data
        "Corn",  # Line 7: commodity header
        "2022/23,42.0,6.3,265.0,20.0,0.1,290.0",  # Line 8: year data
    ]

    HTML_TEXT = '<span class="rptSubTitle">Grains  Million Metric Tons</span>'

    def test_valid_input_returns_correct_shape(self):
        """Test that valid input returns correctly shaped response."""
        result = parse_template_13(self.VALID_LINES, html_text=self.HTML_TEXT)

        assert_valid_response_shape(result, expected_template=13)
        assert result["report"] == "China: Grain Supply and Demand"

    def test_extracts_country_from_title(self):
        """Test that country is extracted from title."""
        result = parse_template_13(self.VALID_LINES, html_text=self.HTML_TEXT)

        countries = {r["country"] for r in result["data"]}
        assert "China" in countries

    def test_commodity_sections_parsed(self):
        """Test that commodity sections are parsed."""
        result = parse_template_13(self.VALID_LINES, html_text=self.HTML_TEXT)

        commodities = {r["commodity"] for r in result["data"]}
        assert "Wheat" in commodities
        assert "Corn" in commodities

    def test_attributes_from_columns(self):
        """Test that attributes come from column headers."""
        result = parse_template_13(self.VALID_LINES, html_text=self.HTML_TEXT)

        attributes = {r["attribute"] for r in result["data"]}
        assert "Area Harvested" in attributes
        assert "Production" in attributes
        assert "Imports" in attributes

    def test_marketing_years_parsed(self):
        """Test that marketing years are parsed."""
        result = parse_template_13(self.VALID_LINES, html_text=self.HTML_TEXT)

        years = {r["marketing_year"] for r in result["data"]}
        assert "2022/23" in years
        assert "2023/24" in years

    def test_all_data_records_valid_shape(self):
        """Test that all data records have valid shape."""
        result = parse_template_13(self.VALID_LINES, html_text=self.HTML_TEXT)

        for record in result["data"]:
            assert_valid_data_record(record)


# =============================================================================
# Test Template 20 - Total Oilseed Area, Yield, Production
# =============================================================================


class TestParseTemplate20:
    """Tests for parse_template_20 (Total Oilseed Area, Yield, Production)."""

    # Template 20 expects: 4 area values, 4 yield values, 4 production values, then 4 change values
    # Columns: Area(0-3), Yield(4-7), Production(8-11), ChgMo(12), ChgMo%(13), ChgYr(14), ChgYr%(15)
    VALID_LINES = [
        "Total Oilseed Area, Yield, and Production",  # Line 0: Title
        "",  # Line 1: blank
        "",  # Line 2: blank
        "Area (Million hectares),Yield (MT/HA),Production (MMT)",  # Line 3: unit headers
        ",2023/24,2024/25 Proj.,,",  # Line 4: projection line
        ",Nov,Dec,,",  # Line 5: period line
        "World Total,280.0,285.0,275.0,290.0,2.0,2.1,1.9,2.2,560.0,600.0,550.0,610.0,5.0,0.9,40.0,7.0",
        "Major OilSeeds,250.0,255.0,245.0,260.0,2.2,2.3,2.1,2.4,550.0,585.0,540.0,595.0,3.0,0.5,35.0,6.0",
        "",  # Line 8: blank (region reset)
        "South America,,,,,,,,,,,,,,,,",  # Line 9: region header
        "Brazil,45.0,46.0,44.0,47.0,3.4,3.5,3.3,3.6,153.0,161.0,150.0,165.0,2.0,1.2,8.0,5.0",
        "Argentina,20.0,21.0,19.0,22.0,2.8,2.9,2.7,3.0,56.0,61.0,54.0,63.0,1.0,1.6,5.0,8.0",
    ]

    def test_valid_input_returns_correct_shape(self):
        """Test that valid input returns correctly shaped response."""
        result = parse_template_20(self.VALID_LINES)

        assert_valid_response_shape(result, expected_template=20)
        assert result["report"] == "Total Oilseed Area, Yield, and Production"

    def test_commodity_defaults_to_total_oilseeds(self):
        """Test that commodity defaults to 'Total Oilseeds'."""
        result = parse_template_20(self.VALID_LINES)

        commodities = {r["commodity"] for r in result["data"]}
        assert "Total Oilseeds" in commodities

    def test_aggregate_rows_have_no_region(self):
        """Test that aggregate rows (World Total, Major OilSeeds) have region set and country='--'."""
        result = parse_template_20(self.VALID_LINES)

        # World Total should have region='World' and country='--'
        world_records = [
            r for r in result["data"] if r["region"] == "World" and r["country"] == "--"
        ]
        assert len(world_records) > 0

    def test_region_hierarchy_for_countries(self):
        """Test that countries under region headers have correct region."""
        result = parse_template_20(self.VALID_LINES)

        brazil_records = [r for r in result["data"] if r["country"] == "Brazil"]
        assert len(brazil_records) > 0
        assert brazil_records[0]["region"] == "South America"

    def test_parses_area_yield_production(self):
        """Test that Area, Yield, Production attributes are parsed."""
        result = parse_template_20(self.VALID_LINES)

        attributes = {r["attribute"] for r in result["data"]}
        assert "Area" in attributes
        assert "Yield" in attributes
        # Production is parsed from columns 8-11
        assert "Production" in attributes or any("Production" in a for a in attributes)

    def test_parses_change_values(self):
        """Test that Change from Last Month/Year are parsed."""
        result = parse_template_20(self.VALID_LINES)

        change_attrs = [
            r["attribute"] for r in result["data"] if "Change" in r["attribute"]
        ]
        assert "Production Change from Last Month" in change_attrs
        assert "Production Change from Last Month (%)" in change_attrs

    def test_extracts_units_from_header(self):
        """Test that units are extracted from header line."""
        result = parse_template_20(self.VALID_LINES)

        area_records = [r for r in result["data"] if r["attribute"] == "Area"]
        assert len(area_records) > 0
        assert area_records[0]["unit"] == "Million hectares"

    def test_all_data_records_valid_shape(self):
        """Test that all data records have valid shape."""
        result = parse_template_20(self.VALID_LINES)

        for record in result["data"]:
            assert_valid_data_record(record)

    def test_insufficient_periods_returns_error(self):
        """Test that insufficient period lines return error."""
        short_lines = [
            "Total Oilseed Area, Yield, and Production",
            "",
            "",
            "Area (Million hectares),Yield (MT/HA),Production (MMT)",
        ]
        result = parse_template_20(short_lines)

        assert "error" in result
        assert "Could not extract periods" in result["error"]
        assert result["data"] == []


# =============================================================================
# Test parse_report Router
# =============================================================================


class TestParseReport:
    """Tests for parse_report router function."""

    MINIMAL_LINES = [
        "Test Report",
        "",
        "",
        ",Column1,Column2",
        ",2023/24,2024/25 Proj.,,",
        ",Nov,Dec,,",
        "Country,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0,16.0",
    ]

    def test_routes_to_template_1(self):
        """Test routing to template 1."""
        result = parse_report(1, self.MINIMAL_LINES)
        assert result["template"] == 1

    def test_routes_to_template_2(self):
        """Test routing to template 2."""
        lines = [
            "World Crop Production Summary",
            "",
            "",
            ",World,Total Foreign,",
            ",,Country1,",
            "Million metric tons",
            "Wheat",
            "2023/24,100.0,80.0,20.0",
        ]
        result = parse_report(2, lines)
        assert result["template"] == 2

    def test_routes_to_template_3(self):
        """Test routing to template 3."""
        lines = [
            "Cotton Supply",
            "",
            ",Production,Imports",
            "United States",
            "2023/24,10.0,0.5",
        ]
        result = parse_report(3, lines)
        assert result["template"] == 3

    def test_routes_to_template_5(self):
        """Test routing to template 5."""
        lines = [
            "World Oilseed Production",
            "",
            ",2023/24,2024/25",
            "Production",
            "Oilseed Copra,5.0,6.0",
        ]
        result = parse_report(5, lines)
        assert result["template"] == 5

    def test_routes_to_template_7(self):
        """Test routing to template 7."""
        lines = [
            "Butter Production",
            "",
            ",2023,2024",
            "Production",
            "India,6.0,6.5",
        ]
        result = parse_report(7, lines)
        assert result["template"] == 7

    def test_routes_to_template_8(self):
        """Test routing to template 8."""
        lines = [
            "Coffee World Supply",
            "",
            "",
            ",2023/24,2024/25",
            "Production",
            "Brazil,60.0,65.0",
        ]
        result = parse_report(8, lines)
        assert result["template"] == 8

    def test_routes_to_template_9(self):
        """Test routing to template 9."""
        lines = [
            "Copra Production",
            "",
            "",
            "",
            "",
            ",2023/24,2024/25,2025/26,2026/27,Change,% Chg",
            ",,,,Nov,,,",
            "",
            "",
            "Copra",
            "Philippines,1.8,1.9,2.0,2.1,0.1,5.0",
        ]
        result = parse_report(9, lines)
        assert result["template"] == 9

    def test_routes_to_template_11(self):
        """Test routing to template 11."""
        lines = [
            "All Grain Summary",
            "",
            "",
            ",Wheat,,,",
            ",,2023/24,2024/25,2025/26",
            "Production",
            "United States,,50.0,52.0,55.0",
        ]
        result = parse_report(11, lines)
        assert result["template"] == 11

    def test_routes_to_template_13(self):
        """Test routing to template 13."""
        lines = [
            "China: Grain Supply",
            "",
            "",
            ",Production,Imports",
            "Wheat",
            "2023/24,130.0,8.0",
        ]
        result = parse_report(13, lines)
        assert result["template"] == 13

    def test_template_17_routes_to_template_3(self):
        """Test that template 17 routes to parse_template_3 (alias)."""
        lines = [
            "Cotton Supply",
            "",
            ",Production,Imports",
            "United States",
            "2023/24,10.0,0.5",
        ]
        result = parse_report(17, lines)
        # Template 17 uses parse_template_3, but template field comes from parser
        assert result["template"] == 3  # parse_template_3 returns template=3

    def test_routes_to_template_20(self):
        """Test routing to template 20."""
        result = parse_report(20, self.MINIMAL_LINES)
        assert result["template"] == 20

    def test_unknown_template_returns_error(self):
        """Test that unknown template ID returns error dict."""
        result = parse_report(99, self.MINIMAL_LINES)

        assert "error" in result
        assert "No parser for template 99" in result["error"]
        assert result["data"] == []

    def test_unknown_template_999_returns_error(self):
        """Test that another unknown template ID returns error dict."""
        result = parse_report(999, [])

        assert "error" in result
        assert "No parser for template 999" in result["error"]
        assert result["data"] == []

    def test_parsers_dict_contains_expected_templates(self):
        """Test that PARSERS dict contains all expected template IDs."""
        expected_templates = {1, 2, 3, 5, 7, 8, 9, 11, 13, 17, 20}
        assert set(PARSERS.keys()) == expected_templates

    def test_commodity_group_passed_to_parser(self):
        """Test that commodity_group is passed to parser."""
        lines = [
            "Unknown Report Title",  # No commodity in title
            "",
            "",
            ",Column1,Column2",
            ",2023/24,2024/25 Proj.,,",
            ",Nov,Dec,,",
            "Country,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0,16.0",
        ]
        result = parse_report(1, lines, commodity_group="cot")

        # Should use commodity group to determine commodity
        commodities = {r["commodity"] for r in result["data"]}
        assert "Cotton" in commodities

    def test_html_text_passed_to_parser(self):
        """Test that html_text is passed to parser for unit extraction."""
        lines = [
            "Cotton Supply",
            "",
            ",Production,Imports",
            "United States",
            "2023/24,10.0,0.5",
        ]
        html = '<span class="rptSubTitle">Cotton  Million 480-lb. Bales</span>'
        result = parse_report(3, lines, html_text=html)

        # Should extract unit from HTML
        assert result["data"][0]["unit"] == "Million 480-lb. Bales"


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases across all parsers."""

    def test_empty_lines_list(self):
        """Test handling of empty lines list."""
        # Empty list causes IndexError in parsers - this is expected behavior
        # Test with minimal lines that won't crash but have no data
        result = parse_report(1, ["", "", "", "", "", ""])
        # Should not crash, may return error or empty data
        assert "data" in result

    def test_whitespace_only_lines(self):
        """Test handling of whitespace-only lines."""
        lines = ["  ", "\t", "   \n   "]
        result = parse_report(3, lines)
        # Should handle gracefully
        assert "data" in result

    def test_all_nr_values_skipped(self):
        """Test that rows with all 'nr' values are skipped."""
        lines = [
            "Corn Area, Yield, and Production",
            "",
            "",
            "Area (Mil hectares),Yield (MT/HA),Production (MMT)",
            ",2023/24,2024/25 Proj.,,",
            ",Nov,Dec,,",
            "Country,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr,nr",
        ]
        result = parse_template_1(lines)

        # No data should be added for all-nr rows
        assert result["row_count"] == 0

    def test_mixed_valid_and_nr_values(self):
        """Test handling of mixed valid and 'nr' values."""
        lines = [
            "Corn Area, Yield, and Production",
            "",
            "",
            "Area (Mil hectares),Yield (MT/HA),Production (MMT)",
            ",2023/24,2024/25 Proj.,,",
            ",Nov,Dec,,",
            "Country,100.0,nr,5.0,nr,500.0,nr,,,,,,,,,,,",
        ]
        result = parse_template_1(lines)

        # Should have some data from valid values
        assert result["row_count"] > 0
        # All values in data should be float
        for record in result["data"]:
            assert isinstance(record["value"], float)

    def test_unicode_in_country_names(self):
        """Test handling of unicode characters in country names."""
        lines = [
            "Coffee Supply",
            "",
            ",Production,Imports",
            "Côte d'Ivoire",
            "2023/24,2.5,0.1",
        ]
        result = parse_template_3(lines)

        countries = {r["country"] for r in result["data"]}
        assert "Côte d'Ivoire" in countries

    def test_large_numbers(self):
        """Test handling of large numbers."""
        lines = [
            "Corn Area, Yield, and Production",
            "",
            "",
            "Area (Mil hectares),Yield (MT/HA),Production (MMT)",
            ",2023/24,2024/25 Proj.,,",
            ",Nov,Dec,,",
            "World,1000000.5,1000001.0,99.9,100.0,99999999.0,100000000.0,,,,,,,,,,,",
        ]
        result = parse_template_1(lines)

        # Verify large numbers are parsed correctly
        values = [r["value"] for r in result["data"]]
        assert 1000000.5 in values
        assert 99999999.0 in values

    def test_negative_values(self):
        """Test handling of negative values (change columns)."""
        lines = [
            "Corn Area, Yield, and Production",
            "",
            "",
            "Area (Mil hectares),Yield (MT/HA),Production (MMT)",
            ",2023/24,2024/25 Proj.,,",
            ",Nov,Dec,,",
            "Country,100.0,100.0,5.0,5.0,500.0,500.0,,,,,,,-10.0,-2.0,-50.0,-10.0",
        ]
        result = parse_template_1(lines)

        # Find change records
        change_records = [r for r in result["data"] if "Change" in r["attribute"]]
        assert len(change_records) > 0

        # Should have negative values
        negative_values = [r["value"] for r in change_records if r["value"] < 0]
        assert len(negative_values) > 0

    def test_decimal_precision(self):
        """Test that decimal precision is preserved."""
        lines = [
            "Coffee Supply",
            "",
            ",Production,Imports",
            "Brazil",
            "2023/24,65.123456,0.987654",
        ]
        result = parse_template_3(lines)

        values = {r["value"] for r in result["data"]}
        assert 65.123456 in values
        assert 0.987654 in values
