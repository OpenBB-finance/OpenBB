# IMPORTATION STANDARD
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest
import requests

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import alphaquery_model


@pytest.mark.vcr
def test_get_put_call_ratio(recorder):
    result_df = alphaquery_model.get_put_call_ratio(
        ticker="PM",
        window=10,
        start_date=datetime.strptime("2021-12-01", "%Y-%m-%d"),
    )

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_put_call_ratio_invalid_status(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = alphaquery_model.get_put_call_ratio(
        ticker="PM",
        window=10,
        start_date=datetime.strptime("2021-12-01", "%Y-%m-%d"),
    )

    assert result_df.empty
