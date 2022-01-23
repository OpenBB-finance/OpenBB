# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import ark_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr
def test_get_ark_orders(recorder):
    result_df = ark_model.get_ark_orders()
    recorder.capture(result_df)


@pytest.mark.vcr
def test_add_order_total(recorder, mocker):
    yf_download = ark_model.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)
    df_orders = ark_model.get_ark_orders()
    result_df = ark_model.add_order_total(df_orders=df_orders.head(2))
    recorder.capture(result_df)
