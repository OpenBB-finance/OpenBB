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
def test__make_request_status_400(mocker):
    # MOCK GET
    attrs = {
        "status_code": 400,
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    with pytest.raises(Exception) as _:
        dappradar_model._make_request(url="MOCK_URL")


@pytest.mark.vcr(record_mode="none")
def test__make_request_value_error(mocker):
    # MOCK GET
    attrs = {
        "status_code": 200,
        "json.side_effect": UnicodeDecodeError,
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    with pytest.raises(ValueError) as _:
        dappradar_model._make_request(url="MOCK_URL")
