import pytest

from openbb_terminal.keys_controller import KeysController

controller = KeysController(menu_usage=False)

# pylint: disable=R0902,R0903,W1404


@pytest.fixture(autouse=True)
def no_change_env(mocker):
    mocker.patch("openbb_terminal.keys_model.dotenv.set_key")


class MockCFG:
    def __init__(self, **kwargs):
        self.API_GITHUB_KEY = kwargs.get("GITHUB", None)
        self.API_KEY_ALPHAVANTAGE = kwargs.get("AV", None)
        self.API_KEY_FINANCIALMODELINGPREP = kwargs.get("FMP", None)
        self.API_KEY_QUANDL = kwargs.get("QUANDL", None)
        self.API_POLYGON_KEY = kwargs.get("POLYGON", None)
        self.API_FRED_KEY = kwargs.get("FRED", None)
        self.API_NEWS_TOKEN = kwargs.get("NEWS", None)
        self.API_TRADIER_TOKEN = kwargs.get("TRADIER", None)
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
        self.OANDA_TOKEN = kwargs.get("OANDA", None)
        self.OANDA_ACCOUNT = kwargs.get("OANDA", None)
        self.API_BINANCE_KEY = kwargs.get("BINANCE", None)
        self.API_BINANCE_SECRET = kwargs.get("BINANCE", None)
        self.API_BITQUERY_KEY = kwargs.get("BITQUERY", None)
        self.API_SENTIMENTINVESTOR_TOKEN = kwargs.get("SI", None)
        self.API_COINBASE_KEY = kwargs.get("COINBASE", None)
        self.API_COINBASE_SECRET = kwargs.get("COINBASE", None)
        self.API_COINBASE_PASS_PHRASE = kwargs.get("COINBASE", None)
        self.API_WHALE_ALERT_KEY = kwargs.get("WALERT", None)
        self.API_GLASSNODE_KEY = kwargs.get("GLASSNODE", None)
        self.API_COINGLASS_KEY = kwargs.get("COINGLASS", None)
        self.API_CRYPTO_PANIC_KEY = kwargs.get("CPANIC", None)
        self.API_ETHPLORER_KEY = kwargs.get("ETHPLOR", None)
        self.API_SMARTSTAKE_TOKEN = kwargs.get("SMARTSTAKE", None)
        self.API_SMARTSTAKE_KEY = kwargs.get("SMARTSTAKE", None)
        self.API_SANTIMENT_KEY = kwargs.get("SANTIMENT", None)
        self.API_MESSARI_KEY = kwargs.get("MESSARI", None)


# TODO: fix tests for check_api_key
# TODO: add test for set_key and mykeys


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_av_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(AV=key))
    controller.check_key("av")


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_fmp_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(FMP=key))
    controller.check_key("fmp")


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_quandl_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(QUANDL=key))
    controller.check_quandl_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_polygon_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(POLYGON=key))
    controller.check_polygon_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_fred_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(FRED=key))
    controller.check_fred_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_news_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(NEWS=key))
    controller.check_news_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_tradier_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(TRADIER=key))
    controller.check_tradier_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_cmc_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(CMC=key))
    controller.check_cmc_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_finnhub_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(FINNHUB=key))
    controller.check_finnhub_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_iex_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(IEX=key))
    controller.check_iex_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_reddit_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(REDDIT_CLIENT=key))
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(REDDIT_SECRET=key))
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(REDDIT_USERNAME=key))
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(REDDIT_PASSWORD=key))
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(REDDIT_USER=key))
    controller.check_cmc_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_twitter_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(TWITTER=key))
    controller.check_twitter_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_rh_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(RH=key))
    controller.check_rh_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_degiro_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(DEGIRO=key))
    controller.check_degiro_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_oanda_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(OANDA=key))
    controller.check_oanda_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_binance_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(BINANCE=key))
    controller.check_binance_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_bitquery_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(BITQUERY=key))
    controller.check_bitquery_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_si_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(SI=key))
    controller.check_si_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_coinbase_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(COINBASE=key))
    controller.check_coinbase_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_walert_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(WALERT=key))
    controller.check_walert_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_glassnode_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(GLASSNODE=key))
    controller.check_glassnode_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_coinglass_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(COINGLASS=key))
    controller.check_coinglass_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_cpanic_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(CPANIC=key))
    controller.check_cpanic_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_ethplorer_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(ETHPLOR=key))
    controller.check_ethplorer_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_smartstake_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(SMARTSTAKE=key))
    controller.check_smartstake_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_santiment_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(SANTIMENT=key))
    controller.check_santiment_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_github_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(GITHUB=key))
    controller.check_github_key(show_output=output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_messari_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_model.cfg", MockCFG(MESSARI=key))
    controller.check_messari_key(show_output=output)
