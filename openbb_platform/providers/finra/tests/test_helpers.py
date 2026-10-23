"""Tests for the value parsing helpers."""

from datetime import date, datetime

import pytest

from openbb_finra.utils.helpers import (
    clean,
    decode,
    drop_none,
    first,
    market_names,
    normalize_trace_record,
    split_symbols,
    to_bool,
    to_date,
    to_float,
)


class TestClean:
    """Blank and not-available values become None."""

    @pytest.mark.parametrize("value", [None, "", "  ", "-", "NA", "n/a"])
    def test_blank_values(self, value):
        """Blank tokens clean to None."""
        assert clean(value) is None

    def test_text_is_stripped(self):
        """Text keeps its content without padding."""
        assert clean("  APPLE INC ") == "APPLE INC"

    def test_numbers_become_text(self):
        """Numbers are returned as text."""
        assert clean(5231623) == "5231623"


class TestToFloat:
    """Numbers are parsed without being reformatted."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (3, 3.0),
            (4.375, 4.375),
            ("4.3750000000000000000", 4.375),
            ("1,234.5", 1234.5),
            ("0E-19", 0.0),
        ],
    )
    def test_numbers(self, value, expected):
        """Numbers and numeric text parse to floats."""
        assert to_float(value) == expected

    @pytest.mark.parametrize("value", [None, True, "", "NA", "abc"])
    def test_non_numbers(self, value):
        """Booleans, blanks, and text are not numbers."""
        assert to_float(value) is None


class TestToBool:
    """Flags parse from their textual forms."""

    @pytest.mark.parametrize("value", [True, "Y", "yes", "TRUE", "1"])
    def test_true(self, value):
        """True forms parse to True."""
        assert to_bool(value) is True

    @pytest.mark.parametrize("value", [False, "N", "no", "false", "0"])
    def test_false(self, value):
        """False forms parse to False."""
        assert to_bool(value) is False

    @pytest.mark.parametrize("value", [None, "", "maybe"])
    def test_unknown(self, value):
        """Anything else is unknown."""
        assert to_bool(value) is None


class TestToDate:
    """Dates are returned as ISO strings."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (date(2026, 9, 22), "2026-09-22"),
            (datetime(2026, 9, 22, 17, 29), "2026-09-22"),
            ("2028-06-05 00:00:00", "2028-06-05"),
            ("19801212", "1980-12-12"),
            ("09-22-2026", "2026-09-22"),
            ("09/22/2026 12:00:00", "2026-09-22"),
        ],
    )
    def test_dates(self, value, expected):
        """Every supported form parses."""
        assert to_date(value) == expected

    @pytest.mark.parametrize("value", [None, "", "not a date", "2026"])
    def test_non_dates(self, value):
        """Anything else is not a date."""
        assert to_date(value) is None


class TestFirst:
    """The first populated value wins."""

    def test_skips_blanks(self):
        """None and blank tokens are skipped."""
        assert first(None, "", "-", "AAPL", "MSFT") == "AAPL"

    def test_all_blank(self):
        """Nothing populated returns None."""
        assert first(None, "NA") is None


class TestSplitSymbols:
    """Comma-separated symbols are split, upper-cased, and deduplicated."""

    def test_split(self):
        """Blanks and repeats are dropped and order is kept."""
        assert split_symbols(" aapl, msft,,AAPL ,brk.b") == ["AAPL", "MSFT", "BRK.B"]


class TestDropNone:
    """Only populated keys are kept."""

    def test_drop(self):
        """None values are removed, falsy values kept."""
        assert drop_none({"a": None, "b": 0, "c": False, "d": ""}) == {
            "b": 0,
            "c": False,
            "d": "",
        }


class TestDecode:
    """Codes are replaced by their published descriptions."""

    def test_known_code(self):
        """A known code is described, whatever its case."""
        assert decode({"ST": "Stock"}, " st ") == "Stock"

    def test_unknown_code(self):
        """An unknown code is kept."""
        assert decode({"ST": "Stock"}, "ZZ") == "ZZ"

    def test_blank(self):
        """A blank value stays empty."""
        assert decode({"ST": "Stock"}, None) is None

    def test_market_names(self):
        """The bundled exchange names cover the listing markets."""
        names = market_names()

        assert names["19"] == "NASDAQ"
        assert names["14"] == "NYSE"


class TestNormalizeTraceRecord:
    """TRACE records are typed and decoded."""

    def test_types_and_decodes(self):
        """Numbers, flags, dates, and codes are parsed."""
        record = normalize_trace_record(
            {
                "couponRate": "1.4000000000000000000",
                "couponType": "FXPV",
                "industryGroup": "TRON",
                "traceGradeCode": "I",
                "isCallable": "Y",
                "is144A": "N",
                "nextCallDate": "2028-06-05 00:00:00",
                "issuerName": " APPLE INC ",
                "cusip": "037833EH9",
                "finraSecurityIdentifier": 5231623,
                "moodysRating": None,
            },
            "CA",
        )

        assert record == {
            "couponRate": 1.4,
            "couponType": "Fixed Plain Vanilla",
            "industryGroup": "Electronics",
            "traceGradeCode": "Investment Grade",
            "isCallable": True,
            "is144A": False,
            "nextCallDate": "2028-06-05",
            "issuerName": "APPLE INC",
            "cusip": "037833EH9",
            "finraSecurityIdentifier": "5231623",
        }

    def test_every_code_field_is_translated(self):
        """Structured-product and Treasury codes use FINRA's published tables."""
        assert normalize_trace_record(
            {
                "productSubTypeCode": "CMO",
                "subProductType": "HOME",
                "interestType": "PO",
                "mortgageProduct": "M",
                "amortizationType": "L",
                "settlementDateMonth": 12,
                "priceType": "D",
                "productType": "SP",
                "couponType": "FLT",
            },
            "CMO",
        ) == {
            "productSubTypeCode": "Collateralized Mortgage Obligation",
            "subProductType": "Home Equity Loans",
            "interestType": "Principal Only",
            "mortgageProduct": "Multi-Family",
            "amortizationType": "Level Pay",
            "settlementDateMonth": "December",
            "priceType": "Decimal",
            "productType": "Securitized Products",
            "couponType": "Floater",
        }

    def test_unknown_codes_pass_through(self):
        """Codes FINRA does not publish a decode for are kept as given."""
        record = normalize_trace_record(
            {"couponType": "OTH", "industryGroup": "ELHI", "traceGradeCode": "X"},
            "CA",
        )

        assert record == {
            "couponType": "OTH",
            "industryGroup": "ELHI",
            "traceGradeCode": "X",
        }

    def test_coupon_type_without_bond_type(self):
        """Without a bond type the coupon code is kept."""
        assert normalize_trace_record({"couponType": "FIX"}) == {"couponType": "FIX"}

    def test_structured_and_tba_coupon_types(self):
        """Each product decodes against its own table."""
        assert normalize_trace_record({"couponType": "FIX"}, "CMO") == {
            "couponType": "Fixed"
        }
        assert normalize_trace_record({"couponType": "L"}, "TBA") == {
            "couponType": "Level Pay"
        }

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("PERPETUAL", True),
            ("NOT PERPETUAL", False),
            ("Y", True),
            ("N", False),
        ],
    )
    def test_perpetual_flags(self, value, expected):
        """Both perpetual flag conventions parse."""
        assert normalize_trace_record({"isPerpetual": value}) == {
            "isPerpetual": expected
        }

    def test_unknown_perpetual_flag(self):
        """An unrecognised perpetual flag is dropped."""
        assert normalize_trace_record({"isPerpetual": "SOMETIMES"}) == {}

    def test_null_perpetual_flag(self):
        """A null perpetual flag is dropped."""
        assert normalize_trace_record({"isPerpetual": None}) == {}
