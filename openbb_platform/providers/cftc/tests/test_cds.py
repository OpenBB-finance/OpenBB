from datetime import date

from openbb_cftc.utils.cds import (
    curate_print,
    extract_prints,
    is_index_print,
    tenor_at_execution,
)

DISSEM = date(2026, 7, 15)


def _print(
    fisn="NA/CDS Corp Idx",
    index="CDX.NA.IG",
    executed="2026-07-15T13:00:00",
    maturity="2031-06-20",
    notional="10,000,000",
):
    return {
        "UPI FISN": fisn,
        "UPI Underlier Name": index,
        "Execution Timestamp": executed,
        "Expiration Date": maturity,
        "Notional amount-Leg 1": notional,
    }


def test_tenor_at_execution_snaps_to_the_standard_grid():
    assert tenor_at_execution(date(2031, 6, 20), date(2026, 7, 15)) == "5Y"
    assert tenor_at_execution(date(2030, 12, 20), date(2026, 7, 15)) == "5Y"
    assert tenor_at_execution(date(2036, 6, 20), date(2026, 7, 15)) == "10Y"
    assert tenor_at_execution(date(2028, 12, 20), date(2026, 7, 15)) == "2Y"
    assert tenor_at_execution(date(2027, 6, 20), date(2026, 7, 15)) == "1Y"


def test_tenor_at_execution_keeps_long_dated_maturities_off_the_grid():
    assert tenor_at_execution(date(2057, 12, 17), date(2026, 7, 15)) == "31Y"
    assert tenor_at_execution(date(2065, 4, 17), date(2026, 7, 15)) == "39Y"


def test_tenor_at_execution_rejects_a_maturity_at_or_before_execution():
    assert tenor_at_execution(date(2026, 7, 15), date(2026, 7, 15)) is None
    assert tenor_at_execution(date(2026, 7, 1), date(2026, 7, 15)) is None


def test_is_index_print_admits_only_the_index_fisns():
    assert is_index_print(_print()) is True
    assert is_index_print(_print(fisn="NA/CDS Corp Idx Tra")) is True
    assert is_index_print(_print(fisn="NA/CDS Sov Idx")) is True

    assert is_index_print(_print(fisn="NA/CDS Corp SN")) is False
    assert is_index_print(_print(fisn="NA/CDS Idx Swt")) is False
    assert is_index_print({}) is False


def test_curate_print_adds_the_dissemination_date_and_tenor():
    row = curate_print(_print(), DISSEM)

    assert row["dissemination_date"] == DISSEM
    assert row["tenor"] == "5Y"
    assert row["UPI Underlier Name"] == "CDX.NA.IG"


def test_curate_print_needs_both_dates():
    assert curate_print(_print(maturity=""), DISSEM) is None
    assert curate_print(_print(executed=""), DISSEM) is None


def test_extract_prints_filters_by_index_exactly():
    records = [
        _print(index="ITRAXX EUROPE"),
        _print(index="ITRAXX EUROPE CROSSOVER"),
        _print(index="ITRAXX EUROPE SENIOR FINANCIALS"),
    ]
    rows = extract_prints(records, DISSEM, index="itraxx europe")

    assert [r["UPI Underlier Name"] for r in rows] == ["ITRAXX EUROPE"]


def test_extract_prints_filters_by_tenor_and_notional_and_limit():
    records = [
        _print(maturity="2031-06-20", notional="10,000,000"),
        _print(maturity="2036-06-20", notional="10,000,000"),
        _print(maturity="2031-06-20", notional="1,000"),
    ]

    assert len(extract_prints(records, DISSEM, tenor="5y")) == 2
    assert len(extract_prints(records, DISSEM, tenor="10Y")) == 1
    assert len(extract_prints(records, DISSEM, min_notional=1_000_000)) == 2
    assert len(extract_prints(records, DISSEM, limit=1)) == 1


def test_extract_prints_drops_a_print_without_a_readable_notional():
    records = [_print(notional=""), _print(notional="not a number")]

    assert extract_prints(records, DISSEM, min_notional=0) == []
    assert len(extract_prints(records, DISSEM)) == 2


def test_extract_prints_skips_records_it_cannot_date():
    records = [_print(), _print(maturity="")]
    rows = extract_prints(records, DISSEM)

    assert len(rows) == 1


def test_extract_prints_keeps_a_tenorless_print_but_no_tenor_filter_matches_it():
    records = [_print(executed="2031-06-20T13:00:00", maturity="2031-06-20")]
    rows = extract_prints(records, DISSEM)

    assert len(rows) == 1
    assert rows[0]["tenor"] is None
    assert extract_prints(records, DISSEM, tenor="5Y") == []


def test_extract_prints_over_the_real_slice(credits_records):
    rows = extract_prints(credits_records, DISSEM)

    assert len(rows) == 1338

    by_index: dict = {}
    for row in rows:
        by_index[row["UPI Underlier Name"]] = (
            by_index.get(row["UPI Underlier Name"], 0) + 1
        )

    assert by_index["CDX.NA.HY"] == 360
    assert by_index["CDX.NA.IG"] == 359
    assert by_index["ITRAXX EUROPE"] == 252
    assert by_index["ITRAXX EUROPE CROSSOVER"] == 247
    assert len(by_index) == 15

    assert all(row["Expiration Date"] for row in rows)
    assert all(row["tenor"] for row in rows)

    tenors: dict = {}
    for row in rows:
        tenors[row["tenor"]] = tenors.get(row["tenor"], 0) + 1

    assert tenors["5Y"] == 1266
    assert tenors["10Y"] == 7
    assert tenors["3Y"] == 7


def test_extract_prints_excludes_swaptions_and_single_names(credits_records):
    rows = extract_prints(credits_records, DISSEM)
    fisns = {row["UPI FISN"] for row in rows}

    assert fisns == {"NA/CDS Corp Idx", "NA/CDS Corp Idx Tra", "NA/CDS Sov Idx"}

    source = {(r.get("UPI FISN") or "").strip() for r in credits_records}
    assert "NA/CDS Idx Swt" in source
    assert "NA/CDS Corp SN" in source
