# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.discovery import dappradar_model

# pylint: disable=protected-access


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("get_top_nfts", dict()),
        # ("get_top_dexes", dict()),
        # ("get_top_games", dict()),
        # ("get_top_dapps", dict()),
    ],
)
def test_call_func(func, kwargs, recorder):
    result = getattr(dappradar_model, func)(**kwargs)

    recorder.capture(result)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test__make_request_status_400(mocker):
    # MOCK GET
    attrs = {
        "status_code": 400,
        "text": "MOCK_TEXT",
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    dappradar_model._make_request(url="MOCK_URL")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test__make_request_value_error(mocker):
    # MOCK GET
    attrs = {
        "status_code": 200,
        "text": "MOCK_TEXT",
        "json.side_effect": UnicodeDecodeError,
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    dappradar_model._make_request(url="MOCK_URL")
