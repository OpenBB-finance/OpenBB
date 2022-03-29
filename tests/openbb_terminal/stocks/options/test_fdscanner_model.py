# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
import requests

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import fdscanner_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
def test_unusual_options(recorder):
    result_tuple = fdscanner_model.unusual_options(num=5)
    result_tuple = (
        result_tuple[0],
        result_tuple[1].isoformat(),
    )

    recorder.capture_list(result_tuple)


@pytest.mark.vcr(record_mode="none")
def test_unusual_options_invalid_status(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_tuple = fdscanner_model.unusual_options(num=5)

    assert result_tuple[0].empty
    assert isinstance(result_tuple[1], str)
