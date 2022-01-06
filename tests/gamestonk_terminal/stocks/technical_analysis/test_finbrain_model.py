# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
import requests

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.technical_analysis import finbrain_model


@pytest.mark.vcr
def test_get_technical_summary_report(recorder):
    result = finbrain_model.get_technical_summary_report(ticker="PM")
    recorder.capture(result)


@pytest.mark.vcr(record_mode="none")
def test_get_technical_summary_report_invalid_status(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))
    result = finbrain_model.get_technical_summary_report(ticker="TSLA")

    assert result == ""


@pytest.mark.vcr(record_mode="none")
def test_get_technical_summary_report_invalid_json(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 200
    mocker.patch.object(
        target=mock_response,
        attribute="json",
        side_effect=lambda: dict(),
    )
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))
    result = finbrain_model.get_technical_summary_report(ticker="TSLA")

    assert result == ""
