# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import nasdaq_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [("api_key", "MOCK_API_KEY")],
    }


@pytest.mark.vcr(record_mode="none")
def test_check_country_code_type(recorder):
    list_of_codes = "VNM,ARG,AUS"
    result_list = nasdaq_model.check_country_code_type(list_of_codes=list_of_codes)

    recorder.capture(result_list)


@pytest.mark.vcr
def test_get_big_mac_index(recorder):
    result_df = nasdaq_model.get_big_mac_index(country_code="VNM")

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_big_mac_index_no_response(mocker):
    # MOCK GET
    attrs = {"status_code": 400}
    mock_response = mocker.Mock(**attrs)
    mocker.patch(
        target="openbb_terminal.helper_funcs.requests.get",
        new=mocker.Mock(return_value=mock_response),
    )

    result_df = nasdaq_model.get_big_mac_index(country_code="VNM")

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty


@pytest.mark.vcr
def test_get_economic_calendar(recorder):
    result_df = nasdaq_model.get_economic_calendar(
        ["United States"], start_date="2022-10-20", end_date="2022-10-21"
    )

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_economic_calendar_bad_country_name(recorder):
    result_df = nasdaq_model.get_economic_calendar(
        "hidhf", start_date="2022-10-20", end_date="2022-10-21"
    )

    recorder.capture(result_df)


@pytest.mark.record_http
def test_get_big_mac_indices():
    result_df = nasdaq_model.get_big_mac_indices()

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty


def test_get_big_mac_indices_bad_response(mocker):
    # MOCK GET
    attrs = {"status_code": 400}
    mock_response = mocker.Mock(**attrs)
    mocker.patch(
        target="openbb_terminal.helper_funcs.requests.get",
        new=mocker.Mock(return_value=mock_response),
    )

    result_df = nasdaq_model.get_big_mac_indices()

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty


def test_get_country_names():
    result_list = nasdaq_model.get_country_names()

    assert isinstance(result_list, list)


def test_get_country_codes():
    nasdaq_model.get_country_codes()
