import pytest

from openbb_terminal.keys_controller import KeysController

controller = KeysController()


class MockCFG:
    def __init__(self, **kwargs):
        self.API_GITHUB_KEY = kwargs.get("GITHUB", None)
        self.API_KEY_ALPHAVANTAGE = kwargs.get("AV", None)
        self.API_KEY_FINANCIALMODELINGPREP = kwargs.get("FMP", None)
        self.API_KEY_QUANDL = kwargs.get("QUANDL", None)
        self.API_POLYGON_KEY = kwargs.get("POLYGON", None)
        self.API_FRED_KEY = kwargs.get("FRED", None)
        self.API_NEWS_TOKEN = kwargs.get("NEWS", None)
        self.TRADIER_TOKEN = kwargs.get("TRADIER", None)
        self.API_CMC_KEY = kwargs.get("CMC", None)
        self.API_FINNHUB_KEY = kwargs.get("FINNHUB", None)
        self.API_IEX_TOKEN = kwargs.get("IEX", None)
        self.API_REDDIT_CLIENT_ID = kwargs.get("REDDIT_CLIENT", None)
        self.API_REDDIT_CLIENT_SECRET = kwargs.get("REDDIT_SECRET", None)
        self.API_REDDIT_USERNAME = kwargs.get("REDDIT_USERNAME", None)
        self.API_REDDIT_PASSWORD = kwargs.get("REDDIT_PASSWORD", None)
        self.API_REDDIT_USER_AGENT = kwargs.get("REDDIT_USER", None)
        self.API_TWITTER_KEY = kwargs.get("TWITTER", None)
        self.API_TWITTER_SECRET_KEY = kwargs.get("TWITTER", None)
        self.API_TWITTER_BEARER_TOKEN = kwargs.get("TWITTER", None)
        self.RH_USERNAME = kwargs.get("RH", None)
        self.RH_PASSWORD = kwargs.get("RH", None)
        self.DG_USERNAME = kwargs.get("DEGIRO", None)
        self.DG_PASSWORD = kwargs.get("DEGIRO", None)
        self.DG_TOTP_SECRET = kwargs.get("DEGIRO", None)


@pytest.mark.vcr
@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_github_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(GITHUB=key))
    controller.check_github_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_av_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(AV=key))
    controller.check_av_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_fmp_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(FMP=key))
    controller.check_fmp_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_quandl_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(QUANDL=key))
    controller.check_quandl_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_polygon_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(POLYGON=key))
    controller.check_polygon_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_fred_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(FRED=key))
    controller.check_fred_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_news_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(NEWS=key))
    controller.check_news_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_tradier_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(TRADIER=key))
    controller.check_tradier_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_cmc_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(CMC=key))
    controller.check_cmc_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_finnhub_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(FINNHUB=key))
    controller.check_finnhub_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_iex_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(IEX=key))
    controller.check_iex_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_reddit_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(REDDIT_CLIENT=key))
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(REDDIT_SECRET=key))
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(REDDIT_USERNAME=key))
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(REDDIT_PASSWORD=key))
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(REDDIT_USER=key))
    controller.check_cmc_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_twitter_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(TWITTER=key))
    controller.check_twitter_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_rh_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(RH=key))
    controller.check_rh_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_degiro_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(DEGIRO=key))
    controller.check_degiro_key(output)
