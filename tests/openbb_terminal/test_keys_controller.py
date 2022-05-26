import pytest
from openbb_terminal.cryptocurrency.coinbase_helpers import CoinbaseApiException

from openbb_terminal.keys_controller import KeysController

controller = KeysController(menu_usage=False)

# pylint: disable=R0902,R0903,W1404


@pytest.fixture(autouse=True)
def no_change_env(mocker):
    mocker.patch("openbb_terminal.keys_controller.dotenv.set_key")


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


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_oanda_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(OANDA=key))
    controller.check_oanda_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_binance_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(BINANCE=key))
    controller.check_binance_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_bitquery_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(BITQUERY=key))
    controller.check_bitquery_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_si_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(SI=key))
    controller.check_si_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_coinbase_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(COINBASE=key))
    if key == "REPLACE_ME":
        controller.check_coinbase_key(output)
    else:
        with pytest.raises(CoinbaseApiException):
            controller.check_coinbase_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_walert_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(WALERT=key))
    controller.check_walert_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_glassnode_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(GLASSNODE=key))
    controller.check_glassnode_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_coinglass_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(COINGLASS=key))
    controller.check_coinglass_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_cpanic_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(CPANIC=key))
    controller.check_cpanic_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_ethplorer_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(ETHPLOR=key))
    controller.check_ethplorer_key(output)


@pytest.mark.vcr
@pytest.mark.parametrize("key, output", [("REPLACE_ME", True), ("VALIDKEY", False)])
def test_check_smartstake_key(key, output, mocker):
    mocker.patch("openbb_terminal.keys_controller.cfg", MockCFG(SMARTSTAKE=key))
    controller.check_smartstake_key(output)


def test_print_help(mocker):
    mocker.patch("openbb_terminal.keys_controller.KeysController.check_coinbase_key")
    controller.print_help()


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_github(other):
    controller.call_github(other)


@pytest.mark.skip
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_av(other):
    controller.call_av(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_fmp(other):
    controller.call_fmp(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_quandl(other):
    controller.call_quandl(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_polygon(other):
    controller.call_polygon(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_fred(other):
    controller.call_fred(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_news(other):
    controller.call_news(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_tradier(other):
    controller.call_tradier(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_cmc(other):
    controller.call_cmc(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_finnhub(other):
    controller.call_finnhub(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_iex(other):
    controller.call_iex(other)


@pytest.mark.parametrize(
    "other", [[], ["-i", "1234", "-s", "4", "-u", "5", "-p", "6", "-a", "7"]]
)
def test_call_reddit(other):
    controller.call_reddit(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234", "-s", "4567", "-t", "890"]])
def test_call_twitter(other):
    controller.call_twitter(other)


@pytest.mark.parametrize("other", [[], ["-u", "1234", "-p", "4567"]])
def test_call_rh(other):
    controller.call_rh(other)


@pytest.mark.parametrize("other", [[], ["-u", "1234", "-p" "4567", "-s" "890"]])
def test_call_degiro(other):
    controller.call_degiro(other)


@pytest.mark.parametrize("other", [[], ["-a", "1234", "-t", "4567", "-at", "practice"]])
def test_call_oanda(other):
    controller.call_oanda(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234", "-s", "4567"]])
def test_call_binance(other):
    controller.call_binance(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_bitquery(other):
    controller.call_bitquery(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_si(other):
    controller.call_si(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234", "-s", "4567", "-p" "890"]])
def test_call_coinbase(other):
    if not other:
        controller.call_coinbase(other)
    else:
        with pytest.raises(CoinbaseApiException):
            controller.call_coinbase(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_walert(other):
    controller.call_walert(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_glassnode(other):
    controller.call_glassnode(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_coinglass(other):
    controller.call_coinglass(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_cpanic(other):
    controller.call_cpanic(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_ethplorer(other):
    controller.call_ethplorer(other)


@pytest.mark.parametrize("other", [[], ["-k", "1234", "-t", "456"]])
def test_call_smartstake(other):
    controller.call_smartstake(other)
