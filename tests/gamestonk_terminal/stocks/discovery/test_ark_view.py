# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import ark_view

pytest.skip("skipping tests, ark views seems broken", allow_module_level=True)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "val",
    ["Buy", "Sell", "Mocked Value"],
)
def test_direction_color_red_green(val, recorder):
    result_txt = ark_view.direction_color_red_green(val=val)
    recorder.capture(result_txt)


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "kwargs_dict, use_color",
    [
        ({"num": 2}, True),
        ({"num": 2}, False),
        ({"num": 2, "sort_col": "open"}, False),
        ({"num": 2, "buys_only": True}, False),
        ({"num": 2, "sells_only": True}, False),
        ({"num": 2, "fund": "ARKK"}, False),
    ],
)
def test_ark_orders_view(kwargs_dict, mocker, use_color):
    yf_download = ark_view.ark_model.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    mocker.patch.object(target=ark_view.gtff, attribute="USE_COLOR", new=use_color)
    ark_view.ark_orders_view(**kwargs_dict)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_ark_orders_view_empty_df(mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.discovery.ark_view.ark_model.get_ark_orders",
        return_value=pd.DataFrame(),
    )
    ark_view.ark_orders_view(num=2)
