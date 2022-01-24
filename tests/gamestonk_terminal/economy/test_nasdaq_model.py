# IMPORTATION STANDARD
from argparse import ArgumentTypeError

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import nasdaq_model


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


@pytest.mark.vcr(record_mode="none")
def test_check_country_code_type_error(recorder):
    with pytest.raises(ArgumentTypeError) as e:
        list_of_codes = ""
        nasdaq_model.check_country_code_type(list_of_codes=list_of_codes)

    recorder.capture(str(e))


@pytest.mark.vcr
def test_get_big_mac_index(recorder):
    result_df = nasdaq_model.get_big_mac_index(country_code="VNM")

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_big_mac_index_no_response(mocker):
    # MOCK GET
    attrs = {"status_code": 400}
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = nasdaq_model.get_big_mac_index(country_code="VNM")

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty
