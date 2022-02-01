# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import coindix_model


@pytest.mark.vcr
def test_get_defi_vaults(recorder):
    df = coindix_model.get_defi_vaults(
        chain=None,
        protocol=None,
        kind=None,
    )
    recorder.capture(df)


@pytest.mark.vcr(record_mode="none")
def test_get_defi_vaults_no_data(mocker):
    # MOCK GET
    attrs = {
        "status_code": 200,
        "json.return_value": {"data": []},
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    df = coindix_model.get_defi_vaults(
        chain=None,
        protocol=None,
        kind=None,
    )

    assert isinstance(df, pd.DataFrame)
    assert df.empty
