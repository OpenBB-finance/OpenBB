# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.cryptocurrency import crypto_api


def test_models():
    assert isinstance(crypto_api.defi.models, _models)
    assert isinstance(crypto_api.disc.models, _models)
    assert isinstance(crypto_api.dd.models, _models)
    assert isinstance(crypto_api.nft.models, _models)
    assert isinstance(crypto_api.onchain.models, _models)
    assert isinstance(crypto_api.ov.models, _models)
