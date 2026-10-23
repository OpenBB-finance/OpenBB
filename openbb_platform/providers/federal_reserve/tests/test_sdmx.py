"""Tests for the DDP SDMX-ML parser."""

from pathlib import Path

from openbb_federal_reserve.utils import sdmx

FIXTURES = Path(__file__).parent / "fixtures"


def _doc(series_body: str) -> str:
    """Wrap a series fragment in a minimal SDMX message document."""
    return f"<MessageGroup><DataSet>{series_body}</DataSet></MessageGroup>"


class TestParseSeries:
    """Tests for ``parse_series`` across real and synthetic payloads."""

    def test_parses_h15_rates_fixture(self):
        """The H.15 fixture yields daily rate series with maturity dimensions."""
        xml = (FIXTURES / "ddp_h15.sdmx.xml").read_text(encoding="utf-8")
        series = sdmx.parse_series(xml)
        assert series
        first = series[0]
        assert first["series_id"]
        # parse_series keeps the raw FREQ code (9 = "Business day"); to_rows
        # resolves it to the label via the structure codelist.
        assert first["frequency"] == "9"
        assert "maturity" in first["dimensions"]
        assert "instrument" in first["dimensions"]
        assert first["title"]

    def test_parses_h6_money_fixture(self):
        """The H.6 fixture yields monthly money series with an adjusted dimension."""
        xml = (FIXTURES / "ddp_h6.sdmx.xml").read_text(encoding="utf-8")
        series = sdmx.parse_series(xml)
        assert series
        first = series[0]
        assert first["frequency"] == "129"  # raw FREQ code (129 = Monthly)
        assert "adjusted" in first["dimensions"]
        assert first["unit_multiplier"]
        assert first["currency"] == "USD"

    def test_annotation_descriptions_are_captured(self):
        """Short/long descriptions populate title and description."""
        body = (
            '<Series SERIES_NAME="X" FREQ="9">'
            "<Annotations>"
            "<Annotation><AnnotationType>Short Description</AnnotationType>"
            "<AnnotationText>Short</AnnotationText></Annotation>"
            "<Annotation><AnnotationType>Long Description</AnnotationType>"
            "<AnnotationText>Long</AnnotationText></Annotation>"
            "</Annotations>"
            '<Obs OBS_STATUS="A" OBS_VALUE="1.5" TIME_PERIOD="2024-01-01"/>'
            "</Series>"
        )
        series = sdmx.parse_series(_doc(body))
        assert series[0]["title"] == "Short"
        assert series[0]["description"] == "Long"

    def test_missing_value_sentinel_becomes_none(self):
        """An ``ND`` observation with the ``-9999`` sentinel maps to ``None``."""
        body = (
            '<Series SERIES_NAME="X" FREQ="9">'
            '<Obs OBS_STATUS="ND" OBS_VALUE="-9999" TIME_PERIOD="2024-01-01"/></Series>'
        )
        series = sdmx.parse_series(_doc(body))
        assert series[0]["observations"][0]["value"] is None

    def test_non_numeric_value_becomes_none(self):
        """A non-numeric observation value is coerced to ``None``."""
        body = (
            '<Series SERIES_NAME="X" FREQ="9">'
            '<Obs OBS_STATUS="A" OBS_VALUE="N/A" TIME_PERIOD="2024-01-01"/></Series>'
        )
        series = sdmx.parse_series(_doc(body))
        assert series[0]["observations"][0]["value"] is None

    def test_series_without_name_is_skipped(self):
        """A series lacking ``SERIES_NAME`` is dropped."""
        body = '<Series FREQ="9"><Obs OBS_VALUE="1" TIME_PERIOD="2024-01-01"/></Series>'
        assert sdmx.parse_series(_doc(body)) == []

    def test_unknown_frequency_passes_through(self):
        """An unmapped frequency code is returned unchanged."""
        body = (
            '<Series SERIES_NAME="X" FREQ="999">'
            '<Obs OBS_STATUS="A" OBS_VALUE="1" TIME_PERIOD="2024-01-01"/></Series>'
        )
        assert sdmx.parse_series(_doc(body))[0]["frequency"] == "999"

    def test_empty_input_yields_no_series(self):
        """Empty or whitespace-only input parses to no series."""
        assert sdmx.parse_series("") == []
        assert sdmx.parse_series("   ") == []

    def test_falls_back_to_series_id_without_annotations(self):
        """Without annotations the title falls back to the series id."""
        body = (
            '<Series SERIES_NAME="X" FREQ="9">'
            '<Obs OBS_STATUS="A" OBS_VALUE="1" TIME_PERIOD="2024-01-01"/></Series>'
        )
        series = sdmx.parse_series(_doc(body))
        assert series[0]["title"] == "X"
        assert series[0]["description"] == ""


_STRUCTURE = (
    "<Structure>"
    "<CodeLists>"
    '<CodeList id="CL_LOANTYPE"><Name>Loan type</Name>'
    '<Code value="CI"><Description>Commercial and industrial loans</Description></Code>'
    '<Code value="CONCC"><Description>Consumer credit card loans</Description></Code>'
    "</CodeList>"
    '<CodeList id="CL_SA">'
    '<Code value="SA"><Description>Seasonally adjusted</Description></Code>'
    '<Code value="NSA"><Description>Not seasonally adjusted</Description></Code>'
    "</CodeList>"
    "</CodeLists>"
    "<KeyFamily><Components>"
    '<Dimension concept="LOANTYPE" codelist="CL_LOANTYPE"/>'
    '<Dimension concept="SA" codelist="CL_SA"/>'
    '<Attribute concept="SERIES_NAME"/>'
    "</Components></KeyFamily>"
    "</Structure>"
)


class TestParseStructure:
    """Tests for ``parse_structure`` codelist resolution."""

    def test_resolves_dimension_codelists(self):
        """Each dimension maps its codes to the codelist descriptions."""
        result = sdmx.parse_structure(_STRUCTURE)
        assert result["loantype"]["CI"] == "Commercial and industrial loans"
        assert result["loantype"]["CONCC"] == "Consumer credit card loans"
        assert result["sa"]["NSA"] == "Not seasonally adjusted"
        # An attribute with no codelist is omitted.
        assert "series_name" not in result

    def test_strips_utf8_bom(self):
        """A leading UTF-8 BOM does not break parsing."""
        assert sdmx.parse_structure("﻿" + _STRUCTURE)["loantype"]["CI"]

    def test_malformed_returns_empty(self):
        """Empty or non-XML input yields an empty mapping."""
        assert sdmx.parse_structure("") == {}
        assert sdmx.parse_structure("not xml <") == {}


class TestSeasonalFlag:
    """Tests for the seasonal-adjustment code mapping."""

    def test_flags(self):
        """Bare and suffixed seasonal codes map to the right boolean."""
        assert sdmx._seasonal_flag("SA") is True
        assert sdmx._seasonal_flag("SAAR") is True
        assert sdmx._seasonal_flag("SA_BA") is True
        assert sdmx._seasonal_flag("NSA") is False
        assert sdmx._seasonal_flag("NSA_NBA") is False
        assert sdmx._seasonal_flag("BA") is None
        assert sdmx._seasonal_flag("CI") is None


_UNIT_STRUCTURE = (
    "<Structure><CodeLists>"
    '<CodeList id="CL_UNIT">'
    '<Code value="Currency"><Description>Currency</Description></Code>'
    '<Code value="Percent:_Per_Year">'
    "<Description>Percent: Per Year</Description></Code>"
    '<Code value="Index"><Description>Index</Description></Code>'
    '<Code value="Index:_2017_100">'
    "<Description>Index: 2017 = 100</Description></Code>"
    '<Code value="Percentage"><Description>Percentage</Description></Code>'
    '<Code value="Number"><Description>Number</Description></Code>'
    '<Code value="Currency:_Base_2017">'
    "<Description>Currency: Base = 2017</Description></Code>"
    "</CodeList>"
    '<CodeList id="CL_UNIT_MULT">'
    '<Code value="1"><Description>One</Description></Code>'
    '<Code value="1000"><Description>Thousands</Description></Code>'
    '<Code value="1000000"><Description>Millions</Description></Code>'
    '<Code value="1000000000"><Description>Billions</Description></Code>'
    '<Code value="1000000000000"><Description>Trillions</Description></Code>'
    "</CodeList>"
    '<CodeList id="CL_CURRENCY">'
    '<Code value="NA"><Description>Not Applicable</Description></Code>'
    '<Code value="USD">'
    "<Description>United States / United States Dollar</Description></Code>"
    '<Code value="EUR">'
    "<Description>Euro Area / Euro (replacement name for the ECU)</Description>"
    "</Code>"
    "</CodeList>"
    "</CodeLists><KeyFamily><Components>"
    '<Attribute concept="UNIT" codelist="CL_UNIT"/>'
    '<Attribute concept="UNIT_MULT" codelist="CL_UNIT_MULT"/>'
    '<Attribute concept="CURRENCY" codelist="CL_CURRENCY"/>'
    "</Components></KeyFamily></Structure>"
)

_UNIT_CODELISTS = sdmx.parse_structure(_UNIT_STRUCTURE)


class TestToRows:
    """Tests for ``to_rows`` flattening and label resolution."""

    def _series(self, dimensions, unit="u", unit_multiplier=None, currency=None):
        """Build a one-observation series with the given dimensions and units."""
        return [
            {
                "series_id": "X",
                "title": "t",
                "frequency": "daily",
                "unit": unit,
                "unit_multiplier": unit_multiplier,
                "currency": currency,
                "dimensions": dimensions,
                "observations": [{"date": "2024-01-01", "value": 1.0, "status": "A"}],
            }
        ]

    def test_resolves_labels_and_collapses_seasonal(self):
        """Codes resolve to labels; a purely-seasonal dimension becomes the boolean."""
        codelists = sdmx.parse_structure(_STRUCTURE)
        rows = sdmx.to_rows(self._series({"loantype": "CI", "sa": "NSA"}), codelists)
        assert rows == [
            {
                "date": "2024-01-01",
                "series_id": "X",
                "value": 1.0,
                "title": "t",
                "frequency": "daily",
                "unit": "u",
                "unit_multiplier": None,
                "loantype": "Commercial and industrial loans",
                "seasonally_adjusted": False,
            }
        ]

    def test_unknown_codes_pass_through(self):
        """Without codelists, codes pass through and the boolean is None."""
        rows = sdmx.to_rows(self._series({"maturity": "M1"}))
        assert rows[0]["maturity"] == "M1"
        assert rows[0]["seasonally_adjusted"] is None

    def test_empty_series_yield_no_rows(self):
        """A series with no observations contributes no rows."""
        series = [
            {
                "series_id": "X",
                "title": "t",
                "frequency": "daily",
                "unit": "u",
                "unit_multiplier": None,
                "currency": None,
                "dimensions": {},
                "observations": [],
            }
        ]
        assert sdmx.to_rows(series) == []

    def test_currency_millions_label(self):
        """A ``Currency`` unit with a millions factor reads ``Millions of Dollars``."""
        rows = sdmx.to_rows(
            self._series(
                {}, unit="Currency", unit_multiplier="1000000", currency="USD"
            ),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Millions of Dollars"
        assert rows[0]["unit_multiplier"] == "Millions"

    def test_currency_billions_float_factor_label(self):
        """A billions factor in float form (``1e+09``) resolves to ``Billions``."""
        rows = sdmx.to_rows(
            self._series({}, unit="Currency", unit_multiplier="1e+09", currency="USD"),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Billions of Dollars"
        assert rows[0]["unit_multiplier"] == "Billions"

    def test_currency_without_scale_reads_bare_noun(self):
        """A ``Currency`` unit with a unit factor drops the scale word."""
        rows = sdmx.to_rows(
            self._series({}, unit="Currency", unit_multiplier="1", currency="USD"),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Dollars"
        assert rows[0]["unit_multiplier"] is None

    def test_non_usd_currency_pluralizes(self):
        """A non-dollar currency pluralizes its final word."""
        rows = sdmx.to_rows(
            self._series({}, unit="Currency", unit_multiplier="1000", currency="EUR"),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Thousands of Euros"

    def test_currency_unknown_code_falls_back_to_dollars(self):
        """A ``Currency`` unit with no resolvable currency assumes ``Dollars``."""
        rows = sdmx.to_rows(
            self._series({}, unit="Currency", unit_multiplier="1", currency="NA"),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Dollars"

    def test_real_dollar_unit_keeps_base_note(self):
        """A ``Currency: Base = YYYY`` real-dollar unit reads with a base note."""
        rows = sdmx.to_rows(
            self._series(
                {}, unit="Currency:_Base_2017", unit_multiplier="1e+09", currency="USD"
            ),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Billions of Dollars (2017 base)"

    def test_percent_unit_reads_as_label(self):
        """A percent rate unit resolves to its label with no scale word."""
        rows = sdmx.to_rows(
            self._series(
                {}, unit="Percent:_Per_Year", unit_multiplier="1", currency="NA"
            ),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Percent: Per Year"
        assert rows[0]["unit_multiplier"] is None

    def test_index_unit_drops_bogus_scale(self):
        """An index is normalized, so a stray scale factor is dropped."""
        rows = sdmx.to_rows(
            self._series(
                {}, unit="Index:_2017_100", unit_multiplier="1000", currency="NA"
            ),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Index: 2017 = 100"

    def test_percent_unit_drops_bogus_scale(self):
        """A Z.1 rate carrying a millions factor still reads as ``Percent``."""
        rows = sdmx.to_rows(
            self._series(
                {}, unit="Percentage", unit_multiplier="1000000", currency="USD"
            ),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Percentage"

    def test_count_unit_keeps_scale_without_noun(self):
        """A bare count keeps the scale word but drops the ``of Number`` noun."""
        rows = sdmx.to_rows(
            self._series({}, unit="Number", unit_multiplier="1000000", currency="NA"),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Millions"

    def test_count_unit_without_scale_keeps_label(self):
        """A bare count with no scale keeps its resolved label."""
        rows = sdmx.to_rows(
            self._series({}, unit="Number", unit_multiplier="1", currency="NA"),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Number"

    def test_unknown_scalable_unit_prefixes_scale(self):
        """An unrecognized non-normalized unit keeps the ``<scale> of <unit>`` form."""
        rows = sdmx.to_rows(
            self._series({}, unit="u", unit_multiplier="1000", currency="NA"),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Thousands of u"

    def test_missing_unit_with_scale(self):
        """An absent unit code keeps just the scale word as the label."""
        rows = sdmx.to_rows(
            self._series({}, unit=None, unit_multiplier="1000000", currency="NA"),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] == "Millions"

    def test_missing_unit_without_scale(self):
        """An absent unit and no scale yields a None unit label."""
        rows = sdmx.to_rows(
            self._series({}, unit=None, unit_multiplier="1", currency="NA"),
            _UNIT_CODELISTS,
        )
        assert rows[0]["unit"] is None


class TestUnitHelpers:
    """Tests for the unit-label helper functions."""

    def test_scale_word_resolves_and_normalizes(self):
        """Integer and float factors resolve to their scale word."""
        labels = _UNIT_CODELISTS["unit_mult"]
        assert sdmx._scale_word("1000000", labels) == "Millions"
        assert sdmx._scale_word("1e+09", labels) == "Billions"

    def test_scale_word_no_scale_returns_none(self):
        """A unit factor, an empty factor, or an unknown factor carries no scale."""
        labels = _UNIT_CODELISTS["unit_mult"]
        assert sdmx._scale_word("1", labels) is None
        assert sdmx._scale_word(None, labels) is None
        assert sdmx._scale_word("", labels) is None
        assert sdmx._scale_word("7", labels) is None

    def test_scale_word_non_numeric_factor(self):
        """A non-numeric factor string is looked up verbatim."""
        labels = {"Some": "Scaled"}
        assert sdmx._scale_word("Some", labels) == "Scaled"

    def test_currency_noun(self):
        """Currency labels reduce to their plural noun."""
        assert sdmx._currency_noun("United States / United States Dollar") == "Dollars"
        assert (
            sdmx._currency_noun("Euro Area / Euro (replacement name for the ECU)")
            == "Euros"
        )
        assert sdmx._currency_noun("United Kingdom / Pounds") == "Pounds"
        assert sdmx._currency_noun("Not Applicable") is None
        assert sdmx._currency_noun(None) is None
        assert sdmx._currency_noun(" / ") is None
