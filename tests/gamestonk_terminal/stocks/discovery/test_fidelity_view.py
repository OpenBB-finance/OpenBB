# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.discovery import fidelity_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "val",
    [
        "75% Buys, 25% Sells",
        "25% Buys, 75% Sells",
        "Mocked Value",
    ],
)
def test_lambda_buy_sell_ratio_color_red_green(val, recorder):
    result_txt = fidelity_view.lambda_buy_sell_ratio_color_red_green(val=val)
    recorder.capture(result_txt)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "val",
    ["-8.20 (-18.3363%)", "+8.20 (+18.3363%)"],
)
def test_lambda_price_change_color_red_green(val, recorder):
    result_txt = fidelity_view.lambda_price_change_color_red_green(val=val)
    recorder.capture(result_txt)


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "use_color",
    [True, False],
)
def test_orders_view(mocker, use_color):
    mocker.patch.object(target=fidelity_view.gtff, attribute="USE_COLOR", new=use_color)
    fidelity_view.orders_view(num=1, export="")
