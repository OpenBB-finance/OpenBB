# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

from openbb_terminal.core.models.user_model import (
    CredentialsModel,
    PreferencesModel,
    ProfileModel,
    SourcesModel,
    UserModel,
)

# IMPORTATION INTERNAL
from openbb_terminal.keys_controller import KeysController

controller = KeysController(menu_usage=False)

# pylint: disable=R0902,R0903,W1404


@pytest.fixture(autouse=True)
def mock(mocker):
    mocker.patch(
        target="openbb_terminal.keys_model.set_credential",
    )
    mocker.patch("openbb_terminal.keys_model.write_to_dotenv")
    mocker.patch(
        target="openbb_terminal.keys_model.get_current_user",
        return_value=UserModel(
            profile=ProfileModel(),
            credentials=CredentialsModel(),
            preferences=PreferencesModel(),
            sources=SourcesModel(),
        ),
    )


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
        self.API_REDDIT_CLIENT_ID = kwargs.get("REDDIT_CLIENT", None)
        self.API_REDDIT_CLIENT_SECRET = kwargs.get("REDDIT_SECRET", None)
        self.API_REDDIT_USERNAME = kwargs.get("REDDIT_USERNAME", None)
        self.API_REDDIT_PASSWORD = kwargs.get("REDDIT_PASSWORD", None)
        self.API_REDDIT_USER_AGENT = kwargs.get("REDDIT_USER", None)
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
        self.API_MESSARI_KEY = kwargs.get("MESSARI", None)
        self.API_SANTIMENT_KEY = kwargs.get("SANTIMENT", None)
        self.API_TOKENTERMINAL_KEY = kwargs.get("TOKENTERMINAL", None)


@pytest.mark.skip
def test_print_help(mocker):
    mocker.patch("openbb_terminal.keys_controller.KeysController.check_keys_status")
    controller.print_help()


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_av(other):
    controller.call_av(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_fmp(other):
    controller.call_fmp(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_quandl(other):
    controller.call_quandl(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_polygon(other):
    controller.call_polygon(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_fred(other):
    controller.call_fred(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_news(other):
    controller.call_news(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_tradier(other):
    controller.call_tradier(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_cmc(other):
    controller.call_cmc(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"]])
def test_call_finnhub(other):
    controller.call_finnhub(other)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "other", [[], ["-i", "1234", "-s", "4", "-u", "5", "-p", "6", "-a", "7"]]
)
def test_call_reddit(other):
    controller.call_reddit(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-u", "1234", "-p", "4567"]])
def test_call_rh(other):
    controller.call_rh(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-u", "1234", "-p" "4567", "-s" "890"]])
def test_call_degiro(other):
    controller.call_degiro(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-a", "1234", "-t", "4567", "-at", "practice"]])
def test_call_oanda(other):
    controller.call_oanda(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234", "-s", "4567"]])
def test_call_binance(other):
    controller.call_binance(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_bitquery(other):
    controller.call_bitquery(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234", "-s", "4567", "-p" "890"]])
def test_call_coinbase(other):
    controller.call_coinbase(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_walert(other):
    controller.call_walert(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_glassnode(other):
    controller.call_glassnode(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_coinglass(other):
    controller.call_coinglass(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_cpanic(other):
    controller.call_cpanic(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_ethplorer(other):
    controller.call_ethplorer(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234", "-t", "456"]])
def test_call_smartstake(other):
    controller.call_smartstake(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_github(other):
    controller.call_github(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234"], ["1234"]])
def test_call_santiment(other):
    controller.call_santiment(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234", "-t", "456"]])
def test_call_messari(other):
    controller.call_messari(other)


@pytest.mark.vcr
@pytest.mark.parametrize("other", [[], ["-k", "1234", "-t", "456"]])
def test_call_tokenterminal(other):
    controller.call_tokenterminal(other)
