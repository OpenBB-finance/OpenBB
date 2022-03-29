# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.insider import openinsider_model


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "val",
    [1, -1],
)
def test_check_valid_range(recorder, val):
    error_text = openinsider_model.check_valid_range(
        category="General",
        field="SharePriceMin",
        val=val,
        min_range=0,
        max_range=9999,
    )
    recorder.capture(error_text)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "d_date",
    [
        {
            "FilingDate": "MOCK_INVALID_DATE",
            "TradingDate": "MOCK_INVALID_DATE",
        },
        {
            "FilingDate": "All dates",
            "FilingDateFrom": "",
            "FilingDateTo": "",
            "TradingDate": "All dates",
            "TradingDateFrom": "",
            "TradingDateTo": "",
            "FilingDelayMin": "",
            "FilingDelayMax": "",
            "NDaysAgo": "",
        },
        {
            "FilingDate": "Custom",
            "FilingDateFrom": "",
            "FilingDateTo": "",
            "TradingDate": "Custom",
            "TradingDateFrom": "",
            "TradingDateTo": "",
            "FilingDelayMin": "",
            "FilingDelayMax": "",
            "NDaysAgo": "",
        },
    ],
)
def test_check_dates(recorder, d_date):
    error_text = openinsider_model.check_dates(d_date=d_date)
    recorder.capture(error_text)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "multiple, val",
    [(2, "4"), (1, "a")],
)
def test_check_valid_multiple(multiple, val, recorder):
    error_text = openinsider_model.check_valid_multiple(
        category="TransactionFiling",
        field="TradedMinK",
        val=val,
        multiple=multiple,
    )
    recorder.capture(error_text)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "l_possible_vals, val",
    [
        ([1, 2], "1"),
        ([1, 2], "3"),
    ],
)
def test_check_int_in_list(l_possible_vals, val, recorder):
    error_text = openinsider_model.check_int_in_list(
        category="Others",
        field="MaxResults",
        val=val,
        l_possible_vals=l_possible_vals,
    )
    recorder.capture(error_text)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "d_company_totals",
    [
        {
            "FilingsMin": "",
            "FilingsMax": "",
            "InsidersMin": "",
            "InsidersMax": "",
            "OfficersMin": "",
            "OfficersMax": "",
            "TradedMinK": "",
            "TradedMaxK": "",
            "OwnChangeMinPct": "",
            "OwnChangeMaxPct": "",
        },
    ],
)
def test_check_open_insider_company_totals(d_company_totals, recorder):
    error_text = openinsider_model.check_open_insider_company_totals(
        d_company_totals=d_company_totals
    )
    recorder.capture(error_text)


@pytest.mark.vcr(record_mode="none")
def test_get_open_insider_link(recorder):
    link = openinsider_model.get_open_insider_link(preset_loaded="template")
    recorder.capture(link)


@pytest.mark.vcr
def test_get_open_insider_data(recorder):
    ticker = "TSLA"
    link = f"http://openinsider.com/screener?s={ticker}"
    data_df = openinsider_model.get_open_insider_data(
        url=link,
        has_company_name=bool(not ticker),
    )

    recorder.capture(data_df)
