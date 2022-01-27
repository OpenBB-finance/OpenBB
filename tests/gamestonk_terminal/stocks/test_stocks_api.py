# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.stocks import stocks_api


def test_models():
    assert isinstance(stocks_api.bt.models, _models)
    assert isinstance(stocks_api.ca.models, _models)
    assert isinstance(stocks_api.disc.models, _models)
    assert isinstance(stocks_api.dd.models, _models)
    assert isinstance(stocks_api.fa.models, _models)
    assert isinstance(stocks_api.gov.models, _models)
    assert isinstance(stocks_api.ins.models, _models)
    assert isinstance(stocks_api.options.models, _models)
    assert isinstance(stocks_api.qa.models, _models)
    assert isinstance(stocks_api.screener.models, _models)
    assert isinstance(stocks_api.sia.models, _models)
    assert isinstance(stocks_api.ta.models, _models)
